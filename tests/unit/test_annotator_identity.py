import pytest

from phase_annotator.ui.annotator_identity import normalize_annotator_id


def test_normalize_annotator_id_trims_surrounding_whitespace():
    assert normalize_annotator_id("  study_007  ") == "study_007"


@pytest.mark.parametrize("value", ["", "   ", "x" * 101])
def test_normalize_annotator_id_rejects_unusable_values(value):
    with pytest.raises(ValueError):
        normalize_annotator_id(value)
