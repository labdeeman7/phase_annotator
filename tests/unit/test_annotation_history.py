import copy

import pytest

from phase_annotator.domain.annotation_editor import AnnotationEditor
from phase_annotator.domain.annotation_history import AnnotationHistory
from phase_annotator.domain.models import (
    AnnotationInterval,
    AnnotationSession,
    VideoInfo,
)


@pytest.fixture
def editor() -> AnnotationEditor:
    return AnnotationEditor({0, 1, 2, 3}, undefined_phase_id=0, initial_phase_id=1)


@pytest.fixture
def session() -> AnnotationSession:
    return AnnotationSession(
        video_info=VideoInfo("synthetic.mp4", duration_ms=10_000),
        annotator_id="tester",
        intervals=[AnnotationInterval(0, 10_000, 1)],
    )


def test_execute_undo_redo_restores_exact_interval_states(editor, session):
    history = AnnotationHistory()
    before = copy.deepcopy(session.intervals)

    changed = history.execute(
        session,
        description="Assign phase 2",
        anchor_ms=4_000,
        mutation=lambda: editor.apply_transition(session, 2, 4_000),
    )
    after = copy.deepcopy(session.intervals)

    assert changed is True
    assert history.can_undo
    assert not history.can_redo
    undone = history.undo(session, editor)
    assert undone.description == "Assign phase 2"
    assert undone.anchor_ms == 4_000
    assert session.intervals == before
    assert not history.can_undo
    assert history.can_redo

    redone = history.redo(session, editor)
    assert redone == undone
    assert session.intervals == after
    assert history.can_undo
    assert not history.can_redo


def test_no_op_and_failed_command_do_not_enter_history(editor, session):
    history = AnnotationHistory()

    assert not history.execute(
        session,
        description="Already phase 1",
        anchor_ms=2_000,
        mutation=lambda: editor.apply_transition(session, 1, 2_000),
    )
    with pytest.raises(ValueError):
        history.execute(
            session,
            description="Invalid phase",
            anchor_ms=2_000,
            mutation=lambda: editor.apply_transition(session, 99, 2_000),
        )

    assert not history.can_undo
    assert not history.can_redo


def test_new_command_after_undo_clears_redo(editor, session):
    history = AnnotationHistory()
    history.execute(
        session,
        description="Assign phase 2",
        anchor_ms=4_000,
        mutation=lambda: editor.apply_transition(session, 2, 4_000),
    )
    history.undo(session, editor)

    history.execute(
        session,
        description="Assign phase 3",
        anchor_ms=6_000,
        mutation=lambda: editor.apply_transition(session, 3, 6_000),
    )

    assert history.can_undo
    assert not history.can_redo


def test_snapshots_are_isolated_from_later_session_mutation(editor, session):
    history = AnnotationHistory()
    history.execute(
        session,
        description="Assign phase 2",
        anchor_ms=4_000,
        mutation=lambda: editor.apply_transition(session, 2, 4_000),
    )
    session.intervals[0].notes = "changed outside history"

    with pytest.raises(ValueError, match="outside this history"):
        history.undo(session, editor)

    assert history.can_undo
    assert not history.can_redo


def test_history_discards_oldest_entry_at_capacity(editor, session):
    history = AnnotationHistory(max_entries=1)
    history.execute(
        session,
        description="Assign phase 2",
        anchor_ms=4_000,
        mutation=lambda: editor.apply_transition(session, 2, 4_000),
    )
    history.execute(
        session,
        description="Assign phase 3",
        anchor_ms=7_000,
        mutation=lambda: editor.apply_transition(session, 3, 7_000),
    )

    assert history.undo_description == "Assign phase 3"
    history.undo(session, editor)
    assert not history.can_undo


def test_execute_rejects_mutation_that_reports_false_after_changing_session(session):
    history = AnnotationHistory()

    def broken_mutation() -> bool:
        session.intervals[0].notes = "changed"
        return False

    with pytest.raises(RuntimeError, match="reported no change"):
        history.execute(
            session,
            description="broken command",
            anchor_ms=0,
            mutation=broken_mutation,
        )

    assert not history.can_undo
