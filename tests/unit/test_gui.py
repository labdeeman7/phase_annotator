from pathlib import Path

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit

from phase_annotator.config import load_default_ontology
from phase_annotator.ui.main_window import MainWindow
from phase_annotator.ui.player_widget import VideoPlayerWidget
from phase_annotator.ui.timeline_widget import TimelineWidget
from phase_annotator.ui.segment_list_widget import SegmentListWidget
from phase_annotator.ui.segment_note_dialog import SegmentNoteDialog
from phase_annotator.domain.models import AnnotationInterval, AnnotationSession, VideoInfo
from phase_annotator.domain.validation import validate_contiguous_coverage
from phase_annotator.media import MediaMetadata
from phase_annotator.storage import JsonSessionRepository


def make_window() -> MainWindow:
    return MainWindow(ontology=load_default_ontology())


def show_window(qtbot, window: MainWindow) -> None:
    window.show()
    qtbot.waitExposed(window)
    window.activateWindow()
    qtbot.wait(10)


def test_main_window_instantiation(qtbot):
    window = make_window()
    qtbot.addWidget(window)
    assert "Phase Annotator" in window.windowTitle()
    assert window._btn_play.text() == "Play"
    assert not window._btn_play.isEnabled()
    assert window._timeline_widget._ontology is window._ontology
    assert window._segment_list_widget._ontology is window._ontology
    assert [
        button.text() for button in window._phase_palette.phase_buttons
    ] == [
        "1  Identification of the appendix",
        "2  Dissection of adhesions of the appendix (optional)",
        "3  Coagulation/release of mesoappendix",
        "4  Ligation of the base of the appendix",
        "5  Resection/cutting of the appendix",
        "6  Retrieval of the appendix specimen",
        "U  Undefined",
    ]
    assert not window._phase_palette.is_annotation_enabled
    assert not hasattr(window, "_segment_inspector")
    assert not window._btn_undo.isEnabled()
    assert not window._btn_redo.isEnabled()


def test_player_widget_exposes_public_playback_state(qtbot):
    player_widget = VideoPlayerWidget()
    qtbot.addWidget(player_widget)

    assert player_widget.position_ms == 0
    assert player_widget.duration_ms == 0
    assert player_widget.is_playing is False


def test_player_widget_translates_qt_format_error(qtbot):
    player_widget = VideoPlayerWidget()
    qtbot.addWidget(player_widget)
    messages = []
    player_widget.media_error.connect(messages.append)

    player_widget._forward_media_error(
        QMediaPlayer.Error.FormatError, "Backend rejected stream"
    )

    assert messages == [
        "The video format is invalid or its codec is unsupported. "
        "Backend rejected stream"
    ]


def test_play_button_reflects_player_state(qtbot):
    window = make_window()
    qtbot.addWidget(window)

    window._on_playback_state_changed(True)
    assert window._btn_play.text() == "Pause"

    window._on_playback_state_changed(False)
    assert window._btn_play.text() == "Play"


def test_load_status_changes_when_duration_becomes_available(
    qtbot, monkeypatch, tmp_path
):
    window = make_window()
    qtbot.addWidget(window)
    monkeypatch.setattr(window._player_widget, "load_video", lambda path: None)
    video_path = tmp_path / "synthetic_case.mp4"
    video_path.write_bytes(b"synthetic")

    window._load_video(video_path)
    assert window.statusBar().currentMessage() == "Loading: synthetic_case.mp4"
    assert window._btn_play.isEnabled()
    assert window._session.ontology_id == "laparoscopic_appendectomy.default"
    assert window._session.ontology_version == "1.0"
    assert window._session.video_info.source_path == str(
        video_path.resolve()
    )
    assert window._session.video_info.fps_source == "assumed"
    assert window._session.video_info.frame_rate_mode == "unknown"
    assert window._session.video_info.frame_numbers_are_estimated

    window._on_duration_changed(10_000)
    assert window.statusBar().currentMessage() == "Loaded: synthetic_case.mp4"

    sidecar = tmp_path / "synthetic_case.mp4.phase-annotations.json"
    saved = JsonSessionRepository().load(sidecar)
    assert saved.video_info.duration_ms == 10_000
    assert saved.intervals == [AnnotationInterval(0, 10_000, 1)]


def test_annotation_mutation_and_undo_are_immediately_persisted(
    qtbot, monkeypatch, tmp_path
):
    window = make_window()
    qtbot.addWidget(window)
    monkeypatch.setattr(window._player_widget, "load_video", lambda path: None)
    monkeypatch.setattr(
        VideoPlayerWidget, "position_ms", property(lambda self: 4_000)
    )
    video_path = tmp_path / "case.mp4"
    video_path.write_bytes(b"synthetic")
    sidecar = tmp_path / "case.mp4.phase-annotations.json"

    window._load_video(video_path)
    window._on_duration_changed(10_000)
    window.record_phase_transition(2)

    assert [item.phase_id for item in JsonSessionRepository().load(sidecar).intervals] == [
        1,
        2,
    ]
    window._undo_annotation()
    assert JsonSessionRepository().load(sidecar).intervals == [
        AnnotationInterval(0, 10_000, 1)
    ]


def test_existing_matching_sidecar_is_loaded_automatically(
    qtbot, monkeypatch, tmp_path
):
    monkeypatch.setattr(
        VideoPlayerWidget, "position_ms", property(lambda self: 6_000)
    )
    video_path = tmp_path / "case.mp4"
    video_path.write_bytes(b"synthetic")

    first = make_window()
    qtbot.addWidget(first)
    monkeypatch.setattr(first._player_widget, "load_video", lambda path: None)
    first._load_video(video_path)
    first._on_duration_changed(10_000)
    first._session.intervals = [
        AnnotationInterval(0, 3_000, 1),
        AnnotationInterval(3_000, 10_000, 2),
    ]
    first._session.resume_position_ms = 6_000
    first._persist_session()

    second = make_window()
    qtbot.addWidget(second)
    monkeypatch.setattr(second._player_widget, "load_video", lambda path: None)
    second._load_video(video_path)

    assert second._loaded_existing_session
    assert second._session.intervals == first._session.intervals
    assert second._session.resume_position_ms == 6_000


def test_late_qt_metadata_updates_only_the_current_video(
    qtbot, monkeypatch, tmp_path
):
    window = make_window()
    qtbot.addWidget(window)
    monkeypatch.setattr(window._player_widget, "load_video", lambda path: None)
    video_path = tmp_path / "synthetic_case.mp4"
    video_path.write_bytes(b"synthetic")
    window._load_video(video_path)

    window._on_media_metadata_available(
        MediaMetadata(
            source_path=str(video_path.resolve()),
            file_size_bytes=123,
            file_modified_ns=456,
            duration_ms=10_000,
            width=1920,
            height=1080,
            fps=25.0,
            fps_source="qt",
            frame_rate_mode="unknown",
        )
    )

    video_info = window._session.video_info
    assert video_info.duration_ms == 10_000
    assert (video_info.width, video_info.height) == (1920, 1080)
    assert video_info.fps == 25.0
    assert video_info.fps_source == "qt"
    assert video_info.frame_numbers_are_estimated
    assert window._player_widget.fps == 25.0
    assert "(Frame 0)" in window._time_label.text()
    assert "qt" not in window._time_label.text()
    assert "FPS" not in window._time_label.text()
    assert "Milliseconds are authoritative" in window._time_label.toolTip()
    assert window._btn_step_forward.text() == "+1 Frame"

    window._on_media_metadata_available(
        MediaMetadata(
            source_path=str(Path("different.mp4").resolve()),
            fps=60.0,
            fps_source="qt",
        )
    )
    assert window._session.video_info.fps == 25.0


def test_missing_video_disables_media_and_annotation_controls(
    qtbot, monkeypatch, tmp_path
):
    window = make_window()
    qtbot.addWidget(window)
    load_calls = []
    monkeypatch.setattr(
        window._player_widget, "load_video", lambda path: load_calls.append(path)
    )

    window._load_video(tmp_path / "missing.mp4")

    assert load_calls == []
    assert window._media_load_failed
    assert not window._btn_play.isEnabled()
    assert not window._btn_step_back.isEnabled()
    assert not window._btn_step_forward.isEnabled()
    assert not window._slider.isEnabled()
    assert not window._timeline_widget.isEnabled()
    assert not window._segment_list_widget.isEnabled()
    assert not window._phase_palette.is_annotation_enabled
    assert "Could not load missing.mp4" in window.statusBar().currentMessage()


def test_backend_error_disables_controls_and_preserves_actionable_message(
    qtbot, monkeypatch, tmp_path
):
    window = make_window()
    qtbot.addWidget(window)
    monkeypatch.setattr(window._player_widget, "load_video", lambda path: None)
    monkeypatch.setattr(window._player_widget, "pause", lambda: None)
    video_path = tmp_path / "invalid.mp4"
    video_path.write_bytes(b"invalid")
    window._load_video(video_path)

    window._on_media_error(
        "The video format is invalid or its codec is unsupported."
    )

    assert window._media_load_failed
    assert not window._btn_play.isEnabled()
    assert not window._phase_palette.is_annotation_enabled
    assert "codec is unsupported" in window.statusBar().currentMessage()


def test_timeline_widget_position(qtbot):
    timeline = TimelineWidget(ontology=load_default_ontology())
    qtbot.addWidget(timeline)
    timeline.set_duration(10000)
    timeline.set_position(5000)
    assert timeline._current_position_ms == 5000


def test_segment_list_widget_population(qtbot):
    segment_list = SegmentListWidget(ontology=load_default_ontology())
    qtbot.addWidget(segment_list)
    intervals = [
        AnnotationInterval(start_ms=0, end_ms=5000, phase_id=1, notes="Incision"),
        AnnotationInterval(start_ms=5000, end_ms=12000, phase_id=2, notes="Dissection")
    ]
    segment_list.set_intervals(intervals)
    assert segment_list._list_widget.count() == 2

    requests = []
    segment_list.segment_selection_requested.connect(
        lambda index, seek_ms: requests.append((index, seek_ms))
    )
    segment_list._list_widget.itemClicked.emit(segment_list._list_widget.item(1))

    assert requests == [(1, 5_000)]


def test_segment_cards_keep_timing_summary_compact(qtbot):
    segment_list = SegmentListWidget(ontology=load_default_ontology())
    qtbot.addWidget(segment_list)
    segment_list.set_fps(25.0)
    segment_list.set_intervals([AnnotationInterval(0, 1_000, 1)])

    labels = segment_list._cards[0].findChildren(QLabel)
    frame_label = next(label for label in labels if "frames" in label.text())

    assert frame_label.text() == "Duration: 1.000s  |  25 frames"
    assert "ms" not in frame_label.text()
    assert "FPS" not in frame_label.text()


def test_timeline_click_selects_interval_and_requests_seek(qtbot):
    timeline = TimelineWidget(ontology=load_default_ontology())
    qtbot.addWidget(timeline)
    timeline.resize(1_000, 48)
    timeline.set_duration(10_000)
    timeline.set_intervals(
        [
            AnnotationInterval(0, 4_000, 1),
            AnnotationInterval(4_000, 10_000, 2),
        ]
    )
    requests = []
    timeline.segment_selection_requested.connect(
        lambda index, seek_ms: requests.append((index, seek_ms))
    )
    timeline.show()

    qtbot.mouseClick(timeline, Qt.LeftButton, pos=QPoint(750, 24))

    assert requests == [(1, 7_500)]


def test_timeline_boundary_hit_testing_uses_nearest_internal_boundary(qtbot):
    timeline = TimelineWidget(ontology=load_default_ontology())
    qtbot.addWidget(timeline)
    timeline.resize(1_000, 48)
    timeline.set_duration(10_000)
    timeline.set_intervals(
        [
            AnnotationInterval(0, 4_000, 1),
            AnnotationInterval(4_000, 7_000, 2),
            AnnotationInterval(7_000, 10_000, 3),
        ]
    )

    assert timeline.boundary_index_at_x(400) == 1
    assert timeline.boundary_index_at_x(407) == 1
    assert timeline.boundary_index_at_x(693) == 2
    assert timeline.boundary_index_at_x(500) is None
    assert timeline.boundary_index_at_x(0) is None
    assert timeline.boundary_index_at_x(1_000) is None


def test_timeline_boundary_hover_changes_cursor(qtbot):
    timeline = TimelineWidget(ontology=load_default_ontology())
    qtbot.addWidget(timeline)
    timeline.resize(1_000, 48)
    timeline.set_duration(10_000)
    timeline.set_intervals(
        [
            AnnotationInterval(0, 4_000, 1),
            AnnotationInterval(4_000, 10_000, 2),
        ]
    )
    timeline.show()

    qtbot.mouseMove(timeline, QPoint(400, 24))
    assert timeline.hovered_boundary_index == 1
    assert timeline.cursor().shape() == Qt.CursorShape.SplitHCursor

    qtbot.mouseMove(timeline, QPoint(600, 24))
    assert timeline.hovered_boundary_index is None
    assert timeline.cursor().shape() == Qt.CursorShape.PointingHandCursor


def test_timeline_handle_click_is_reserved_without_selecting_or_seeking(qtbot):
    timeline = TimelineWidget(ontology=load_default_ontology())
    qtbot.addWidget(timeline)
    timeline.resize(1_000, 48)
    timeline.set_duration(10_000)
    timeline.set_intervals(
        [
            AnnotationInterval(0, 4_000, 1),
            AnnotationInterval(4_000, 10_000, 2),
        ]
    )
    requests = []
    timeline.segment_selection_requested.connect(
        lambda index, seek_ms: requests.append((index, seek_ms))
    )
    timeline.show()

    qtbot.mouseClick(timeline, Qt.LeftButton, pos=QPoint(400, 24))

    assert requests == []
    assert timeline.drag_boundary_index is None


def test_timeline_valid_drag_previews_then_requests_one_boundary_move(qtbot):
    timeline = TimelineWidget(ontology=load_default_ontology())
    qtbot.addWidget(timeline)
    timeline.resize(1_000, 48)
    timeline.set_duration(10_000)
    intervals = [
        AnnotationInterval(0, 4_000, 1),
        AnnotationInterval(4_000, 7_000, 2),
        AnnotationInterval(7_000, 10_000, 3),
    ]
    timeline.set_intervals(intervals)
    previews = []
    moves = []
    timeline.boundary_preview_requested.connect(previews.append)
    timeline.boundary_move_requested.connect(
        lambda index, position: moves.append((index, position))
    )
    timeline.show()

    qtbot.mousePress(timeline, Qt.LeftButton, pos=QPoint(400, 24))
    qtbot.mouseMove(timeline, QPoint(500, 24))
    assert timeline.drag_boundary_index == 1
    assert timeline.drag_preview_ms == 5_000
    assert timeline.is_drag_preview_valid
    assert intervals[0].end_ms == 4_000
    assert intervals[1].start_ms == 4_000

    qtbot.mouseRelease(timeline, Qt.LeftButton, pos=QPoint(500, 24))

    assert previews
    assert moves == [(1, 5_000)]
    assert timeline.drag_boundary_index is None


def test_timeline_invalid_drag_cancels_without_move_request(qtbot):
    timeline = TimelineWidget(ontology=load_default_ontology())
    qtbot.addWidget(timeline)
    timeline.resize(1_000, 48)
    timeline.set_duration(10_000)
    timeline.set_intervals(
        [
            AnnotationInterval(0, 4_000, 1),
            AnnotationInterval(4_000, 7_000, 2),
            AnnotationInterval(7_000, 10_000, 3),
        ]
    )
    moves = []
    cancellations = []
    timeline.boundary_move_requested.connect(
        lambda index, position: moves.append((index, position))
    )
    timeline.boundary_drag_cancelled.connect(
        lambda reason, original: cancellations.append((reason, original))
    )
    timeline.show()

    qtbot.mousePress(timeline, Qt.LeftButton, pos=QPoint(400, 24))
    qtbot.mouseMove(timeline, QPoint(800, 24))
    assert not timeline.is_drag_preview_valid
    qtbot.mouseRelease(timeline, Qt.LeftButton, pos=QPoint(800, 24))

    assert moves == []
    assert cancellations == [("invalid", 4_000)]


def test_timeline_escape_cancels_active_drag(qtbot):
    timeline = TimelineWidget(ontology=load_default_ontology())
    qtbot.addWidget(timeline)
    timeline.resize(1_000, 48)
    timeline.set_duration(10_000)
    timeline.set_intervals(
        [
            AnnotationInterval(0, 4_000, 1),
            AnnotationInterval(4_000, 10_000, 2),
        ]
    )
    cancellations = []
    timeline.boundary_drag_cancelled.connect(
        lambda reason, original: cancellations.append((reason, original))
    )
    timeline.show()

    qtbot.mousePress(timeline, Qt.LeftButton, pos=QPoint(400, 24))
    qtbot.mouseMove(timeline, QPoint(500, 24))
    qtbot.keyClick(timeline, Qt.Key_Escape)

    assert timeline.drag_boundary_index is None
    assert cancellations == [("cancelled", 4_000)]


def test_committed_timeline_drag_is_one_undoable_command(qtbot):
    window = make_window()
    qtbot.addWidget(window)
    original = [
        AnnotationInterval(0, 4_000, 1),
        AnnotationInterval(4_000, 10_000, 2),
    ]
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=list(original),
    )
    window._timeline_widget.set_duration(10_000)
    window._refresh_annotation_views()

    window._commit_boundary_drag(1, 5_000)

    assert window._session.intervals == [
        AnnotationInterval(0, 5_000, 1),
        AnnotationInterval(5_000, 10_000, 2),
    ]
    assert window._history.undo_description == "drag timeline boundary"
    assert window._selected_segment_index == 1
    assert window._timeline_widget.selected_index == 1
    assert window._segment_list_widget.selected_index == 1
    window._undo_annotation()
    assert window._session.intervals == original
    assert not window._history.can_undo
    assert window._history.can_redo

    window._redo_annotation()
    assert window._session.intervals == [
        AnnotationInterval(0, 5_000, 1),
        AnnotationInterval(5_000, 10_000, 2),
    ]
    assert window._selected_segment_index == 1


def test_mouse_drag_runs_complete_preview_commit_and_history_flow(
    qtbot, monkeypatch
):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=[
            AnnotationInterval(0, 4_000, 1),
            AnnotationInterval(4_000, 10_000, 2),
        ],
    )
    window._timeline_widget.set_duration(10_000)
    window._refresh_annotation_views()
    seeks = []
    monkeypatch.setattr(window._player_widget, "seek_ms", seeks.append)
    show_window(qtbot, window)
    timeline = window._timeline_widget
    boundary_x = timeline._boundary_x(1)
    target_x = round(0.55 * timeline.width())
    target_ms = round((target_x / timeline.width()) * 10_000)

    qtbot.mousePress(timeline, Qt.LeftButton, pos=QPoint(boundary_x, 24))
    qtbot.mouseMove(timeline, QPoint(target_x, 24))
    assert window._session.intervals[0].end_ms == 4_000
    assert seeks[-1] == target_ms
    qtbot.mouseRelease(timeline, Qt.LeftButton, pos=QPoint(target_x, 24))

    assert window._session.intervals == [
        AnnotationInterval(0, target_ms, 1),
        AnnotationInterval(target_ms, 10_000, 2),
    ]
    assert window._history.undo_description == "drag timeline boundary"
    assert window._selected_segment_index == 1
    assert timeline.selected_index == 1
    assert window._segment_list_widget.selected_index == 1


def test_cancelled_boundary_preview_restores_playhead_without_history(
    qtbot, monkeypatch
):
    window = make_window()
    qtbot.addWidget(window)
    intervals = [
        AnnotationInterval(0, 4_000, 1),
        AnnotationInterval(4_000, 10_000, 2),
    ]
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=list(intervals),
    )
    window._timeline_widget.set_duration(10_000)
    window._refresh_annotation_views()
    seeks = []
    monkeypatch.setattr(window._player_widget, "seek_ms", seeks.append)

    window._preview_boundary_drag(7_000)
    window._cancel_boundary_drag("invalid", 4_000)

    assert seeks == [7_000, 4_000]
    assert window._session.intervals == intervals
    assert not window._history.can_undo
    assert window.statusBar().currentMessage().startswith(
        "Boundary drag cancelled"
    )


def test_repeated_boundary_drags_preserve_coverage_and_undo_individually(qtbot):
    window = make_window()
    qtbot.addWidget(window)
    original = [
        AnnotationInterval(0, 3_000, 1),
        AnnotationInterval(3_000, 7_000, 2),
        AnnotationInterval(7_000, 10_000, 3),
    ]
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=list(original),
    )
    window._timeline_widget.set_duration(10_000)
    window._refresh_annotation_views()

    window._commit_boundary_drag(1, 4_000)
    after_first = list(window._session.intervals)
    window._commit_boundary_drag(2, 8_000)

    assert validate_contiguous_coverage(window._session.intervals, 10_000) == []
    window._undo_annotation()
    assert window._session.intervals == after_first
    window._undo_annotation()
    assert window._session.intervals == original


def test_segment_selection_is_synchronized_across_views(qtbot):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=[
            AnnotationInterval(0, 3_000, 1),
            AnnotationInterval(3_000, 7_000, 2),
            AnnotationInterval(7_000, 10_000, 3),
        ],
    )
    window._timeline_widget.set_duration(10_000)
    window._refresh_annotation_views()

    window._segment_list_widget.segment_selection_requested.emit(1, 3_000)

    assert window._selected_segment_index == 1
    assert window._segment_list_widget.selected_index == 1
    assert window._segment_list_widget._list_widget.currentRow() == 1
    assert window._timeline_widget.selected_index == 1
    assert window._segment_list_widget._cards[1]._is_selected


def test_card_right_click_and_actions_button_request_same_segment(qtbot):
    segment_list = SegmentListWidget(ontology=load_default_ontology())
    qtbot.addWidget(segment_list)
    segment_list.set_intervals([AnnotationInterval(0, 10_000, 1)])
    card = segment_list._cards[0]
    assert card._actions_button.text() == "⋮"
    assert card._actions_button.size().width() == 32
    assert card._actions_button.size().height() == 32
    requests = []
    segment_list.segment_actions_requested.connect(
        lambda index, position: requests.append(index)
    )

    card.customContextMenuRequested.emit(QPoint(5, 5))
    qtbot.mouseClick(card._actions_button, Qt.LeftButton)

    assert requests == [0, 0]


def test_note_dialog_exposes_text_only_after_explicit_acceptance(qtbot):
    dialog = SegmentNoteDialog("original")
    qtbot.addWidget(dialog)
    dialog._notes_edit.setPlainText("edited")

    dialog.reject()

    assert dialog.result() == QDialog.DialogCode.Rejected
    assert dialog.notes == "edited"


def test_save_segment_note_uses_editor_and_preserves_selection(qtbot):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=[
            AnnotationInterval(0, 4_000, 1),
            AnnotationInterval(4_000, 10_000, 2),
        ],
    )
    window._refresh_annotation_views()
    window._select_segment(1)

    changed = window._save_segment_note(1, "Difficult dissection")

    assert changed is True
    assert window._session.intervals[1].notes == "Difficult dissection"
    assert window._selected_segment_index == 1
    note_indicator = window._segment_list_widget._cards[1]._note_indicator
    assert not note_indicator.isHidden()
    assert note_indicator.toolTip() == "Difficult dissection"
    assert window.statusBar().currentMessage() == "Segment note saved"


def test_edit_note_dialog_cancel_does_not_change_session(qtbot, monkeypatch):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=[
            AnnotationInterval(0, 4_000, 1),
            AnnotationInterval(4_000, 10_000, 2),
        ],
    )
    window._refresh_annotation_views()
    window._select_segment(0)

    class CancelledDialog:
        def __init__(self, notes, parent):
            self.notes = "discard me"

        def exec(self):
            return QDialog.DialogCode.Rejected

    monkeypatch.setattr(
        "phase_annotator.ui.main_window.SegmentNoteDialog", CancelledDialog
    )

    window._edit_segment_note(0)

    assert window._session.intervals[0].notes == ""


def test_edit_note_dialog_acceptance_saves_note(qtbot, monkeypatch):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=[AnnotationInterval(0, 10_000, 1)],
    )
    window._refresh_annotation_views()

    class AcceptedDialog:
        def __init__(self, notes, parent):
            assert notes == ""
            self.notes = "Unexpected anatomy"

        def exec(self):
            return QDialog.DialogCode.Accepted

    monkeypatch.setattr(
        "phase_annotator.ui.main_window.SegmentNoteDialog", AcceptedDialog
    )

    window._edit_segment_note(0)

    assert window._session.intervals[0].notes == "Unexpected anatomy"


def test_relabel_segment_coalesces_and_selects_result(qtbot):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=[
            AnnotationInterval(0, 3_000, 1),
            AnnotationInterval(3_000, 7_000, 2, notes="reviewed"),
            AnnotationInterval(7_000, 10_000, 1),
        ],
    )
    window._timeline_widget.set_duration(10_000)
    window._refresh_annotation_views()
    window._select_segment(1)

    changed = window._relabel_segment(1, 1)

    assert changed is True
    assert window._session.intervals == [
        AnnotationInterval(0, 10_000, 1, notes="reviewed")
    ]
    assert window._selected_segment_index == 0
    assert window._timeline_widget.selected_index == 0
    assert window._segment_list_widget.selected_index == 0
    assert window.statusBar().currentMessage().startswith("Segment changed to")


def test_move_selected_segment_start_to_playhead_updates_shared_boundary(
    qtbot, monkeypatch
):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=[
            AnnotationInterval(0, 3_000, 1),
            AnnotationInterval(3_000, 7_000, 2),
            AnnotationInterval(7_000, 10_000, 3),
        ],
    )
    window._timeline_widget.set_duration(10_000)
    window._refresh_annotation_views()
    window._select_segment(1)
    monkeypatch.setattr(
        VideoPlayerWidget, "position_ms", property(lambda self: 4_000)
    )

    changed = window._move_segment_boundary(
        1, boundary_index=1, boundary_name="start"
    )

    assert changed is True
    assert window._session.intervals == [
        AnnotationInterval(0, 4_000, 1),
        AnnotationInterval(4_000, 7_000, 2),
        AnnotationInterval(7_000, 10_000, 3),
    ]
    assert window._selected_segment_index == 1
    assert window._timeline_widget._intervals == window._session.intervals
    assert window._segment_list_widget._intervals == window._session.intervals


def test_invalid_boundary_move_leaves_gui_state_unchanged(qtbot, monkeypatch):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=[
            AnnotationInterval(0, 3_000, 1),
            AnnotationInterval(3_000, 7_000, 2),
            AnnotationInterval(7_000, 10_000, 3),
        ],
    )
    window._refresh_annotation_views()
    window._select_segment(1)
    monkeypatch.setattr(
        VideoPlayerWidget, "position_ms", property(lambda self: 8_000)
    )

    changed = window._move_segment_boundary(
        1, boundary_index=1, boundary_name="start"
    )

    assert changed is False
    assert window._session.intervals == [
        AnnotationInterval(0, 3_000, 1),
        AnnotationInterval(3_000, 7_000, 2),
        AnnotationInterval(7_000, 10_000, 3),
    ]
    assert window.statusBar().currentMessage().startswith("Boundary not changed")


@pytest.mark.parametrize(
    ("resolution", "expected_phase", "expected_status"),
    [
        ("undefined", 0, "converted to Undefined"),
        ("left", 1, "merged left"),
        ("right", 3, "merged right"),
    ],
)
def test_resolve_segment_uses_explicit_no_gap_strategy(
    qtbot, resolution, expected_phase, expected_status
):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=[
            AnnotationInterval(0, 3_000, 1),
            AnnotationInterval(3_000, 7_000, 2, notes="keep"),
            AnnotationInterval(7_000, 10_000, 3),
        ],
    )
    window._timeline_widget.set_duration(10_000)
    window._refresh_annotation_views()
    window._select_segment(1)

    changed = window._resolve_segment(1, resolution=resolution)

    assert changed is True
    resulting = window._session.intervals[window._selected_segment_index]
    assert resulting.phase_id == expected_phase
    assert resulting.notes == "keep"
    assert expected_status in window.statusBar().currentMessage()
    assert window._timeline_widget._intervals == window._session.intervals
    assert window._segment_list_widget._intervals == window._session.intervals


def test_annotation_command_undo_and_redo_restore_exact_state(qtbot, monkeypatch):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=[AnnotationInterval(0, 10_000, 1)],
    )
    window._timeline_widget.set_duration(10_000)
    window._refresh_annotation_views()
    monkeypatch.setattr(
        VideoPlayerWidget, "position_ms", property(lambda self: 4_000)
    )

    window.record_phase_transition(2)
    changed_state = list(window._session.intervals)
    assert window._btn_undo.isEnabled()
    assert not window._btn_redo.isEnabled()

    window._undo_annotation()
    assert window._session.intervals == [AnnotationInterval(0, 10_000, 1)]
    assert not window._btn_undo.isEnabled()
    assert window._btn_redo.isEnabled()
    assert window.statusBar().currentMessage() == "Undid assign phase 2"

    window._redo_annotation()
    assert window._session.intervals == changed_state
    assert window._btn_undo.isEnabled()
    assert not window._btn_redo.isEnabled()
    assert window.statusBar().currentMessage() == "Redid assign phase 2"


def test_note_edit_is_undoable_and_new_edit_after_undo_clears_redo(qtbot):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=[AnnotationInterval(0, 10_000, 1)],
    )
    window._refresh_annotation_views()

    window._save_segment_note(0, "first")
    window._undo_annotation()
    assert window._session.intervals[0].notes == ""
    assert window._history.can_redo

    window._save_segment_note(0, "replacement")
    assert window._session.intervals[0].notes == "replacement"
    assert not window._history.can_redo


def test_loading_video_clears_annotation_history(qtbot, monkeypatch):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("first.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=[AnnotationInterval(0, 10_000, 1)],
    )
    window._save_segment_note(0, "history entry")
    assert window._history.can_undo
    monkeypatch.setattr(window._player_widget, "load_video", lambda path: None)

    window._load_video(Path("second.mp4"))

    assert not window._history.can_undo
    assert not window._history.can_redo
    assert not window._btn_undo.isEnabled()
    assert not window._btn_redo.isEnabled()


def test_text_focus_reserves_undo_shortcut_for_text_widget(qtbot):
    window = make_window()
    line_edit = QLineEdit(window)
    qtbot.addWidget(window)
    show_window(qtbot, window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=[AnnotationInterval(0, 10_000, 1)],
    )
    window._save_segment_note(0, "history entry")
    line_edit.show()
    line_edit.setFocus(Qt.OtherFocusReason)
    qtbot.waitUntil(line_edit.hasFocus)
    window._update_history_controls()

    assert window._history.can_undo
    assert not window._undo_shortcut.isEnabled()
    assert window._btn_undo.isEnabled()


def test_selected_and_playhead_active_segments_are_independent(qtbot):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=10_000),
        annotator_id="annotator_01",
        intervals=[
            AnnotationInterval(0, 3_000, 1),
            AnnotationInterval(3_000, 7_000, 2),
            AnnotationInterval(7_000, 10_000, 3),
        ],
    )
    window._timeline_widget.set_duration(10_000)
    window._refresh_annotation_views()
    window._select_segment(0)

    window._on_slider_moved(8_000)

    assert window._selected_segment_index == 0
    assert window._timeline_widget.selected_index == 0
    assert window._timeline_widget.active_index == 2
    assert window._segment_list_widget.selected_index == 0
    assert window._segment_list_widget.active_index == 2
    assert window._segment_list_widget._cards[0]._is_selected
    assert window._segment_list_widget._cards[2]._is_active


def test_duration_initializes_full_configured_phase_coverage(qtbot):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=0),
        annotator_id="annotator_01",
    )

    window._on_duration_changed(10_000)

    assert window._session.intervals == [AnnotationInterval(0, 10_000, 1)]
    assert window._timeline_widget._intervals == window._session.intervals
    assert window._segment_list_widget._intervals == window._session.intervals
    assert window._segment_list_widget._list_widget.count() == 1
    assert window._phase_palette.active_phase_id == 1
    assert window._phase_palette.is_annotation_enabled


def test_mouse_and_hotkey_phase_selection_use_same_command(qtbot, monkeypatch):
    mouse_window = make_window()
    keyboard_window = make_window()
    qtbot.addWidget(mouse_window)
    qtbot.addWidget(keyboard_window)

    for window in (mouse_window, keyboard_window):
        window._session = AnnotationSession(
            video_info=VideoInfo("synthetic_case.mp4", duration_ms=0),
            annotator_id="annotator_01",
        )
        window._on_duration_changed(10_000)

    monkeypatch.setattr(
        VideoPlayerWidget,
        "position_ms",
        property(lambda self: 4_000),
    )

    qtbot.mouseClick(mouse_window._phase_palette.button_for_phase(3), Qt.LeftButton)
    show_window(qtbot, keyboard_window)
    qtbot.mouseClick(keyboard_window._timeline_widget, Qt.LeftButton)
    qtbot.keyClick(keyboard_window._timeline_widget, Qt.Key_3)

    assert mouse_window._session.intervals == keyboard_window._session.intervals
    assert mouse_window._session.intervals == [
        AnnotationInterval(0, 4_000, 1),
        AnnotationInterval(4_000, 10_000, 3),
    ]
    assert mouse_window._phase_palette.active_phase_id == 3
    assert keyboard_window._phase_palette.active_phase_id == 3


def test_undefined_hotkey_uses_configured_mapping(qtbot, monkeypatch):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=0),
        annotator_id="annotator_01",
    )
    window._on_duration_changed(10_000)
    monkeypatch.setattr(
        VideoPlayerWidget,
        "position_ms",
        property(lambda self: 2_500),
    )
    show_window(qtbot, window)
    qtbot.mouseClick(window._timeline_widget, Qt.LeftButton)

    qtbot.keyClick(window._timeline_widget, Qt.Key_U)

    assert window._session.intervals == [
        AnnotationInterval(0, 2_500, 1),
        AnnotationInterval(2_500, 10_000, 0),
    ]
    assert window._phase_palette.active_phase_id == 0

    window._on_slider_moved(1_000)
    assert window._phase_palette.active_phase_id == 1

    window._on_slider_moved(5_000)
    assert window._phase_palette.active_phase_id == 0


def test_phase_hotkey_is_ignored_while_typing(qtbot, monkeypatch):
    window = make_window()
    qtbot.addWidget(window)
    show_window(qtbot, window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=0),
        annotator_id="annotator_01",
    )
    window._on_duration_changed(10_000)
    monkeypatch.setattr(
        VideoPlayerWidget,
        "position_ms",
        property(lambda self: 2_500),
    )
    text_entry = QLineEdit(window)
    text_entry.show()
    text_entry.setFocus(Qt.OtherFocusReason)
    qtbot.waitUntil(text_entry.hasFocus)

    qtbot.keyClick(text_entry, Qt.Key_U)

    assert text_entry.text() == "u"
    assert window._session.intervals == [AnnotationInterval(0, 10_000, 1)]


def test_phase_hotkey_is_reserved_while_segment_list_has_focus(qtbot, monkeypatch):
    window = make_window()
    qtbot.addWidget(window)
    show_window(qtbot, window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=0),
        annotator_id="annotator_01",
    )
    window._on_duration_changed(10_000)
    monkeypatch.setattr(
        VideoPlayerWidget,
        "position_ms",
        property(lambda self: 4_000),
    )
    window.activateWindow()
    window._segment_list_widget._list_widget.setCurrentRow(0)
    window._segment_list_widget._list_widget.setFocus(Qt.OtherFocusReason)
    qtbot.waitUntil(
        lambda: window._segment_list_widget._list_widget.hasFocus()
    )

    qtbot.keyClick(window._segment_list_widget._list_widget, Qt.Key_3)

    assert window._session.intervals == [AnnotationInterval(0, 10_000, 1)]


def test_clicking_timeline_restores_annotation_hotkeys(qtbot, monkeypatch):
    window = make_window()
    qtbot.addWidget(window)
    show_window(qtbot, window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=0),
        annotator_id="annotator_01",
    )
    window._on_duration_changed(10_000)
    monkeypatch.setattr(
        VideoPlayerWidget,
        "position_ms",
        property(lambda self: 4_000),
    )
    window.activateWindow()
    window._segment_list_widget._list_widget.setCurrentRow(0)
    window._segment_list_widget._list_widget.setFocus(Qt.OtherFocusReason)
    qtbot.waitUntil(
        lambda: window._segment_list_widget._list_widget.hasFocus()
    )

    qtbot.mouseClick(window._timeline_widget, Qt.LeftButton)
    assert window._timeline_widget.hasFocus()
    qtbot.keyClick(window._timeline_widget, Qt.Key_3)

    assert window._session.intervals == [
        AnnotationInterval(0, 4_000, 1),
        AnnotationInterval(4_000, 10_000, 3),
    ]


def test_gui_transition_uses_editor_and_refreshes_both_views(qtbot, monkeypatch):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=0),
        annotator_id="annotator_01",
    )
    window._on_duration_changed(10_000)
    window._select_segment(0)
    monkeypatch.setattr(
        VideoPlayerWidget,
        "position_ms",
        property(lambda self: 4_000),
    )

    window.record_phase_transition(phase_id=2)

    assert window._session.intervals == [
        AnnotationInterval(0, 4_000, 1),
        AnnotationInterval(4_000, 10_000, 2),
    ]
    assert window._selected_segment_index is None
    assert window._timeline_widget.selected_index is None
    assert window._segment_list_widget.selected_index is None
    assert window._timeline_widget._intervals == window._session.intervals
    assert window._segment_list_widget._intervals == window._session.intervals
    assert window._segment_list_widget._list_widget.count() == 2


def test_backward_gui_transition_replaces_stale_segment_cards(qtbot, monkeypatch):
    window = make_window()
    qtbot.addWidget(window)
    window._session = AnnotationSession(
        video_info=VideoInfo("synthetic_case.mp4", duration_ms=0),
        annotator_id="annotator_01",
    )
    window._on_duration_changed(10_000)
    playhead = {"position_ms": 0}
    monkeypatch.setattr(
        VideoPlayerWidget,
        "position_ms",
        property(lambda self: playhead["position_ms"]),
    )

    window.record_phase_transition(phase_id=1)
    playhead["position_ms"] = 3_000
    window.record_phase_transition(phase_id=2)
    playhead["position_ms"] = 7_000
    window.record_phase_transition(phase_id=3)
    playhead["position_ms"] = 4_000
    window.record_phase_transition(phase_id=3)

    assert window._session.intervals == [
        AnnotationInterval(0, 3_000, 1),
        AnnotationInterval(3_000, 4_000, 2),
        AnnotationInterval(4_000, 10_000, 3),
    ]
    assert window._timeline_widget._intervals == window._session.intervals
    assert window._segment_list_widget._intervals == window._session.intervals
    assert window._segment_list_widget._list_widget.count() == 3
