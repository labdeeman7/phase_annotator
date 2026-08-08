from typing import List
from phase_annotator.domain.models import AnnotationInterval


def validate_no_overlaps(intervals: List[AnnotationInterval]) -> List[str]:
    """
    Validates that no two intervals overlap temporally.
    
    Returns a list of human-readable error messages for any detected overlaps.
    """
    # TODO (Student Exercise): Implement overlap checking logic
    # Tip: Sort intervals by start_ms, then check if interval[i].start_ms < interval[i-1].end_ms

    errors = []
    sorted_intervals = sorted(intervals, key=lambda x: x.start_ms)
    for i in range(1, len(sorted_intervals)):
        current_interval = sorted_intervals[i]
        previous_interval = sorted_intervals[i-1]
        if current_interval.start_ms < previous_interval.end_ms:
            errors.append(
                f"Overlap detected between Phase {previous_interval.phase_id} "
                f"[{previous_interval.start_ms}ms–{previous_interval.end_ms}ms] and Phase {current_interval.phase_id} "
                f"[{current_interval.start_ms}ms–{current_interval.end_ms}ms]."
            )

    return errors
