import pytest
from phase_annotator.domain.ontology import Phase, PhaseOntology


def test_phase_creation():
    p = Phase(id=1, name="Preparation", is_optional=False, description="Initial phase")
    assert p.id == 1
    assert p.name == "Preparation"
    assert not p.is_optional


def test_default_appendectomy_ontology():
    ontology = PhaseOntology.default_appendectomy()
    assert ontology.name == "Laparoscopic Appendectomy Ontology"
    assert len(ontology.phases) == 6

    phase_1 = ontology.get_phase_by_id(1)
    assert phase_1.name == "Identification of the appendix"
    assert phase_1.color_hex == "#3B82F6"


def test_invalid_phase_lookup():
    ontology = PhaseOntology.default_appendectomy()
    with pytest.raises(KeyError):
        ontology.get_phase_by_id(99)
