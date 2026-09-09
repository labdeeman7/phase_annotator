from pathlib import Path
from typing import Iterable, Optional

from PySide6.QtCore import QSize
from PySide6.QtMultimedia import QMediaMetaData

from phase_annotator.media.metadata import MediaMetadata, probe_local_file


def read_qt_media_metadata(
    path: Path,
    container_metadata: QMediaMetaData,
    video_tracks: Iterable[QMediaMetaData],
    fallback_duration_ms: int,
) -> MediaMetadata:
    """Translate backend-dependent Qt metadata into the neutral contract."""
    track_metadata = next(iter(video_tracks), None)

    def first_value(key: QMediaMetaData.Key):
        for metadata in (track_metadata, container_metadata):
            if metadata is not None:
                value = metadata.value(key)
                if value is not None:
                    return value
        return None

    duration_value = first_value(QMediaMetaData.Key.Duration)
    duration_ms = _positive_int(duration_value) or _positive_int(fallback_duration_ms)
    resolution = first_value(QMediaMetaData.Key.Resolution)
    width, height = _resolution_parts(resolution)
    fps = _positive_float(first_value(QMediaMetaData.Key.VideoFrameRate))

    return probe_local_file(path).with_playback_metadata(
        duration_ms=duration_ms,
        width=width,
        height=height,
        fps=fps,
    )


def _positive_int(value: object) -> Optional[int]:
    if isinstance(value, bool):
        return None
    try:
        converted = int(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return converted if converted > 0 else None


def _positive_float(value: object) -> Optional[float]:
    if isinstance(value, bool):
        return None
    try:
        converted = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return converted if converted > 0 else None


def _resolution_parts(value: object) -> tuple[Optional[int], Optional[int]]:
    if not isinstance(value, QSize) or not value.isValid():
        return None, None
    return value.width(), value.height()
