from dataclasses import dataclass, replace
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class MediaProbeFailure:
    """A non-fatal metadata failure suitable for later UI presentation."""

    code: str
    message: str


@dataclass(frozen=True)
class MediaMetadata:
    """Facts learned about one source without depending on a UI toolkit."""

    source_path: str
    file_size_bytes: Optional[int] = None
    file_modified_ns: Optional[int] = None
    duration_ms: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    fps_source: str = "unknown"
    frame_rate_mode: str = "unknown"
    failure: Optional[MediaProbeFailure] = None

    def with_playback_metadata(
        self,
        *,
        duration_ms: Optional[int],
        width: Optional[int],
        height: Optional[int],
        fps: Optional[float],
    ) -> "MediaMetadata":
        """Return a combined snapshot while retaining filesystem evidence."""
        return replace(
            self,
            duration_ms=duration_ms,
            width=width,
            height=height,
            fps=fps,
            fps_source="qt" if fps is not None else "unknown",
            # Qt reports a rate value, but not whether timestamps are CFR or VFR.
            frame_rate_mode="unknown",
        )


def probe_local_file(path: Path) -> MediaMetadata:
    """Read cheap filesystem evidence without opening or hashing video contents."""
    resolved_path = path.resolve()
    try:
        stat = resolved_path.stat()
    except OSError as exc:
        return MediaMetadata(
            source_path=str(resolved_path),
            failure=MediaProbeFailure(code="file_stat_failed", message=str(exc)),
        )
    return MediaMetadata(
        source_path=str(resolved_path),
        file_size_bytes=stat.st_size,
        file_modified_ns=stat.st_mtime_ns,
    )
