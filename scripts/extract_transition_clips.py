"""Create indexed clips centered on reference annotation boundaries."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from phase_annotator.config import load_procedure_ontology
from phase_annotator.storage import JsonSessionRepository

CLIP_MANIFEST_SCHEMA_VERSION = "1.0"


class ClipExtractionError(ValueError):
    """Raised when clip planning or extraction cannot proceed safely."""


@dataclass(frozen=True)
class TransitionClip:
    clip_id: str
    filename: str
    source_video_filename: str
    boundary_index: int
    boundary_ms: int
    clip_start_ms: int
    clip_end_ms: int
    from_phase_id: int
    from_phase_name: str
    from_phase_color: str
    to_phase_id: int
    to_phase_name: str
    to_phase_color: str


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return normalized or "phase"


def _escape_drawtext(value: str) -> str:
    """Escape text embedded in FFmpeg's drawtext filter expression."""
    return (
        value.replace("\\", r"\\")
        .replace("'", r"\'")
        .replace(":", r"\:")
        .replace("%", r"\%")
    )


def _escape_filter_path(path: Path) -> str:
    return (
        str(path.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
    )


def _phase_overlay_filter(clip: TransitionClip, *, font_path: Path) -> str:
    """Label every output frame with the phase active at that source time."""
    boundary_seconds = (clip.boundary_ms - clip.clip_start_ms) / 1_000

    def style(color_hex: str) -> str:
        ffmpeg_color = color_hex.replace("#", "0x")
        return (
            f"fontfile='{_escape_filter_path(font_path)}':"
            f"x=w-tw-20:y=20:fontsize=h/18:fontcolor={ffmpeg_color}:box=1:"
            "boxcolor=black@0.78:boxborderw=8"
        )

    before = _escape_drawtext(f"P{clip.from_phase_id} | {clip.from_phase_name}")
    after = _escape_drawtext(f"P{clip.to_phase_id} | {clip.to_phase_name}")
    return (
        f"drawtext=text='{before}':{style(clip.from_phase_color)}:"
        f"enable='lt(t\\,{boundary_seconds:.3f})',"
        f"drawtext=text='{after}':{style(clip.to_phase_color)}:"
        f"enable='gte(t\\,{boundary_seconds:.3f})'"
    )


def phase_label_overlay_filter(
    phase_id: int, phase_name: str, phase_color: str, *, font_path: Path
) -> str:
    """Return a constant top-right phase overlay for an in-phase example."""
    color = phase_color.replace("#", "0x")
    label = _escape_drawtext(f"P{phase_id} | {phase_name}")
    return (
        f"drawtext=text='{label}':"
        f"fontfile='{_escape_filter_path(font_path)}':"
        f"x=w-tw-20:y=20:fontsize=h/18:fontcolor={color}:box=1:"
        "boxcolor=black@0.78:boxborderw=8"
    )


def plan_transition_clips(
    session_path: Path,
    *,
    context_ms: int = 30_000,
    allow_draft: bool = False,
    case_id: str | None = None,
) -> list[TransitionClip]:
    """Plan one clip around every internal boundary in an annotation session."""
    if context_ms <= 0:
        raise ClipExtractionError("context_ms must be positive.")
    session = JsonSessionRepository().load(session_path)
    ontology = load_procedure_ontology("cholecystectomy")
    if session.ontology_id != ontology.ontology_id:
        raise ClipExtractionError(
            "Session is not a Cholec80 cholecystectomy reference."
        )
    if session.status != "completed" and not allow_draft:
        raise ClipExtractionError(
            "Reference session must be completed before clipping."
        )
    if len(session.intervals) < 2:
        return []

    if case_id is not None:
        case_token = _slug(case_id).upper()
    else:
        match = re.fullmatch(r"video(\d+)\.mp4", session.video_info.video_id)
        case_token = (
            f"V{int(match.group(1)):02d}"
            if match
            else _slug(Path(session.video_info.video_id).stem)
        )
    clips: list[TransitionClip] = []
    for boundary_index, (left, right) in enumerate(
        zip(session.intervals, session.intervals[1:], strict=False), start=1
    ):
        if left.end_ms != right.start_ms:
            raise ClipExtractionError("Reference intervals are not contiguous.")
        boundary_ms = right.start_ms
        from_phase = ontology.get_phase_by_id(left.phase_id)
        to_phase = ontology.get_phase_by_id(right.phase_id)
        clip_id = f"{case_token}-B{boundary_index:02d}"
        filename = (
            f"{clip_id}_P{left.phase_id}-{_slug(from_phase.name)}_to_"
            f"P{right.phase_id}-{_slug(to_phase.name)}.mp4"
        )
        clips.append(
            TransitionClip(
                clip_id=clip_id,
                filename=filename,
                source_video_filename=session.video_info.video_id,
                boundary_index=boundary_index,
                boundary_ms=boundary_ms,
                clip_start_ms=max(0, boundary_ms - context_ms),
                clip_end_ms=min(
                    session.video_info.duration_ms, boundary_ms + context_ms
                ),
                from_phase_id=left.phase_id,
                from_phase_name=from_phase.name,
                from_phase_color=from_phase.color_hex,
                to_phase_id=right.phase_id,
                to_phase_name=to_phase.name,
                to_phase_color=to_phase.color_hex,
            )
        )
    return clips


def extract_transition_clips(
    *,
    ffmpeg_path: Path,
    font_path: Path,
    video_path: Path,
    session_path: Path,
    output_dir: Path,
    context_ms: int = 30_000,
    overwrite: bool = False,
    allow_draft: bool = False,
    case_id: str | None = None,
    manifest_purpose: str = "Cholec80 source-boundary rule inference",
    boundary_indices: set[int] | None = None,
) -> tuple[list[TransitionClip], Path]:
    """Extract planned clips with an explicitly selected offline FFmpeg binary."""
    if not ffmpeg_path.is_file():
        raise ClipExtractionError(f"FFmpeg executable not found: {ffmpeg_path}")
    if not font_path.is_file():
        raise ClipExtractionError(f"Overlay font not found: {font_path}")
    if not video_path.is_file():
        raise ClipExtractionError(f"Video not found: {video_path}")
    clips = plan_transition_clips(
        session_path,
        context_ms=context_ms,
        allow_draft=allow_draft,
        case_id=case_id,
    )
    if boundary_indices is not None:
        clips = [clip for clip in clips if clip.boundary_index in boundary_indices]
    if not clips:
        raise ClipExtractionError("No requested internal boundaries were found.")

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / f"{video_path.stem}.transition-clips.json"
    targets = [output_dir / clip.filename for clip in clips] + [manifest_path]
    existing = [path.name for path in targets if path.exists()]
    if existing and not overwrite:
        raise ClipExtractionError(
            "Refusing to overwrite existing clip output: " + ", ".join(existing)
        )

    version = subprocess.run(
        [str(ffmpeg_path), "-version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()[0]
    for clip in clips:
        duration_seconds = (clip.clip_end_ms - clip.clip_start_ms) / 1_000
        command = [
            str(ffmpeg_path),
            "-hide_banner",
            "-loglevel",
            "error",
            "-y" if overwrite else "-n",
            "-ss",
            f"{clip.clip_start_ms / 1_000:.3f}",
            "-i",
            str(video_path),
            "-t",
            f"{duration_seconds:.3f}",
            "-map",
            "0:v:0",
            "-an",
            "-vf",
            _phase_overlay_filter(clip, font_path=font_path),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "22",
            "-movflags",
            "+faststart",
            str(output_dir / clip.filename),
        ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as exc:
            raise ClipExtractionError(f"FFmpeg failed for {clip.clip_id}.") from exc

    manifest = {
        "schema_version": CLIP_MANIFEST_SCHEMA_VERSION,
        "purpose": manifest_purpose,
        "source_video_filename": video_path.name,
        "reference_session_filename": session_path.name,
        "source_session_status": JsonSessionRepository().load(session_path).status,
        "draft_explicitly_accepted": allow_draft,
        "context_before_ms": context_ms,
        "context_after_ms": context_ms,
        "ffmpeg_version": version,
        "encoding": {
            "video_codec": "libx264",
            "preset": "veryfast",
            "crf": 22,
            "audio": "omitted",
            "phase_overlay": (
                "burned into every frame; switches at the exact source boundary"
            ),
            "overlay_font_filename": font_path.name,
        },
        "clips": [asdict(clip) for clip in clips],
    }
    temp_path = manifest_path.with_name(f".{manifest_path.name}.tmp")
    try:
        with temp_path.open("w", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=2)
            stream.write("\n")
        temp_path.replace(manifest_path)
    finally:
        temp_path.unlink(missing_ok=True)
    return clips, manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("session", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--ffmpeg-path", type=Path, required=True)
    parser.add_argument("--font-path", type=Path, required=True)
    parser.add_argument("--context-seconds", type=int, default=30)
    parser.add_argument("--allow-draft", action="store_true")
    parser.add_argument("--case-id")
    parser.add_argument("--purpose", default="Cholec80 source-boundary rule inference")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        clips, manifest = extract_transition_clips(
            ffmpeg_path=args.ffmpeg_path,
            font_path=args.font_path,
            video_path=args.video,
            session_path=args.session,
            output_dir=args.output_dir,
            context_ms=args.context_seconds * 1_000,
            overwrite=args.overwrite,
            allow_draft=args.allow_draft,
            case_id=args.case_id,
            manifest_purpose=args.purpose,
        )
    except (ClipExtractionError, OSError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"Clip extraction failed: {exc}\n")
    print(f"Created {len(clips)} clips")
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
