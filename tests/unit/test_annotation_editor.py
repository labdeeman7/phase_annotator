import copy

import pytest

from phase_annotator.domain.annotation_editor import AnnotationEditor
from phase_annotator.domain.models import AnnotationInterval, AnnotationSession, VideoInfo


@pytest.fixture
def editor() -> AnnotationEditor:
    return AnnotationEditor(valid_phase_ids={0, 1, 2, 3}, undefined_phase_id=0)


def make_session(duration_ms: int = 10_000) -> AnnotationSession:
    return AnnotationSession(
        video_info=VideoInfo(video_id="synthetic_case.mp4", duration_ms=duration_ms),
        annotator_id="annotator_01",
    )


def test_initialize_coverage_creates_one_undefined_interval(editor: AnnotationEditor):
    session = make_session()

    changed = editor.initialize_coverage(session)

    assert changed is True
    assert session.intervals == [
        AnnotationInterval(start_ms=0, end_ms=10_000, phase_id=0)
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

    changed = editor.apply_transition(session, phase_id=1, position_ms=2_000)

    assert changed is True
    assert session.intervals == [
        AnnotationInterval(start_ms=0, end_ms=2_000, phase_id=0),
        AnnotationInterval(start_ms=2_000, end_ms=10_000, phase_id=1),
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
