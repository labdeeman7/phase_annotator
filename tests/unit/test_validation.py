import pytest
from phase_annotator.domain.models import AnnotationInterval
from phase_annotator.domain.validation import validate_no_overlaps


def test_validate_no_overlaps_with_valid_sequence():
    intervals = [
        AnnotationInterval(start_ms=0, end_ms=5000, phase_id=1),
        AnnotationInterval(start_ms=5000, end_ms=10000, phase_id=2),
        AnnotationInterval(start_ms=10000, end_ms=15000, phase_id=3),
    ]
    errors = validate_no_overlaps(intervals)
    assert len(errors) == 0


def test_validate_no_overlaps_detects_overlap():
    intervals = [
        AnnotationInterval(start_ms=0, end_ms=6000, phase_id=1),
        AnnotationInterval(start_ms=5000, end_ms=10000, phase_id=2),  # Overlaps 5000..6000
    ]
    errors = validate_no_overlaps(intervals)
    assert len(errors) == 1
    assert "overlap" in errors[0].lower()
