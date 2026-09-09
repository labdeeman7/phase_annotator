"""Media metadata adapters kept separate from annotation-domain behavior."""

from .metadata import MediaMetadata, MediaProbeFailure, probe_local_file
from .matching import SourceComparison, SourceMatchStatus, compare_video_source

__all__ = [
    "MediaMetadata",
    "MediaProbeFailure",
    "SourceComparison",
    "SourceMatchStatus",
    "compare_video_source",
    "probe_local_file",
]
