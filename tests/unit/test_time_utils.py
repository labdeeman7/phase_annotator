import pytest
from phase_annotator.domain.time_utils import ms_to_frame, frame_to_ms, format_timecode


def test_ms_to_frame():
    # 30 fps -> 1 frame = ~33.33ms
    assert ms_to_frame(0, fps=30.0) == 0
    assert ms_to_frame(1000, fps=30.0) == 30
    assert ms_to_frame(500, fps=25.0) == 12  # 0.5 sec * 25 fps = 12.5 -> 12


def test_frame_to_ms():
    assert frame_to_ms(0, fps=30.0) == 0
    assert frame_to_ms(30, fps=30.0) == 1000
    assert frame_to_ms(25, fps=25.0) == 1000


def test_format_timecode():
    assert format_timecode(0) == "00:00:00.000"
    assert format_timecode(1000) == "00:00:01.000"
    assert format_timecode(65432) == "00:01:05.432"
    assert format_timecode(3665432) == "01:01:05.432"


def test_time_utils_defensive_validation():
    with pytest.raises(ValueError, match="cannot be negative"):
        ms_to_frame(-100, fps=30.0)

    with pytest.raises(ValueError, match="FPS must be positive"):
        ms_to_frame(100, fps=0)

    with pytest.raises(ValueError, match="cannot be negative"):
        format_timecode(-50)
