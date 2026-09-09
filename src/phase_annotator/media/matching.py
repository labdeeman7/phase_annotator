from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from phase_annotator.domain.models import VideoInfo
from phase_annotator.media.metadata import MediaMetadata


class SourceMatchStatus(str, Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    UNKNOWN = "unknown"


class EvidenceStatus(str, Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SourceEvidence:
    field: str
    status: EvidenceStatus
    expected: object
    actual: object


@dataclass(frozen=True)
class SourceComparison:
    """Explainable comparison of lightweight evidence, never proof of identity."""

    status: SourceMatchStatus
    evidence: tuple[SourceEvidence, ...]

    @property
    def mismatched_fields(self) -> tuple[str, ...]:
        return tuple(
            item.field
            for item in self.evidence
            if item.status is EvidenceStatus.MISMATCH
        )


def compare_video_source(
    expected: VideoInfo,
    actual: MediaMetadata,
    *,
    duration_tolerance_ms: int = 100,
) -> SourceComparison:
    """Compare descriptors conservatively without implying content identity."""
    if duration_tolerance_ms < 0:
        raise ValueError("duration_tolerance_ms cannot be negative.")

    actual_name = Path(actual.source_path).name
    evidence = [
        _exact_evidence("filename", expected.video_id, actual_name),
        _path_evidence(expected.source_path, actual.source_path),
        _exact_evidence(
            "file_size_bytes", expected.file_size_bytes, actual.file_size_bytes
        ),
        _exact_evidence(
            "file_modified_ns", expected.file_modified_ns, actual.file_modified_ns
        ),
        _duration_evidence(
            expected.duration_ms, actual.duration_ms, duration_tolerance_ms
        ),
        _exact_evidence("width", expected.width, actual.width),
        _exact_evidence("height", expected.height, actual.height),
    ]

    discriminating = [item for item in evidence if item.field != "source_path"]
    if any(item.status is EvidenceStatus.MISMATCH for item in discriminating):
        status = SourceMatchStatus.MISMATCH
    else:
        corroborating_matches = [
            item
            for item in discriminating
            if item.field != "filename" and item.status is EvidenceStatus.MATCH
        ]
        filename_matches = evidence[0].status is EvidenceStatus.MATCH
        status = (
            SourceMatchStatus.MATCH
            if filename_matches and corroborating_matches
            else SourceMatchStatus.UNKNOWN
        )
    return SourceComparison(status=status, evidence=tuple(evidence))


def _exact_evidence(field: str, expected: object, actual: object) -> SourceEvidence:
    if expected is None or actual is None:
        status = EvidenceStatus.UNKNOWN
    else:
        status = (
            EvidenceStatus.MATCH if expected == actual else EvidenceStatus.MISMATCH
        )
    return SourceEvidence(field, status, expected, actual)


def _path_evidence(expected: Optional[str], actual: str) -> SourceEvidence:
    if expected is None:
        status = EvidenceStatus.UNKNOWN
    else:
        status = (
            EvidenceStatus.MATCH
            if _normalized_path(expected) == _normalized_path(actual)
            else EvidenceStatus.MISMATCH
        )
    return SourceEvidence("source_path", status, expected, actual)


def _normalized_path(value: str) -> str:
    # Path agreement is only a location clue, so lexical normalization is enough.
    return str(Path(value).resolve()).casefold()


def _duration_evidence(
    expected: int, actual: Optional[int], tolerance_ms: int
) -> SourceEvidence:
    if expected <= 0 or actual is None:
        status = EvidenceStatus.UNKNOWN
    else:
        status = (
            EvidenceStatus.MATCH
            if abs(expected - actual) <= tolerance_ms
            else EvidenceStatus.MISMATCH
        )
    return SourceEvidence("duration_ms", status, expected, actual)
