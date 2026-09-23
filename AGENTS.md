# Codex Project Guide

## Purpose and current maturity

This repository is a configurable desktop tool for producing temporal phase annotations for surgical videos. It currently ships with provisional laparoscopic appendectomy and laparoscopic cholecystectomy ontologies. It is an early prototype implemented through Codex milestone C9.7, not yet a production annotation system: playback, annotation/correction, undo/redo, media checks, continuous canonical JSON persistence, attribution/history, protected completion/reopening, prominent failure feedback, playback efficiency controls, shortcut help, packaged procedure selection, and safe procedure-mismatch handling exist, while distribution and cross-platform validation do not.

Start with `docs/CURRENT_STATE.md` and `docs/ROADMAP.md`, then use `docs/ARCHITECTURE.md`, `docs/ANNOTATION_WORKFLOW.md`, and `docs/DATA_MODEL.md` for deeper context. `docs/C10_RELEASE_ENGINEERING.md` defines the active release contract and C10.1–C10.7 plan; earlier milestone documents record their respective contracts. C10.1–C10.4 are complete; C10.5 continuous integration is next. Packaging must verify both ontology resources in the executable. `GEMINI.md`, if added later, and `.gemini/rules/` are historical Antigravity context rather than authoritative Codex instructions.

## Repository map

- `src/phase_annotator/__main__.py`: `python -m phase_annotator` entry point.
- `src/phase_annotator/domain/`: pure-Python dataclasses, ontology, time conversion, and validation.
- `src/phase_annotator/config/`: packaged JSON ontology resources and resource-loading adapter.
- `src/phase_annotator/media/`: lightweight source descriptors, Qt metadata translation, and source comparison.
- `src/phase_annotator/storage/`: JSON serialization, atomic replacement, sidecar policy, validation, source decisions, and dirty-state coordination used by the GUI.
- `src/phase_annotator/ui/`: PySide6 main window, Qt Multimedia player, timeline, and segment cards.
- `tests/unit/`, `tests/integration/`: domain/storage tests plus lightweight Qt widget tests.
- `scripts/`: explicit local validation utilities; representative videos remain ignored.
- `docs/`: architecture, schema/workflow, decisions, status/backlog, testing, and learning notes.

## Architectural constraints

- Keep `domain/` free of PySide6 and storage/IO imports. Domain behavior must remain testable with ordinary pytest.
- Treat `AnnotationSession` as the in-memory aggregate and `AnnotationInterval` timestamps as milliseconds. Interval semantics are currently effectively half-open `[start_ms, end_ms)` because adjacent boundaries are accepted.
- Do not claim frame accuracy from the current FPS approximation. Keep FPS provenance and CFR/VFR knowledge explicit; VFR videos cannot be mapped reliably with the current helpers.
- Never hash source videos. Use the lightweight source descriptor documented for C5. Absolute paths are local session data and must not leak into research exports, logs, screenshots, or committed examples.
- C5 deliberately uses the packaged PySide6/Qt metadata APIs, not `ffprobe`. Never invoke a system executable from `PATH`; reconsidering a bundled probe belongs to future distribution work with explicit binary provenance, licensing, and platform testing.
- Preserve session metadata and schema compatibility. Never silently discard unknown or existing annotation data during migrations.
- C6 requires the canonical annotation to be `<video filename>.phase-annotations.json` beside the video and to save automatically after successful annotation mutations. Session writes must remain same-directory temporary writes followed by `os.replace`. Do not add routine Save/Save As or a second autosave/recovery artifact without revisiting ADR 010.
- C9.7 deliberately keeps this one sidecar procedure-neutral. If its persisted ontology differs from the selected procedure, block loading, name both procedures, and preserve the file unchanged; do not create procedure-specific parallel sidecars.
- C7 supports sequential identifiable annotators, not simultaneous collaborative editing. One identity is confirmed on every launch and remains fixed for that run. Keep application identity, persisted mutation attribution, shared resume position, canonical dirty state, and changed-since-video-open state distinct. Historical snapshots are local recovery/trail artifacts, not a regulated or tamper-proof audit log.
- Do not add patient-identifying information to source control, fixtures, logs, screenshots, or example session files. Use synthetic identifiers and metadata.
- Do not treat the unused `ui/table_widget.py` duplicate as the active UI; `MainWindow` imports `SegmentListWidget` from `ui/segment_list_widget.py`.

## Development workflow

Use Python 3.10 or newer. From a virtual environment:

```powershell
python -m pip install -e ".[dev]"
python -m ruff format src tests scripts --check
python -m ruff check src tests scripts
python -m mypy
$env:QT_QPA_PLATFORM = "offscreen"
python -m pytest -v tests
python -m compileall -q src tests
python -m phase_annotator
```

Ruff formatting/linting and scoped Mypy checks are configured. Mypy currently gates `config/`, `domain/`, `media/`, and `storage/`, not `ui/`; do not imply whole-application type coverage.

The Windows packaging recipe is `PhaseAnnotator.spec`; `scripts/build_windows.ps1` uses `.release-venv` by default and verifies the executable plus both ontology resources. The approved local release environment is standard 64-bit CPython 3.13, not the Miniconda-derived development `.venv`. `.github/workflows/windows-ci.yml` defines source validation on pushes/pull requests and a manually dispatched packaging artifact; do not call C10.5 complete until both jobs run green remotely. No coverage threshold is configured.

Before changing behavior:

1. Read the relevant implementation and tests, not only the backlog or historical docs.
2. Check `git status --short` and preserve unrelated user changes.
3. Reconcile the requested behavior with `docs/CURRENT_STATE.md` and update that document if the implementation status changes.
4. Add tests first where practical, especially for domain rules and persistence failure cases.
5. Run the narrow tests while iterating and the complete suite before handoff. Report environment blockers explicitly.

Keep changes small and explain non-obvious Qt signal flow or domain decisions. This is also a learning project: whenever the user learns or asks about an important reusable software-engineering concept, help capture the explanation concisely in `docs/LEARNING_JOURNAL.md`; do not wait only for milestone completion. Leave the code understandable for a developer to inspect, and avoid filling the journal with routine or project-specific trivia.

Codex owns and completes the core implementation as the senior engineering partner. At each milestone, explain the design, give the user time to inspect it, and offer one small focused exercise that reinforces the concept without transferring responsibility for core delivery. Follow the milestone loop and quality gates in `docs/ROADMAP.md`.

## Collaboration style

Default to **learning mode** for architecture, annotation semantics, data integrity, and important UI behavior. Work in small vertical slices: agree on observable behavior, implement with tests, run full validation, give the user a focused manual check and short reading map, answer their questions, then commit/push after acceptance. Identify the one central concept and at most a few important functions; explicitly say which styling, boilerplate, or repetitive test code can be skimmed. Also call out a small number of genuinely useful Python or software-engineering idioms present in the slice (for example factories, lazy generator expressions, closure binding, derived properties, or transactional updates), explain why they fit, and capture reusable ones in `docs/LEARNING_JOURNAL.md`. Prefer teach-back on real project code over assigning artificial coding exercises.

Use **delivery mode** when the user says the outcome matters more than studying the implementation. In that mode Codex may complete a broader coherent scope autonomously, but must still surface product decisions, data-integrity risks, validation evidence, and user-visible acceptance checks. Use deep review only when requested or when a high-risk design needs joint attention. Review effort should be risk-based: spend more time on domain mutations, validation, persistence, recovery, undo/redo, completion, and export than on layouts or mechanical code.

Keep product semantics, architecture, and implementation questions distinct and resolve them in that order. Do not make a commit merely because tests pass: for user-visible slices, allow manual review first unless the user explicitly asks to commit immediately.

When a substantial milestone is divided into named sub-slices, create one focused document under `docs/` that records their interaction contract, data-integrity rules, status, tests, and learning-mode reading map; link it from `ROADMAP.md` rather than overloading `AGENTS.md` with implementation detail.

## Annotation-data expectations

Validate data at boundaries rather than trusting UI state. At minimum, persistence work must enforce known phase IDs, non-negative ordered timestamps, video-duration bounds, non-overlap, and continuous coverage before loading/saving. Avoid mutating an existing valid interval until a proposed transition has been validated. Continuous saving and loading require tests covering round trips, source decisions, write failures, and dirty-state behavior. JSON is canonical; CSV is deferred until a real consumer requires it.

Do not redesign the ontology or persisted schema casually. The six-phase ontology is provisional and phase 2 is optional; schema or ontology changes need a documented decision and migration/compatibility plan.

Treat phase IDs, expected order, hotkeys, `initial_phase_id`, and `undefined_phase_id` as distinct configured concepts. See `docs/ONTOLOGY_CONFIGURATION.md`; do not reintroduce hard-coded phase metadata into UI handlers.

Keep procedure/resource selection at the application composition root (`__main__.py` or a future startup/settings controller). Inject `PhaseOntology` into `MainWindow` and annotation views; reusable UI/domain components must not call appendectomy-specific loaders.
