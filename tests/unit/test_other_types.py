"""Typed Other segments: tag parsing, tag-aware merging, completion facts, old files."""

import pytest

from phase_annotator.config import load_procedure_ontology
from phase_annotator.domain.annotation_editor import AnnotationEditor
from phase_annotator.domain.completion import (
    summarize_completion,
    with_privacy_check,
)
from phase_annotator.domain.models import (
    AnnotationInterval,
    AnnotationSession,
    VideoInfo,
)
from phase_annotator.domain.ontology import OntologyConfigError, PhaseOntology
from phase_annotator.domain.other_types import compose_note, split_tag
from phase_annotator.storage import SessionPersistenceCoordinator


def make_session(intervals, notes=""):
    end = intervals[-1].end_ms
    return AnnotationSession(
        VideoInfo("case.mp4", end),
        "annotator",
        ontology_id="laparoscopic_cholecystectomy.cholec80",
        ontology_version="1.1",
        intervals=intervals,
        session_notes=notes,
    )


def editor():
    return AnnotationEditor(range(8), undefined_phase_id=0, initial_phase_id=1)


def test_tag_is_split_from_and_composed_into_the_note():
    assert split_tag("[DEIDENTIFY] surgeon's face") == ("DEIDENTIFY", "surgeon's face")
    assert split_tag("plain words") == (None, "plain words")
    assert split_tag("[lower] not a tag") == (None, "[lower] not a tag")
    assert compose_note("DRAIN_INSERTION", "  under the liver ") == (
        "[DRAIN_INSERTION] under the liver"
    )
    assert compose_note(None, " described ") == "described"
    assert compose_note("LIVER_BIOPSY", "") == "[LIVER_BIOPSY]"


def test_other_segments_of_different_types_do_not_merge():
    session = make_session(
        [
            AnnotationInterval(0, 40_000, 0, notes="[DRAIN_INSERTION] drain"),
            AnnotationInterval(40_000, 50_000, 4),
            AnnotationInterval(50_000, 60_000, 0, notes="[DEIDENTIFY] face"),
        ]
    )
    assert editor().relabel_interval(session, 1, 0)
    assert [(i.start_ms, i.end_ms, i.notes) for i in session.intervals] == [
        (0, 40_000, "[DRAIN_INSERTION] drain"),
        (40_000, 50_000, ""),
        (50_000, 60_000, "[DEIDENTIFY] face"),
    ]


def test_same_type_and_ordinary_phases_still_merge():
    session = make_session(
        [
            AnnotationInterval(0, 10_000, 2, notes="a"),
            AnnotationInterval(10_000, 20_000, 4),
            AnnotationInterval(20_000, 30_000, 2, notes="b"),
        ]
    )
    assert editor().relabel_interval(session, 1, 2)
    assert [(i.start_ms, i.end_ms, i.notes) for i in session.intervals] == [
        (0, 30_000, "a\nb")
    ]


def test_merging_into_a_typed_other_keeps_its_tag_first():
    session = make_session(
        [
            AnnotationInterval(0, 10_000, 4, notes="bleeding"),
            AnnotationInterval(10_000, 20_000, 0, notes="[DEIDENTIFY] gown"),
        ]
    )
    assert editor().merge_right(session, 0)
    assert [(i.start_ms, i.end_ms, i.phase_id, i.notes) for i in session.intervals] == [
        (0, 20_000, 0, "[DEIDENTIFY] gown\nbleeding")
    ]


def test_completion_counts_undescribed_and_short_other_and_privacy():
    session = make_session(
        [
            AnnotationInterval(0, 10_000, 0),
            AnnotationInterval(10_000, 15_000, 0, notes="[DEIDENTIFY] face"),
            AnnotationInterval(15_000, 30_000, 1),
            AnnotationInterval(30_000, 40_000, 0, notes="[LIVER_BIOPSY]"),
            AnnotationInterval(40_000, 80_000, 0, notes="described in words"),
        ],
        notes="Privacy checked",
    )
    summary = summarize_completion(session, undefined_phase_id=0)
    assert summary.undescribed_other_count == 1
    assert summary.short_other_count == 2  # untyped 10 s and biopsy 10 s
    assert summary.has_privacy_check


def test_privacy_line_is_added_once():
    assert with_privacy_check("") == "Privacy checked"
    assert with_privacy_check("Looked fine") == "Looked fine\nPrivacy checked"
    assert with_privacy_check("privacy checked: none found") == (
        "privacy checked: none found"
    )


def test_round_one_files_still_validate_and_unknown_versions_do_not():
    coordinator = SessionPersistenceCoordinator(
        load_procedure_ontology("cholecystectomy")
    )
    old = make_session([AnnotationInterval(0, 10_000, 0, notes="drainage")])
    old.ontology_version = "1.0"
    assert coordinator.validation_errors(old) == []
    old.ontology_version = "0.9"
    assert any(
        "ontology version" in error for error in coordinator.validation_errors(old)
    )


@pytest.mark.parametrize(
    "subtypes",
    [
        [{"tag": "lower", "label": "x"}],
        [{"tag": "A", "label": "x"}, {"tag": "A", "label": "y"}],
        [{"tag": "A"}],
    ],
)
def test_bad_other_subtypes_are_rejected(subtypes):
    config = {
        "schema_version": "1.0",
        "ontology_id": "synthetic",
        "ontology_version": "1",
        "name": "Synthetic",
        "initial_phase_id": 1,
        "undefined_phase_id": 0,
        "phases": [
            {"id": 1, "name": "A", "hotkey": "1", "color_hex": "#000000", "order": 1},
            {
                "id": 0,
                "name": "Other",
                "hotkey": "0",
                "color_hex": "#000000",
                "order": 2,
            },
        ],
        "other_subtypes": subtypes,
    }
    with pytest.raises(OntologyConfigError):
        PhaseOntology.from_config(config)
