import pytest

from phase_annotator.ui.annotator_identity import normalize_annotator_id


def test_normalize_annotator_id_trims_and_lowercases_first_name():
    assert normalize_annotator_id("  Tosin  ") == "tosin"


@pytest.mark.parametrize("value", ["", "   ", "Mary Jane", "x" * 51])
def test_normalize_annotator_id_rejects_unusable_values(value):
    with pytest.raises(ValueError):
        normalize_annotator_id(value)
