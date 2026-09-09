from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from phase_annotator.domain.models import (
    CURRENT_SESSION_SCHEMA_VERSION,
    AnnotationSession,
)
from phase_annotator.domain.ontology import PhaseOntology
from phase_annotator.domain.validation import validate_contiguous_coverage
from phase_annotator.media import MediaMetadata, SourceComparison, SourceMatchStatus
from phase_annotator.media import compare_video_source
from phase_annotator.storage.json_repo import JsonSessionRepository


SUPPORTED_SESSION_SCHEMA_VERSIONS = frozenset(
    {"1.0", "1.1", CURRENT_SESSION_SCHEMA_VERSION}
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

    @property
    def sidecar_path(self) -> Optional[Path]:
        return self._sidecar_path

    @property
    def is_dirty(self) -> bool:
        return self._dirty

    @staticmethod
    def sidecar_path_for(video_path: Path) -> Path:
        return video_path.with_name(f"{video_path.name}.phase-annotations.json")

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

        errors = self.validation_errors(session)
        if errors:
            return LoadResult(
                LoadStatus.BLOCKED,
                sidecar_path,
                message="The annotation sidecar failed validation: " + "; ".join(errors),
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
        return LoadResult(status, sidecar_path, session=session, source_comparison=comparison)

    def bind(self, sidecar_path: Path) -> None:
        self._sidecar_path = sidecar_path
        self._dirty = False

    def mark_dirty(self) -> None:
        self._dirty = True

    def save(self, session: AnnotationSession) -> None:
        if self._sidecar_path is None:
            raise SessionPersistenceError("No annotation sidecar is bound.")
        errors = self.validation_errors(session)
        if errors:
            self._dirty = True
            raise SessionPersistenceError("Session is invalid: " + "; ".join(errors))
        self._dirty = True
        try:
            self._repository.save(session, self._sidecar_path)
        except OSError as exc:
            raise SessionPersistenceError(f"Could not write annotation sidecar: {exc}") from exc
        self._dirty = False

    def validation_errors(self, session: AnnotationSession) -> list[str]:
        errors: list[str] = []
        if session.schema_version not in SUPPORTED_SESSION_SCHEMA_VERSIONS:
            errors.append(f"unsupported schema version {session.schema_version!r}")
        if session.ontology_id != self._ontology.ontology_id:
            errors.append("ontology ID does not match the active configuration")
        if session.ontology_version != self._ontology.ontology_version:
            errors.append("ontology version does not match the active configuration")
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
