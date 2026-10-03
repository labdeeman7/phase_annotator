import json
from pathlib import Path

import pytest

from phase_annotator.config import load_procedure_ontology
from phase_annotator.storage import JsonSessionRepository, SessionPersistenceCoordinator
from scripts.convert_cholec80_phase import (
    ConversionError,
    build_session,
    read_source_runs,
    write_conversion,
)


def write_labels(path: Path, rows: list[tuple[int, str]]) -> None:
    text = "Frame\tPhase\n" + "\n".join(f"{frame}\t{phase}" for frame, phase in rows)
    path.write_text(text + "\n", encoding="utf-8")


def make_inputs(tmp_path: Path) -> tuple[Path, Path]:
    labels = tmp_path / "video01-phase.txt"
    video = tmp_path / "video01.mp4"
    video.write_bytes(b"synthetic video descriptor only")
    write_labels(
        labels,
        [
            (0, "Preparation"),
            (1, "Preparation"),
            (2, "ClippingCutting"),
            (3, "Preparation"),
        ],
    )
    return labels, video


def test_conversion_preserves_repeated_out_of_order_runs_and_frame_boundaries(
    tmp_path: Path,
):
    labels, video = make_inputs(tmp_path)
    session, manifest = build_session(labels, video, video_duration_ms=160)
    assert [
        (item.start_ms, item.end_ms, item.phase_id) for item in session.intervals
    ] == [(0, 80, 1), (80, 120, 3), (120, 160, 1)]
    assert session.status == "completed"
    assert session.completed_at == 0.0
    assert session.completed_by == "cholec80_reference_import"
    assert session.created_by == "cholec80_reference_import"
    assert session.session_notes.startswith("Cholec80 reference import.")
    assert "not created by a human" in session.session_notes
    assert manifest["review"] == {"status": "not_reviewed"}
    assert not SessionPersistenceCoordinator(
        load_procedure_ontology("cholecystectomy")
    ).validation_errors(session)


@pytest.mark.parametrize("video_duration_ms", [59, 261])
def test_conversion_rejects_duration_difference_over_100ms(
    tmp_path: Path, video_duration_ms: int
):
    labels, video = make_inputs(tmp_path)
    with pytest.raises(ConversionError, match="differs from video duration"):
        build_session(labels, video, video_duration_ms=video_duration_ms)


def test_conversion_snaps_only_final_endpoint_within_tolerance(tmp_path: Path):
    labels, video = make_inputs(tmp_path)
    session, manifest = build_session(labels, video, video_duration_ms=199)
    assert [(item.start_ms, item.end_ms) for item in session.intervals] == [
        (0, 80),
        (80, 120),
        (120, 199),
    ]
    assert manifest["timing"]["final_endpoint_adjustment_ms"] == 39


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("wrong header\n0\tPreparation\n", "exact header"),
        ("Frame\tPhase\n0\tPreparation\n2\tPreparation\n", "expected frame 1"),
        ("Frame\tPhase\n0\tMystery\n", "unknown phase label"),
    ],
)
def test_source_validation_rejects_malformed_or_ambiguous_input(
    tmp_path: Path, text: str, message: str
):
    path = tmp_path / "labels.txt"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ConversionError, match=message):
        read_source_runs(path)


def test_write_is_deterministic_loadable_and_refuses_overwrite(tmp_path: Path):
    labels, video = make_inputs(tmp_path)
    session, manifest = build_session(labels, video, video_duration_ms=160)
    output_dir = tmp_path / "references"
    session_path, manifest_path = write_conversion(
        session, manifest, output_dir=output_dir
    )
    first_session_text = session_path.read_text(encoding="utf-8")
    first_manifest_text = manifest_path.read_text(encoding="utf-8")
    assert JsonSessionRepository().load(session_path) == session
    assert json.loads(first_manifest_text)["validation"]["result"] == "passed"
    with pytest.raises(ConversionError, match="Refusing to overwrite"):
        write_conversion(session, manifest, output_dir=output_dir)
    write_conversion(session, manifest, output_dir=output_dir, overwrite=True)
    assert session_path.read_text(encoding="utf-8") == first_session_text
    assert manifest_path.read_text(encoding="utf-8") == first_manifest_text
