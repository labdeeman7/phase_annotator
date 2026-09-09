"""Media metadata adapters kept separate from annotation-domain behavior."""

from .metadata import MediaMetadata, MediaProbeFailure, probe_local_file

__all__ = ["MediaMetadata", "MediaProbeFailure", "probe_local_file"]
