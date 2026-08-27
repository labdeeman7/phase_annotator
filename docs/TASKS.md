# Project Task Backlog & State Handover

The authoritative milestone sequence, completion definition, workflow, and quality gates are in `ROADMAP.md`. This file remains the concise checklist and historical milestone record.

## Completed Milestones

- [x] **Milestone 0: Engineering Foundation** (Repo layout, workspace rules, documentation contracts, Git setup)
- [x] **Milestone 1: Core Domain & Atomic Storage** (Phase ontology, session models, TDD validation, atomic JSON repo, integration suite)
- [x] **Milestone 2: Video Playback & PySide6 Shell** (Time/frame utils, PySide6 MainWindow, QMediaPlayer wrapper, GUI pytest-qt suite)
- [x] **Milestone 3: Phase Annotation UI & Interactive Timeline** (Custom painted timeline canvas, LosslessCut-style segment card list, keyboard hotkeys `1`-`6`, `Space`, `Left`/`Right`, click-to-seek synchronization)

## Handover status

Milestones below reflect historical intent. M3 is present as a prototype, but transition edge cases and end-to-end media behavior are not yet robust; see `CURRENT_STATE.md`.

## Active Codex milestone: C0 — Annotation contract and safe transition engine

- [x] Specify transition, gap, final-interval, repeat, and ordering semantics
- [x] Add tests for invalid/same-time/backward transitions and avoid partial mutation
- [x] Enforce phase IDs, video bounds, and coverage policy in the transactional domain editor
- [ ] Expose player position/duration without reaching into private Qt internals
- [ ] Decide media identity and annotator configuration

Accepted rules: full timeline coverage, explicit Undefined (`U`), no gaps/overlaps, repeated/out-of-order phases allowed, Delete converts to Undefined, explicit Merge Left/Right, and adjacent identical segments coalesce.

Next: C1 configurable phase definitions/Undefined, C2 visible mouse-and-keyboard phase palette, C3 selection/precise correction, and C4 draggable boundaries plus undo/redo. See `ROADMAP.md` for the complete C0-C10 sequence.

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
