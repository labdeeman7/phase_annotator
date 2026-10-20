from dataclasses import dataclass

from phase_annotator.domain.models import AnnotationSession
from phase_annotator.domain.other_types import DEIDENTIFY_TAG, split_tag

# OAUTHC round-two rules (2026-10-20): Other is for activities of 30 s or more, except
# footage marked for de-identification; signing off means the privacy check was done.
OTHER_MINIMUM_MS = 30_000
PRIVACY_CHECKED = "Privacy checked"


@dataclass(frozen=True)
class CompletionSummary:
    duration_ms: int
    segment_count: int
    undefined_segment_count: int
    undefined_duration_ms: int
    has_session_note: bool
    # Other segments with neither a type tag nor any description.
    undescribed_other_count: int = 0
    # Other segments shorter than the 30 s rule, de-identification marks excepted.
    short_other_count: int = 0
    has_privacy_check: bool = False


def summarize_completion(
    session: AnnotationSession, *, undefined_phase_id: int
) -> CompletionSummary:
    """Build the review facts shown before a human completion declaration."""
    undefined = [
        interval
        for interval in session.intervals
        if interval.phase_id == undefined_phase_id
    ]
    typed = [(interval, *split_tag(interval.notes)) for interval in undefined]
    return CompletionSummary(
        duration_ms=session.video_info.duration_ms,
        segment_count=len(session.intervals),
        undefined_segment_count=len(undefined),
        undefined_duration_ms=sum(interval.duration_ms for interval in undefined),
        has_session_note=bool(session.session_notes.strip()),
        undescribed_other_count=sum(
            1 for _, tag, text in typed if tag is None and not text.strip()
        ),
        short_other_count=sum(
            1
            for interval, tag, _ in typed
            if tag != DEIDENTIFY_TAG and interval.duration_ms < OTHER_MINIMUM_MS
        ),
        has_privacy_check=PRIVACY_CHECKED.casefold()
        in session.session_notes.casefold(),
    )


def with_privacy_check(session_notes: str) -> str:
    """The video note with the sign-off line added once."""
    if PRIVACY_CHECKED.casefold() in session_notes.casefold():
        return session_notes
    return f"{session_notes.rstrip()}\n{PRIVACY_CHECKED}".lstrip()
