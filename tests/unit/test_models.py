import pytest
from phase_annotator.domain.models import AnnotationInterval, AnnotationSession, VideoInfo


def test_annotation_interval_duration():
    interval = AnnotationInterval(start_ms=1000, end_ms=5000, phase_id=1, notes="Initial view")
    assert interval.duration_ms == 4000
    assert interval.phase_id == 1


def test_annotation_interval_invalid_times():
    with pytest.raises(ValueError, match="must be less than end_ms"):
        AnnotationInterval(start_ms=5000, end_ms=1000, phase_id=1)


def test_annotation_session_creation():
    video = VideoInfo(video_id="appendectomy_case_01.mp4", duration_ms=120000, fps=30.0)
    session = AnnotationSession(video_info=video, annotator_id="researcher_1")

    assert session.video_info.video_id == "appendectomy_case_01.mp4"
    assert session.annotator_id == "researcher_1"
    assert len(session.intervals) == 0
