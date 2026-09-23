from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

from phase_annotator.domain.models import (
    CURRENT_SESSION_SCHEMA_VERSION,
    AnnotationSession,
)
from phase_annotator.domain.ontology import PhaseOntology
from phase_annotator.domain.validation import validate_contiguous_coverage
from phase_annotator.media import (
    MediaMetadata,
    SourceComparison,
    SourceMatchStatus,
    compare_video_source,
)
from phase_annotator.storage.json_repo import JsonSessionRepository

SUPPORTED_SESSION_SCHEMA_VERSIONS = frozenset(
    {"1.0", "1.1", "1.2", "1.3", CURRENT_SESSION_SCHEMA_VERSION}
)


class LoadStatus(str, Enum):
    NEW = "new"
    LOADED = "loaded"
    UNKNOWN_SOURCE = "unknown_source"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class LoadResult:
    status: LoadStatus
    sidecar_path: Path
    session: Optional[AnnotationSession] = None
    message: str = ""
    source_comparison: Optional[SourceComparison] = None


class SessionPersistenceError(RuntimeError):
    pass


class ExternalSidecarChangeError(SessionPersistenceError):
    pass


class HistorySnapshotError(SessionPersistenceError):
    pass


@dataclass(frozen=True)
class FileRevision:
    size_bytes: int
    modified_ns: int


class SessionPersistenceCoordinator:
    """Own sidecar policy and saved/dirty state above the JSON repository."""

    def __init__(
        self,
        ontology: PhaseOntology,
        repository: Optional[JsonSessionRepository] = None,
    ) -> None:
        self._ontology = ontology
        self._repository = repository or JsonSessionRepository()
        self._sidecar_path: Optional[Path] = None
        self._dirty = False
        self._annotation_changed = False
        self._expected_revision: Optional[FileRevision] = None

    @property
    def sidecar_path(self) -> Optional[Path]:
        return self._sidecar_path

    @property
    def is_dirty(self) -> bool:
        return self._dirty

    @property
    def annotation_changed(self) -> bool:
        return self._annotation_changed

    @staticmethod
    def sidecar_path_for(video_path: Path) -> Path:
        return video_path.with_name(f"{video_path.name}.phase-annotations.json")

    @staticmethod
    def history_dir_for(video_path: Path) -> Path:
        return video_path.with_name(f"{video_path.name}.phase-annotations-history")

    def inspect(self, video_path: Path, actual: MediaMetadata) -> LoadResult:
        sidecar_path = self.sidecar_path_for(video_path)
        if not sidecar_path.exists():
            return LoadResult(LoadStatus.NEW, sidecar_path)
        try:
            session = self._repository.load(sidecar_path)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            return LoadResult(
                LoadStatus.BLOCKED,
                sidecar_path,
                message=f"The annotation sidecar is invalid: {exc}",
            )

        # Preserve the loaded session only for this explicit mismatch so the
        # composition/UI layer can translate both ontology IDs into friendly
        # procedure names without coupling storage to packaged configuration.
        if session.ontology_id != self._ontology.ontology_id:
            return LoadResult(
                LoadStatus.BLOCKED,
                sidecar_path,
                session=session,
                message="The annotation sidecar uses a different procedure.",
            )

        errors = self.validation_errors(session)
        if errors:
            return LoadResult(
                LoadStatus.BLOCKED,
                sidecar_path,
                message="The annotation sidecar failed validation: "
                + "; ".join(errors),
            )

        comparison = compare_video_source(session.video_info, actual)
        if comparison.status is SourceMatchStatus.MISMATCH:
            fields = ", ".join(comparison.mismatched_fields)
            return LoadResult(
                LoadStatus.BLOCKED,
                sidecar_path,
                message=f"The sidecar conflicts with this video ({fields}).",
                source_comparison=comparison,
            )
        status = (
            LoadStatus.LOADED
            if comparison.status is SourceMatchStatus.MATCH
            else LoadStatus.UNKNOWN_SOURCE
        )
        return LoadResult(
            status, sidecar_path, session=session, source_comparison=comparison
        )

    def bind(self, sidecar_path: Path) -> None:
        self._sidecar_path = sidecar_path
        self._dirty = False
        self._annotation_changed = False
        self._expected_revision = self._revision(sidecar_path)

    def mark_dirty(self) -> None:
        self._dirty = True

    def mark_annotation_changed(self) -> None:
        self._annotation_changed = True

    def reset_annotation_changed(self) -> None:
        self._annotation_changed = False

    def save(self, session: AnnotationSession) -> None:
        if self._sidecar_path is None:
            raise SessionPersistenceError("No annotation sidecar is bound.")
        errors = self.validation_errors(session)
        if errors:
            self._dirty = True
            raise SessionPersistenceError("Session is invalid: " + "; ".join(errors))
        self._dirty = True
        if self._revision(self._sidecar_path) != self._expected_revision:
            raise ExternalSidecarChangeError(
                "The annotation sidecar changed outside this application. "
                "Reload it before making further edits."
            )
        try:
            self._repository.save(session, self._sidecar_path)
        except OSError as exc:
            raise SessionPersistenceError(
                f"Could not write annotation sidecar: {exc}"
            ) from exc
        self._expected_revision = self._revision(self._sidecar_path)
        self._dirty = False

    def archive_snapshot(
        self, session: AnnotationSession, *, timestamp: Optional[datetime] = None
    ) -> Path:
        if self._sidecar_path is None:
            raise HistorySnapshotError("No annotation sidecar is bound.")
        errors = self.validation_errors(session)
        if errors:
            raise HistorySnapshotError("Session is invalid: " + "; ".join(errors))
        history_dir = self._sidecar_path.with_name(
            self._sidecar_path.name.removesuffix(".phase-annotations.json")
            + ".phase-annotations-history"
        )
        stamp = (timestamp or datetime.now(timezone.utc)).astimezone(timezone.utc)
        stem = stamp.strftime("%Y-%m-%dT%H-%M-%S.%fZ")
        candidate = history_dir / f"{stem}.json"
        suffix = 1
        while candidate.exists():
            candidate = history_dir / f"{stem}-{suffix}.json"
            suffix += 1
        try:
            self._repository.save(session, candidate)
        except OSError as exc:
            raise HistorySnapshotError(
                f"Could not write annotation history: {exc}"
            ) from exc
        self._annotation_changed = False
        return candidate

    @staticmethod
    def _revision(path: Path) -> Optional[FileRevision]:
        try:
            stat = path.stat()
        except FileNotFoundError:
            return None
        return FileRevision(stat.st_size, stat.st_mtime_ns)

    def validation_errors(self, session: AnnotationSession) -> list[str]:
        errors: list[str] = []
        if session.schema_version not in SUPPORTED_SESSION_SCHEMA_VERSIONS:
            errors.append(f"unsupported schema version {session.schema_version!r}")
        if session.ontology_id != self._ontology.ontology_id:
            errors.append("ontology ID does not match the active configuration")
        if session.ontology_version != self._ontology.ontology_version:
            errors.append("ontology version does not match the active configuration")
        if session.status == "completed":
            if session.completed_at is None:
                errors.append("completed session has no completion timestamp")
            if (
                not isinstance(session.completed_by, str)
                or not session.completed_by.strip()
            ):
                errors.append("completed session has no completer attribution")
        elif session.status == "draft":
            if session.completed_at is not None or session.completed_by is not None:
                errors.append("draft session contains completion metadata")
        else:
            errors.append(f"unsupported session status {session.status!r}")
        if not isinstance(session.session_notes, str):
            errors.append("video note is not text")
        valid_phase_ids = set(self._ontology.phases)
        unknown_ids = sorted(
            {interval.phase_id for interval in session.intervals} - valid_phase_ids
        )
        if unknown_ids:
            errors.append(f"unknown phase IDs: {unknown_ids}")
        errors.extend(
            validate_contiguous_coverage(
                session.intervals, session.video_info.duration_ms
            )
        )
        if session.resume_position_ms > session.video_info.duration_ms:
            errors.append("resume position exceeds video duration")
        return errors
