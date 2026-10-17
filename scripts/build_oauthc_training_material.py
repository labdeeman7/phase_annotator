"""Build the phase-organised OAUTHC cholecystectomy training material."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from PySide6.QtWidgets import QApplication

if __package__:
    from scripts.build_clinician_pilot_package import render_markdown_pdf
    from scripts.extract_transition_clips import (
        extract_transition_clips,
        phase_label_overlay_filter,
    )
else:
    from build_clinician_pilot_package import render_markdown_pdf
    from extract_transition_clips import (
        extract_transition_clips,
        phase_label_overlay_filter,
    )

from phase_annotator.config import load_procedure_ontology
from phase_annotator.storage import JsonSessionRepository

MATERIAL_VERSION = "0.4"
CONTEXT_MS = 15_000


@dataclass(frozen=True)
class ExampleSpec:
    phase_id: int
    example_number: int
    source: str
    source_video: str
    case_id: str
    boundary_index: int | None
    description: str


@dataclass(frozen=True)
class BuiltExample:
    phase_id: int
    example_number: int
    source: str
    case_id: str
    filename: str
    description: str
    clip_start_ms: int
    clip_end_ms: int
    boundary_ms: int | None
    from_phase_id: int | None


EXAMPLES = (
    ExampleSpec(
        1,
        1,
        "OAUTHC",
        "20260505_221257.mp4",
        "LOCAL-01",
        None,
        "Preparation immediately before focused hepatocystic-triangle dissection. "
        "Hook use for exposure or tissue clearance remains P1.",
    ),
    ExampleSpec(
        1,
        2,
        "OAUTHC",
        "20260519_215628.mp4",
        "LOCAL-02",
        None,
        "A difficult exposure interval in which the operative objective has not yet "
        "changed to sustained Calot triangle dissection.",
    ),
    ExampleSpec(
        2,
        1,
        "OAUTHC",
        "20260505_221257.mp4",
        "LOCAL-01",
        1,
        "Entry into sustained hepatocystic-triangle dissection after preparatory "
        "exposure work.",
    ),
    ExampleSpec(
        2,
        2,
        "OAUTHC",
        "20260519_215628.mp4",
        "LOCAL-02",
        1,
        "The clinician-selected change from general exposure to focused dissection "
        "aimed at identifying the cystic structures.",
    ),
    ExampleSpec(
        3,
        1,
        "OAUTHC",
        "20260505_221257.mp4",
        "LOCAL-01",
        2,
        "Calot triangle dissection gives way to purposeful clipping or occlusion of "
        "the cystic structures.",
    ),
    ExampleSpec(
        3,
        2,
        "OAUTHC",
        "20260519_215628.mp4",
        "LOCAL-02",
        2,
        "A second local example of entry into clipping and cutting after dissection.",
    ),
    ExampleSpec(
        4,
        1,
        "OAUTHC",
        "20260505_221257.mp4",
        "LOCAL-01",
        3,
        "Division of the secured cystic structures is complete and purposeful "
        "separation from the liver bed begins.",
    ),
    ExampleSpec(
        4,
        2,
        "OAUTHC",
        "20260519_215628.mp4",
        "LOCAL-02",
        3,
        "A second local transition into gallbladder dissection from the liver bed.",
    ),
    ExampleSpec(
        5,
        1,
        "OAUTHC",
        "20260505_221257.mp4",
        "LOCAL-01",
        5,
        "Cleaning or haemostasis ends and the specimen-retrieval bag is positioned "
        "for gallbladder packaging.",
    ),
    ExampleSpec(
        5,
        2,
        "Cholec80",
        "video44.mp4",
        "V44",
        4,
        "Cholec80 fallback: the detached gallbladder is prepared for placement in a "
        "specimen-retrieval bag.",
    ),
    ExampleSpec(
        6,
        1,
        "OAUTHC",
        "20260505_221257.mp4",
        "LOCAL-01",
        4,
        "Gallbladder dissection ends and liver-bed inspection, cleaning, or "
        "haemostasis becomes the dominant task.",
    ),
    ExampleSpec(
        6,
        2,
        "OAUTHC",
        "20260519_215628.mp4",
        "LOCAL-02",
        4,
        "A second local example in which cleaning or haemostasis becomes distinct "
        "from continuing gallbladder dissection.",
    ),
    ExampleSpec(
        7,
        1,
        "Cholec80",
        "video14.mp4",
        "V14",
        5,
        "Cholec80 fallback: sustained withdrawal of the contained specimen begins "
        "after packaging.",
    ),
    ExampleSpec(
        7,
        2,
        "Cholec80",
        "video50.mp4",
        "V50",
        5,
        "A second Cholec80 example of the transition from packaging to specimen "
        "extraction.",
    ),
)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def _source_paths(repository: Path, spec: ExampleSpec) -> tuple[Path, Path, bool]:
    if spec.source == "OAUTHC":
        source_dir = (
            repository
            / "test_dataset"
            / "clinician_pilot"
            / "Phase_Annotator_Cholecystectomy_0.1_Pilot"
            / "04_Local_Study"
            / "Videos_to_annotate"
        )
        return (
            source_dir / spec.source_video,
            source_dir / f"{spec.source_video}.phase-annotations.json",
            True,
        )
    reference_root = repository / "test_dataset" / "reference_cases"
    return (
        reference_root / "videos" / spec.source_video,
        reference_root
        / "reference_answers"
        / f"{spec.source_video}.phase-annotations.json",
        False,
    )


def _phase_dir(output_dir: Path, phase_id: int, phase_name: str) -> Path:
    directory = output_dir / "examples" / f"P{phase_id}_{_slug(phase_name)}"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _build_p1_excerpt(
    repository: Path,
    output_dir: Path,
    spec: ExampleSpec,
    *,
    ffmpeg_path: Path,
    font_path: Path,
) -> BuiltExample:
    video_path, session_path, _ = _source_paths(repository, spec)
    session = JsonSessionRepository().load(session_path)
    if session.intervals[0].phase_id != 1 or len(session.intervals) < 2:
        raise ValueError(f"Expected an initial P1 interval in {session_path.name}")
    next_boundary_ms = session.intervals[1].start_ms
    clip_end_ms = next_boundary_ms - CONTEXT_MS
    clip_start_ms = clip_end_ms - (2 * CONTEXT_MS)
    if clip_start_ms < 0:
        raise ValueError(
            f"P1 is too short for the requested excerpt: {session_path.name}"
        )
    ontology = load_procedure_ontology("cholecystectomy")
    phase = ontology.get_phase_by_id(1)
    filename = f"P1_EX{spec.example_number:02d}_{spec.source}_{spec.case_id}.mp4"
    destination = _phase_dir(output_dir, 1, phase.name) / filename
    command = [
        str(ffmpeg_path),
        "-hide_banner",
        "-loglevel",
        "error",
        "-n",
        "-ss",
        f"{clip_start_ms / 1_000:.3f}",
        "-i",
        str(video_path),
        "-t",
        f"{(clip_end_ms - clip_start_ms) / 1_000:.3f}",
        "-map",
        "0:v:0",
        "-an",
        "-vf",
        phase_label_overlay_filter(
            phase.id, phase.name, phase.color_hex, font_path=font_path
        ),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "22",
        "-movflags",
        "+faststart",
        str(destination),
    ]
    subprocess.run(command, check=True)
    return BuiltExample(
        1,
        spec.example_number,
        spec.source,
        spec.case_id,
        filename,
        spec.description,
        clip_start_ms,
        clip_end_ms,
        None,
        None,
    )


def _build_transition_example(
    repository: Path,
    output_dir: Path,
    spec: ExampleSpec,
    *,
    ffmpeg_path: Path,
    font_path: Path,
) -> BuiltExample:
    if spec.boundary_index is None:
        raise ValueError("Transition example requires a boundary index.")
    video_path, session_path, allow_draft = _source_paths(repository, spec)
    temporary = output_dir / f".{spec.source}-{spec.case_id}-P{spec.phase_id}-build"
    clips, _ = extract_transition_clips(
        ffmpeg_path=ffmpeg_path,
        font_path=font_path,
        video_path=video_path,
        session_path=session_path,
        output_dir=temporary,
        context_ms=CONTEXT_MS,
        allow_draft=allow_draft,
        case_id=spec.case_id,
        manifest_purpose="Phase-organised OAUTHC clinical training material",
        boundary_indices={spec.boundary_index},
    )
    clip = clips[0]
    if clip.to_phase_id != spec.phase_id:
        raise ValueError(
            f"{spec.case_id} boundary {spec.boundary_index} enters "
            f"P{clip.to_phase_id}, not requested P{spec.phase_id}."
        )
    ontology = load_procedure_ontology("cholecystectomy")
    phase = ontology.get_phase_by_id(spec.phase_id)
    filename = (
        f"P{spec.phase_id}_EX{spec.example_number:02d}_{spec.source}_{spec.case_id}.mp4"
    )
    destination = _phase_dir(output_dir, spec.phase_id, phase.name) / filename
    shutil.move(temporary / clip.filename, destination)
    shutil.rmtree(temporary)
    return BuiltExample(
        spec.phase_id,
        spec.example_number,
        spec.source,
        spec.case_id,
        filename,
        spec.description,
        clip.clip_start_ms,
        clip.clip_end_ms,
        clip.boundary_ms,
        clip.from_phase_id,
    )


def _format_timecode(milliseconds: int | None) -> str:
    if milliseconds is None:
        return "Representative in-phase excerpt"
    total_seconds, millis = divmod(milliseconds, 1_000)
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"


def write_html_index(
    examples: list[BuiltExample], destination: Path, *, ontology
) -> None:
    sections = []
    phases = ontology.ordered_phases
    for phase in phases:
        cards = []
        for example in sorted(
            (item for item in examples if item.phase_id == phase.id),
            key=lambda item: item.example_number,
        ):
            relative = f"examples/P{phase.id}_{_slug(phase.name)}/{example.filename}"
            source_class = "oauthc" if example.source == "OAUTHC" else "cholec80"
            boundary_text = (
                f"Entry boundary: {_format_timecode(example.boundary_ms)}"
                if example.boundary_ms is not None
                else _format_timecode(None)
            )
            fallback = (
                "<p class='fallback-note'>No suitable example was available in the "
                "two OAUTHC pilot annotations. This Cholec80 example provides "
                "provisional guidance until an OAUTHC example is reviewed.</p>"
                if example.source == "Cholec80"
                else ""
            )
            cards.append(
                f"""
                <article>
                  <div class="card-title"><strong>Example {example.example_number}</strong><span class="source {source_class}">{html.escape(example.source)}</span></div>
                  <p class="case">{html.escape(example.case_id)} &middot; {html.escape(boundary_text)}</p>
                  <p>{html.escape(example.description)}</p>
                  {fallback}
                  <video controls preload="none" src="{html.escape(relative)}"></video>
                  <p><a href="{html.escape(relative)}">Open this clip in your video player</a></p>
                </article>
                """
            )
        sections.append(
            f"""
            <section id="p{phase.id}">
              <h2><span style="background:{html.escape(phase.color_hex)}">P{phase.id}</span>{html.escape(phase.name)}</h2>
              <div class="grid">{"".join(cards)}</div>
            </section>
            """
        )
    destination.write_text(
        f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OAUTHC Cholecystectomy Phase Training</title>
<style>
body{{margin:0;font-family:"Segoe UI",Arial,sans-serif;background:#f2f5f7;color:#18242c}}header{{background:#12324a;color:white;padding:28px max(24px,6vw)}}header p{{max-width:950px;line-height:1.5}}main{{max-width:1200px;margin:auto;padding:20px}}nav a{{display:inline-block;margin:4px;padding:7px 10px;background:#e4edf2;border-radius:5px;color:#174b6b;text-decoration:none}}section{{margin:30px 0}}h2{{display:flex;gap:12px;align-items:center}}h2 span{{color:white;padding:6px 10px;border-radius:7px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(390px,1fr));gap:18px}}article{{background:white;border:1px solid #ccd7dd;border-radius:10px;padding:17px;box-shadow:0 2px 8px #00000012}}.card-title{{display:flex;justify-content:space-between;align-items:center;font-size:1.08rem}}.source{{color:white;padding:5px 9px;border-radius:6px;font-weight:700}}.oauthc{{background:#176c91}}.cholec80{{background:#71549c}}.case{{color:#456473;font-weight:600}}.fallback-note{{background:#fff4d6;border-left:4px solid #d89b00;padding:10px}}video{{width:100%;background:black;margin-top:10px}}a{{color:#075f87;font-weight:600}}
</style></head><body><header><h1>OAUTHC Cholecystectomy Phase-Annotation Training</h1><p>Two examples for each phase, organised by phase rather than source video. OAUTHC examples are preferred. Clearly labelled Cholec80 examples fill gaps where the two pilot annotations did not contain enough local examples.</p></header><main>
<nav>{"".join(f'<a href="#p{p.id}">P{p.id} {html.escape(p.name)}</a>' for p in phases)}</nav>
{"".join(sections)}</main></body></html>""",
        encoding="utf-8",
    )


def build_material(
    repository: Path,
    output_dir: Path,
    *,
    ffmpeg_path: Path,
    font_path: Path,
    browser_path: Path,
) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    ontology = load_procedure_ontology("cholecystectomy")
    built = []
    for spec in EXAMPLES:
        builder = _build_p1_excerpt if spec.phase_id == 1 else _build_transition_example
        built.append(
            builder(
                repository,
                output_dir,
                spec,
                ffmpeg_path=ffmpeg_path,
                font_path=font_path,
            )
        )

    write_html_index(
        built, output_dir / "OPEN_TRAINING_LIBRARY.html", ontology=ontology
    )
    QApplication.instance() or QApplication([])
    html_dir = output_dir / ".pdf-build"
    html_dir.mkdir()
    try:
        render_markdown_pdf(
            repository
            / "docs"
            / "studies"
            / "OAUTHC_CHOLECYSTECTOMY_TRAINING_MANUAL.md",
            output_dir / "OAUTHC_CHOLECYSTECTOMY_TRAINING_MANUAL.pdf",
            browser_path=browser_path,
            html_dir=html_dir,
        )
    finally:
        shutil.rmtree(html_dir, ignore_errors=True)

    ffmpeg_version = subprocess.run(
        [str(ffmpeg_path), "-version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]
    manifest = {
        "material_version": MATERIAL_VERSION,
        "purpose": "OAUTHC phase-organised cholecystectomy annotation training",
        "example_count": len(built),
        "examples_per_phase": 2,
        "context_before_ms_for_transitions": CONTEXT_MS,
        "context_after_ms_for_transitions": CONTEXT_MS,
        "source_policy": "Prefer OAUTHC; label Cholec80 fallbacks explicitly",
        "ffmpeg_version": ffmpeg_version,
        "audio": "omitted",
        "examples": [asdict(example) for example in built],
    }
    (output_dir / "training-material-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--ffmpeg-path", type=Path, required=True)
    parser.add_argument("--font-path", type=Path, required=True)
    parser.add_argument("--browser-path", type=Path, required=True)
    args = parser.parse_args()
    repository = args.repository.resolve()
    output_dir = args.output_dir.resolve()
    expected_parent = repository / "test_dataset" / "clinician_pilot"
    if expected_parent not in output_dir.parents:
        parser.error(
            "output-dir must be a dedicated directory under "
            "test_dataset/clinician_pilot"
        )
    build_material(
        repository,
        output_dir,
        ffmpeg_path=args.ffmpeg_path.resolve(),
        font_path=args.font_path.resolve(),
        browser_path=args.browser_path.resolve(),
    )
    print(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
