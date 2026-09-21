import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from phase_annotator.config import load_default_ontology
from phase_annotator.domain.models import (
    AnnotationInterval,
    AnnotationSession,
    VideoInfo,
)
from phase_annotator.media import MediaMetadata
from phase_annotator.storage import (
    ExternalSidecarChangeError,
    LoadStatus,
    SessionPersistenceCoordinator,
    SessionPersistenceError,
)
from phase_annotator.storage.json_repo import JsonSessionRepository


def make_session(video_path: Path, **video_overrides) -> AnnotationSession:
    values = {
        "video_id": video_path.name,
        "duration_ms": 10_000,
        "source_path": str(video_path.resolve()),
        "file_size_bytes": video_path.stat().st_size,
        "file_modified_ns": video_path.stat().st_mtime_ns,
    }
    values.update(video_overrides)
    return AnnotationSession(
        video_info=VideoInfo(**values),
        annotator_id="synthetic_annotator",
        ontology_id="laparoscopic_appendectomy.default",
        ontology_version="1.0",
        intervals=[AnnotationInterval(0, 10_000, 1)],
    )


def actual_metadata(video_path: Path) -> MediaMetadata:
    stat = video_path.stat()
    return MediaMetadata(
        source_path=str(video_path.resolve()),
        file_size_bytes=stat.st_size,
        file_modified_ns=stat.st_mtime_ns,
    )


def test_sidecar_path_keeps_complete_video_filename(tmp_path: Path):
    video_path = tmp_path / "case.v2.mp4"

    assert SessionPersistenceCoordinator.sidecar_path_for(video_path) == (
        tmp_path / "case.v2.mp4.phase-annotations.json"
    )


def test_inspect_reports_new_when_sidecar_does_not_exist(tmp_path: Path):
    video_path = tmp_path / "case.mp4"
    video_path.write_bytes(b"video")
    coordinator = SessionPersistenceCoordinator(load_default_ontology())

    result = coordinator.inspect(video_path, actual_metadata(video_path))

    assert result.status is LoadStatus.NEW
    assert result.session is None


def test_save_and_inspect_matching_sidecar_round_trip(tmp_path: Path):
    video_path = tmp_path / "case.mp4"
    video_path.write_bytes(b"video")
    coordinator = SessionPersistenceCoordinator(load_default_ontology())
    sidecar = coordinator.sidecar_path_for(video_path)
    coordinator.bind(sidecar)
    coordinator.mark_dirty()

    coordinator.save(make_session(video_path))
    result = coordinator.inspect(video_path, actual_metadata(video_path))

    assert not coordinator.is_dirty
    assert result.status is LoadStatus.LOADED
    assert result.session is not None
    assert result.session.intervals == [AnnotationInterval(0, 10_000, 1)]


def test_filename_only_legacy_evidence_requires_confirmation(tmp_path: Path):
    video_path = tmp_path / "legacy.mp4"
    video_path.write_bytes(b"video")
    sidecar = SessionPersistenceCoordinator.sidecar_path_for(video_path)
    sidecar.write_text(
        json.dumps(
            {
                "video_info": {"video_id": "legacy.mp4", "duration_ms": 1000},
                "annotator_id": "synthetic",
                "ontology_id": "laparoscopic_appendectomy.default",
                "ontology_version": "1.0",
                "intervals": [
                    {"start_ms": 0, "end_ms": 1000, "phase_id": 1, "notes": ""}
                ],
                "schema_version": "1.0",
            }
        ),
        encoding="utf-8",
    )

    result = SessionPersistenceCoordinator(load_default_ontology()).inspect(
        video_path, actual_metadata(video_path)
    )

    assert result.status is LoadStatus.UNKNOWN_SOURCE
    assert result.session is not None


def test_conflicting_sidecar_is_blocked(tmp_path: Path):
    video_path = tmp_path / "case.mp4"
    video_path.write_bytes(b"video")
    coordinator = SessionPersistenceCoordinator(load_default_ontology())
    coordinator.bind(coordinator.sidecar_path_for(video_path))
    coordinator.save(make_session(video_path, file_size_bytes=999))

    result = coordinator.inspect(video_path, actual_metadata(video_path))

    assert result.status is LoadStatus.BLOCKED
    assert "file_size_bytes" in result.message


@pytest.mark.parametrize(
    "mutation",
    [
        lambda session: setattr(session, "schema_version", "99"),
        lambda session: setattr(session, "ontology_id", "other"),
        lambda session: session.intervals.append(AnnotationInterval(9_000, 10_000, 2)),
        lambda session: setattr(session, "resume_position_ms", 10_001),
    ],
)
def test_invalid_sidecar_is_blocked(tmp_path: Path, mutation):
    video_path = tmp_path / "case.mp4"
    video_path.write_bytes(b"video")
    session = make_session(video_path)
    mutation(session)
    sidecar = SessionPersistenceCoordinator.sidecar_path_for(video_path)
    from phase_annotator.storage import JsonSessionRepository

    JsonSessionRepository().save(session, sidecar)

    result = SessionPersistenceCoordinator(load_default_ontology()).inspect(
        video_path, actual_metadata(video_path)
    )

    assert result.status is LoadStatus.BLOCKED


def test_validation_rejects_inconsistent_lifecycle_metadata(tmp_path: Path):
    video_path = tmp_path / "case.mp4"
    video_path.write_bytes(b"video")
    session = make_session(video_path)
    session.completed_by = "reviewer"

    errors = SessionPersistenceCoordinator(
        load_default_ontology()
    ).validation_errors(session)

    assert "draft session contains completion metadata" in errors


def test_save_failure_leaves_coordinator_dirty(tmp_path: Path):
    class FailingRepository:
        def save(self, session, filepath):
            raise OSError("disk full")

    video_path = tmp_path / "case.mp4"
    video_path.write_bytes(b"video")
    coordinator = SessionPersistenceCoordinator(
        load_default_ontology(), repository=FailingRepository()
    )
    coordinator.bind(coordinator.sidecar_path_for(video_path))

    with pytest.raises(SessionPersistenceError, match="disk full"):
        coordinator.save(make_session(video_path))

    assert coordinator.is_dirty


def test_external_sidecar_change_is_not_overwritten(tmp_path: Path):
    video_path = tmp_path / "case.mp4"
    video_path.write_bytes(b"video")
    coordinator = SessionPersistenceCoordinator(load_default_ontology())
    sidecar = coordinator.sidecar_path_for(video_path)
    coordinator.bind(sidecar)
    session = make_session(video_path)
    coordinator.save(session)
    sidecar.write_text(sidecar.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(ExternalSidecarChangeError, match="changed outside"):
        coordinator.save(session)

    assert coordinator.is_dirty


def test_changed_run_snapshot_is_collision_safe(tmp_path: Path):
    video_path = tmp_path / "case.mp4"
    video_path.write_bytes(b"video")
    coordinator = SessionPersistenceCoordinator(load_default_ontology())
    coordinator.bind(coordinator.sidecar_path_for(video_path))
    session = make_session(video_path)
    coordinator.save(session)
    coordinator.mark_annotation_changed()
    timestamp = datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc)

    first = coordinator.archive_snapshot(session, timestamp=timestamp)
    coordinator.mark_annotation_changed()
    second = coordinator.archive_snapshot(session, timestamp=timestamp)

    assert first.parent == coordinator.history_dir_for(video_path)
    assert first.name == "2026-09-21T12-00-00.000000Z.json"
    assert second.name == "2026-09-21T12-00-00.000000Z-1.json"
    assert not coordinator.annotation_changed


def test_snapshot_failure_preserves_changed_run_state(tmp_path: Path):
    class SnapshotFailingRepository:
        def save(self, session, filepath):
            if filepath.parent.name.endswith("phase-annotations-history"):
                raise OSError("history unavailable")
            JsonSessionRepository().save(session, filepath)

        def load(self, filepath):
            return JsonSessionRepository().load(filepath)

    video_path = tmp_path / "case.mp4"
    video_path.write_bytes(b"video")
    coordinator = SessionPersistenceCoordinator(
        load_default_ontology(), repository=SnapshotFailingRepository()
    )
    coordinator.bind(coordinator.sidecar_path_for(video_path))
    session = make_session(video_path)
    coordinator.save(session)
    coordinator.mark_annotation_changed()

    from phase_annotator.storage import HistorySnapshotError

    with pytest.raises(HistorySnapshotError, match="history unavailable"):
        coordinator.archive_snapshot(session)

    assert coordinator.annotation_changed
    assert not coordinator.is_dirty
