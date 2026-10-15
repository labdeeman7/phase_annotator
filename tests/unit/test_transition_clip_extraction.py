import json
from pathlib import Path

import pytest

from phase_annotator.config import load_procedure_ontology
from phase_annotator.domain.models import (
    AnnotationInterval,
    AnnotationSession,
    VideoInfo,
)
from phase_annotator.storage import JsonSessionRepository
from scripts.extract_transition_clips import (
    ClipExtractionError,
    extract_transition_clips,
    plan_transition_clips,
)


def write_reference(path: Path, *, status: str = "completed") -> None:
    ontology = load_procedure_ontology("cholecystectomy")
    session = AnnotationSession(
        VideoInfo("video04.mp4", 100_000),
        "cholec80_reference_import",
        ontology_id=ontology.ontology_id,
        ontology_version=ontology.ontology_version,
        intervals=[
            AnnotationInterval(0, 20_000, 1),
            AnnotationInterval(20_000, 70_000, 2),
            AnnotationInterval(70_000, 100_000, 3),
        ],
        status=status,
        completed_at=0.0 if status == "completed" else None,
        completed_by=("cholec80_reference_import" if status == "completed" else None),
    )
    JsonSessionRepository().save(session, path)


def test_plan_uses_source_boundaries_and_clamps_at_video_edges(tmp_path: Path):
    session_path = tmp_path / "video04.mp4.phase-annotations.json"
    write_reference(session_path)

    clips = plan_transition_clips(session_path, context_ms=30_000)

    assert [
        (clip.boundary_ms, clip.clip_start_ms, clip.clip_end_ms) for clip in clips
    ] == [
        (20_000, 0, 50_000),
        (70_000, 40_000, 100_000),
    ]
    assert clips[0].clip_id == "V04-B01"
    assert clips[0].filename == (
        "V04-B01_P1-preparation_to_P2-calot-triangle-dissection.mp4"
    )


def test_plan_rejects_draft_reference(tmp_path: Path):
    session_path = tmp_path / "draft.json"
    write_reference(session_path, status="draft")

    with pytest.raises(ClipExtractionError, match="must be completed"):
        plan_transition_clips(session_path)


def test_extract_records_commands_and_manifest_without_absolute_paths(
    tmp_path: Path, monkeypatch
):
    session_path = tmp_path / "video04.mp4.phase-annotations.json"
    video_path = tmp_path / "video04.mp4"
    ffmpeg_path = tmp_path / "ffmpeg.exe"
    font_path = tmp_path / "font.ttf"
    output_dir = tmp_path / "clips"
    write_reference(session_path)
    video_path.write_bytes(b"video")
    ffmpeg_path.write_bytes(b"binary")
    font_path.write_bytes(b"font")
    commands = []

    class Result:
        stdout = "ffmpeg version synthetic\n"

    def fake_run(command, **kwargs):
        commands.append((command, kwargs))
        return Result()

    monkeypatch.setattr("scripts.extract_transition_clips.subprocess.run", fake_run)

    clips, manifest_path = extract_transition_clips(
        ffmpeg_path=ffmpeg_path,
        font_path=font_path,
        video_path=video_path,
        session_path=session_path,
        output_dir=output_dir,
    )

    assert len(clips) == 2
    assert commands[0][0] == [str(ffmpeg_path), "-version"]
    assert commands[1][0][commands[1][0].index("-ss") + 1] == "0.000"
    assert commands[1][0][commands[1][0].index("-t") + 1] == "50.000"
    overlay = commands[1][0][commands[1][0].index("-vf") + 1]
    assert "P1 | Preparation" in overlay
    assert "P2 | Calot triangle dissection" in overlay
    assert "fontcolor=0x3B82F6" in overlay
    assert "fontcolor=0x10B981" in overlay
    assert "x=w-tw-20" in overlay
    assert "lt(t\\,20.000)" in overlay
    assert "gte(t\\,20.000)" in overlay
    assert "font.ttf" in overlay
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["source_video_filename"] == "video04.mp4"
    assert manifest["clips"][0]["boundary_ms"] == 20_000
    assert manifest["clips"][0]["from_phase_color"] == "#3B82F6"
    assert manifest["clips"][0]["to_phase_color"] == "#10B981"
    assert "burned into every frame" in manifest["encoding"]["phase_overlay"]
    assert manifest["encoding"]["overlay_font_filename"] == "font.ttf"
    assert str(tmp_path) not in manifest_path.read_text(encoding="utf-8")


def test_extract_refuses_existing_output_before_running_ffmpeg(
    tmp_path: Path, monkeypatch
):
    session_path = tmp_path / "video04.mp4.phase-annotations.json"
    video_path = tmp_path / "video04.mp4"
    ffmpeg_path = tmp_path / "ffmpeg.exe"
    font_path = tmp_path / "font.ttf"
    output_dir = tmp_path / "clips"
    write_reference(session_path)
    video_path.write_bytes(b"video")
    ffmpeg_path.write_bytes(b"binary")
    font_path.write_bytes(b"font")
    output_dir.mkdir()
    (output_dir / "video04.transition-clips.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        "scripts.extract_transition_clips.subprocess.run",
        lambda *args, **kwargs: pytest.fail("FFmpeg should not run"),
    )

    with pytest.raises(ClipExtractionError, match="Refusing to overwrite"):
        extract_transition_clips(
            ffmpeg_path=ffmpeg_path,
            font_path=font_path,
            video_path=video_path,
            session_path=session_path,
            output_dir=output_dir,
        )
