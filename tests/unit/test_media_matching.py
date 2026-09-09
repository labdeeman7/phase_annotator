from pathlib import Path

import pytest

from phase_annotator.domain.models import VideoInfo
from phase_annotator.media.matching import (
    EvidenceStatus,
    SourceMatchStatus,
    compare_video_source,
)
from phase_annotator.media.metadata import MediaMetadata


def expected_video(tmp_path: Path, **overrides) -> VideoInfo:
    values = {
        "video_id": "case.mp4",
        "duration_ms": 10_000,
        "width": 1920,
        "height": 1080,
        "source_path": str((tmp_path / "original" / "case.mp4").resolve()),
        "file_size_bytes": 1_000,
        "file_modified_ns": 2_000,
    }
    values.update(overrides)
    return VideoInfo(**values)


def actual_video(tmp_path: Path, **overrides) -> MediaMetadata:
    values = {
        "source_path": str((tmp_path / "original" / "case.mp4").resolve()),
        "duration_ms": 10_000,
        "width": 1920,
        "height": 1080,
        "file_size_bytes": 1_000,
        "file_modified_ns": 2_000,
    }
    values.update(overrides)
    return MediaMetadata(**values)


def test_matching_descriptor_returns_explainable_match(tmp_path: Path):
    comparison = compare_video_source(expected_video(tmp_path), actual_video(tmp_path))

    assert comparison.status is SourceMatchStatus.MATCH
    assert comparison.mismatched_fields == ()
    assert all(item.status is EvidenceStatus.MATCH for item in comparison.evidence)


@pytest.mark.parametrize(
    ("expected_overrides", "actual_overrides", "field"),
    [
        ({}, {"source_path": "different.mp4"}, "filename"),
        ({}, {"file_size_bytes": 999}, "file_size_bytes"),
        ({}, {"file_modified_ns": 999}, "file_modified_ns"),
        ({}, {"duration_ms": 10_101}, "duration_ms"),
        ({}, {"width": 1280}, "width"),
        ({}, {"height": 720}, "height"),
    ],
)
def test_conflicting_descriptor_evidence_returns_mismatch(
    tmp_path: Path, expected_overrides, actual_overrides, field
):
    comparison = compare_video_source(
        expected_video(tmp_path, **expected_overrides),
        actual_video(tmp_path, **actual_overrides),
    )

    assert comparison.status is SourceMatchStatus.MISMATCH
    assert field in comparison.mismatched_fields


def test_changed_path_alone_is_a_relocation_not_a_mismatch(tmp_path: Path):
    relocated = actual_video(
        tmp_path,
        source_path=str((tmp_path / "moved" / "case.mp4").resolve()),
    )

    comparison = compare_video_source(expected_video(tmp_path), relocated)

    assert comparison.status is SourceMatchStatus.MATCH
    path_evidence = next(
        item for item in comparison.evidence if item.field == "source_path"
    )
    assert path_evidence.status is EvidenceStatus.MISMATCH
    assert "source_path" in comparison.mismatched_fields


def test_filename_only_agreement_is_unknown(tmp_path: Path):
    expected = expected_video(
        tmp_path,
        duration_ms=0,
        width=None,
        height=None,
        file_size_bytes=None,
        file_modified_ns=None,
    )
    actual = MediaMetadata(
        source_path=str((tmp_path / "elsewhere" / "case.mp4").resolve())
    )

    comparison = compare_video_source(expected, actual)

    assert comparison.status is SourceMatchStatus.UNKNOWN


def test_duration_comparison_allows_small_backend_rounding_difference(tmp_path: Path):
    comparison = compare_video_source(
        expected_video(tmp_path),
        actual_video(tmp_path, duration_ms=10_100),
    )

    assert comparison.status is SourceMatchStatus.MATCH


def test_negative_duration_tolerance_is_rejected(tmp_path: Path):
    with pytest.raises(ValueError, match="cannot be negative"):
        compare_video_source(
            expected_video(tmp_path),
            actual_video(tmp_path),
            duration_tolerance_ms=-1,
        )
