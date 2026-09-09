import math
import time
from dataclasses import dataclass, field
from typing import List, Optional


CURRENT_SESSION_SCHEMA_VERSION = "1.1"
FPS_SOURCES = frozenset({"unknown", "assumed", "qt", "ffprobe"})
FRAME_RATE_MODES = frozenset({"unknown", "cfr", "vfr"})


@dataclass
class VideoInfo:
    """Metadata describing the target video being annotated."""

    video_id: str
    duration_ms: int
    fps: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    source_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    file_modified_ns: Optional[int] = None
    fps_source: str = "unknown"
    frame_rate_mode: str = "unknown"

    def __post_init__(self) -> None:
        if not isinstance(self.video_id, str) or not self.video_id.strip():
            raise ValueError("video_id must be non-empty text.")
        if not isinstance(self.duration_ms, int) or isinstance(self.duration_ms, bool):
            raise ValueError("duration_ms must be an integer.")
        if self.duration_ms < 0:
            raise ValueError("duration_ms cannot be negative.")
        if self.fps is not None and (
            isinstance(self.fps, bool)
            or not isinstance(self.fps, (int, float))
            or not math.isfinite(self.fps)
            or self.fps <= 0
        ):
            raise ValueError("fps must be a positive finite number or None.")
        for field_name in ("width", "height"):
            value = getattr(self, field_name)
            if value is not None and (
                not isinstance(value, int) or isinstance(value, bool) or value <= 0
            ):
                raise ValueError(f"{field_name} must be a positive integer or None.")
        if self.source_path is not None and (
            not isinstance(self.source_path, str) or not self.source_path.strip()
        ):
            raise ValueError("source_path must be non-empty text or None.")
        for field_name in ("file_size_bytes", "file_modified_ns"):
            value = getattr(self, field_name)
            if value is not None and (
                not isinstance(value, int) or isinstance(value, bool) or value < 0
            ):
                raise ValueError(
                    f"{field_name} must be a non-negative integer or None."
                )
        if self.fps_source not in FPS_SOURCES:
            raise ValueError(
                f"fps_source must be one of {sorted(FPS_SOURCES)}."
            )
        if self.frame_rate_mode not in FRAME_RATE_MODES:
            raise ValueError(
                f"frame_rate_mode must be one of {sorted(FRAME_RATE_MODES)}."
            )
        if self.fps is None and self.fps_source != "unknown":
            raise ValueError("fps_source must be 'unknown' when fps is None.")
        if self.frame_rate_mode == "cfr" and self.fps is None:
            raise ValueError("CFR media requires an fps value.")

    @property
    def frame_numbers_are_estimated(self) -> bool:
        """Whether timestamp-to-frame conversion lacks measured CFR evidence."""
        return not (
            self.frame_rate_mode == "cfr"
            and self.fps is not None
            and self.fps_source in {"qt", "ffprobe"}
        )


@dataclass
class AnnotationInterval:
    """Represents a continuous temporal phase interval [start_ms, end_ms)."""

    start_ms: int
    end_ms: int
    phase_id: int
    notes: str = ""

    def __post_init__(self):
        if self.start_ms < 0:
            raise ValueError(f"start_ms ({self.start_ms}) cannot be negative.")
        if self.start_ms >= self.end_ms:
            raise ValueError(
                f"start_ms ({self.start_ms}) must be less than end_ms ({self.end_ms})."
            )

    @property
    def duration_ms(self) -> int:
        return self.end_ms - self.start_ms


@dataclass
class AnnotationSession:
    """Encapsulates a full annotation session for a video."""

    video_info: VideoInfo
    annotator_id: str
    ontology_id: str = ""
    ontology_version: str = ""
    intervals: List[AnnotationInterval] = field(default_factory=list)
    schema_version: str = CURRENT_SESSION_SCHEMA_VERSION
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def add_interval(self, interval: AnnotationInterval) -> None:
        self.intervals.append(interval)
        self.updated_at = time.time()
