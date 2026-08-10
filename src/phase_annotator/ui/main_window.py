from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QFileDialog, QStyle, QSplitter
)

from phase_annotator.ui.player_widget import VideoPlayerWidget
from phase_annotator.ui.timeline_widget import TimelineWidget
from phase_annotator.ui.segment_list_widget import SegmentListWidget
from phase_annotator.domain.models import AnnotationSession, AnnotationInterval, VideoInfo
from phase_annotator.domain.ontology import PhaseOntology
from phase_annotator.domain.time_utils import format_timecode, ms_to_frame


class MainWindow(QMainWindow):
    """Main application window for Appendectomy Phase Annotation Tool."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Appendectomy Phase Annotation Tool v0.2.0")
        self.resize(1200, 800)

        # Domain State
        self._ontology = PhaseOntology.default_appendectomy()
        self._session: Optional[AnnotationSession] = None

        # Core UI Widgets
        self._player_widget = VideoPlayerWidget(self)
        self._timeline_widget = TimelineWidget(self)
        self._segment_list_widget = SegmentListWidget(self)

        # Central Splitter Layout (Left: Video + Controls + Timeline, Right: Segment List Cards)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # Left Panel (Media & Timeline)
        left_panel = QWidget(self)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self._player_widget, stretch=1)
        left_layout.addWidget(self._timeline_widget)

        # Controls & Timecode
        control_layout = QVBoxLayout()
        slider_layout = QHBoxLayout()
        self._slider = QSlider(Qt.Orientation.Horizontal, self)
        self._slider.setRange(0, 0)
        self._slider.sliderMoved.connect(self._on_slider_moved)

        self._time_label = QLabel("00:00:00.000 / 00:00:00.000 (Frame 0)", self)
        slider_layout.addWidget(self._slider, stretch=1)
        slider_layout.addWidget(self._time_label)
        control_layout.addLayout(slider_layout)

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
        left_layout.addLayout(control_layout)

        # Add Panels to Splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(self._segment_list_widget)
        splitter.setSizes([750, 450])
        main_layout.addWidget(splitter)

        # Wire Signals & Inter-Widget Connections
        self._player_widget.position_changed.connect(self._on_position_changed)
        self._player_widget.duration_changed.connect(self._on_duration_changed)
        self._timeline_widget.seek_requested.connect(self._player_widget.seek_ms)
        self._segment_list_widget.seek_requested.connect(self._player_widget.seek_ms)

    def keyPressEvent(self, event) -> None:
        """Keyboard Hotkey Handling (1-6 for phases, Space for play/pause, Left/Right for step)."""
        key = event.key()

        if key == Qt.Key.Key_Space:
            self._player_widget.toggle_play()
        elif key == Qt.Key.Key_Left:
            self._player_widget.step_frames(-1)
        elif key == Qt.Key.Key_Right:
            self._player_widget.step_frames(1)
        elif Qt.Key.Key_1 <= key <= Qt.Key.Key_6:
            phase_id = key - Qt.Key.Key_0
            self.record_phase_transition(phase_id)
        else:
            super().keyPressEvent(event)

    def record_phase_transition(self, phase_id: int) -> None:
        """Records a phase transition at the current video position timestamp."""
        if not self._session:
            return

        current_ms = self._player_widget._player.position()
        duration_ms = self._player_widget._player.duration()

        # Update or close current interval and start new interval
        if self._session.intervals:
            self._session.intervals[-1].end_ms = current_ms

        new_interval = AnnotationInterval(
            start_ms=current_ms,
            end_ms=duration_ms if duration_ms > 0 else current_ms + 5000,
            phase_id=phase_id
        )
        self._session.add_interval(new_interval)

        # Refresh UI Views
        self._timeline_widget.set_intervals(self._session.intervals)
        self._segment_list_widget.set_intervals(self._session.intervals)

    def _open_file_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Surgical Video",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov);;All Files (*)"
        )
        if file_path:
            path = Path(file_path)
            self._player_widget.load_video(path)
            
            # Initialize Annotation Session
            video_info = VideoInfo(video_id=path.name, duration_ms=0, fps=self._player_widget.fps)
            self._session = AnnotationSession(video_info=video_info, annotator_id="surgeon_01")
            self._timeline_widget.set_intervals([])
            self._segment_list_widget.set_intervals([])

    def _on_position_changed(self, position_ms: int) -> None:
        if not self._slider.isSliderDown():
            self._slider.setValue(position_ms)
        self._timeline_widget.set_position(position_ms)
        self._update_time_label(position_ms, self._slider.maximum())

    def _on_duration_changed(self, duration_ms: int) -> None:
        self._slider.setRange(0, duration_ms)
        self._timeline_widget.set_duration(duration_ms)
        if self._session:
            self._session.video_info.duration_ms = duration_ms
        self._update_time_label(self._player_widget._player.position(), duration_ms)

    def _on_slider_moved(self, position_ms: int) -> None:
        self._player_widget.seek_ms(position_ms)
        self._timeline_widget.set_position(position_ms)
        self._update_time_label(position_ms, self._slider.maximum())

    def _update_time_label(self, current_ms: int, duration_ms: int) -> None:
        current_str = format_timecode(current_ms)
        duration_str = format_timecode(duration_ms)
        frame_idx = ms_to_frame(current_ms, self._player_widget.fps)
        self._time_label.setText(f"{current_str} / {duration_str} (Frame {frame_idx})")
