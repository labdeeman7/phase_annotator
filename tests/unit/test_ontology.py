import pytest
from phase_annotator.config import load_default_ontology
from phase_annotator.domain.ontology import Phase


def test_phase_creation():
    p = Phase(id=1, name="Preparation", is_optional=False, description="Initial phase")
    assert p.id == 1
    assert p.name == "Preparation"
    assert not p.is_optional


def test_default_appendectomy_ontology():
    ontology = load_default_ontology()
    assert ontology.name == "Laparoscopic Appendectomy Ontology"
    assert len(ontology.phases) == 7

    undefined = ontology.get_phase_by_id(0)
    assert undefined.name == "Undefined"
    assert undefined.color_hex == "#6B7280"

    phase_1 = ontology.get_phase_by_id(1)
    assert phase_1.name == "Identification of the appendix"
    assert phase_1.color_hex == "#3B82F6"


def test_invalid_phase_lookup():
    ontology = load_default_ontology()
    with pytest.raises(KeyError):
        ontology.get_phase_by_id(99)
