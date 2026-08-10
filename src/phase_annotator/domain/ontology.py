from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Phase:
    """Represents a single surgical phase in an ontology."""

    id: int
    name: str
    is_optional: bool = False
    description: str = ""
    color_hex: str = "#3B82F6"


@dataclass
class PhaseOntology:
    """Collection of phase definitions for a surgical procedure."""

    name: str
    phases: Dict[int, Phase] = field(default_factory=dict)

    def get_phase_by_id(self, phase_id: int) -> Phase:
        """Looks up a Phase by its integer ID. Raises KeyError if not found."""
        if phase_id not in self.phases:
            raise KeyError(f"Phase ID {phase_id} is not defined in ontology '{self.name}'.")
        return self.phases[phase_id]

    @classmethod
    def default_appendectomy(cls) -> "PhaseOntology":
        """Returns the provisional 6-phase laparoscopic appendectomy ontology with visual colors."""
        phases_list = [
            Phase(id=1, name="Identification of the appendix", color_hex="#3B82F6"),        # Blue
            Phase(id=2, name="Dissection of adhesions of the appendix", color_hex="#10B981", is_optional=True), # Green
            Phase(id=3, name="Coagulation/release of mesoappendix", color_hex="#F59E0B"),    # Amber
            Phase(id=4, name="Ligation of the base of the appendix", color_hex="#EF4444"),    # Red
            Phase(id=5, name="Resection/cutting of the appendix", color_hex="#8B5CF6"),      # Purple
            Phase(id=6, name="Retrieval of the appendix specimen", color_hex="#EC4899"),     # Pink
        ]
        return cls(
            name="Laparoscopic Appendectomy Ontology",
            phases={p.id: p for p in phases_list},
        )
