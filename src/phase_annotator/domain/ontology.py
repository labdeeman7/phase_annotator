import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Tuple

from phase_annotator.domain.other_types import TAG_PATTERN

SUPPORTED_ONTOLOGY_SCHEMA_VERSION = "1.0"
COLOR_HEX_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


class OntologyConfigError(ValueError):
    """Raised when an ontology configuration violates its schema contract."""


@dataclass(frozen=True)
class Phase:
    """Represents a single surgical phase in an ontology."""

    id: int
    name: str
    is_optional: bool = False
    description: str = ""
    color_hex: str = "#3B82F6"
    hotkey: str = ""
    order: int = 0


@dataclass(frozen=True)
class OtherSubtype:
    """One choice offered when a segment is labelled as the ontology's Other phase."""

    tag: str
    label: str


@dataclass
class PhaseOntology:
    """Collection of phase definitions for a surgical procedure."""

    ontology_id: str
    ontology_version: str
    schema_version: str
    name: str
    initial_phase_id: int
    undefined_phase_id: int
    phases: Dict[int, Phase] = field(default_factory=dict)
    # Types offered for the Other (undefined_phase_id) phase; empty keeps the old behaviour.
    other_subtypes: Tuple[OtherSubtype, ...] = ()
    # Earlier versions with identical phase IDs whose sessions still load (and are
    # restamped with ontology_version when next saved).
    compatible_ontology_versions: Tuple[str, ...] = ()
    # Marking complete requires the annotator's privacy declaration.
    completion_requires_privacy_check: bool = False

    def accepts_version(self, version: str) -> bool:
        """Whether a session stamped with ``version`` can be opened by this ontology."""
        return version == self.ontology_version or (
            version in self.compatible_ontology_versions
        )

    def get_phase_by_id(self, phase_id: int) -> Phase:
        """Looks up a Phase by its integer ID. Raises KeyError if not found."""
        if phase_id not in self.phases:
            raise KeyError(
                f"Phase ID {phase_id} is not defined in ontology '{self.name}'."
            )
        return self.phases[phase_id]

    @property
    def ordered_phases(self) -> List[Phase]:
        """Phases in configured expected display order."""
        return sorted(self.phases.values(), key=lambda phase: phase.order)

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "PhaseOntology":
        """Builds and validates an ontology from already-decoded configuration data."""
        if not isinstance(config, Mapping):
            raise OntologyConfigError("Ontology config must be a JSON object.")

        schema_version = cls._required_string(config, "schema_version")
        if schema_version != SUPPORTED_ONTOLOGY_SCHEMA_VERSION:
            raise OntologyConfigError(
                f"Unsupported schema_version '{schema_version}'; expected "
                f"'{SUPPORTED_ONTOLOGY_SCHEMA_VERSION}'."
            )

        ontology_id = cls._required_string(config, "ontology_id")
        ontology_version = cls._required_string(config, "ontology_version")
        name = cls._required_string(config, "name")
        initial_phase_id = cls._required_int(config, "initial_phase_id")
        undefined_phase_id = cls._required_int(config, "undefined_phase_id")

        phase_items = config.get("phases")
        if not isinstance(phase_items, list) or not phase_items:
            raise OntologyConfigError("'phases' must be a non-empty JSON array.")

        phases: Dict[int, Phase] = {}
        hotkeys = set()
        orders = set()
        for index, item in enumerate(phase_items):
            if not isinstance(item, Mapping):
                raise OntologyConfigError(f"Phase at index {index} must be an object.")

            phase_id = cls._required_int(item, "id", context=f"phase[{index}]")
            if phase_id in phases:
                raise OntologyConfigError(f"Duplicate phase id {phase_id}.")

            phase_name = cls._required_string(item, "name", context=f"phase[{index}]")
            hotkey = cls._required_string(
                item, "hotkey", context=f"phase[{index}]"
            ).upper()
            if len(hotkey) != 1 or not hotkey.isprintable():
                raise OntologyConfigError(
                    f"phase[{index}].hotkey must be one printable character."
                )
            if hotkey in hotkeys:
                raise OntologyConfigError(f"Duplicate phase hotkey '{hotkey}'.")

            color_hex = cls._required_string(
                item, "color_hex", context=f"phase[{index}]"
            )
            if not COLOR_HEX_PATTERN.fullmatch(color_hex):
                raise OntologyConfigError(
                    f"phase[{index}].color_hex must use #RRGGBB format."
                )

            order = cls._required_int(item, "order", context=f"phase[{index}]")
            if order <= 0:
                raise OntologyConfigError(f"phase[{index}].order must be positive.")
            if order in orders:
                raise OntologyConfigError(f"Duplicate phase order {order}.")

            is_optional = item.get("is_optional", False)
            if not isinstance(is_optional, bool):
                raise OntologyConfigError(
                    f"phase[{index}].is_optional must be a Boolean."
                )
            description = item.get("description", "")
            if not isinstance(description, str):
                raise OntologyConfigError(
                    f"phase[{index}].description must be a string."
                )

            phases[phase_id] = Phase(
                id=phase_id,
                name=phase_name,
                is_optional=is_optional,
                description=description.strip(),
                color_hex=color_hex.upper(),
                hotkey=hotkey,
                order=order,
            )
            hotkeys.add(hotkey)
            orders.add(order)

        if initial_phase_id not in phases:
            raise OntologyConfigError(
                f"initial_phase_id {initial_phase_id} is not defined in phases."
            )
        if undefined_phase_id not in phases:
            raise OntologyConfigError(
                f"undefined_phase_id {undefined_phase_id} is not defined in phases."
            )

        return cls(
            ontology_id=ontology_id,
            ontology_version=ontology_version,
            schema_version=schema_version,
            name=name,
            initial_phase_id=initial_phase_id,
            undefined_phase_id=undefined_phase_id,
            phases=phases,
            other_subtypes=cls._other_subtypes(config),
            compatible_ontology_versions=cls._compatible_versions(
                config, ontology_version
            ),
            completion_requires_privacy_check=cls._optional_bool(
                config, "completion_requires_privacy_check"
            ),
        )

    @staticmethod
    def _optional_bool(config: Mapping[str, Any], key: str) -> bool:
        value = config.get(key, False)
        if not isinstance(value, bool):
            raise OntologyConfigError(f"'{key}' must be a Boolean.")
        return value

    @staticmethod
    def _other_subtypes(config: Mapping[str, Any]) -> Tuple[OtherSubtype, ...]:
        items = config.get("other_subtypes", [])
        if not isinstance(items, list):
            raise OntologyConfigError("'other_subtypes' must be a JSON array.")
        subtypes: List[OtherSubtype] = []
        for index, item in enumerate(items):
            context = f"other_subtypes[{index}]"
            if not isinstance(item, Mapping):
                raise OntologyConfigError(f"{context} must be an object.")
            tag = PhaseOntology._required_string(item, "tag", context=context)
            if not TAG_PATTERN.fullmatch(f"[{tag}]"):
                raise OntologyConfigError(
                    f"{context}.tag must be capital letters, digits or underscores."
                )
            if any(existing.tag == tag for existing in subtypes):
                raise OntologyConfigError(f"Duplicate other subtype tag '{tag}'.")
            label = PhaseOntology._required_string(item, "label", context=context)
            subtypes.append(OtherSubtype(tag=tag, label=label))
        return tuple(subtypes)

    @staticmethod
    def _compatible_versions(
        config: Mapping[str, Any], ontology_version: str
    ) -> Tuple[str, ...]:
        items = config.get("compatible_ontology_versions", [])
        if not isinstance(items, list) or not all(
            isinstance(item, str) and item.strip() for item in items
        ):
            raise OntologyConfigError(
                "'compatible_ontology_versions' must be an array of strings."
            )
        return tuple(item.strip() for item in items if item.strip() != ontology_version)

    @staticmethod
    def _required_string(
        data: Mapping[str, Any], key: str, context: str = "ontology"
    ) -> str:
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            raise OntologyConfigError(f"{context}.{key} must be a non-empty string.")
        return value.strip()

    @staticmethod
    def _required_int(
        data: Mapping[str, Any], key: str, context: str = "ontology"
    ) -> int:
        value = data.get(key)
        if not isinstance(value, int) or isinstance(value, bool):
            raise OntologyConfigError(f"{context}.{key} must be an integer.")
        return value
