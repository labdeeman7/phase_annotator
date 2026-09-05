# Codex Project Guide

## Purpose and current maturity

This repository is a desktop tool for producing temporal surgical-phase annotations for laparoscopic appendectomy videos. It is an early prototype currently progressing through Codex milestone C3, not yet a production annotation system: playback, in-memory annotation, configurable mouse/hotkey phase selection, and synchronized segment navigation exist, while correction tools, UI-integrated saving, recovery, export, and distribution do not.

Start with `docs/CURRENT_STATE.md` and `docs/ROADMAP.md`, then use `docs/ARCHITECTURE.md`, `docs/ANNOTATION_WORKFLOW.md`, and `docs/DATA_MODEL.md` for deeper context. While C3 is active, use `docs/C3_CORRECTION_WORKFLOW.md` as its detailed interaction and data-integrity contract. `GEMINI.md`, if added later, and `.gemini/rules/` are historical Antigravity context rather than authoritative Codex instructions.

## Repository map

- `src/phase_annotator/__main__.py`: `python -m phase_annotator` entry point.
- `src/phase_annotator/domain/`: pure-Python dataclasses, ontology, time conversion, and validation.
- `src/phase_annotator/config/`: packaged JSON ontology resources and resource-loading adapter.
- `src/phase_annotator/storage/`: JSON serialization and atomic replacement. It is not wired into the GUI yet.
- `src/phase_annotator/ui/`: PySide6 main window, Qt Multimedia player, timeline, and segment cards.
- `tests/unit/`, `tests/integration/`: domain/storage tests plus lightweight Qt widget tests.
- `docs/`: architecture, schema/workflow, decisions, status/backlog, testing, and learning notes.

## Architectural constraints

- Keep `domain/` free of PySide6 and storage/IO imports. Domain behavior must remain testable with ordinary pytest.
- Treat `AnnotationSession` as the in-memory aggregate and `AnnotationInterval` timestamps as milliseconds. Interval semantics are currently effectively half-open `[start_ms, end_ms)` because adjacent boundaries are accepted.
- Do not claim frame accuracy from the current FPS approximation. The player defaults to 30 FPS and does not inspect source metadata; VFR videos cannot be mapped reliably with the current helpers.
- Preserve session metadata and schema compatibility. Never silently discard unknown or existing annotation data during migrations.
- Session writes must remain same-directory temporary writes followed by `os.replace`. Before promising backup/recovery behavior, implement and test it; current code does not create `.bak` files.
- Do not add patient-identifying information to source control, fixtures, logs, screenshots, or example session files. Use synthetic identifiers and metadata.
- Do not treat the unused `ui/table_widget.py` duplicate as the active UI; `MainWindow` imports `SegmentListWidget` from `ui/segment_list_widget.py`.

## Development workflow

Use Python 3.10 or newer. From a virtual environment:

```powershell
python -m pip install -e ".[dev]"
$env:QT_QPA_PLATFORM = "offscreen"
python -m pytest -v tests
python -m compileall -q src tests
python -m phase_annotator
```

No linter, formatter, type checker, coverage threshold, CI workflow, or packaging script is currently configured. Do not invent a validation claim for tools the repository has not configured.

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

Validate data at boundaries rather than trusting UI state. At minimum, future work should enforce known phase IDs, non-negative ordered timestamps, video-duration bounds, non-overlap, and an explicit gap policy before saving/exporting. Avoid mutating an existing valid interval until a proposed transition has been validated. Saving, autosaving, loading, crash recovery, and CSV export require tests covering round trips and failure behavior.

Do not redesign the ontology or persisted schema casually. The six-phase ontology is provisional and phase 2 is optional; schema or ontology changes need a documented decision and migration/compatibility plan.

Treat phase IDs, expected order, hotkeys, `initial_phase_id`, and `undefined_phase_id` as distinct configured concepts. See `docs/ONTOLOGY_CONFIGURATION.md`; do not reintroduce hard-coded phase metadata into UI handlers.

Keep procedure/resource selection at the application composition root (`__main__.py` or a future startup/settings controller). Inject `PhaseOntology` into `MainWindow` and annotation views; reusable UI/domain components must not call appendectomy-specific loaders.
