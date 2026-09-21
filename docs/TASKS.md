# Project Task Backlog & State Handover

The authoritative milestone sequence, completion definition, workflow, and quality gates are in `ROADMAP.md`. This file remains the concise checklist and historical milestone record.

## Completed Milestones

- [x] **Milestone 0: Engineering Foundation** (Repo layout, workspace rules, documentation contracts, Git setup)
- [x] **Milestone 1: Core Domain & Atomic Storage** (Phase ontology, session models, TDD validation, atomic JSON repo, integration suite)
- [x] **Milestone 2: Video Playback & PySide6 Shell** (Time/frame utils, PySide6 MainWindow, QMediaPlayer wrapper, GUI pytest-qt suite)
- [x] **Milestone 3: Phase Annotation UI & Interactive Timeline** (Custom painted timeline canvas, LosslessCut-style segment card list, keyboard hotkeys `1`-`6`, `Space`, `Left`/`Right`, click-to-seek synchronization)

## Handover status

The historical M0-M3 work was stabilized and extended through Codex milestones C0-C5. `ROADMAP.md` is authoritative for the current C0-C10 sequence; this file is only its concise checklist.

## Completed Codex milestone: C0 — Annotation contract and safe transition engine

- [x] Specify transition, gap, final-interval, repeat, and ordering semantics
- [x] Add tests for invalid/same-time/backward transitions and avoid partial mutation
- [x] Enforce phase IDs, video bounds, and coverage policy in the transactional domain editor
- [x] Expose player position/duration without reaching into private Qt internals
- [x] Wire `MainWindow` transitions through `AnnotationEditor` and synchronize both views
- [x] Initialize full coverage with the ontology's configured initial phase when media duration becomes known
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

## Completed Codex milestone: C3 — Selection and precise correction

**Status: completed and manually accepted on 2026-09-05.**

- [x] C3.1: synchronize segment selection between timeline and segment list
- [x] C3.1: distinguish selected (cyan) from playhead-active (white) segments
- [x] C3.1: preserve selection during slider seeking and clear it after structural edits
- [x] C3.1: remove the duplicate double-click seek connection
- [x] C3.2: replace the unaccepted permanent inspector prototype with a segment context menu, visible **⋮** action, modal note editor, and compact note indicator
- [x] C3.3: add explicit whole-segment relabeling
- [x] C3.4: add set-start/set-end-to-playhead correction commands
- [x] C3.5: add the Undefined/merge-left/merge-right/cancel removal flow

## Completed Codex milestone: C4 — Undo/redo and draggable boundaries

- [x] C4.1: add bounded snapshot history and validated Undo/Redo for every annotation mutation
- [x] C4.1: add visible controls plus safe `Ctrl+Z`, `Ctrl+Shift+Z`, and `Ctrl+Y` shortcuts
- [x] C4.2: add internal-boundary handles, hover feedback, and hit testing
- [x] C4.3: add transient drag preview, seek feedback, cancel, and one-command commit
- [x] C4.4: integrate drag history and complete synchronization/acceptance coverage

## Completed Codex milestone: C5 — Media metadata and playback reliability

- [x] C5.1: define versioned optional media metadata and lightweight source-descriptor fields
- [x] C5.2: implement Qt metadata adapter and defer `ffprobe` bundling
- [x] C5.3: implement explicit lightweight match/mismatch/unknown source comparison
- [x] C5.4: label frame timing honestly and propagate measured/assumed FPS
- [x] C5.5: surface actionable media/backend failures and disable invalid annotation state
- [x] C5.6: validate with synthetic and representative non-committed media

## Upcoming Milestones

- [x] C6.1: persist continuous-sidecar, dirty-state, loading, resume, and schema contract
- [x] C6.2: add backward-compatible lifecycle/resume fields and persistence coordinator
- [x] C6.3: automatically create and save new-session sidecars
- [x] C6.4: automatically validate, source-check, and load existing sidecars
- [x] C6.5: persist and restore bounded resume checkpoints
- [x] C6.6: guard dirty close/replacement; retain sidecar-only storage until evidence justifies a fallback
- [x] C6.7: complete persistence failure and round-trip validation
- [x] C7.1: add backward-compatible creator/last-editor attribution
- [x] C7.2: require one annotator identity per application launch
- [x] C7.3: create one history snapshot per changed video run
- [x] C7.4: detect external canonical-sidecar changes before overwrite
- [x] C7.5: validate migration, failure, collision, and sequential-user behavior
- [x] C8.1: add schema 1.4 general-note and completion-attribution fields
- [x] C8.2: add optional modal general video-note editing
- [x] C8.3: implement completion validation and Undefined summary
- [x] C8.4: persist explicit completion with current annotator and timestamp
- [x] C8.5: archive completed state before deliberate reopening/editing
- [x] C8.6: validate lifecycle migration, failures, GUI, and automated workflow (manual acceptance pending)
- [x] C8.7: unify the application shell and controls with a high-contrast dark workstation theme
- [x] C9.1: add prominent dismissible error/warning notifications
- [x] C9.2: add playback speed and five-second navigation controls
- [x] C9.3: add an in-application shortcuts/workflow reference
- [x] C9.4: add presentation-only timeline zoom and horizontal navigation
- [x] C9.5: run automated usability acceptance (representative manual acceptance pending)
- [ ] C10: Packaging, documentation, and release readiness

## Known cleanup (do not confuse with feature work)

- [ ] Resolve unused duplicate `src/phase_annotator/ui/table_widget.py`
- [x] Unify package/window version reporting
- [ ] Remove stale TODO and unused imports after confirming intended behavior
- [ ] Add a configured lint/format/type-check toolchain

## Beautification and UI polish (later)

- [x] Replace the mixed default-light/custom-dark appearance with one coherent application theme.
- [x] Replace status-bar-only critical failures with a prominent, non-blocking notification banner near the top of the window.
- [x] Keep routine playback, loading, save, and successful-action feedback in the status bar rather than treating every message as an error.
- [x] Define consistent error, warning, and informational banner colors, dismissal, and accessibility behavior.
