"""Media metadata adapters kept separate from annotation-domain behavior."""

from .matching import SourceComparison, SourceMatchStatus, compare_video_source
from .metadata import MediaMetadata, MediaProbeFailure, probe_local_file

__all__ = [
    "MediaMetadata",
    "MediaProbeFailure",
    "SourceComparison",
    "SourceMatchStatus",
    "compare_video_source",
    "probe_local_file",
]
