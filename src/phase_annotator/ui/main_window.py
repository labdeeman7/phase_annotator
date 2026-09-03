from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QFileDialog, QStyle, QSplitter, QApplication,
    QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox, QComboBox
)

from phase_annotator.ui.player_widget import VideoPlayerWidget
from phase_annotator.ui.timeline_widget import TimelineWidget
from phase_annotator.ui.segment_list_widget import SegmentListWidget
from phase_annotator.ui.phase_palette_widget import PhasePaletteWidget
from phase_annotator.domain.annotation_editor import AnnotationEditor
from phase_annotator.domain.models import AnnotationSession, VideoInfo
from phase_annotator.domain.ontology import PhaseOntology
from phase_annotator.domain.time_utils import format_timecode, ms_to_frame


class MainWindow(QMainWindow):
    """Main application window for Appendectomy Phase Annotation Tool."""

    def __init__(self, ontology: PhaseOntology):
        super().__init__()
        self.setWindowTitle("Appendectomy Phase Annotation Tool v0.2.0")
        self.resize(1200, 800)

        # Domain State
        self._ontology = ontology
        self._editor = AnnotationEditor(
            valid_phase_ids=self._ontology.phases,
            undefined_phase_id=self._ontology.undefined_phase_id,
            initial_phase_id=self._ontology.initial_phase_id,
        )
        self._session: Optional[AnnotationSession] = None
        self._video_path: Optional[Path] = None
        # Transient UI selection; valid only for the current interval sequence.
        self._selected_segment_index: Optional[int] = None

        # Core UI Widgets
        self._player_widget = VideoPlayerWidget(self)
        self._timeline_widget = TimelineWidget(self, ontology=self._ontology)
        self._segment_list_widget = SegmentListWidget(
            self, ontology=self._ontology
        )
        self._phase_palette = PhasePaletteWidget(self, ontology=self._ontology)
        self._phase_shortcuts = []

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

        self._btn_play = QPushButton("Play", self)
        self._btn_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self._btn_play.clicked.connect(self._player_widget.toggle_play)
        self._btn_play.setEnabled(False)

        self._btn_step_back = QPushButton("-1 Frame", self)
        self._btn_step_back.clicked.connect(lambda: self._player_widget.step_frames(-1))
        self._btn_step_back.setEnabled(False)

        self._btn_step_forward = QPushButton("+1 Frame", self)
        self._btn_step_forward.clicked.connect(lambda: self._player_widget.step_frames(1))
        self._btn_step_forward.setEnabled(False)

        btn_layout.addWidget(self._btn_open)
        btn_layout.addWidget(self._btn_play)
        btn_layout.addWidget(self._btn_step_back)
        btn_layout.addWidget(self._btn_step_forward)
        btn_layout.addStretch()

        control_layout.addLayout(btn_layout)
        left_layout.addLayout(control_layout)

        # Right Panel (Always-visible phase palette + segment cards)
        right_panel = QWidget(self)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self._phase_palette)
        right_layout.addWidget(self._segment_list_widget, stretch=1)

        # Add Panels to Splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([750, 450])
        main_layout.addWidget(splitter)

        # Wire Signals & Inter-Widget Connections
        self._player_widget.position_changed.connect(self._on_position_changed)
        self._player_widget.duration_changed.connect(self._on_duration_changed)
        self._player_widget.playback_state_changed.connect(
            self._on_playback_state_changed
        )
        self._timeline_widget.seek_requested.connect(self._player_widget.seek_ms)
        self._segment_list_widget.seek_requested.connect(self._player_widget.seek_ms)
        self._timeline_widget.segment_selected.connect(self._select_segment)
        self._segment_list_widget.segment_selected.connect(self._select_segment)
        self._phase_palette.phase_selected.connect(self.record_phase_transition)
        self._create_phase_shortcuts()
        QApplication.instance().focusChanged.connect(
            self._update_phase_shortcut_state
        )
        self.statusBar().showMessage("No video loaded")

    def keyPressEvent(self, event) -> None:
        """Dispatch configured phase hotkeys and playback/navigation keys."""
        key = event.key()

        if self._text_entry_has_focus():
            super().keyPressEvent(event)
            return

        if key == Qt.Key.Key_Space and self._btn_play.isEnabled():
            self._player_widget.toggle_play()
        elif key == Qt.Key.Key_Left:
            self._player_widget.step_frames(-1)
        elif key == Qt.Key.Key_Right:
            self._player_widget.step_frames(1)
        else:
            super().keyPressEvent(event)

    @staticmethod
    def _text_entry_has_focus() -> bool:
        focused = QApplication.focusWidget()
        if isinstance(focused, (QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox)):
            return True
        return isinstance(focused, QComboBox) and focused.isEditable()

    def _create_phase_shortcuts(self) -> None:
        """Create ontology-driven shortcuts that work across child widgets."""
        for phase in self._ontology.ordered_phases:
            shortcut = QShortcut(QKeySequence(phase.hotkey), self)
            shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
            shortcut.setAutoRepeat(False)
            shortcut.activated.connect(
                lambda phase_id=phase.id: self.record_phase_transition(phase_id)
            )
            shortcut.setEnabled(False)
            self._phase_shortcuts.append(shortcut)

    def _update_phase_shortcut_state(self, *_) -> None:
        """Reserve phase keys while focus belongs to editing/list contexts."""
        focused = QApplication.focusWidget()
        segment_list_has_focus = focused is not None and (
            focused is self._segment_list_widget
            or self._segment_list_widget.isAncestorOf(focused)
        )
        enabled = (
            self._session is not None
            and bool(self._session.intervals)
            and not self._text_entry_has_focus()
            and not segment_list_has_focus
        )
        for shortcut in self._phase_shortcuts:
            shortcut.setEnabled(enabled)

    def record_phase_transition(self, phase_id: int) -> None:
        """Records a phase transition at the current video position timestamp."""
        if not self._session or not self._session.intervals:
            return

        try:
            changed = self._editor.apply_transition(
                self._session,
                phase_id=phase_id,
                position_ms=self._player_widget.position_ms,
            )
        except ValueError as error:
            self.statusBar().showMessage(f"Annotation not changed: {error}", 5000)
            return

        if changed:
            # Splitting/coalescing can change every later index. Do not leave an
            # apparently selected card pointing at a different interval.
            self._select_segment(None)
            self._refresh_annotation_views()
            phase = self._ontology.get_phase_by_id(phase_id)
            self.statusBar().showMessage(
                f"Assigned {phase.name} at "
                f"{format_timecode(self._player_widget.position_ms)}",
                3000,
            )
        else:
            phase = self._ontology.get_phase_by_id(phase_id)
            self.statusBar().showMessage(
                f"Already {phase.name} at "
                f"{format_timecode(self._player_widget.position_ms)}",
                3000,
            )
        self._update_active_phase(self._player_widget.position_ms)

    def _open_file_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Surgical Video",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov);;All Files (*)"
        )
        if file_path:
            self._load_video(Path(file_path))

    def _load_video(self, path: Path) -> None:
        """Starts loading a video and prepares its empty annotation session."""
        self._video_path = path
        video_info = VideoInfo(
            video_id=path.name,
            duration_ms=0,
            fps=self._player_widget.fps,
        )
        self._session = AnnotationSession(
            video_info=video_info,
            annotator_id="surgeon_01",
            ontology_id=self._ontology.ontology_id,
            ontology_version=self._ontology.ontology_version,
        )
        self._select_segment(None)
        self._phase_palette.set_annotation_enabled(False)
        self._phase_palette.set_active_phase(None)
        self._update_phase_shortcut_state()
        self._refresh_annotation_views()
        self._on_playback_state_changed(False)
        self._btn_play.setEnabled(True)
        self._btn_step_back.setEnabled(True)
        self._btn_step_forward.setEnabled(True)
        self.statusBar().showMessage(f"Loading: {path.name}")
        self._player_widget.load_video(path)

    def _on_position_changed(self, position_ms: int) -> None:
        if not self._slider.isSliderDown():
            self._slider.setValue(position_ms)
        self._timeline_widget.set_position(position_ms)
        self._update_active_phase(position_ms)
        self._update_time_label(position_ms, self._slider.maximum())

    def _on_duration_changed(self, duration_ms: int) -> None:
        self._slider.setRange(0, duration_ms)
        self._timeline_widget.set_duration(duration_ms)
        if self._session and duration_ms > 0:
            self._session.video_info.duration_ms = duration_ms
            if not self._session.intervals:
                self._editor.initialize_coverage(self._session)
                self._refresh_annotation_views()
            self._phase_palette.set_annotation_enabled(bool(self._session.intervals))
            self._update_phase_shortcut_state()
            self._update_active_phase(self._player_widget.position_ms)
            if self._video_path:
                self.statusBar().showMessage(f"Loaded: {self._video_path.name}")
        self._update_time_label(self._player_widget.position_ms, duration_ms)

    def _on_playback_state_changed(self, is_playing: bool) -> None:
        if is_playing:
            self._btn_play.setText("Pause")
            icon = QStyle.StandardPixmap.SP_MediaPause
        else:
            self._btn_play.setText("Play")
            icon = QStyle.StandardPixmap.SP_MediaPlay
        self._btn_play.setIcon(self.style().standardIcon(icon))

    def _refresh_annotation_views(self) -> None:
        """Rebuild both interval views from the session source of truth."""
        intervals = self._session.intervals if self._session else []
        self._timeline_widget.set_intervals(intervals)
        self._segment_list_widget.set_intervals(intervals)
        # Protect future load/removal paths that may replace the interval
        # sequence without first clearing the transient selection.
        if (
            self._selected_segment_index is not None
            and self._selected_segment_index >= len(intervals)
        ):
            self._selected_segment_index = None
        self._timeline_widget.set_selected_index(self._selected_segment_index)
        self._segment_list_widget.set_selected_index(self._selected_segment_index)

    def _select_segment(self, index: Optional[int]) -> None:
        """Own one selection centrally and project it into both UI views."""
        if (
            index is not None
            and self._session
            and 0 <= index < len(self._session.intervals)
        ):
            self._selected_segment_index = index
        else:
            self._selected_segment_index = None
        self._timeline_widget.set_selected_index(self._selected_segment_index)
        self._segment_list_widget.set_selected_index(self._selected_segment_index)

    def _update_active_phase(self, position_ms: int) -> None:
        """Derive playhead-active state independently from edit selection."""
        active_phase_id = None
        active_index = None
        if self._session:
            for index, interval in enumerate(self._session.intervals):
                if interval.start_ms <= position_ms < interval.end_ms:
                    active_phase_id = interval.phase_id
                    active_index = index
                    break
        self._phase_palette.set_active_phase(active_phase_id)
        self._timeline_widget.set_active_index(active_index)
        self._segment_list_widget.set_active_index(active_index)

    def _on_slider_moved(self, position_ms: int) -> None:
        self._player_widget.seek_ms(position_ms)
        self._timeline_widget.set_position(position_ms)
        self._update_active_phase(position_ms)
        self._update_time_label(position_ms, self._slider.maximum())

    def _update_time_label(self, current_ms: int, duration_ms: int) -> None:
        current_str = format_timecode(current_ms)
        duration_str = format_timecode(duration_ms)
        frame_idx = ms_to_frame(current_ms, self._player_widget.fps)
        self._time_label.setText(f"{current_str} / {duration_str} (Frame {frame_idx})")
