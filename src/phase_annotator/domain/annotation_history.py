from dataclasses import dataclass, field, replace
from typing import Callable, List, Optional, Tuple

from phase_annotator.domain.annotation_editor import AnnotationEditor
from phase_annotator.domain.models import AnnotationInterval, AnnotationSession


IntervalSnapshot = Tuple[AnnotationInterval, ...]


def _snapshot(intervals: List[AnnotationInterval]) -> IntervalSnapshot:
    """Copy mutable interval objects so history cannot drift with the session."""
    return tuple(replace(interval) for interval in intervals)


@dataclass(frozen=True)
class AnnotationHistoryEntry:
    """One successful annotation command and its reversible states."""

    description: str
    anchor_ms: int
    _before: IntervalSnapshot = field(repr=False)
    _after: IntervalSnapshot = field(repr=False)


class AnnotationHistory:
    """Bounded in-memory undo/redo history for annotation interval commands."""

    def __init__(self, max_entries: int = 100):
        if max_entries <= 0:
            raise ValueError("max_entries must be positive.")
        self._max_entries = max_entries
        self._undo_stack: List[AnnotationHistoryEntry] = []
        self._redo_stack: List[AnnotationHistoryEntry] = []

    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    @property
    def undo_description(self) -> Optional[str]:
        return self._undo_stack[-1].description if self._undo_stack else None

    @property
    def redo_description(self) -> Optional[str]:
        return self._redo_stack[-1].description if self._redo_stack else None

    def execute(
        self,
        session: AnnotationSession,
        *,
        description: str,
        anchor_ms: int,
        mutation: Callable[[], bool],
    ) -> bool:
        """Run a transactional mutation and record it only when it changes data."""
        if not description.strip():
            raise ValueError("History description cannot be empty.")
        before = _snapshot(session.intervals)
        changed = mutation()
        if not changed:
            if before != _snapshot(session.intervals):
                raise RuntimeError(
                    "Mutation reported no change but modified the intervals."
                )
            return False

        after = _snapshot(session.intervals)
        if before == after:
            raise RuntimeError("Mutation reported a change but intervals are unchanged.")
        self._undo_stack.append(
            AnnotationHistoryEntry(description, anchor_ms, before, after)
        )
        if len(self._undo_stack) > self._max_entries:
            del self._undo_stack[0]
        self._redo_stack.clear()
        return True

    def undo(
        self,
        session: AnnotationSession,
        editor: AnnotationEditor,
    ) -> Optional[AnnotationHistoryEntry]:
        """Restore the newest before-state and make it available to Redo."""
        if not self._undo_stack:
            return None
        entry = self._undo_stack[-1]
        self._require_current_snapshot(session, entry._after, "undo")
        editor.restore_intervals(session, entry._before)
        self._undo_stack.pop()
        self._redo_stack.append(entry)
        return entry

    def redo(
        self,
        session: AnnotationSession,
        editor: AnnotationEditor,
    ) -> Optional[AnnotationHistoryEntry]:
        """Restore the newest after-state and make it available to Undo."""
        if not self._redo_stack:
            return None
        entry = self._redo_stack[-1]
        self._require_current_snapshot(session, entry._before, "redo")
        editor.restore_intervals(session, entry._after)
        self._redo_stack.pop()
        self._undo_stack.append(entry)
        return entry

    def clear(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()

    @staticmethod
    def _require_current_snapshot(
        session: AnnotationSession,
        expected: IntervalSnapshot,
        operation: str,
    ) -> None:
        if _snapshot(session.intervals) != expected:
            raise ValueError(
                f"Cannot {operation}: annotation changed outside this history."
            )
