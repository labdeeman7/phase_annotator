import json
from pathlib import Path
import pytest

from phase_annotator.domain.models import AnnotationInterval, AnnotationSession, VideoInfo
from phase_annotator.storage.json_repo import JsonSessionRepository


def test_save_session_atomic(tmp_path: Path):
    repo = JsonSessionRepository()
    video = VideoInfo(
        video_id="case_01.mp4",
        duration_ms=60000,
        fps=30.0,
        width=1920,
        height=1080,
        source_path=str((tmp_path / "case_01.mp4").resolve()),
        file_size_bytes=123456,
        file_modified_ns=987654321,
        fps_source="qt",
        frame_rate_mode="unknown",
    )
    session = AnnotationSession(
        video_info=video,
        annotator_id="dr_smith",
        ontology_id="laparoscopic_appendectomy.default",
        ontology_version="1.0",
    )
    session.add_interval(AnnotationInterval(start_ms=0, end_ms=5000, phase_id=1, notes="Start"))

    save_file = tmp_path / "session_case_01.json"
    repo.save(session, save_file)

    assert save_file.exists()

    # Inspect raw JSON content
    with open(save_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["annotator_id"] == "dr_smith"
    assert data["video_info"]["video_id"] == "case_01.mp4"
    assert data["video_info"]["source_path"] == video.source_path
    assert data["video_info"]["file_size_bytes"] == 123456
    assert data["video_info"]["file_modified_ns"] == 987654321
    assert data["video_info"]["fps_source"] == "qt"
    assert data["video_info"]["frame_rate_mode"] == "unknown"
    assert data["schema_version"] == "1.4"
    assert data["created_by"] == "dr_smith"
    assert data["last_edited_by"] is None
    assert data["status"] == "draft"
    assert data["completed_at"] is None
    assert data["completed_by"] is None
    assert data["session_notes"] == ""
    assert data["resume_position_ms"] == 0
    assert data["ontology_id"] == "laparoscopic_appendectomy.default"
    assert data["ontology_version"] == "1.0"
    assert len(data["intervals"]) == 1
    assert data["intervals"][0]["phase_id"] == 1


def test_load_session(tmp_path: Path):
    repo = JsonSessionRepository()
    video = VideoInfo(video_id="case_02.mp4", duration_ms=120000, fps=25.0)
    original_session = AnnotationSession(
        video_info=video,
        annotator_id="researcher_2",
        ontology_id="laparoscopic_appendectomy.default",
        ontology_version="1.0",
    )
    original_session.add_interval(AnnotationInterval(start_ms=0, end_ms=4000, phase_id=1))
    original_session.add_interval(AnnotationInterval(start_ms=4000, end_ms=12000, phase_id=2))

    save_file = tmp_path / "session_case_02.json"
    repo.save(original_session, save_file)

    loaded_session = repo.load(save_file)
    assert loaded_session.annotator_id == "researcher_2"
    assert loaded_session.video_info.video_id == "case_02.mp4"
    assert loaded_session.video_info.fps == 25.0
    assert loaded_session.ontology_id == "laparoscopic_appendectomy.default"
    assert loaded_session.ontology_version == "1.0"
    assert len(loaded_session.intervals) == 2
    assert loaded_session.intervals[1].phase_id == 2
    assert loaded_session.intervals[1].duration_ms == 8000


def test_completed_session_and_video_note_round_trip(tmp_path: Path):
    repository = JsonSessionRepository()
    path = tmp_path / "completed.json"
    original = AnnotationSession(
        video_info=VideoInfo("case.mp4", 1_000),
        annotator_id="creator",
        intervals=[AnnotationInterval(0, 1_000, 1)],
        status="completed",
        completed_at=123.0,
        completed_by="reviewer",
        session_notes="Unexpected anatomy was reviewed.",
    )

    repository.save(original, path)
    loaded = repository.load(path)

    assert loaded.status == "completed"
    assert loaded.completed_at == 123.0
    assert loaded.completed_by == "reviewer"
    assert loaded.session_notes == "Unexpected anatomy was reviewed."


def test_legacy_completed_session_defaults_completer_to_legacy_annotator(
    tmp_path: Path,
):
    path = tmp_path / "legacy_completed.json"
    path.write_text(
        json.dumps(
            {
                "video_info": {"video_id": "case.mp4", "duration_ms": 1_000},
                "annotator_id": "legacy_reviewer",
                "intervals": [
                    {"start_ms": 0, "end_ms": 1_000, "phase_id": 1, "notes": ""}
                ],
                "status": "completed",
                "completed_at": 123.0,
                "schema_version": "1.2",
            }
        ),
        encoding="utf-8",
    )

    loaded = JsonSessionRepository().load(path)

    assert loaded.completed_by == "legacy_reviewer"
    assert loaded.session_notes == ""


def test_load_legacy_session_defaults_missing_ontology_identity(tmp_path: Path):
    save_file = tmp_path / "legacy_session.json"
    save_file.write_text(
        json.dumps(
            {
                "video_info": {
                    "video_id": "legacy_case.mp4",
                    "duration_ms": 1000,
                    "fps": 30.0,
                    "width": None,
                    "height": None,
                },
                "annotator_id": "legacy_annotator",
                "intervals": [
                    {"start_ms": 0, "end_ms": 1000, "phase_id": 1, "notes": ""}
                ],
                "schema_version": "1.0",
                "created_at": 0.0,
                "updated_at": 0.0,
            }
        ),
        encoding="utf-8",
    )

    session = JsonSessionRepository().load(save_file)

    assert session.ontology_id == ""
    assert session.ontology_version == ""
    assert session.schema_version == "1.0"
    assert session.video_info.source_path is None
    assert session.video_info.file_size_bytes is None
    assert session.video_info.file_modified_ns is None
    assert session.video_info.fps_source == "unknown"
    assert session.video_info.frame_rate_mode == "unknown"
    assert session.video_info.frame_numbers_are_estimated
    assert session.status == "draft"
    assert session.completed_at is None
    assert session.completed_by is None
    assert session.session_notes == ""
    assert session.resume_position_ms == 0
    assert session.created_by == "legacy_annotator"
    assert session.last_edited_by == "legacy_annotator"


def test_load_rejects_unknown_fields_instead_of_silently_dropping_them(
    tmp_path: Path,
):
    path = tmp_path / "future.json"
    path.write_text(
        json.dumps(
            {
                "video_info": {
                    "video_id": "case.mp4",
                    "duration_ms": 1000,
                    "fps": 30.0,
                    "future_video_field": "keep me",
                },
                "annotator_id": "annotator",
                "ontology_id": "laparoscopic_appendectomy.default",
                "ontology_version": "1.0",
                "intervals": [],
                "schema_version": "1.2",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown fields in video_info"):
        JsonSessionRepository().load(path)


def test_rejected_work_session_prototype_data_is_preserved_but_not_added_new(
    tmp_path: Path,
):
    repository = JsonSessionRepository()
    session = AnnotationSession(
        VideoInfo("case.mp4", 1_000),
        "annotator_A",
        intervals=[AnnotationInterval(0, 1_000, 1)],
        _legacy_work_sessions=[
            {
                "annotator_id": "annotator_A",
                "started_at": 1.0,
                "ended_at": 2.0,
            }
        ],
    )
    migrated_path = tmp_path / "migrated.json"
    new_path = tmp_path / "new.json"

    repository.save(session, migrated_path)
    loaded = repository.load(migrated_path)
    repository.save(loaded, migrated_path)
    repository.save(
        AnnotationSession(VideoInfo("new.mp4", 1_000), "annotator_B"), new_path
    )

    migrated = json.loads(migrated_path.read_text(encoding="utf-8"))
    new = json.loads(new_path.read_text(encoding="utf-8"))
    assert migrated["work_sessions"][0]["annotator_id"] == "annotator_A"
    assert "work_sessions" not in new
