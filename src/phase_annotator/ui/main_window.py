from dataclasses import replace
from pathlib import Path
import time
from typing import Callable, Optional
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QFileDialog, QStyle, QSplitter, QApplication,
    QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox, QComboBox,
    QDialog, QMenu, QMessageBox
)

from phase_annotator.ui.player_widget import VideoPlayerWidget
from phase_annotator.ui.timeline_widget import TimelineWidget
from phase_annotator.ui.segment_list_widget import SegmentListWidget
from phase_annotator.ui.phase_palette_widget import PhasePaletteWidget
from phase_annotator.ui.segment_note_dialog import SegmentNoteDialog
from phase_annotator.ui.theme import APPLICATION_STYLESHEET
from phase_annotator.domain.annotation_editor import AnnotationEditor
from phase_annotator.domain.annotation_history import AnnotationHistory
from phase_annotator.domain.completion import summarize_completion
from phase_annotator.domain.models import AnnotationSession, VideoInfo
from phase_annotator.domain.ontology import PhaseOntology
from phase_annotator.domain.time_utils import format_timecode, ms_to_frame
from phase_annotator.media import MediaMetadata, probe_local_file
from phase_annotator import __version__
from phase_annotator.domain.models import CURRENT_SESSION_SCHEMA_VERSION
from phase_annotator.storage import (
    HistorySnapshotError,
    LoadStatus,
    SessionPersistenceCoordinator,
    SessionPersistenceError,
)


class MainWindow(QMainWindow):
    """Main application window for the configured phase ontology."""

    def __init__(self, ontology: PhaseOntology, annotator_id: str = "surgeon_01"):
        super().__init__()
        self._base_window_title = (
            f"Phase Annotator v{__version__} — {annotator_id}"
        )
        self.setWindowTitle(self._base_window_title)
        self.setStyleSheet(APPLICATION_STYLESHEET)
        self.resize(1200, 800)

        # Domain State
        self._ontology = ontology
        self._active_annotator_id = annotator_id
        self._editor = AnnotationEditor(
            valid_phase_ids=self._ontology.phases,
            undefined_phase_id=self._ontology.undefined_phase_id,
            initial_phase_id=self._ontology.initial_phase_id,
        )
        self._history = AnnotationHistory(max_entries=100)
        self._persistence = SessionPersistenceCoordinator(self._ontology)
        self._session: Optional[AnnotationSession] = None
        self._video_path: Optional[Path] = None
        self._media_load_failed = False
        self._sidecar_load_blocked = False
        self._sidecar_block_message = ""
        self._loaded_existing_session = False
        self._loading_video = False
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
        self._slider.setEnabled(False)
        self._slider.sliderMoved.connect(self._on_slider_moved)

        self._time_label = QLabel("00:00:00.000 / 00:00:00.000", self)
        slider_layout.addWidget(self._slider, stretch=1)
        slider_layout.addWidget(self._time_label)
        control_layout.addLayout(slider_layout)

        btn_layout = QHBoxLayout()
        self._btn_open = QPushButton("Open Video", self)
        self._btn_open.setObjectName("openVideoButton")
        self._btn_open.clicked.connect(self._open_file_dialog)

        self._btn_play = QPushButton("Play", self)
        self._btn_play.setObjectName("playButton")
        self._btn_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self._btn_play.clicked.connect(self._player_widget.toggle_play)
        self._btn_play.setEnabled(False)

        self._btn_step_back = QPushButton("-1 Frame", self)
        self._btn_step_back.clicked.connect(lambda: self._player_widget.step_frames(-1))
        self._btn_step_back.setEnabled(False)

        self._btn_step_forward = QPushButton("+1 Frame", self)
        self._btn_step_forward.clicked.connect(lambda: self._player_widget.step_frames(1))
        self._btn_step_forward.setEnabled(False)

        self._btn_undo = QPushButton("Undo", self)
        self._btn_undo.setToolTip("Nothing to undo (Ctrl+Z)")
        self._btn_undo.clicked.connect(self._undo_annotation)
        self._btn_undo.setEnabled(False)

        self._btn_redo = QPushButton("Redo", self)
        self._btn_redo.setToolTip("Nothing to redo (Ctrl+Shift+Z or Ctrl+Y)")
        self._btn_redo.clicked.connect(self._redo_annotation)
        self._btn_redo.setEnabled(False)

        btn_layout.addWidget(self._btn_open)
        btn_layout.addWidget(self._btn_play)
        btn_layout.addWidget(self._btn_step_back)
        btn_layout.addWidget(self._btn_step_forward)
        btn_layout.addWidget(self._btn_undo)
        btn_layout.addWidget(self._btn_redo)
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
        self._player_widget.metadata_available.connect(
            self._on_media_metadata_available
        )
        self._player_widget.media_error.connect(self._on_media_error)
        self._timeline_widget.segment_selection_requested.connect(
            self._request_segment_selection
        )
        self._timeline_widget.boundary_preview_requested.connect(
            self._preview_boundary_drag
        )
        self._timeline_widget.boundary_move_requested.connect(
            self._commit_boundary_drag
        )
        self._timeline_widget.boundary_drag_cancelled.connect(
            self._cancel_boundary_drag
        )
        self._segment_list_widget.segment_selection_requested.connect(
            self._request_segment_selection
        )
        self._segment_list_widget.segment_actions_requested.connect(
            self._show_segment_actions
        )
        self._phase_palette.phase_selected.connect(self.record_phase_transition)
        self._create_phase_shortcuts()
        self._create_history_shortcuts()

        self._resume_timer = QTimer(self)
        self._resume_timer.setInterval(10_000)
        self._resume_timer.timeout.connect(self._checkpoint_resume_during_playback)
        self._resume_timer.start()
        QApplication.instance().focusChanged.connect(
            self._update_phase_shortcut_state
        )
        QApplication.instance().focusChanged.connect(self._update_history_controls)
        self._create_annotation_menu()
        self._update_annotation_menu()
        self.statusBar().showMessage("No video loaded")

    def _create_annotation_menu(self) -> None:
        menu = self.menuBar().addMenu("Annotation")
        self._action_video_note = QAction("Edit video note...", self)
        self._action_video_note.triggered.connect(self._edit_video_note)
        menu.addAction(self._action_video_note)
        menu.addSeparator()
        self._action_mark_complete = QAction("Mark complete...", self)
        self._action_mark_complete.triggered.connect(self._mark_complete)
        menu.addAction(self._action_mark_complete)
        self._action_reopen = QAction("Reopen for editing...", self)
        self._action_reopen.triggered.connect(self._reopen_completed_session)
        menu.addAction(self._action_reopen)

    def _update_annotation_menu(self) -> None:
        has_session = self._session is not None and bool(self._session.intervals)
        completed = has_session and self._session.status == "completed"
        self._action_video_note.setEnabled(has_session)
        self._action_video_note.setText(
            "View/edit video note..." if completed else "Edit video note..."
        )
        self._action_mark_complete.setEnabled(has_session and not completed)
        self._action_reopen.setEnabled(bool(completed))

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

    def _create_history_shortcuts(self) -> None:
        """Create application history shortcuts without stealing text undo."""
        self._undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self._undo_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self._undo_shortcut.activated.connect(self._undo_annotation)

        self._redo_shortcuts = []
        for sequence in ("Ctrl+Shift+Z", "Ctrl+Y"):
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
            shortcut.activated.connect(self._redo_annotation)
            self._redo_shortcuts.append(shortcut)
        self._update_history_controls()

    def _update_history_controls(self, *_) -> None:
        """Project stack availability into buttons, tooltips, and shortcuts."""
        can_undo = self._session is not None and self._history.can_undo
        can_redo = self._session is not None and self._history.can_redo
        self._btn_undo.setEnabled(can_undo)
        self._btn_redo.setEnabled(can_redo)

        undo_description = self._history.undo_description
        redo_description = self._history.redo_description
        self._btn_undo.setToolTip(
            f"Undo {undo_description} (Ctrl+Z)"
            if undo_description
            else "Nothing to undo (Ctrl+Z)"
        )
        self._btn_redo.setToolTip(
            f"Redo {redo_description} (Ctrl+Shift+Z or Ctrl+Y)"
            if redo_description
            else "Nothing to redo (Ctrl+Shift+Z or Ctrl+Y)"
        )

        shortcuts_allowed = not self._text_entry_has_focus()
        self._undo_shortcut.setEnabled(can_undo and shortcuts_allowed)
        for shortcut in self._redo_shortcuts:
            shortcut.setEnabled(can_redo and shortcuts_allowed)

    def _ensure_session_editable(self) -> bool:
        if self._session is None:
            return False
        if self._session.status != "completed":
            return True
        return self._reopen_completed_session()

    def _execute_annotation_command(
        self,
        *,
        description: str,
        anchor_ms: int,
        mutation: Callable[[], bool],
    ) -> bool:
        """Run one mutation through the shared history boundary."""
        if not self._session or not self._ensure_session_editable():
            return False
        changed = self._history.execute(
            self._session,
            description=description,
            anchor_ms=anchor_ms,
            mutation=mutation,
        )
        if changed:
            self._mark_annotation_changed()
            self._persist_session()
        self._update_history_controls()
        return changed

    def record_phase_transition(self, phase_id: int) -> None:
        """Records a phase transition at the current video position timestamp."""
        if not self._session or not self._session.intervals:
            return
        position_ms = self._player_widget.position_ms
        try:
            changed = self._execute_annotation_command(
                description=f"assign phase {phase_id}",
                anchor_ms=position_ms,
                mutation=lambda: self._editor.apply_transition(
                    self._session,
                    phase_id=phase_id,
                    position_ms=position_ms,
                ),
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
                f"{format_timecode(position_ms)}",
                3000,
            )
        else:
            phase = self._ontology.get_phase_by_id(phase_id)
            self.statusBar().showMessage(
                f"Already {phase.name} at "
                f"{format_timecode(position_ms)}",
                3000,
            )
        self._update_active_phase(position_ms)

    def _open_file_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Surgical Video",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov);;All Files (*)"
        )
        if file_path:
            self._load_video(Path(file_path))

    def _load_video(self, path: Path) -> bool:
        """Starts loading a video and prepares its empty annotation session."""
        if not self._prepare_to_leave_current_session("open another video"):
            return False
        self._video_path = path
        self._loading_video = True
        self._media_load_failed = False
        self._sidecar_load_blocked = False
        self._sidecar_block_message = ""
        self._loaded_existing_session = False
        source_metadata = probe_local_file(path)
        video_info = VideoInfo(
            video_id=path.name,
            duration_ms=0,
            fps=self._player_widget.fps,
            source_path=source_metadata.source_path,
            file_size_bytes=source_metadata.file_size_bytes,
            file_modified_ns=source_metadata.file_modified_ns,
            fps_source="assumed",
            frame_rate_mode="unknown",
        )
        new_session = AnnotationSession(
            video_info=video_info,
            annotator_id=self._active_annotator_id,
            created_by=self._active_annotator_id,
            ontology_id=self._ontology.ontology_id,
            ontology_version=self._ontology.ontology_version,
        )
        load_result = self._persistence.inspect(path, source_metadata)
        if load_result.status is LoadStatus.NEW:
            self._session = new_session
            self._persistence.bind(load_result.sidecar_path)
        elif load_result.status is LoadStatus.LOADED:
            self._accept_loaded_session(load_result.session, source_metadata)
            self._persistence.bind(load_result.sidecar_path)
        elif load_result.status is LoadStatus.UNKNOWN_SOURCE:
            answer = QMessageBox.question(
                self,
                "Confirm annotation sidecar",
                "The existing annotation sidecar lacks enough source metadata "
                "to confirm this video. Load it anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._accept_loaded_session(load_result.session, source_metadata)
                self._persistence.bind(load_result.sidecar_path)
            else:
                self._session = new_session
                self._block_sidecar("Existing annotations were not confirmed.")
        else:
            self._session = new_session
            self._block_sidecar(load_result.message)
        self._history.clear()
        self._update_history_controls()
        self._update_annotation_menu()
        self._select_segment(None)
        self._phase_palette.set_annotation_enabled(False)
        self._phase_palette.set_active_phase(None)
        self._update_phase_shortcut_state()
        self._refresh_annotation_views()
        self._on_playback_state_changed(False)
        self._loading_video = False
        self._set_media_controls_enabled(True)
        if self._sidecar_load_blocked:
            self._timeline_widget.setEnabled(False)
            self._segment_list_widget.setEnabled(False)
        if source_metadata.failure is not None:
            self._on_media_error(
                f"The video file is missing or unreadable: {path.name}"
            )
            return False
        if self._sidecar_load_blocked:
            self.statusBar().showMessage(self._sidecar_block_message)
        else:
            self.statusBar().showMessage(f"Loading: {path.name}")
        self._player_widget.load_video(path)
        return True

    def _accept_loaded_session(
        self, session: AnnotationSession, source_metadata: MediaMetadata
    ) -> None:
        self._session = session
        self._loaded_existing_session = True
        self._session.schema_version = CURRENT_SESSION_SCHEMA_VERSION
        self._session.video_info = replace(
            self._session.video_info,
            source_path=source_metadata.source_path,
            file_size_bytes=source_metadata.file_size_bytes,
            file_modified_ns=source_metadata.file_modified_ns,
        )

    def _block_sidecar(self, message: str) -> None:
        self._sidecar_load_blocked = True
        self._sidecar_block_message = f"Annotations unavailable: {message}"

    def _mark_annotation_changed(self) -> None:
        if self._session is None:
            return
        self._session.last_edited_by = self._active_annotator_id
        self._persistence.mark_annotation_changed()

    def _update_dirty_indicator(self) -> None:
        suffix = " [UNSAVED]" if self._persistence.is_dirty else ""
        lifecycle = ""
        if self._session is not None:
            lifecycle = (
                " — Completed"
                if self._session.status == "completed"
                else " — Draft"
            )
        self.setWindowTitle(f"{self._base_window_title}{lifecycle}{suffix}")

    def _persist_session(self) -> bool:
        """Write the current valid session to its canonical sidecar immediately."""
        if (
            self._session is None
            or self._persistence.sidecar_path is None
            or self._sidecar_load_blocked
            or not self._session.intervals
        ):
            return False

        duration_ms = self._session.video_info.duration_ms
        self._session.resume_position_ms = min(
            max(self._player_widget.position_ms, 0), duration_ms
        )
        self._session.updated_at = time.time()
        self._persistence.mark_dirty()
        self._update_dirty_indicator()
        try:
            self._persistence.save(self._session)
        except SessionPersistenceError as error:
            self.statusBar().showMessage(f"Annotations not saved: {error}")
            return False
        self._update_dirty_indicator()
        return True

    def _edit_video_note(self) -> None:
        if self._session is None:
            return
        dialog = SegmentNoteDialog(
            self._session.session_notes,
            self,
            title="Edit video note",
            label="Video note",
            placeholder="Optional: record an overall observation about this video",
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_video_note(dialog.notes)

    def _save_video_note(self, notes: str) -> bool:
        """Persist a video-level note without confusing it with interval history."""
        if self._session is None or notes == self._session.session_notes:
            return False
        if not self._ensure_session_editable():
            return False
        self._session.session_notes = notes
        self._mark_annotation_changed()
        saved = self._persist_session()
        self._update_annotation_menu()
        if saved:
            self.statusBar().showMessage("Video note saved", 3000)
        return saved

    def _mark_complete(self) -> bool:
        """Validate, summarize, and persist the annotator's declaration."""
        if self._session is None or self._session.status == "completed":
            return False
        errors = self._persistence.validation_errors(self._session)
        if self._persistence.is_dirty:
            errors.append("the latest annotation changes are not saved")
        if errors:
            QMessageBox.warning(
                self,
                "Cannot mark complete",
                "Resolve these problems first:\n\n- " + "\n- ".join(errors),
            )
            return False

        summary = summarize_completion(
            self._session,
            undefined_phase_id=self._ontology.undefined_phase_id,
        )
        answer = QMessageBox.question(
            self,
            "Mark annotation complete?",
            f"Duration: {format_timecode(summary.duration_ms)}\n"
            f"Segments: {summary.segment_count}\n"
            f"Undefined: {summary.undefined_segment_count} segment(s), "
            f"{format_timecode(summary.undefined_duration_ms)}\n"
            f"Video note: {'present' if summary.has_session_note else 'none'}\n\n"
            "This declares that you have reviewed the annotation. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return False

        self._session.status = "completed"
        self._session.completed_at = time.time()
        self._session.completed_by = self._active_annotator_id
        self._mark_annotation_changed()
        saved = self._persist_session()
        if saved:
            self._history.clear()
            self._update_history_controls()
            self._update_annotation_menu()
            self._update_dirty_indicator()
            self.statusBar().showMessage("Annotation marked complete", 4000)
        return saved

    def _reopen_completed_session(self, *_) -> bool:
        """Archive the completed record before permitting any correction."""
        if self._session is None:
            return False
        if self._session.status != "completed":
            return True
        answer = QMessageBox.question(
            self,
            "Reopen completed annotation?",
            "A recovery copy of the completed annotation will be archived before "
            "it returns to Draft. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return False
        # Verify the canonical completed record is still writable/current before
        # using it as the recovery point for a new draft revision.
        if not self._persist_session():
            return False
        try:
            self._persistence.archive_snapshot(self._session)
        except HistorySnapshotError as error:
            QMessageBox.warning(
                self,
                "Could not reopen annotation",
                "The completed annotation was not changed because its recovery "
                f"copy could not be written: {error}",
            )
            return False

        self._session.status = "draft"
        self._session.completed_at = None
        self._session.completed_by = None
        self._history.clear()
        self._mark_annotation_changed()
        saved = self._persist_session()
        self._update_history_controls()
        self._update_annotation_menu()
        self._update_dirty_indicator()
        if saved:
            self.statusBar().showMessage("Annotation reopened as Draft", 4000)
        return saved

    def _checkpoint_resume(self) -> None:
        """Persist a meaningful playback checkpoint without saving every tick."""
        if (
            self._loading_video
            or self._session is None
            or not self._session.intervals
        ):
            return
        position_ms = min(
            max(self._player_widget.position_ms, 0),
            self._session.video_info.duration_ms,
        )
        if position_ms != self._session.resume_position_ms:
            self._persist_session()

    def _checkpoint_resume_during_playback(self) -> None:
        if self._player_widget.is_playing:
            self._checkpoint_resume()

    def _prepare_to_leave_current_session(self, action: str) -> bool:
        """Save current state and archive it once when annotations changed."""
        self._checkpoint_resume()
        if self._persistence.is_dirty:
            if not self._resolve_dirty_state(action):
                return False
            # Discard permits leaving without turning unresolved memory into a
            # misleading canonical save or history snapshot.
            if self._persistence.is_dirty:
                return True
        if (
            self._session is None
            or not self._session.intervals
            or self._persistence.sidecar_path is None
            or self._sidecar_load_blocked
        ):
            return True
        if not self._persistence.annotation_changed:
            return True
        return self._archive_changed_run(action)

    def _resolve_dirty_state(self, action: str) -> bool:
        choice = QMessageBox.warning(
            self,
            "Unsaved annotations",
            f"The latest annotations could not be written before trying to {action}.",
            QMessageBox.StandardButton.Retry
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Retry,
        )
        if choice == QMessageBox.StandardButton.Retry:
            return self._persist_session()
        return choice == QMessageBox.StandardButton.Discard

    def _archive_changed_run(self, action: str) -> bool:
        while True:
            try:
                self._persistence.archive_snapshot(self._session)
                return True
            except HistorySnapshotError as error:
                choice = QMessageBox.warning(
                    self,
                    "History snapshot not created",
                    f"Annotations are saved, but their history snapshot failed: {error}",
                    QMessageBox.StandardButton.Retry
                    | QMessageBox.StandardButton.Ignore
                    | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Retry,
                )
                if choice == QMessageBox.StandardButton.Retry:
                    continue
                if choice == QMessageBox.StandardButton.Ignore:
                    self._persistence.reset_annotation_changed()
                    return True
                self.statusBar().showMessage(
                    f"Cancelled {action}: history snapshot was not created"
                )
                return False

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._prepare_to_leave_current_session("close the application"):
            event.accept()
        else:
            event.ignore()

    def _on_media_metadata_available(self, metadata: MediaMetadata) -> None:
        """Apply late Qt metadata only when it belongs to the current video."""
        if (
            self._media_load_failed
            or self._session is None
            or self._video_path is None
        ):
            return
        if metadata.source_path != str(self._video_path.resolve()):
            return

        current = self._session.video_info
        fps = metadata.fps if metadata.fps is not None else current.fps
        fps_source = metadata.fps_source if metadata.fps is not None else current.fps_source
        self._session.video_info = replace(
            current,
            duration_ms=(
                current.duration_ms
                if self._loaded_existing_session
                else metadata.duration_ms or current.duration_ms
            ),
            width=metadata.width or current.width,
            height=metadata.height or current.height,
            file_size_bytes=metadata.file_size_bytes,
            file_modified_ns=metadata.file_modified_ns,
            fps=fps,
            fps_source=fps_source,
            frame_rate_mode=metadata.frame_rate_mode,
        )
        if metadata.fps is not None:
            self._player_widget.fps = metadata.fps
        self._refresh_annotation_views()
        self._update_time_label(
            self._player_widget.position_ms, self._slider.maximum()
        )

    def _on_position_changed(self, position_ms: int) -> None:
        if not self._slider.isSliderDown():
            self._slider.setValue(position_ms)
        self._timeline_widget.set_position(position_ms)
        self._update_active_phase(position_ms)
        self._update_time_label(position_ms, self._slider.maximum())

    def _on_duration_changed(self, duration_ms: int) -> None:
        self._slider.setRange(0, duration_ms)
        self._timeline_widget.set_duration(duration_ms)
        if (
            self._session
            and duration_ms > 0
            and not self._media_load_failed
            and not self._sidecar_load_blocked
        ):
            if (
                self._loaded_existing_session
                and abs(self._session.video_info.duration_ms - duration_ms) > 100
            ):
                self._block_sidecar(
                    "The saved duration conflicts with the loaded video."
                )
                self._phase_palette.set_annotation_enabled(False)
                self._timeline_widget.setEnabled(False)
                self._segment_list_widget.setEnabled(False)
                self.statusBar().showMessage(self._sidecar_block_message)
                self._update_phase_shortcut_state()
                self._update_time_label(self._player_widget.position_ms, duration_ms)
                return
            if not self._loaded_existing_session:
                self._session.video_info.duration_ms = duration_ms
            if not self._session.intervals:
                self._editor.initialize_coverage(self._session)
                self._refresh_annotation_views()
                self._persist_session()
            elif self._loaded_existing_session:
                self._timeline_widget.set_duration(
                    self._session.video_info.duration_ms
                )
                self._persist_session()
                self._player_widget.seek_ms(self._session.resume_position_ms)
            self._phase_palette.set_annotation_enabled(bool(self._session.intervals))
            self._update_phase_shortcut_state()
            self._update_active_phase(self._player_widget.position_ms)
            if self._video_path:
                if not self._persistence.is_dirty:
                    self.statusBar().showMessage(f"Loaded: {self._video_path.name}")
        self._update_time_label(self._player_widget.position_ms, duration_ms)

    def _on_media_error(self, message: str) -> None:
        """Leave a failed load visible but impossible to annotate accidentally."""
        self._media_load_failed = True
        self._player_widget.pause()
        self._set_media_controls_enabled(False)
        self._phase_palette.set_annotation_enabled(False)
        self._phase_palette.set_active_phase(None)
        self._update_phase_shortcut_state()
        name = self._video_path.name if self._video_path else "video"
        self.statusBar().showMessage(f"Could not load {name}: {message}")

    def _set_media_controls_enabled(self, enabled: bool) -> None:
        self._btn_play.setEnabled(enabled)
        self._btn_step_back.setEnabled(enabled)
        self._btn_step_forward.setEnabled(enabled)
        self._slider.setEnabled(enabled)
        self._timeline_widget.setEnabled(enabled)
        self._segment_list_widget.setEnabled(enabled)

    def _on_playback_state_changed(self, is_playing: bool) -> None:
        if is_playing:
            self._btn_play.setText("Pause")
            icon = QStyle.StandardPixmap.SP_MediaPause
        else:
            self._btn_play.setText("Play")
            icon = QStyle.StandardPixmap.SP_MediaPlay
        self._btn_play.setIcon(self.style().standardIcon(icon))
        if not is_playing:
            self._checkpoint_resume()

    def _refresh_annotation_views(self) -> None:
        """Rebuild both interval views from the session source of truth."""
        intervals = self._session.intervals if self._session else []
        if self._session is not None and self._session.video_info.fps is not None:
            video_info = self._session.video_info
            self._segment_list_widget.set_fps(video_info.fps)
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
        self._update_annotation_menu()

    def _request_segment_selection(self, index: int, seek_ms: int) -> None:
        """Select one segment and perform its associated navigation request."""
        self._select_segment(index)
        self._player_widget.seek_ms(seek_ms)

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

    def _show_segment_actions(self, index: int, screen_position) -> None:
        """Show the shared action menu for a segment card."""
        if not self._session or not 0 <= index < len(self._session.intervals):
            return
        self._select_segment(index)
        menu = QMenu(self)
        edit_note_action = menu.addAction("Edit note...")
        phase_menu = menu.addMenu("Change phase")
        phase_actions = []
        current_phase_id = self._session.intervals[index].phase_id
        for phase in self._ontology.ordered_phases:
            action = phase_menu.addAction(f"{phase.hotkey}  {phase.name}")
            action.setCheckable(True)
            action.setChecked(phase.id == current_phase_id)
            phase_actions.append((action, phase.id))
        menu.addSeparator()
        set_start_action = menu.addAction("Set start to playhead")
        set_start_action.setEnabled(index > 0)
        set_end_action = menu.addAction("Set end to playhead")
        set_end_action.setEnabled(index < len(self._session.intervals) - 1)
        resolve_menu = menu.addMenu("Remove / merge")
        undefined_phase = self._ontology.get_phase_by_id(
            self._ontology.undefined_phase_id
        )
        undefined_action = resolve_menu.addAction(
            f"Convert to {undefined_phase.name}"
        )
        merge_left_action = resolve_menu.addAction("Merge left")
        merge_left_action.setEnabled(index > 0)
        merge_right_action = resolve_menu.addAction("Merge right")
        merge_right_action.setEnabled(index < len(self._session.intervals) - 1)
        chosen_action = menu.exec(screen_position)
        if chosen_action is edit_note_action:
            self._edit_segment_note(index)
            return
        for action, phase_id in phase_actions:
            if chosen_action is action:
                self._relabel_segment(index, phase_id)
                return
        if chosen_action is set_start_action:
            self._move_segment_boundary(
                index, boundary_index=index, boundary_name="start"
            )
        elif chosen_action is set_end_action:
            self._move_segment_boundary(
                index, boundary_index=index + 1, boundary_name="end"
            )
        elif chosen_action is undefined_action:
            self._resolve_segment(index, resolution="undefined")
        elif chosen_action is merge_left_action:
            self._resolve_segment(index, resolution="left")
        elif chosen_action is merge_right_action:
            self._resolve_segment(index, resolution="right")

    def _edit_segment_note(self, index: int) -> None:
        """Edit one segment note without exposing a persistent UI draft."""
        if not self._session or not 0 <= index < len(self._session.intervals):
            return
        dialog = SegmentNoteDialog(self._session.intervals[index].notes, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_segment_note(index, dialog.notes)

    def _save_segment_note(self, index: int, notes: str) -> bool:
        """Commit one dialog result while preserving segment selection."""
        if not self._session or not 0 <= index < len(self._session.intervals):
            return False
        try:
            changed = self._execute_annotation_command(
                description="edit segment note",
                anchor_ms=self._session.intervals[index].start_ms,
                mutation=lambda: self._editor.update_notes(
                    self._session, index, notes
                ),
            )
        except ValueError as error:
            self.statusBar().showMessage(f"Note not saved: {error}", 5000)
            return False
        if not changed:
            self.statusBar().showMessage("Segment note unchanged", 3000)
            return False
        self._refresh_annotation_views()
        self.statusBar().showMessage("Segment note saved", 3000)
        return True

    def _relabel_segment(self, index: int, phase_id: int) -> bool:
        """Relabel a complete segment and keep its resulting interval selected."""
        if not self._session or not 0 <= index < len(self._session.intervals):
            return False
        anchor_ms = self._session.intervals[index].start_ms
        try:
            changed = self._execute_annotation_command(
                description=f"change segment to phase {phase_id}",
                anchor_ms=anchor_ms,
                mutation=lambda: self._editor.relabel_interval(
                    self._session, interval_index=index, phase_id=phase_id
                ),
            )
        except ValueError as error:
            self.statusBar().showMessage(f"Segment not relabeled: {error}", 5000)
            return False

        phase = self._ontology.get_phase_by_id(phase_id)
        if not changed:
            self.statusBar().showMessage(
                f"Segment is already {phase.name}", 3000
            )
            return False

        self._select_interval_containing(anchor_ms)
        self._refresh_annotation_views()
        self._update_active_phase(self._player_widget.position_ms)
        self.statusBar().showMessage(f"Segment changed to {phase.name}", 3000)
        return True

    def _select_interval_containing(self, position_ms: int) -> None:
        """Relocate selection after an edit may have coalesced intervals."""
        if not self._session:
            self._selected_segment_index = None
            return
        self._selected_segment_index = next(
            (
                candidate_index
                for candidate_index, interval in enumerate(self._session.intervals)
                if interval.start_ms <= position_ms < interval.end_ms
            ),
            None,
        )

    def _move_segment_boundary(
        self,
        segment_index: int,
        *,
        boundary_index: int,
        boundary_name: str,
    ) -> bool:
        """Move a selected segment boundary to the current playhead."""
        if (
            not self._session
            or not 0 <= segment_index < len(self._session.intervals)
        ):
            return False
        return self._move_boundary_to_position(
            segment_index,
            boundary_index=boundary_index,
            boundary_name=boundary_name,
            position_ms=self._player_widget.position_ms,
            history_description=f"move segment {boundary_name}",
        )

    def _move_boundary_to_position(
        self,
        segment_index: int,
        *,
        boundary_index: int,
        boundary_name: str,
        position_ms: int,
        history_description: str,
    ) -> bool:
        """Commit one boundary position through validation and history."""
        if (
            not self._session
            or not 0 <= segment_index < len(self._session.intervals)
        ):
            return False
        selected = self._session.intervals[segment_index]
        anchor_ms = (
            selected.end_ms - 1
            if boundary_name == "start"
            else selected.start_ms
        )
        try:
            changed = self._execute_annotation_command(
                description=history_description,
                anchor_ms=anchor_ms,
                mutation=lambda: self._editor.move_boundary(
                    self._session,
                    boundary_index=boundary_index,
                    position_ms=position_ms,
                ),
            )
        except ValueError as error:
            self.statusBar().showMessage(f"Boundary not changed: {error}", 5000)
            return False
        if not changed:
            self.statusBar().showMessage("Boundary is already at the playhead", 3000)
            return False

        self._selected_segment_index = segment_index
        self._refresh_annotation_views()
        self._update_active_phase(position_ms)
        self.statusBar().showMessage(
            f"Segment {boundary_name} set to {format_timecode(position_ms)}",
            3000,
        )
        return True

    def _preview_boundary_drag(self, position_ms: int) -> None:
        """Seek with a transient drag preview without changing annotation data."""
        self._player_widget.seek_ms(position_ms)
        self._timeline_widget.set_position(position_ms)
        self._update_active_phase(position_ms)
        self._update_time_label(position_ms, self._slider.maximum())

    def _commit_boundary_drag(self, boundary_index: int, position_ms: int) -> None:
        """Commit a completed timeline drag as exactly one history command."""
        self._move_boundary_to_position(
            boundary_index,
            boundary_index=boundary_index,
            boundary_name="start",
            position_ms=position_ms,
            history_description="drag timeline boundary",
        )

    def _cancel_boundary_drag(self, reason: str, original_ms: int) -> None:
        """Restore preview seeking and report why no drag command was created."""
        self._preview_boundary_drag(original_ms)
        messages = {
            "unchanged": "Boundary drag made no change",
            "invalid": "Boundary drag cancelled: position would invalidate a segment",
            "cancelled": "Boundary drag cancelled",
        }
        self.statusBar().showMessage(messages.get(reason, "Boundary drag cancelled"), 3000)

    def _resolve_segment(self, index: int, *, resolution: str) -> bool:
        """Apply one explicit no-gap resolution for a selected segment."""
        if not self._session or not 0 <= index < len(self._session.intervals):
            return False
        anchor_ms = self._session.intervals[index].start_ms
        operations = {
            "undefined": self._editor.convert_to_undefined,
            "left": self._editor.merge_left,
            "right": self._editor.merge_right,
        }
        operation = operations.get(resolution)
        if operation is None:
            raise ValueError(f"Unknown segment resolution '{resolution}'.")
        try:
            changed = self._execute_annotation_command(
                description={
                    "undefined": "convert segment to Undefined",
                    "left": "merge segment left",
                    "right": "merge segment right",
                }[resolution],
                anchor_ms=anchor_ms,
                mutation=lambda: operation(self._session, index),
            )
        except ValueError as error:
            self.statusBar().showMessage(f"Segment not changed: {error}", 5000)
            return False
        if not changed:
            self.statusBar().showMessage("Segment is already Undefined", 3000)
            return False

        self._select_interval_containing(anchor_ms)
        self._refresh_annotation_views()
        self._update_active_phase(self._player_widget.position_ms)
        labels = {
            "undefined": "Segment converted to Undefined",
            "left": "Segment merged left",
            "right": "Segment merged right",
        }
        self.statusBar().showMessage(labels[resolution], 3000)
        return True

    def _undo_annotation(self) -> None:
        """Restore the previous validated annotation snapshot."""
        if not self._session or not self._ensure_session_editable():
            return
        try:
            entry = self._history.undo(self._session, self._editor)
        except ValueError as error:
            self.statusBar().showMessage(f"Undo failed: {error}", 5000)
            return
        if entry is None:
            return
        self._select_interval_containing(entry.anchor_ms)
        self._refresh_annotation_views()
        self._update_active_phase(self._player_widget.position_ms)
        self._update_history_controls()
        self._mark_annotation_changed()
        self._persist_session()
        self.statusBar().showMessage(f"Undid {entry.description}", 3000)

    def _redo_annotation(self) -> None:
        """Restore the next validated annotation snapshot."""
        if not self._session or not self._ensure_session_editable():
            return
        try:
            entry = self._history.redo(self._session, self._editor)
        except ValueError as error:
            self.statusBar().showMessage(f"Redo failed: {error}", 5000)
            return
        if entry is None:
            return
        self._select_interval_containing(entry.anchor_ms)
        self._refresh_annotation_views()
        self._update_active_phase(self._player_widget.position_ms)
        self._update_history_controls()
        self._mark_annotation_changed()
        self._persist_session()
        self.statusBar().showMessage(f"Redid {entry.description}", 3000)

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
        if self._session is None or self._session.video_info.fps is None:
            self._time_label.setText(f"{current_str} / {duration_str}")
            self._time_label.setToolTip("")
            return

        video_info = self._session.video_info
        frame_idx = ms_to_frame(current_ms, video_info.fps)
        if video_info.frame_numbers_are_estimated:
            tooltip = (
                "Milliseconds are authoritative. The frame number is estimated "
                "because constant frame rate has not been confirmed."
            )
        else:
            tooltip = "Frame mapping uses measured constant-frame-rate metadata."
        self._time_label.setText(
            f"{current_str} / {duration_str} (Frame {frame_idx})"
        )
        self._time_label.setToolTip(tooltip)
