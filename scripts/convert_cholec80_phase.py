"""Convert Cholec80 frame labels into Phase Annotator session JSON."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from phase_annotator.config import load_procedure_ontology
from phase_annotator.domain.models import (
    CURRENT_SESSION_SCHEMA_VERSION,
    AnnotationInterval,
    AnnotationSession,
    VideoInfo,
)
from phase_annotator.storage import SessionPersistenceCoordinator

SOURCE_FPS = 25
FRAME_DURATION_MS = 1_000 // SOURCE_FPS
MAX_DURATION_DIFFERENCE_MS = 100
CONVERSION_CONTRACT_VERSION = "1.0"
IMPORT_IDENTITY = "cholec80_reference_import"

SOURCE_LABEL_TO_PHASE_ID = {
    "Preparation": 1,
    "CalotTriangleDissection": 2,
    "ClippingCutting": 3,
    "GallbladderDissection": 4,
    "GallbladderPackaging": 5,
    "CleaningCoagulation": 6,
    "GallbladderRetraction": 7,
}


class ConversionError(ValueError):
    """Raised when source data cannot be converted without guessing."""


@dataclass(frozen=True)
class SourceRun:
    start_frame: int
    end_frame: int
    label: str


def read_source_runs(label_path: Path) -> tuple[list[SourceRun], int]:
    """Parse contiguous per-frame labels and coalesce equal adjacent labels."""
    try:
        lines = label_path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        raise ConversionError(f"Could not read source labels: {exc}") from exc
    if not lines or lines[0] != "Frame\tPhase":
        raise ConversionError("Expected the exact header 'Frame<TAB>Phase'.")

    runs: list[SourceRun] = []
    previous_frame = -1
    for line_number, line in enumerate(lines[1:], start=2):
        parts = line.split("\t")
        if len(parts) != 2:
            raise ConversionError(f"Line {line_number} must contain two tab fields.")
        frame_text, label = parts
        try:
            frame = int(frame_text)
        except ValueError as exc:
            raise ConversionError(
                f"Line {line_number} has a non-integer frame index."
            ) from exc
        if frame != previous_frame + 1:
            raise ConversionError(
                f"Line {line_number} expected frame {previous_frame + 1}, got {frame}."
            )
        if label not in SOURCE_LABEL_TO_PHASE_ID:
            raise ConversionError(
                f"Line {line_number} contains unknown phase label {label!r}."
            )
        if runs and runs[-1].label == label:
            last = runs[-1]
            runs[-1] = SourceRun(last.start_frame, frame, label)
        else:
            runs.append(SourceRun(frame, frame, label))
        previous_frame = frame

    if previous_frame < 0:
        raise ConversionError("The source annotation contains no frame labels.")
    return runs, previous_frame + 1


def runs_to_intervals(
    runs: Iterable[SourceRun], *, labelled_frames: int, video_duration_ms: int
) -> list[AnnotationInterval]:
    """Translate inclusive frame runs to half-open millisecond intervals."""
    label_duration_ms = labelled_frames * FRAME_DURATION_MS
    difference_ms = video_duration_ms - label_duration_ms
    if abs(difference_ms) > MAX_DURATION_DIFFERENCE_MS:
        raise ConversionError(
            "Label-derived duration "
            f"({label_duration_ms}ms) differs from video duration "
            f"({video_duration_ms}ms) by {abs(difference_ms)}ms; maximum is "
            f"{MAX_DURATION_DIFFERENCE_MS}ms."
        )
    intervals = [
        AnnotationInterval(
            start_ms=run.start_frame * FRAME_DURATION_MS,
            end_ms=(run.end_frame + 1) * FRAME_DURATION_MS,
            phase_id=SOURCE_LABEL_TO_PHASE_ID[run.label],
        )
        for run in runs
    ]
    if not intervals:
        raise ConversionError("No phase runs were produced.")
    if video_duration_ms <= intervals[-1].start_ms:
        raise ConversionError("Video duration would make the final interval empty.")
    intervals[-1].end_ms = video_duration_ms
    return intervals


def build_session(
    label_path: Path, video_path: Path, *, video_duration_ms: int
) -> tuple[AnnotationSession, dict[str, object]]:
    """Build and validate a truthful imported reference session plus provenance."""
    if video_duration_ms <= 0:
        raise ConversionError("Video duration must be positive.")
    try:
        video_stat = video_path.stat()
    except OSError as exc:
        raise ConversionError(f"Could not inspect source video: {exc}") from exc

    runs, labelled_frames = read_source_runs(label_path)
    intervals = runs_to_intervals(
        runs, labelled_frames=labelled_frames, video_duration_ms=video_duration_ms
    )
    ontology = load_procedure_ontology("cholecystectomy")
    session = AnnotationSession(
        video_info=VideoInfo(
            video_id=video_path.name,
            duration_ms=video_duration_ms,
            fps=float(SOURCE_FPS),
            source_path=str(video_path.resolve()),
            file_size_bytes=video_stat.st_size,
            file_modified_ns=video_stat.st_mtime_ns,
            fps_source="assumed",
            frame_rate_mode="cfr",
        ),
        annotator_id=IMPORT_IDENTITY,
        created_by=IMPORT_IDENTITY,
        ontology_id=ontology.ontology_id,
        ontology_version=ontology.ontology_version,
        intervals=intervals,
        status="completed",
        completed_at=0.0,
        completed_by=IMPORT_IDENTITY,
        session_notes=(
            "Cholec80 reference import. These labels were not created by a "
            "human annotator in the Phase Annotator GUI."
        ),
        created_at=0.0,
        updated_at=0.0,
    )
    errors = SessionPersistenceCoordinator(ontology).validation_errors(session)
    if errors:
        raise ConversionError(
            "Converted session failed validation: " + "; ".join(errors)
        )

    manifest: dict[str, object] = {
        "conversion_contract_version": CONVERSION_CONTRACT_VERSION,
        "session_schema_version": CURRENT_SESSION_SCHEMA_VERSION,
        "source": {
            "video_filename": video_path.name,
            "annotation_filename": label_path.name,
            "annotation_format": "Cholec80 Frame<TAB>Phase, one row per frame",
            "labelled_frames": labelled_frames,
        },
        "ontology": {"id": ontology.ontology_id, "version": ontology.ontology_version},
        "timing": {
            "source_fps": SOURCE_FPS,
            "fps_provenance": "Cholec80 dataset documentation",
            "label_duration_ms": labelled_frames * FRAME_DURATION_MS,
            "video_duration_ms": video_duration_ms,
            "final_endpoint_adjustment_ms": (
                video_duration_ms - labelled_frames * FRAME_DURATION_MS
            ),
            "convention": (
                "source frame n covers [n*40ms, (n+1)*40ms); only the final "
                "endpoint is adjusted to the supplied video duration"
            ),
        },
        "mapping": SOURCE_LABEL_TO_PHASE_ID,
        "output": {
            "session_filename": f"{video_path.name}.phase-annotations.json",
            "interval_count": len(intervals),
            "status": "completed",
            "created_by": IMPORT_IDENTITY,
        },
        "validation": {"result": "passed", "errors": []},
        "review": {"status": "not_reviewed"},
    }
    return session, manifest


def write_conversion(
    session: AnnotationSession,
    manifest: dict[str, object],
    *,
    output_dir: Path,
    overwrite: bool = False,
) -> tuple[Path, Path]:
    """Atomically write session and provenance files with overwrite safety."""
    session_path = output_dir / f"{session.video_info.video_id}.phase-annotations.json"
    manifest_path = output_dir / f"{session.video_info.video_id}.conversion.json"
    targets = (session_path, manifest_path)
    existing = [path.name for path in targets if path.exists()]
    if existing and not overwrite:
        raise ConversionError(
            "Refusing to overwrite existing output: " + ", ".join(existing)
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    session_payload = asdict(session)
    # Match JsonSessionRepository's compatibility behavior: this private field
    # is emitted only when preserving data from the rejected C7 prototype.
    legacy_work_sessions = session_payload.pop("_legacy_work_sessions", None)
    if legacy_work_sessions is not None:
        session_payload["work_sessions"] = legacy_work_sessions
    payloads = (session_payload, manifest)
    temp_paths = [path.with_name(f".{path.name}.tmp") for path in targets]
    try:
        for temp_path, payload in zip(temp_paths, payloads, strict=True):
            with temp_path.open("w", encoding="utf-8") as stream:
                json.dump(payload, stream, indent=2)
                stream.write("\n")
        for temp_path, target in zip(temp_paths, targets, strict=True):
            os.replace(temp_path, target)
    finally:
        for temp_path in temp_paths:
            temp_path.unlink(missing_ok=True)
    return session_path, manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("labels", type=Path, help="Cholec80 phase TXT")
    parser.add_argument("video", type=Path, help="matching staged MP4")
    parser.add_argument("output_dir", type=Path, help="reference-output directory")
    parser.add_argument(
        "--video-duration-ms",
        type=int,
        required=True,
        help="duration reported by the Phase Annotator/Qt media pipeline",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace both existing generated files intentionally",
    )
    args = parser.parse_args()
    try:
        session, manifest = build_session(
            args.labels, args.video, video_duration_ms=args.video_duration_ms
        )
        paths = write_conversion(
            session, manifest, output_dir=args.output_dir, overwrite=args.overwrite
        )
    except ConversionError as exc:
        parser.exit(2, f"Conversion failed: {exc}\n")
    print(*(str(path) for path in paths), sep="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
