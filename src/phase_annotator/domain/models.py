import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class VideoInfo:
    """Metadata describing the target video being annotated."""

    video_id: str
    duration_ms: int
    fps: float = 30.0
    width: Optional[int] = None
    height: Optional[int] = None


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
    intervals: List[AnnotationInterval] = field(default_factory=list)
    schema_version: str = "1.0"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def add_interval(self, interval: AnnotationInterval) -> None:
        self.intervals.append(interval)
        self.updated_at = time.time()
