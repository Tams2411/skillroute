"""Tests for optional Gemini interview feedback and its failure handling."""

import io
import json
from urllib.error import HTTPError, URLError

import pytest

from career_coach.domain.schemas import InterviewSession
from career_coach.services.gemini_interview_service import (
    GeminiFeedbackError,
    generate_gemini_interview_feedback,
)
from career_coach.services.interview_service import get_rubric_for_question


def _session() -> InterviewSession:
    return InterviewSession(
        target_role="Platform Engineer",
        category="terraform",
        question="How would you organize Terraform state?",
        answer="I would isolate state by environment.",
    )


def _response_body(session: InterviewSession) -> bytes:
    rubric = get_rubric_for_question(
        session.question,
        session.category,
        session.question_type,
    )
    feedback = {
        "scores": [
            {
                "criterion": criterion.value,
                "score": 3,
                "evidence": "You described isolating state by environment.",
                "improvement_action": "Explain how you would protect state access.",
            }
            for criterion in rubric
        ],
        "overall_feedback": "The answer identifies a useful state boundary.",
        "practice_task": "Add a sentence about access control and recovery.",
    }
    return json.dumps(
        {"candidates": [{"content": {"parts": [{"text": json.dumps(feedback)}]}}]}
    ).encode("utf-8")


def test_gemini_request_keeps_key_out_of_url_and_validates_rubric(monkeypatch):
    session = _session()
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return io.BytesIO(_response_body(session))

    monkeypatch.setattr(
        "career_coach.services.gemini_interview_service.urlopen",
        fake_urlopen,
    )

    feedback = generate_gemini_interview_feedback(
        "test-key-not-for-logs",
        session,
        session.answer,
    )

    request = captured["request"]
    request_payload = json.loads(request.data)
    prompt = request_payload["contents"][0]["parts"][0]["text"]
    response_format = request_payload["generationConfig"]["responseFormat"]["text"]
    assert "test-key-not-for-logs" not in request.full_url
    assert request.get_header("X-goog-api-key") == "test-key-not-for-logs"
    assert captured["timeout"] == 30
    assert response_format["mimeType"] == "APPLICATION_JSON"
    assert response_format["schema"]["type"] == "object"
    assert session.question in prompt
    assert session.answer in prompt
    assert len(feedback.scores) == len(
        get_rubric_for_question(session.question, session.category, session.question_type)
    )
    assert feedback.overall_feedback


def test_missing_key_fails_before_network_request(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("Gemini must not be called without a key")

    monkeypatch.setattr(
        "career_coach.services.gemini_interview_service.urlopen",
        fail_if_called,
    )

    with pytest.raises(GeminiFeedbackError) as error:
        generate_gemini_interview_feedback("", _session(), "My answer")

    assert error.value.code == "missing_api_key"


def test_invalid_key_characters_fail_before_network_request(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("Invalid API key must not reach the network")

    monkeypatch.setattr(
        "career_coach.services.gemini_interview_service.urlopen",
        fail_if_called,
    )

    with pytest.raises(GeminiFeedbackError) as error:
        generate_gemini_interview_feedback("invalid\r\nkey", _session(), "My answer")

    assert error.value.code == "invalid_api_key"


@pytest.mark.parametrize(
    ("http_status", "expected_code"),
    [(403, "invalid_api_key"), (429, "rate_limited")],
)
def test_provider_http_errors_are_safe_and_classified(
    monkeypatch,
    http_status,
    expected_code,
):
    def raise_http_error(*args, **kwargs):
        raise HTTPError("https://example.invalid", http_status, "provider error", None, None)

    monkeypatch.setattr(
        "career_coach.services.gemini_interview_service.urlopen",
        raise_http_error,
    )

    with pytest.raises(GeminiFeedbackError) as error:
        generate_gemini_interview_feedback("private-key", _session(), "My answer")

    assert error.value.code == expected_code
    assert "private-key" not in str(error.value)


def test_network_failure_is_reported_as_provider_unavailable(monkeypatch):
    def raise_network_error(*args, **kwargs):
        raise URLError("connection failed")

    monkeypatch.setattr(
        "career_coach.services.gemini_interview_service.urlopen",
        raise_network_error,
    )

    with pytest.raises(GeminiFeedbackError) as error:
        generate_gemini_interview_feedback("private-key", _session(), "My answer")

    assert error.value.code == "connection_error"
    assert "private-key" not in str(error.value)


def test_incomplete_rubric_response_is_rejected(monkeypatch):
    session = _session()
    response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "scores": [
                                        {
                                            "criterion": "technical_accuracy",
                                            "score": 4,
                                            "evidence": "A claim.",
                                            "improvement_action": "Add detail.",
                                        }
                                    ],
                                    "overall_feedback": "Good start.",
                                    "practice_task": "Practice more.",
                                }
                            )
                        }
                    ]
                }
            }
        ]
    }
    monkeypatch.setattr(
        "career_coach.services.gemini_interview_service.urlopen",
        lambda *args, **kwargs: io.BytesIO(json.dumps(response).encode("utf-8")),
    )

    with pytest.raises(GeminiFeedbackError) as error:
        generate_gemini_interview_feedback("valid-format-key", session, "My answer")

    assert error.value.code == "invalid_response"
