import pytest
from phase_annotator.domain.models import (
    AnnotationInterval,
    AnnotationSession,
    VideoInfo,
)


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
    assert session.schema_version == "1.3"
    assert session.created_by == "researcher_1"
    assert session.last_edited_by is None


def test_annotation_session_lifecycle_defaults_and_validation():
    video = VideoInfo("synthetic.mp4", duration_ms=1_000)
    session = AnnotationSession(video, annotator_id="annotator")

    assert session.status == "draft"
    assert session.completed_at is None
    assert session.resume_position_ms == 0

    with pytest.raises(ValueError, match="completed sessions require"):
        AnnotationSession(video, "annotator", status="completed")
    with pytest.raises(ValueError, match="draft sessions cannot"):
        AnnotationSession(video, "annotator", completed_at=1.0)
    with pytest.raises(ValueError, match="resume_position_ms"):
        AnnotationSession(video, "annotator", resume_position_ms=-1)


def test_video_info_distinguishes_assumed_from_measured_cfr():
    assumed = VideoInfo(
        video_id="assumed.mp4",
        duration_ms=1_000,
        fps=30.0,
        fps_source="assumed",
        frame_rate_mode="unknown",
    )
    measured_cfr = VideoInfo(
        video_id="measured.mp4",
        duration_ms=1_000,
        fps=25.0,
        fps_source="ffprobe",
        frame_rate_mode="cfr",
    )

    assert assumed.frame_numbers_are_estimated
    assert not measured_cfr.frame_numbers_are_estimated


@pytest.mark.parametrize(
    "overrides",
    [
        {"duration_ms": -1},
        {"fps": 0},
        {"width": 0},
        {"height": -1},
        {"file_size_bytes": -1},
        {"file_modified_ns": -1},
        {"fps": 30.0, "fps_source": "invented"},
        {"frame_rate_mode": "sometimes"},
        {"fps": None, "fps_source": "assumed"},
        {"fps": None, "frame_rate_mode": "cfr"},
    ],
)
def test_video_info_rejects_invalid_metadata(overrides):
    values = {"video_id": "synthetic.mp4", "duration_ms": 1_000}
    values.update(overrides)

    with pytest.raises(ValueError):
        VideoInfo(**values)
