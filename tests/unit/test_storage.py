import json
from pathlib import Path
import pytest

from phase_annotator.domain.models import AnnotationInterval, AnnotationSession, VideoInfo
from phase_annotator.storage.json_repo import JsonSessionRepository


def test_save_session_atomic(tmp_path: Path):
    repo = JsonSessionRepository()
    video = VideoInfo(video_id="case_01.mp4", duration_ms=60000, fps=30.0)
    session = AnnotationSession(video_info=video, annotator_id="dr_smith")
    session.add_interval(AnnotationInterval(start_ms=0, end_ms=5000, phase_id=1, notes="Start"))

    save_file = tmp_path / "session_case_01.json"
    repo.save(session, save_file)

    assert save_file.exists()

    # Inspect raw JSON content
    with open(save_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["annotator_id"] == "dr_smith"
    assert data["video_info"]["video_id"] == "case_01.mp4"
    assert len(data["intervals"]) == 1
    assert data["intervals"][0]["phase_id"] == 1


def test_load_session(tmp_path: Path):
    repo = JsonSessionRepository()
    video = VideoInfo(video_id="case_02.mp4", duration_ms=120000, fps=25.0)
    original_session = AnnotationSession(video_info=video, annotator_id="researcher_2")
    original_session.add_interval(AnnotationInterval(start_ms=0, end_ms=4000, phase_id=1))
    original_session.add_interval(AnnotationInterval(start_ms=4000, end_ms=12000, phase_id=2))

    save_file = tmp_path / "session_case_02.json"
    repo.save(original_session, save_file)

    loaded_session = repo.load(save_file)
    assert loaded_session.annotator_id == "researcher_2"
    assert loaded_session.video_info.video_id == "case_02.mp4"
    assert loaded_session.video_info.fps == 25.0
    assert len(loaded_session.intervals) == 2
    assert loaded_session.intervals[1].phase_id == 2
    assert loaded_session.intervals[1].duration_ms == 8000
