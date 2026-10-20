"""Typed "Other" segments: a short tag at the start of the segment note.

Round-two rule (OAUTHC, 2026-10-20): phase 0 is "Other", and its note starts with a tag
such as ``[DEIDENTIFY]`` followed by free text, so analysis code can parse the type
without a schema change. A note without a tag is a plain Other described in words.
"""

import re
from typing import Optional, Tuple

TAG_PATTERN = re.compile(r"^\[([A-Z][A-Z0-9_]*)\][ \t]*")
DEIDENTIFY_TAG = "DEIDENTIFY"


def split_tag(notes: str) -> Tuple[Optional[str], str]:
    """Return (tag or None, remaining text) for a segment note."""
    match = TAG_PATTERN.match(notes)
    if match is None:
        return None, notes
    return match.group(1), notes[match.end() :]


def compose_note(tag: Optional[str], text: str) -> str:
    """Build a segment note with the tag first, as the analysis side parses it."""
    text = text.strip()
    if not tag:
        return text
    return f"[{tag}] {text}".rstrip()
