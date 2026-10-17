from collections import Counter

from phase_annotator.config import load_procedure_ontology
from scripts.build_oauthc_training_material import (
    EXAMPLES,
    BuiltExample,
    write_html_index,
)


def test_example_plan_has_two_examples_per_phase_and_explicit_fallbacks() -> None:
    assert len(EXAMPLES) == 14
    assert Counter(example.phase_id for example in EXAMPLES) == {
        phase_id: 2 for phase_id in range(1, 8)
    }
    assert Counter(example.source for example in EXAMPLES) == {
        "OAUTHC": 11,
        "Cholec80": 3,
    }
    assert {
        (example.phase_id, example.example_number)
        for example in EXAMPLES
        if example.source == "Cholec80"
    } == {(5, 2), (7, 1), (7, 2)}


def test_html_index_groups_examples_by_phase_and_labels_fallbacks(tmp_path) -> None:
    ontology = load_procedure_ontology("cholecystectomy")
    examples = [
        BuiltExample(
            phase_id=spec.phase_id,
            example_number=spec.example_number,
            source=spec.source,
            case_id=spec.case_id,
            filename=f"P{spec.phase_id}_EX{spec.example_number:02d}.mp4",
            description=spec.description,
            clip_start_ms=0,
            clip_end_ms=30_000,
            boundary_ms=None if spec.phase_id == 1 else 15_000,
            from_phase_id=None if spec.phase_id == 1 else spec.phase_id - 1,
        )
        for spec in EXAMPLES
    ]
    destination = tmp_path / "index.html"

    write_html_index(examples, destination, ontology=ontology)

    page = destination.read_text(encoding="utf-8")
    assert all(f'id="p{phase_id}"' in page for phase_id in range(1, 8))
    assert page.count("<video ") == 14
    assert page.count(">OAUTHC</span>") == 11
    assert page.count(">Cholec80</span>") == 3
    assert page.count("This Cholec80 example provides provisional guidance") == 3
