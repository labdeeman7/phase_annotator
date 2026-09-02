"""Packaged ontology configuration loading adapters."""

import json
from importlib import resources
from pathlib import Path

from phase_annotator.domain.ontology import OntologyConfigError, PhaseOntology


DEFAULT_APPENDECTOMY_FILENAME = "default_appendectomy.json"


def load_ontology_from_path(path: Path) -> PhaseOntology:
    """Loads and validates an ontology JSON file selected by the application/user."""
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as stream:
            config = json.load(stream)
    except json.JSONDecodeError as error:
        raise OntologyConfigError(
            f"Ontology file '{path}' contains invalid JSON: {error}"
        ) from error
    return PhaseOntology.from_config(config)


def load_packaged_ontology(filename: str) -> PhaseOntology:
    """Loads a validated ontology resource shipped inside the application package."""
    resource = resources.files(__package__).joinpath(filename)
    try:
        with resource.open("r", encoding="utf-8") as stream:
            config = json.load(stream)
    except json.JSONDecodeError as error:
        raise OntologyConfigError(
            f"Packaged ontology '{filename}' contains invalid JSON: {error}"
        ) from error
    return PhaseOntology.from_config(config)


def load_default_ontology() -> PhaseOntology:
    """Loads the application's currently configured packaged default ontology."""
    return load_packaged_ontology(DEFAULT_APPENDECTOMY_FILENAME)
