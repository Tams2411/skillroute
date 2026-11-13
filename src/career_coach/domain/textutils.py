"""Text utilities shared by the extraction services."""

from __future__ import annotations


def snap_slice(text: str, start: int, end: int) -> str:
    """Return ``text[start:end]`` adjusted to start and end on word boundaries.

    Evidence snippets are sliced at a fixed character offset around a skill
    mention, which lands mid-word (``"ience with Apache Spark"``). Snapping to
    whitespace keeps the quoted phrase readable.
    """
    if start > 0:
        boundary = text.find(" ", start)
        start = boundary + 1 if boundary != -1 else start
    if end < len(text):
        boundary = text.rfind(" ", 0, end)
        end = boundary if boundary > start else end
    return text[start:end].strip()
