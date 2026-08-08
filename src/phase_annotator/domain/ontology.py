from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class Phase:
    """Represents a single surgical phase in an ontology."""

    id: int
    name: str
    is_optional: bool = False
    description: str = ""


@dataclass
class PhaseOntology:
    """Collection of phase definitions for a surgical procedure."""

    name: str
    phases: Dict[int, Phase] = field(default_factory=dict)

    def get_phase(self, phase_id: int) -> Phase:
        if phase_id not in self.phases:
            raise KeyError(f"Phase ID {phase_id} is not defined in ontology '{self.name}'.")
        return self.phases[phase_id]

    @classmethod
    def default_appendectomy(cls) -> "PhaseOntology":
        """Returns the provisional 6-phase laparoscopic appendectomy ontology."""
        phases_list = [
            Phase(id=1, name="Identification of the appendix", is_optional=False),
            Phase(id=2, name="Dissection of adhesions of the appendix", is_optional=True),
            Phase(id=3, name="Coagulation and release of the mesoappendix", is_optional=False),
            Phase(id=4, name="Ligation of the base of the appendix", is_optional=False),
            Phase(id=5, name="Resection/cutting of the appendix", is_optional=False),
            Phase(id=6, name="Retrieval of the appendix specimen", is_optional=False),
        ]
        return cls(
            name="Laparoscopic Appendectomy Ontology",
            phases={p.id: p for p in phases_list},
        )
