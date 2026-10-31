"""Tests for upload validation before temporary-file writes."""

import pytest

import app
from career_coach.config import settings


class UploadedFileStub:
    def __init__(self, *, name: str, size: int):
        self.name = name
        self.size = size

    def getvalue(self):
        raise AssertionError("Oversized upload should be rejected before reading it")


def test_upload_size_is_checked_before_reading_contents():
    uploaded_file = UploadedFileStub(
        name="resume.pdf",
        size=settings.max_pdf_size_mb * 1024 * 1024 + 1,
    )

    with pytest.raises(ValueError, match="size limit"):
        app.process_resume_file(uploaded_file)


def test_unsupported_upload_type_is_rejected_before_reading_contents():
    uploaded_file = UploadedFileStub(name="resume.exe", size=1)

    with pytest.raises(ValueError, match="Unsupported resume format"):
        app.process_resume_file(uploaded_file)
