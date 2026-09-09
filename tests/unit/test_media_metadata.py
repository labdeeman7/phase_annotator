from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtMultimedia import QMediaMetaData

from phase_annotator.media.metadata import probe_local_file
from phase_annotator.media.qt_metadata import read_qt_media_metadata


def test_probe_local_file_records_descriptor_without_reading_contents(tmp_path: Path):
    video_path = tmp_path / "synthetic.mp4"
    video_path.write_bytes(b"not-real-video")

    metadata = probe_local_file(video_path)

    assert metadata.source_path == str(video_path.resolve())
    assert metadata.file_size_bytes == len(b"not-real-video")
    assert metadata.file_modified_ns == video_path.stat().st_mtime_ns
    assert metadata.failure is None


def test_probe_local_file_returns_structured_failure_for_missing_file(tmp_path: Path):
    metadata = probe_local_file(tmp_path / "missing.mp4")

    assert metadata.file_size_bytes is None
    assert metadata.failure is not None
    assert metadata.failure.code == "file_stat_failed"


def test_qt_adapter_prefers_video_track_metadata_and_keeps_rate_mode_unknown(
    tmp_path: Path,
):
    video_path = tmp_path / "synthetic.mp4"
    video_path.write_bytes(b"metadata-test")
    container = QMediaMetaData()
    container.insert(QMediaMetaData.Key.Duration, 12_000)
    track = QMediaMetaData()
    track.insert(QMediaMetaData.Key.Resolution, QSize(1920, 1080))
    track.insert(QMediaMetaData.Key.VideoFrameRate, 25.0)

    metadata = read_qt_media_metadata(video_path, container, [track], 0)

    assert metadata.duration_ms == 12_000
    assert (metadata.width, metadata.height) == (1920, 1080)
    assert metadata.fps == 25.0
    assert metadata.fps_source == "qt"
    assert metadata.frame_rate_mode == "unknown"


def test_qt_adapter_uses_duration_fallback_and_ignores_invalid_values(tmp_path: Path):
    video_path = tmp_path / "synthetic.mp4"
    video_path.write_bytes(b"metadata-test")
    container = QMediaMetaData()
    container.insert(QMediaMetaData.Key.VideoFrameRate, 0.0)

    metadata = read_qt_media_metadata(video_path, container, [], 8_000)

    assert metadata.duration_ms == 8_000
    assert metadata.fps is None
    assert metadata.fps_source == "unknown"
    assert metadata.width is None
    assert metadata.height is None
