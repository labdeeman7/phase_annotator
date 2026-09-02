# Project Task Backlog & State Handover

The authoritative milestone sequence, completion definition, workflow, and quality gates are in `ROADMAP.md`. This file remains the concise checklist and historical milestone record.

## Completed Milestones

- [x] **Milestone 0: Engineering Foundation** (Repo layout, workspace rules, documentation contracts, Git setup)
- [x] **Milestone 1: Core Domain & Atomic Storage** (Phase ontology, session models, TDD validation, atomic JSON repo, integration suite)
- [x] **Milestone 2: Video Playback & PySide6 Shell** (Time/frame utils, PySide6 MainWindow, QMediaPlayer wrapper, GUI pytest-qt suite)
- [x] **Milestone 3: Phase Annotation UI & Interactive Timeline** (Custom painted timeline canvas, LosslessCut-style segment card list, keyboard hotkeys `1`-`6`, `Space`, `Left`/`Right`, click-to-seek synchronization)

## Handover status

Milestones below reflect historical intent. M3 is present as a prototype, but transition edge cases and end-to-end media behavior are not yet robust; see `CURRENT_STATE.md`.

## Completed Codex milestone: C0 — Annotation contract and safe transition engine

- [x] Specify transition, gap, final-interval, repeat, and ordering semantics
- [x] Add tests for invalid/same-time/backward transitions and avoid partial mutation
- [x] Enforce phase IDs, video bounds, and coverage policy in the transactional domain editor
- [x] Expose player position/duration without reaching into private Qt internals
- [x] Wire `MainWindow` transitions through `AnnotationEditor` and synchronize both views
- [x] Initialize full Undefined coverage when media duration becomes known
- [x] Add Play/Pause state and Loading/Loaded feedback

Media identity is deferred to C5, where media metadata and playback reliability are addressed. Configurable annotator identity belongs with the later session lifecycle rather than the transition engine.

Accepted rules: full timeline coverage, configurable expected initial phase, explicit Undefined (`U`), no gaps/overlaps, repeated/out-of-order phases allowed, Delete asks how to resolve the segment, and adjacent identical segments coalesce. Draft/completed status, resume position, and contiguous review progress are distinct persisted concepts.

## Completed Codex milestone: C1 — Configurable phase definitions and Undefined

- [x] Define and test a versioned JSON phase-configuration schema
- [x] Validate stable IDs, hotkeys, colors, expected ordering, initial/Undefined roles, and schema version
- [x] Package the default appendectomy configuration, including Undefined (`U`)
- [x] Load the default ontology from configuration rather than hard-coded phase objects
- [x] Record configuration identity/version in the session data model

## Completed Codex milestone: C2 — Visible mouse-and-keyboard phase palette

- [x] Add an always-visible palette above the right-side segment list
- [x] Render configured key, color, phase name, order, and optional status
- [x] Route configured hotkeys—including `U`—and mouse clicks through the same transition command
- [x] Show the phase active at the playhead and immediate transition feedback
- [x] Prevent annotation hotkeys from firing while typing in text-entry controls
- [x] Add accessibility labels/tooltips and GUI equivalence tests

Next: C3 selection/precise correction, then C4 draggable boundaries plus undo/redo. See `ROADMAP.md` for the complete C0-C10 sequence.

## Planned Milestone 4 — Session Saving, Loading, Autosave & Crash Recovery

- [ ] Manual Save (`Ctrl+S`) session action to atomic JSON repository
- [ ] Explicit session loading and dirty-state/replace-video protection
- [ ] Background periodic autosave timer
- [ ] Crash recovery prompt on startup
- [ ] Define and test backup, stale-temp, and persistence error behavior
- [ ] Student Hands-on Exercise (M4)

## Upcoming Milestones

- [ ] Milestone 5: Research CSV Export
- [ ] Milestone 6: Cross-Platform Windows Distribution
- [ ] Milestone 7: CI / GitHub Actions

## Known cleanup (do not confuse with feature work)

- [ ] Resolve unused duplicate `src/phase_annotator/ui/table_widget.py`
- [ ] Unify package/window version reporting
- [ ] Remove stale TODO and unused imports after confirming intended behavior
- [ ] Add a configured lint/format/type-check toolchain
