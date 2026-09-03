from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit

from phase_annotator.config import load_default_ontology
from phase_annotator.ui.main_window import MainWindow
from phase_annotator.ui.player_widget import VideoPlayerWidget
from phase_annotator.ui.timeline_widget import TimelineWidget
from phase_annotator.ui.segment_list_widget import SegmentListWidget
from phase_annotator.domain.models import AnnotationInterval, AnnotationSession, VideoInfo


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
    assert "Appendectomy Phase Annotation Tool" in window.windowTitle()
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


def test_player_widget_exposes_public_playback_state(qtbot):
    player_widget = VideoPlayerWidget()
    qtbot.addWidget(player_widget)

    assert player_widget.position_ms == 0
    assert player_widget.duration_ms == 0
    assert player_widget.is_playing is False


def test_play_button_reflects_player_state(qtbot):
    window = make_window()
    qtbot.addWidget(window)

    window._on_playback_state_changed(True)
    assert window._btn_play.text() == "Pause"

    window._on_playback_state_changed(False)
    assert window._btn_play.text() == "Play"


def test_load_status_changes_when_duration_becomes_available(qtbot, monkeypatch):
    window = make_window()
    qtbot.addWidget(window)
    monkeypatch.setattr(window._player_widget, "load_video", lambda path: None)

    window._load_video(Path("synthetic_case.mp4"))
    assert window.statusBar().currentMessage() == "Loading: synthetic_case.mp4"
    assert window._btn_play.isEnabled()
    assert window._session.ontology_id == "laparoscopic_appendectomy.default"
    assert window._session.ontology_version == "1.0"

    window._on_duration_changed(10_000)
    assert window.statusBar().currentMessage() == "Loaded: synthetic_case.mp4"


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
    monkeypatch.setattr(
        VideoPlayerWidget,
        "position_ms",
        property(lambda self: 4_000),
    )

    window.record_phase_transition(phase_id=1)

    assert window._session.intervals == [
        AnnotationInterval(0, 10_000, 1),
    ]
    assert window._timeline_widget._intervals == window._session.intervals
    assert window._segment_list_widget._intervals == window._session.intervals
    assert window._segment_list_widget._list_widget.count() == 1


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
