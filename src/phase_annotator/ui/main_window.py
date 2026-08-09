from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QFileDialog, QStyle
)

from phase_annotator.ui.player_widget import VideoPlayerWidget
from phase_annotator.domain.time_utils import format_timecode, ms_to_frame


class MainWindow(QMainWindow):
    """Main application window for Appendectomy Phase Annotation Tool."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Appendectomy Phase Annotation Tool v0.1.0")
        self.resize(1024, 720)

        # Core Components
        self._player_widget = VideoPlayerWidget(self)

        # Central Widget Layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # 1. Video Display
        main_layout.addWidget(self._player_widget, stretch=1)

        # 2. Scrubber & Timecode Controls
        control_layout = QVBoxLayout()
        
        slider_layout = QHBoxLayout()
        self._slider = QSlider(Qt.Orientation.Horizontal, self)
        self._slider.setRange(0, 0)
        self._slider.sliderMoved.connect(self._on_slider_moved)

        self._time_label = QLabel("00:00:00.000 / 00:00:00.000 (Frame 0)", self)

        slider_layout.addWidget(self._slider, stretch=1)
        slider_layout.addWidget(self._time_label)
        control_layout.addLayout(slider_layout)

        # 3. Playback Buttons
        btn_layout = QHBoxLayout()
        
        self._btn_open = QPushButton("Open Video", self)
        self._btn_open.clicked.connect(self._open_file_dialog)

        self._btn_play = QPushButton(self)
        self._btn_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self._btn_play.clicked.connect(self._player_widget.toggle_play)

        self._btn_step_back = QPushButton("-1 Frame", self)
        self._btn_step_back.clicked.connect(lambda: self._player_widget.step_frames(-1))

        self._btn_step_forward = QPushButton("+1 Frame", self)
        self._btn_step_forward.clicked.connect(lambda: self._player_widget.step_frames(1))

        btn_layout.addWidget(self._btn_open)
        btn_layout.addWidget(self._btn_play)
        btn_layout.addWidget(self._btn_step_back)
        btn_layout.addWidget(self._btn_step_forward)
        btn_layout.addStretch()

        control_layout.addLayout(btn_layout)
        main_layout.addLayout(control_layout)

        # Wire Signals
        self._player_widget.position_changed.connect(self._on_position_changed)
        self._player_widget.duration_changed.connect(self._on_duration_changed)

    def _open_file_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Surgical Video",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov);;All Files (*)"
        )
        if file_path:
            self._player_widget.load_video(Path(file_path))

    def _on_position_changed(self, position_ms: int) -> None:
        if not self._slider.isSliderDown():
            self._slider.setValue(position_ms)
        self._update_time_label(position_ms, self._slider.maximum())

    def _on_duration_changed(self, duration_ms: int) -> None:
        self._slider.setRange(0, duration_ms)
        self._update_time_label(self._player_widget._player.position(), duration_ms)

    def _on_slider_moved(self, position_ms: int) -> None:
        self._player_widget.seek_ms(position_ms)
        self._update_time_label(position_ms, self._slider.maximum())

    def _update_time_label(self, current_ms: int, duration_ms: int) -> None:
        current_str = format_timecode(current_ms)
        duration_str = format_timecode(duration_ms)
        frame_idx = ms_to_frame(current_ms, self._player_widget.fps)
        self._time_label.setText(f"{current_str} / {duration_str} (Frame {frame_idx})")
