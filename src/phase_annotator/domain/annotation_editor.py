"""Transactional operations for editing a continuously covered annotation timeline."""

import time
from dataclasses import dataclass
from typing import Iterable, List

from phase_annotator.domain.models import AnnotationInterval, AnnotationSession
from phase_annotator.domain.validation import validate_contiguous_coverage


@dataclass(frozen=True)
class AnnotationEditor:
    """Applies validated annotation changes without depending on Qt or storage."""

    valid_phase_ids: frozenset[int]
    undefined_phase_id: int
    initial_phase_id: int

    def __init__(
        self,
        valid_phase_ids: Iterable[int],
        undefined_phase_id: int,
        initial_phase_id: int,
    ):
        phase_ids = frozenset(valid_phase_ids)
        if not phase_ids:
            raise ValueError("valid_phase_ids cannot be empty.")
        if undefined_phase_id not in phase_ids:
            raise ValueError("undefined_phase_id must be included in valid_phase_ids.")
        if initial_phase_id not in phase_ids:
            raise ValueError("initial_phase_id must be included in valid_phase_ids.")

        object.__setattr__(self, "valid_phase_ids", phase_ids)
        object.__setattr__(self, "undefined_phase_id", undefined_phase_id)
        object.__setattr__(self, "initial_phase_id", initial_phase_id)

    def initialize_coverage(self, session: AnnotationSession) -> bool:
        """Covers an empty session with its configured initial phase."""
        duration_ms = session.video_info.duration_ms
        if duration_ms <= 0:
            raise ValueError("Video duration must be positive before coverage is initialized.")
        if session.intervals:
            raise ValueError("Coverage can only be initialized for an empty session.")

        candidate = [
            AnnotationInterval(
                start_ms=0,
                end_ms=duration_ms,
                phase_id=self.initial_phase_id,
            )
        ]
        self._commit(session, candidate)
        return True

    def apply_transition(
        self,
        session: AnnotationSession,
        phase_id: int,
        position_ms: int,
    ) -> bool:
        """Applies ``phase_id`` from the playhead to the containing segment's end.

        Later segments remain intact. A transition inside a segment splits it;
        a transition at an existing boundary relabels the segment beginning at
        that boundary. Adjacent segments with equal labels are coalesced.
        """
        if phase_id not in self.valid_phase_ids:
            raise ValueError(f"Phase ID {phase_id} is not valid for this annotation.")

        duration_ms = session.video_info.duration_ms
        if position_ms < 0 or position_ms >= duration_ms:
            raise ValueError(
                f"Transition position ({position_ms}) must be within "
                f"[0, {duration_ms})."
            )

        self._require_valid_coverage(session.intervals, duration_ms)
        containing_index = next(
            (
                index
                for index, interval in enumerate(session.intervals)
                if interval.start_ms <= position_ms < interval.end_ms
            ),
            None,
        )
        if containing_index is None:
            raise ValueError(f"No interval contains transition position {position_ms}.")

        containing = session.intervals[containing_index]
        if containing.phase_id == phase_id:
            return False

        candidate = list(session.intervals[:containing_index])
        if position_ms > containing.start_ms:
            candidate.append(
                AnnotationInterval(
                    start_ms=containing.start_ms,
                    end_ms=position_ms,
                    phase_id=containing.phase_id,
                    notes=containing.notes,
                )
            )

        candidate.append(
            AnnotationInterval(
                start_ms=position_ms,
                end_ms=containing.end_ms,
                phase_id=phase_id,
            )
        )
        candidate.extend(session.intervals[containing_index + 1 :])
        candidate = self._coalesce_adjacent(candidate)

        self._require_valid_coverage(candidate, duration_ms)
        self._commit(session, candidate)
        return True

    @staticmethod
    def _coalesce_adjacent(
        intervals: List[AnnotationInterval],
    ) -> List[AnnotationInterval]:
        coalesced: List[AnnotationInterval] = []
        for interval in intervals:
            if coalesced and coalesced[-1].phase_id == interval.phase_id:
                previous = coalesced[-1]
                notes = "\n".join(
                    note for note in (previous.notes, interval.notes) if note
                )
                coalesced[-1] = AnnotationInterval(
                    start_ms=previous.start_ms,
                    end_ms=interval.end_ms,
                    phase_id=previous.phase_id,
                    notes=notes,
                )
            else:
                coalesced.append(interval)
        return coalesced

    def _require_valid_coverage(
        self, intervals: List[AnnotationInterval], duration_ms: int
    ) -> None:
        for interval in intervals:
            if interval.phase_id not in self.valid_phase_ids:
                raise ValueError(
                    f"Phase ID {interval.phase_id} is not valid for this annotation."
                )
        errors = validate_contiguous_coverage(intervals, duration_ms)
        if errors:
            raise ValueError("Invalid interval coverage: " + " ".join(errors))

    @staticmethod
    def _commit(
        session: AnnotationSession, candidate: List[AnnotationInterval]
    ) -> None:
        session.intervals = candidate
        session.updated_at = time.time()
