"""Packaged ontology configuration loading adapters."""

import json
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from phase_annotator.domain.ontology import OntologyConfigError, PhaseOntology

DEFAULT_APPENDECTOMY_FILENAME = "default_appendectomy.json"
CHOLEC80_FILENAME = "cholec80_cholecystectomy.json"


@dataclass(frozen=True)
class PackagedProcedure:
    key: str
    display_name: str
    ontology_filename: str
    ontology_id: str


PACKAGED_PROCEDURES = (
    PackagedProcedure(
        "appendectomy",
        "Laparoscopic appendectomy",
        DEFAULT_APPENDECTOMY_FILENAME,
        "laparoscopic_appendectomy.default",
    ),
    PackagedProcedure(
        "cholecystectomy",
        "Laparoscopic cholecystectomy",
        CHOLEC80_FILENAME,
        "laparoscopic_cholecystectomy.cholec80",
    ),
)


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


def load_procedure_ontology(procedure_key: str) -> PhaseOntology:
    """Load one reviewed ontology from the packaged procedure registry."""
    procedure = next(
        (item for item in PACKAGED_PROCEDURES if item.key == procedure_key),
        None,
    )
    if procedure is None:
        raise OntologyConfigError(f"Unknown packaged procedure '{procedure_key}'.")
    return load_packaged_ontology(procedure.ontology_filename)


def procedure_name_for_ontology_id(ontology_id: str) -> str:
    """Return a clinician-facing procedure name, with a safe unknown fallback."""
    procedure = next(
        (item for item in PACKAGED_PROCEDURES if item.ontology_id == ontology_id),
        None,
    )
    return procedure.display_name if procedure is not None else ontology_id
