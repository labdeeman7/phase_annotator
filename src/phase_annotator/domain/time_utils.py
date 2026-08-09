def ms_to_frame(timestamp_ms: int, fps: float) -> int:
    """Converts a millisecond timestamp to the nearest frame index given an FPS rate."""
    if timestamp_ms < 0:
        raise ValueError("Timestamp cannot be negative.")
    if fps <= 0:
        raise ValueError("FPS must be positive.")

    frame = int(timestamp_ms * fps / 1000.0)
    return frame


def frame_to_ms(frame_index: int, fps: float) -> int:
    """Converts a frame index to the corresponding millisecond timestamp given an FPS rate."""
    if frame_index < 0:
        raise ValueError("Frame index cannot be negative.")
    if fps <= 0:
        raise ValueError("FPS must be positive.")

    timestamp_ms = int(frame_index / fps * 1000.0)
    return timestamp_ms


def format_timecode(timestamp_ms: int) -> str:
    """Formats milliseconds into HH:MM:SS.mmm string (e.g. 65432 -> '00:01:05.432')."""
    if timestamp_ms < 0:
        raise ValueError("Timestamp cannot be negative.")

    total_seconds = timestamp_ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = timestamp_ms % 1000

    timecode = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    return timecode
