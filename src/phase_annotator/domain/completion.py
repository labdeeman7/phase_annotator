from dataclasses import dataclass

from phase_annotator.domain.models import AnnotationSession


@dataclass(frozen=True)
class CompletionSummary:
    duration_ms: int
    segment_count: int
    undefined_segment_count: int
    undefined_duration_ms: int
    has_session_note: bool


def summarize_completion(
    session: AnnotationSession, *, undefined_phase_id: int
) -> CompletionSummary:
    """Build the review facts shown before a human completion declaration."""
    undefined = [
        interval
        for interval in session.intervals
        if interval.phase_id == undefined_phase_id
    ]
    return CompletionSummary(
        duration_ms=session.video_info.duration_ms,
        segment_count=len(session.intervals),
        undefined_segment_count=len(undefined),
        undefined_duration_ms=sum(interval.duration_ms for interval in undefined),
        has_session_note=bool(session.session_notes.strip()),
    )
