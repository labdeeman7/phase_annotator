import pytest
from PySide6.QtCore import Qt
from phase_annotator.ui.main_window import MainWindow
from phase_annotator.ui.player_widget import VideoPlayerWidget
from phase_annotator.ui.timeline_widget import TimelineWidget
from phase_annotator.ui.segment_list_widget import SegmentListWidget
from phase_annotator.domain.models import AnnotationInterval


def test_main_window_instantiation(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert "Appendectomy Phase Annotation Tool" in window.windowTitle()


def test_timeline_widget_position(qtbot):
    timeline = TimelineWidget()
    qtbot.addWidget(timeline)
    timeline.set_duration(10000)
    timeline.set_position(5000)
    assert timeline._current_position_ms == 5000


def test_segment_list_widget_population(qtbot):
    segment_list = SegmentListWidget()
    qtbot.addWidget(segment_list)
    intervals = [
        AnnotationInterval(start_ms=0, end_ms=5000, phase_id=1, notes="Incision"),
        AnnotationInterval(start_ms=5000, end_ms=12000, phase_id=2, notes="Dissection")
    ]
    segment_list.set_intervals(intervals)
    assert segment_list._list_widget.count() == 2
