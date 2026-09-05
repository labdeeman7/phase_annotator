import copy

import pytest

from phase_annotator.domain.annotation_editor import AnnotationEditor
from phase_annotator.domain.models import AnnotationInterval, AnnotationSession, VideoInfo


@pytest.fixture
def editor() -> AnnotationEditor:
    return AnnotationEditor(
        valid_phase_ids={0, 1, 2, 3},
        undefined_phase_id=0,
        initial_phase_id=1,
    )


def make_session(duration_ms: int = 10_000) -> AnnotationSession:
    return AnnotationSession(
        video_info=VideoInfo(video_id="synthetic_case.mp4", duration_ms=duration_ms),
        annotator_id="annotator_01",
    )


def test_initialize_coverage_uses_configured_initial_phase(editor: AnnotationEditor):
    session = make_session()

    changed = editor.initialize_coverage(session)

    assert changed is True
    assert session.intervals == [
        AnnotationInterval(start_ms=0, end_ms=10_000, phase_id=1)
    ]


def test_initialize_coverage_rejects_unknown_duration_without_mutation(
    editor: AnnotationEditor,
):
    session = make_session(duration_ms=0)
    original = copy.deepcopy(session)

    with pytest.raises(ValueError, match="duration"):
        editor.initialize_coverage(session)

    assert session == original


def test_transition_splits_the_segment_at_the_playhead(editor: AnnotationEditor):
    session = make_session()
    editor.initialize_coverage(session)

    changed = editor.apply_transition(session, phase_id=2, position_ms=2_000)

    assert changed is True
    assert session.intervals == [
        AnnotationInterval(start_ms=0, end_ms=2_000, phase_id=1),
        AnnotationInterval(start_ms=2_000, end_ms=10_000, phase_id=2),
    ]


def test_selecting_the_current_phase_is_a_no_op(editor: AnnotationEditor):
    session = make_session()
    editor.initialize_coverage(session)
    editor.apply_transition(session, phase_id=1, position_ms=2_000)
    original = copy.deepcopy(session)

    changed = editor.apply_transition(session, phase_id=1, position_ms=5_000)

    assert changed is False
    assert session == original


def test_transition_at_existing_boundary_relabels_the_segment_starting_there(
    editor: AnnotationEditor,
):
    session = make_session()
    session.intervals = [
        AnnotationInterval(0, 2_000, 1),
        AnnotationInterval(2_000, 6_000, 2),
        AnnotationInterval(6_000, 10_000, 3),
    ]

    editor.apply_transition(session, phase_id=1, position_ms=2_000)

    assert session.intervals == [
        AnnotationInterval(0, 6_000, 1),
        AnnotationInterval(6_000, 10_000, 3),
    ]


def test_backward_transition_preserves_later_established_segments(
    editor: AnnotationEditor,
):
    session = make_session()
    session.intervals = [
        AnnotationInterval(0, 3_000, 1),
        AnnotationInterval(3_000, 7_000, 2),
        AnnotationInterval(7_000, 10_000, 3),
    ]

    editor.apply_transition(session, phase_id=3, position_ms=5_000)

    assert session.intervals == [
        AnnotationInterval(0, 3_000, 1),
        AnnotationInterval(3_000, 5_000, 2),
        AnnotationInterval(5_000, 10_000, 3),
    ]


@pytest.mark.parametrize(
    ("phase_id", "position_ms", "message"),
    [
        (99, 5_000, "Phase ID"),
        (1, -1, "position"),
        (1, 10_000, "position"),
    ],
)
def test_invalid_transition_leaves_session_unchanged(
    editor: AnnotationEditor,
    phase_id: int,
    position_ms: int,
    message: str,
):
    session = make_session()
    editor.initialize_coverage(session)
    original = copy.deepcopy(session)

    with pytest.raises(ValueError, match=message):
        editor.apply_transition(session, phase_id=phase_id, position_ms=position_ms)

    assert session == original


def test_transition_rejects_non_contiguous_input_without_mutation(
    editor: AnnotationEditor,
):
    session = make_session()
    session.intervals = [
        AnnotationInterval(0, 4_000, 1),
        AnnotationInterval(5_000, 10_000, 2),
    ]
    original = copy.deepcopy(session)

    with pytest.raises(ValueError, match="coverage"):
        editor.apply_transition(session, phase_id=3, position_ms=2_000)

    assert session == original


def test_transition_rejects_existing_unknown_phase_without_mutation(
    editor: AnnotationEditor,
):
    session = make_session()
    session.intervals = [AnnotationInterval(0, 10_000, 99)]
    original = copy.deepcopy(session)

    with pytest.raises(ValueError, match="Phase ID 99"):
        editor.apply_transition(session, phase_id=1, position_ms=2_000)

    assert session == original


def test_update_notes_changes_only_selected_interval(editor: AnnotationEditor):
    session = make_session()
    session.intervals = [
        AnnotationInterval(0, 4_000, 1, notes="first"),
        AnnotationInterval(4_000, 10_000, 2),
    ]

    changed = editor.update_notes(session, interval_index=1, notes="reviewed")

    assert changed is True
    assert session.intervals == [
        AnnotationInterval(0, 4_000, 1, notes="first"),
        AnnotationInterval(4_000, 10_000, 2, notes="reviewed"),
    ]


def test_update_notes_with_same_text_is_no_op(editor: AnnotationEditor):
    session = make_session()
    session.intervals = [AnnotationInterval(0, 10_000, 1, notes="unchanged")]
    original = copy.deepcopy(session)

    changed = editor.update_notes(session, interval_index=0, notes="unchanged")

    assert changed is False
    assert session == original


@pytest.mark.parametrize("interval_index", [-1, 1])
def test_update_notes_rejects_invalid_index_without_mutation(
    editor: AnnotationEditor, interval_index: int
):
    session = make_session()
    editor.initialize_coverage(session)
    original = copy.deepcopy(session)

    with pytest.raises(ValueError, match="index"):
        editor.update_notes(session, interval_index=interval_index, notes="note")

    assert session == original


def test_update_notes_validates_existing_coverage_before_mutation(
    editor: AnnotationEditor,
):
    session = make_session()
    session.intervals = [
        AnnotationInterval(0, 4_000, 1),
        AnnotationInterval(5_000, 10_000, 2),
    ]
    original = copy.deepcopy(session)

    with pytest.raises(ValueError, match="coverage"):
        editor.update_notes(session, interval_index=0, notes="note")

    assert session == original


def test_relabel_interval_changes_complete_segment_and_preserves_note(
    editor: AnnotationEditor,
):
    session = make_session()
    session.intervals = [
        AnnotationInterval(0, 4_000, 1),
        AnnotationInterval(4_000, 10_000, 2, notes="important"),
    ]

    changed = editor.relabel_interval(session, interval_index=1, phase_id=3)

    assert changed is True
    assert session.intervals == [
        AnnotationInterval(0, 4_000, 1),
        AnnotationInterval(4_000, 10_000, 3, notes="important"),
    ]


def test_relabel_interval_coalesces_both_neighbours_and_combines_notes(
    editor: AnnotationEditor,
):
    session = make_session()
    session.intervals = [
        AnnotationInterval(0, 3_000, 1, notes="left"),
        AnnotationInterval(3_000, 7_000, 2, notes="middle"),
        AnnotationInterval(7_000, 10_000, 1, notes="right"),
    ]

    editor.relabel_interval(session, interval_index=1, phase_id=1)

    assert session.intervals == [
        AnnotationInterval(0, 10_000, 1, notes="left\nmiddle\nright")
    ]


def test_relabel_interval_with_current_phase_is_no_op(editor: AnnotationEditor):
    session = make_session()
    editor.initialize_coverage(session)
    original = copy.deepcopy(session)

    changed = editor.relabel_interval(session, interval_index=0, phase_id=1)

    assert changed is False
    assert session == original


@pytest.mark.parametrize(
    ("interval_index", "phase_id", "message"),
    [(-1, 1, "index"), (1, 1, "index"), (0, 99, "Phase ID")],
)
def test_relabel_interval_rejects_invalid_request_without_mutation(
    editor: AnnotationEditor,
    interval_index: int,
    phase_id: int,
    message: str,
):
    session = make_session()
    editor.initialize_coverage(session)
    original = copy.deepcopy(session)

    with pytest.raises(ValueError, match=message):
        editor.relabel_interval(session, interval_index, phase_id)

    assert session == original


def test_move_boundary_updates_both_neighbours_and_preserves_notes(
    editor: AnnotationEditor,
):
    session = make_session()
    session.intervals = [
        AnnotationInterval(0, 4_000, 1, notes="left"),
        AnnotationInterval(4_000, 10_000, 2, notes="right"),
    ]

    changed = editor.move_boundary(session, boundary_index=1, position_ms=6_000)

    assert changed is True
    assert session.intervals == [
        AnnotationInterval(0, 6_000, 1, notes="left"),
        AnnotationInterval(6_000, 10_000, 2, notes="right"),
    ]


def test_move_boundary_at_existing_position_is_no_op(editor: AnnotationEditor):
    session = make_session()
    session.intervals = [
        AnnotationInterval(0, 4_000, 1),
        AnnotationInterval(4_000, 10_000, 2),
    ]
    original = copy.deepcopy(session)

    changed = editor.move_boundary(session, boundary_index=1, position_ms=4_000)

    assert changed is False
    assert session == original


@pytest.mark.parametrize(
    ("boundary_index", "position_ms", "message"),
    [
        (0, 2_000, "internal shared boundary"),
        (2, 8_000, "internal shared boundary"),
        (1, 0, "greater than"),
        (1, 10_000, "less than"),
    ],
)
def test_move_boundary_rejects_invalid_request_without_mutation(
    editor: AnnotationEditor,
    boundary_index: int,
    position_ms: int,
    message: str,
):
    session = make_session()
    session.intervals = [
        AnnotationInterval(0, 4_000, 1),
        AnnotationInterval(4_000, 10_000, 2),
    ]
    original = copy.deepcopy(session)

    with pytest.raises(ValueError, match=message):
        editor.move_boundary(session, boundary_index, position_ms)

    assert session == original


def test_convert_to_undefined_relabels_and_coalesces(editor: AnnotationEditor):
    session = make_session()
    session.intervals = [
        AnnotationInterval(0, 3_000, 0, notes="left"),
        AnnotationInterval(3_000, 7_000, 2, notes="selected"),
        AnnotationInterval(7_000, 10_000, 0, notes="right"),
    ]

    changed = editor.convert_to_undefined(session, interval_index=1)

    assert changed is True
    assert session.intervals == [
        AnnotationInterval(0, 10_000, 0, notes="left\nselected\nright")
    ]


def test_merge_left_adopts_left_phase_and_preserves_notes(editor: AnnotationEditor):
    session = make_session()
    session.intervals = [
        AnnotationInterval(0, 4_000, 1, notes="left"),
        AnnotationInterval(4_000, 10_000, 2, notes="selected"),
    ]

    editor.merge_left(session, interval_index=1)

    assert session.intervals == [
        AnnotationInterval(0, 10_000, 1, notes="left\nselected")
    ]


def test_merge_right_adopts_right_phase_and_preserves_notes(editor: AnnotationEditor):
    session = make_session()
    session.intervals = [
        AnnotationInterval(0, 4_000, 1, notes="selected"),
        AnnotationInterval(4_000, 10_000, 2, notes="right"),
    ]

    editor.merge_right(session, interval_index=0)

    assert session.intervals == [
        AnnotationInterval(0, 10_000, 2, notes="selected\nright")
    ]


@pytest.mark.parametrize(
    ("operation_name", "interval_index", "message"),
    [
        ("merge_left", 0, "cannot merge left"),
        ("merge_right", 1, "cannot merge right"),
        ("merge_left", -1, "out of range"),
        ("merge_right", 2, "out of range"),
    ],
)
def test_merge_rejects_unavailable_direction_without_mutation(
    editor: AnnotationEditor,
    operation_name: str,
    interval_index: int,
    message: str,
):
    session = make_session()
    session.intervals = [
        AnnotationInterval(0, 4_000, 1),
        AnnotationInterval(4_000, 10_000, 2),
    ]
    original = copy.deepcopy(session)

    with pytest.raises(ValueError, match=message):
        getattr(editor, operation_name)(session, interval_index)

    assert session == original
