import pytest
from PySide6.QtCore import Qt
from phase_annotator.ui.main_window import MainWindow
from phase_annotator.ui.player_widget import VideoPlayerWidget


def test_main_window_instantiation(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.windowTitle() == "Appendectomy Phase Annotation Tool v0.1.0"


def test_player_widget_default_fps(qtbot):
    player_widget = VideoPlayerWidget()
    qtbot.addWidget(player_widget)
    assert player_widget.fps == 30.0
    player_widget.fps = 25.0
    assert player_widget.fps == 25.0
