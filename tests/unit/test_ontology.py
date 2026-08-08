import pytest
from phase_annotator.domain.ontology import Phase, PhaseOntology


def test_phase_creation():
    phase = Phase(id=1, name="Identification of the appendix", is_optional=False)
    assert phase.id == 1
    assert phase.name == "Identification of the appendix"
    assert not phase.is_optional


def test_default_appendectomy_ontology():
    ontology = PhaseOntology.default_appendectomy()
    assert len(ontology.phases) == 6
    assert ontology.get_phase(1).name == "Identification of the appendix"
    assert ontology.get_phase(2).is_optional is True
    assert ontology.get_phase(3).is_optional is False


def test_invalid_phase_lookup():
    ontology = PhaseOntology.default_appendectomy()
    with pytest.raises(KeyError):
        ontology.get_phase(99)
