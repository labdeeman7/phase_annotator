import copy
import json

import pytest

from phase_annotator.config import load_default_ontology, load_ontology_from_path
from phase_annotator.domain.ontology import OntologyConfigError, PhaseOntology


@pytest.fixture
def valid_config() -> dict:
    return {
        "schema_version": "1.0",
        "ontology_id": "synthetic.procedure",
        "ontology_version": "1.0",
        "name": "Synthetic Procedure",
        "initial_phase_id": 1,
        "undefined_phase_id": 0,
        "phases": [
            {
                "id": 1,
                "name": "Expected first phase",
                "hotkey": "1",
                "color_hex": "#112233",
                "order": 1,
                "is_optional": False,
                "description": "First expected phase.",
            },
            {
                "id": 0,
                "name": "Undefined",
                "hotkey": "U",
                "color_hex": "#6B7280",
                "order": 2,
                "is_optional": False,
                "description": "No confident label.",
            },
        ],
    }


def test_parse_valid_config_preserves_roles_and_expected_order(valid_config):
    ontology = PhaseOntology.from_config(valid_config)

    assert ontology.ontology_id == "synthetic.procedure"
    assert ontology.ontology_version == "1.0"
    assert ontology.schema_version == "1.0"
    assert ontology.initial_phase_id == 1
    assert ontology.undefined_phase_id == 0
    assert [phase.id for phase in ontology.ordered_phases] == [1, 0]
    assert ontology.get_phase_by_id(0).hotkey == "U"


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda config: config.update(schema_version="9.9"), "schema_version"),
        (
            lambda config: config["phases"][1].update(id=1),
            "Duplicate phase id",
        ),
        (
            lambda config: config["phases"][1].update(hotkey="1"),
            "Duplicate phase hotkey",
        ),
        (
            lambda config: config["phases"][1].update(order=1),
            "Duplicate phase order",
        ),
        (
            lambda config: config["phases"][0].update(color_hex="blue"),
            "color_hex",
        ),
        (lambda config: config.update(initial_phase_id=99), "initial_phase_id"),
        (
            lambda config: config.update(undefined_phase_id=99),
            "undefined_phase_id",
        ),
    ],
)
def test_invalid_config_is_rejected(valid_config, mutate, message):
    config = copy.deepcopy(valid_config)
    mutate(config)

    with pytest.raises(OntologyConfigError, match=message):
        PhaseOntology.from_config(config)


def test_packaged_appendectomy_config_has_expected_roles():
    ontology = load_default_ontology()

    assert ontology.ontology_id == "laparoscopic_appendectomy.default"
    assert ontology.ontology_version == "1.0"
    assert ontology.initial_phase_id == 1
    assert ontology.undefined_phase_id == 0
    assert [phase.id for phase in ontology.ordered_phases] == [1, 2, 3, 4, 5, 6, 0]
    assert ontology.get_phase_by_id(0).hotkey == "U"
    assert ontology.get_phase_by_id(2).is_optional is True


def test_load_ontology_from_user_selected_path(valid_config, tmp_path):
    config_path = tmp_path / "custom_ontology.json"
    config_path.write_text(json.dumps(valid_config), encoding="utf-8")

    ontology = load_ontology_from_path(config_path)

    assert ontology.ontology_id == "synthetic.procedure"
    assert ontology.initial_phase_id == 1
