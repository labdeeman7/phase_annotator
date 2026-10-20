"""Round-two cholecystectomy flows: Other picker, Delete, privacy sign-off, old files."""

import json

from phase_annotator.config import load_procedure_ontology
from phase_annotator.domain.completion import summarize_completion
from phase_annotator.domain.models import AnnotationInterval
from phase_annotator.storage import JsonSessionRepository
from phase_annotator.ui.completion_dialog import CompletionDialog
from phase_annotator.ui.main_window import MainWindow
from phase_annotator.ui.other_details_dialog import OtherDetailsDialog
from phase_annotator.ui.player_widget import VideoPlayerWidget


def cholecystectomy_window(qtbot, monkeypatch, tmp_path, annotator="doctor_A"):
    window = MainWindow(
        load_procedure_ontology("cholecystectomy"), annotator_id=annotator
    )
    qtbot.addWidget(window)
    monkeypatch.setattr(window._player_widget, "load_video", lambda path: None)
    video_path = tmp_path / "case.mp4"
    if not video_path.exists():
        video_path.write_bytes(b"synthetic")
    window._load_video(video_path)
    return window, video_path


def test_assigning_other_asks_for_its_type(qtbot, monkeypatch, tmp_path):
    monkeypatch.setattr(VideoPlayerWidget, "position_ms", property(lambda self: 4_000))
    window, _ = cholecystectomy_window(qtbot, monkeypatch, tmp_path)
    window._on_duration_changed(60_000)
    asked = []
    monkeypatch.setattr(
        window,
        "_ask_other_notes",
        lambda notes: asked.append(notes) or "[DEIDENTIFY] face on screen",
    )

    window.record_phase_transition(0)

    assert asked == [""]
    other = window._session.intervals[1]
    assert (other.start_ms, other.phase_id, other.notes) == (
        4_000,
        0,
        "[DEIDENTIFY] face on screen",
    )


def test_cancelled_picker_undoes_the_press_and_delete_never_asks(
    qtbot, monkeypatch, tmp_path
):
    monkeypatch.setattr(VideoPlayerWidget, "position_ms", property(lambda self: 4_000))
    window, _ = cholecystectomy_window(qtbot, monkeypatch, tmp_path)
    window._on_duration_changed(60_000)
    asked = []
    monkeypatch.setattr(
        window, "_ask_other_notes", lambda notes: asked.append(notes) or None
    )

    window.record_phase_transition(0)
    assert [(i.start_ms, i.end_ms, i.phase_id) for i in window._session.intervals] == [
        (0, 60_000, 1)
    ]

    window.record_phase_transition(2)  # a phase, then clear it with Delete
    window._select_segment(1)
    window._convert_selected_segment_to_undefined()
    assert window._session.intervals[1].phase_id == 0
    assert len(asked) == 1


def test_same_type_merges_and_cancelled_split_changes_nothing(
    qtbot, monkeypatch, tmp_path
):
    window, _ = cholecystectomy_window(qtbot, monkeypatch, tmp_path)
    window._on_duration_changed(120_000)
    window._session.intervals = [
        AnnotationInterval(0, 30_000, 1),
        AnnotationInterval(30_000, 120_000, 0, notes="[DRAIN_INSERTION] drain"),
    ]
    before = list(window._session.intervals)
    monkeypatch.setattr(VideoPlayerWidget, "position_ms", property(lambda self: 70_000))

    monkeypatch.setattr(window, "_ask_other_notes", lambda notes: None)
    window.record_phase_transition(0)
    assert window._session.intervals == before

    monkeypatch.setattr(
        window, "_ask_other_notes", lambda notes: "[DRAIN_INSERTION] second look"
    )
    window.record_phase_transition(0)
    assert [(i.start_ms, i.end_ms, i.notes) for i in window._session.intervals] == [
        (0, 30_000, ""),
        (30_000, 120_000, "[DRAIN_INSERTION] drain\nsecond look"),
    ]


def test_editing_an_other_note_uses_the_picker(qtbot, monkeypatch, tmp_path):
    window, _ = cholecystectomy_window(qtbot, monkeypatch, tmp_path)
    window._on_duration_changed(60_000)
    window._session.intervals = [
        AnnotationInterval(0, 30_000, 1),
        AnnotationInterval(30_000, 60_000, 0, notes="[LIVER_BIOPSY] edge of liver"),
    ]
    monkeypatch.setattr(window, "_ask_other_notes", lambda notes: f"{notes}, segment 5")

    window._edit_segment_note(1)

    assert (
        window._session.intervals[1].notes == "[LIVER_BIOPSY] edge of liver, segment 5"
    )


def test_completion_requires_privacy_and_records_it(qtbot, monkeypatch, tmp_path):
    window, video_path = cholecystectomy_window(qtbot, monkeypatch, tmp_path)
    window._on_duration_changed(60_000)
    monkeypatch.setattr(window, "_confirm_completion_with_privacy", lambda s: False)
    assert not window._mark_complete()
    assert window._session.status == "draft"

    monkeypatch.setattr(window, "_confirm_completion_with_privacy", lambda s: True)
    assert window._mark_complete()

    saved = JsonSessionRepository().load(tmp_path / "case.mp4.phase-annotations.json")
    assert saved.status == "completed" and saved.completed_by == "doctor_A"
    assert saved.session_notes == "Privacy checked"


def test_round_one_file_opens_and_is_restamped(qtbot, monkeypatch, tmp_path):
    first, video_path = cholecystectomy_window(qtbot, monkeypatch, tmp_path)
    first._on_duration_changed(60_000)
    first._session.intervals = [
        AnnotationInterval(0, 20_000, 1),
        AnnotationInterval(20_000, 60_000, 0, notes="drainage of the gallbladder"),
    ]
    first._persist_session()
    first._persistence.reset_annotation_changed()
    sidecar = tmp_path / "case.mp4.phase-annotations.json"
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    data["ontology_version"] = "1.0"
    sidecar.write_text(json.dumps(data), encoding="utf-8")

    second, _ = cholecystectomy_window(qtbot, monkeypatch, tmp_path)

    assert second._loaded_existing_session
    assert second._session.ontology_version == "1.1"
    assert second._session.intervals[1].notes == "drainage of the gallbladder"
    second._persistence.reset_annotation_changed()


def test_other_dialog_round_trips_tags_and_keeps_unknown_text(qtbot):
    subtypes = load_procedure_ontology("cholecystectomy").other_subtypes
    dialog = OtherDetailsDialog("[DRAIN_INSERTION] under liver", subtypes)
    qtbot.addWidget(dialog)
    assert dialog.tag == "DRAIN_INSERTION"
    assert dialog.notes == "[DRAIN_INSERTION] under liver"

    unknown = OtherDetailsDialog("[SOMETHING_OLD] keep me", subtypes)
    qtbot.addWidget(unknown)
    assert unknown.tag is None
    assert unknown.notes == "[SOMETHING_OLD] keep me"


def test_completion_dialog_needs_the_tick(qtbot, monkeypatch, tmp_path):
    window, _ = cholecystectomy_window(qtbot, monkeypatch, tmp_path)
    window._on_duration_changed(60_000)
    summary = summarize_completion(window._session, undefined_phase_id=0)
    dialog = CompletionDialog(summary, "Other")
    qtbot.addWidget(dialog)
    assert not dialog._yes_button.isEnabled()
    dialog._privacy_checkbox.setChecked(True)
    assert dialog._yes_button.isEnabled() and dialog.privacy_checked


def test_back_to_back_other_activities(qtbot, monkeypatch, tmp_path):
    """Gallbladder drainage straight into drain insertion: press 0 again inside it."""
    window, _ = cholecystectomy_window(qtbot, monkeypatch, tmp_path)
    window._on_duration_changed(120_000)
    answers = iter(["[GALLBLADDER_DRAINAGE] aspiration", "[DRAIN_INSERTION] drain"])
    monkeypatch.setattr(window, "_ask_other_notes", lambda notes: next(answers))

    monkeypatch.setattr(VideoPlayerWidget, "position_ms", property(lambda self: 30_000))
    window.record_phase_transition(0)
    monkeypatch.setattr(VideoPlayerWidget, "position_ms", property(lambda self: 70_000))
    window.record_phase_transition(0)

    assert [
        (i.start_ms, i.end_ms, i.phase_id, i.notes) for i in window._session.intervals
    ] == [
        (0, 30_000, 1, ""),
        (30_000, 70_000, 0, "[GALLBLADDER_DRAINAGE] aspiration"),
        (70_000, 120_000, 0, "[DRAIN_INSERTION] drain"),
    ]
