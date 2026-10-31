"""Tests for resume file limits and safe parser errors."""

import pytest

from career_coach.services.resume_parser import ResumeParser


def test_oversized_resume_file_is_rejected(temp_txt_file, monkeypatch):
    monkeypatch.setattr(ResumeParser, "MAX_SIZE_BYTES", 1)

    with pytest.raises(ValueError, match="File too large"):
        ResumeParser().extract_text(temp_txt_file)


def test_pdf_page_limit_is_reported_without_fallback(temp_pdf_file, monkeypatch):
    monkeypatch.setattr(ResumeParser, "MAX_PAGES", 0)

    with pytest.raises(ValueError, match="PDF has 1 pages"):
        ResumeParser().extract_text(temp_pdf_file)


def test_malformed_pdf_uses_safe_error_message(tmp_path):
    malformed_pdf = tmp_path / "malformed.pdf"
    malformed_pdf.write_bytes(b"not a PDF")

    with pytest.raises(ValueError, match="PDF extraction failed"):
        ResumeParser().extract_text(malformed_pdf)


def test_resume_parser_logs_neither_filename_nor_resume_text(tmp_path, caplog):
    filename = "candidate-private@example.com.txt"
    sensitive_text = "Candidate phone number 555-123-4567"
    resume_path = tmp_path / filename
    resume_path.write_text(sensitive_text, encoding="utf-8")

    ResumeParser().extract_text(resume_path)

    assert filename not in caplog.text
    assert sensitive_text not in caplog.text
