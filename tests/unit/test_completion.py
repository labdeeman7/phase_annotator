from phase_annotator.domain.completion import summarize_completion
from phase_annotator.domain.models import (
    AnnotationInterval,
    AnnotationSession,
    VideoInfo,
)


def test_completion_summary_reports_undefined_footage_and_video_note():
    session = AnnotationSession(
        VideoInfo("case.mp4", 10_000),
        "annotator",
        intervals=[
            AnnotationInterval(0, 2_000, 0),
            AnnotationInterval(2_000, 7_000, 1),
            AnnotationInterval(7_000, 10_000, 0),
        ],
        session_notes="Reviewed unusual anatomy",
    )

    summary = summarize_completion(session, undefined_phase_id=0)

    assert summary.duration_ms == 10_000
    assert summary.segment_count == 3
    assert summary.undefined_segment_count == 2
    assert summary.undefined_duration_ms == 5_000
    assert summary.has_session_note
