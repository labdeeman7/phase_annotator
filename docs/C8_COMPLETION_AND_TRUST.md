# C8 Completion and Trustworthy JSON

## Outcome

An annotator can add an optional video-level note, explicitly declare a structurally valid annotation complete, see who completed it and when, and deliberately reopen completed work for correction without losing the previously completed state.

Completion is a human declaration. Full interval coverage does not prove that all footage was reviewed because the initial phase provisionally covers unwatched footage.

## Minimal interaction contract

- Add an **Annotation** menu rather than permanent panels or large buttons.
- Draft menu actions: **Edit video note...** and **Mark complete...**.
- Completed menu actions: **View/edit video note...** and **Reopen for editing...**.
- Display `Draft` or `Completed` in the window title with the fixed launch annotator.
- Playback, seeking, and selection never change lifecycle state.

## Schema 1.4

- `session_notes`: optional video-level text, distinct from interval notes.
- `completed_by`: nullable annotator ID paired with `completed_at`.
- Draft requires both completion fields to be null.
- Completed requires both completion fields to be valid.
- `created_by` never changes. Completion and note edits update `last_edited_by`.
- Known legacy schemas load with empty notes and a compatible completion attribution default where necessary.

## Completion validation and summary

Before completion validate schema, ontology identity, known phase IDs, contiguous full coverage, bounds, source association, attribution, and persistence state. Present duration, segment count, Undefined segment count/duration, and whether a general note is present.

Structural failures block completion without partial mutation. Undefined footage requires explicit confirmation but is allowed because it may be clinically legitimate.

## Reopening completed work

Completed annotations remain navigable but cannot be mutated silently. Reopening first archives the completed canonical JSON, then changes the lifecycle to draft, clears completion attribution/time, saves, and permits correction. Cancelling leaves the completed annotation unchanged. The guard applies to phase/boundary/note/merge operations, undo/redo, and video-level notes.

## Sub-slices

- **C8.1 — Schema and lifecycle (implemented):** schema 1.4 fields, validation, migration, and round trips.
- **C8.2 — General video note (implemented):** modal Save/Cancel editing through the persistence boundary.
- **C8.3 — Completion summary (implemented):** pure summary logic including Undefined statistics plus persistence validation.
- **C8.4 — Mark complete (implemented):** minimal menu action, confirmation, attribution, atomic persistence, and visible state.
- **C8.5 — Reopen safely (implemented):** archive completed state before an explicit or edit-triggered draft transition.
- **C8.6 — Acceptance (automated complete; manual pending):** migration, lifecycle, recovery, GUI, and full-suite coverage.

## Learning-mode reading map

Start with lifecycle invariants in `domain/models.py` and their tests. The central engineering idea is a small state machine: `Draft -> Completed -> Draft`, with validation and side effects at transitions rather than scattered Boolean checks.

## Current status

C8 is implemented pending manual acceptance. The **Annotation** menu exposes the optional video note, completion, and reopening actions without consuming permanent screen space. Completion shows the duration, segment count, Undefined count/duration, and note presence before confirmation. The window title exposes Draft/Completed state.

A completed annotation remains navigable. Any explicit reopening or attempted mutation asks for confirmation, verifies the canonical sidecar, archives the completed JSON, and only then returns the working session to Draft. Cancelling or failing to create the recovery copy leaves the completed annotation unchanged.
