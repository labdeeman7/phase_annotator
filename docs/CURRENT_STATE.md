# Current State and Handover

Last verified on 2026-09-02 against `main` at `ee06e96` plus the current C0-C2 worktree.

## What the application currently does

The application starts a PySide6 desktop window, lets the user choose a local video, and delegates playback to Qt Multimedia. The user can play/pause with a state-aware button, seek with a slider or timeline, click a segment card to seek, and step by an approximate frame duration. The status bar reports Loading/Loaded state. An always-visible configured phase palette shows each color, name, hotkey, and optional status. Clicking a phase or pressing its configured hotkey, including `U`, records the same validated transition and refreshes the palette, colored timeline, and segment-card list.

The pure-Python layer provides Undefined plus the six provisional appendectomy phases, session/video/interval dataclasses, millisecond/frame formatting helpers, coverage/overlap validation, and JSON round-trip persistence through a stateless repository.

Codex milestone C0 adds a pure-Python transactional `AnnotationEditor`. It initializes full-video coverage and safely applies playhead transitions using half-open intervals, validation, same-class no-ops, backward-local splitting, and adjacent-label coalescing. `MainWindow` now uses it and refreshes the timeline and segment list from the same normalized session state.

Codex milestone C1 replaces hard-coded ontology construction with a validated packaged JSON configuration. The default explicitly uses Phase 1 as its provisional initial phase, orders phases 1-6 as expected clinical guidance, places Undefined (`U`) last, and records ontology identity/version in sessions.

## What is only partial or unsafe

- Annotation state exists only in `MainWindow._session`; opening another video replaces it without a dirty-state warning.
- The UI never calls `JsonSessionRepository`. There is no manual save, session-open flow, autosave, crash recovery, or close protection.
- `MainWindow` still combines view construction and presenter/controller coordination; a dedicated presenter has not been extracted.
- Selected-segment correction tools, delete/merge choices, boundary editing, and undo/redo are not implemented yet.
- FPS remains the hard-coded 30.0 default unless code sets it manually. No media metadata is extracted. Frame stepping is millisecond seeking, not decoder-accurate frame navigation.
- Only the video basename is stored as `video_id`; there is no path, hash, size, or other identity check for reconnecting sessions to source media.
- JSON saving uses a same-directory dot-prefixed temporary file and `os.replace`, but does not fsync, clean stale temp files, lock concurrent writers, validate schema, or create the `.bak` backup claimed by historical rules.
- GUI tests cover editor-backed forward/backward transitions, synchronized views, configured initial coverage, public player state, Play/Pause/Loading/Loaded feedback, mouse/hotkey equivalence, `U`, active-phase feedback, and focus protection for text entry and the segment list. They also verify that clicking the timeline restores annotation shortcuts. They do not yet cover correction tools, save/recovery, or a complete GUI workflow.

## Planned but absent

- Manual save (`Ctrl+S`), autosave, session loading, and crash recovery.
- Research CSV export. There is no `storage/export_csv.py`, despite older architecture documentation naming it.
- Distribution/installer work and Windows/Linux media-backend verification.
- Continuous integration.
- A real presenter/controller layer. `MainWindow` currently combines orchestration, session creation, and annotation mutations.
- User-configurable annotator identity and ontology/configuration loading.

## Technical debt and inconsistencies

- `ui/table_widget.py` is an unused near-duplicate of `ui/segment_list_widget.py`; both were added in M3, but only the latter is imported.
- `docs/DECISIONS.md` previously described a `QTableWidget`/`IntervalTableView`; the implementation uses custom cards in a `QListWidget`.
- The package metadata and `src/phase_annotator.__version__` say `0.1.0`, while the window title says `v0.2.0`.
- Historical docs described Clean Architecture/MVP and a storage/export layer more fully than implemented. There is no presenter, repository interface, or CSV adapter yet.
- Several imports are unused, and no lint/type-check configuration exists to catch them.

## Git evolution and latest Antigravity work

The six commits form a linear milestone history:

1. M0 created the layout, documentation contracts, and `.gemini/rules/`.
2. M1 added models, ontology, overlap validation, atomic JSON persistence, and tests.
3. Documentation added the learning journal/backlog.
4. M2 added the PySide6/Qt Multimedia shell and time utilities.
5. M3 (`141d6df`, 2026-08-10) added the painted timeline, segment-card list, colored ontology, splitter layout, click-to-seek wiring, and keyboard transitions/frame controls.

The stated next milestone was M4: manual saving, periodic autosave, crash recovery, and a learning exercise. No M4 implementation is present.

## Validation baseline

On 2026-09-03, the repository-local Python 3.11.5 environment passed all 53 tests with PySide6/Qt 6.11.1, pytest 9.1.1, and pytest-qt 4.5.0. `python -m compileall -q src tests` also passed. An offscreen smoke test loaded the local ignored representative H.264/AAC MP4, obtained a positive duration, initialized exactly one Phase 1 interval over the full duration, stored `laparoscopic_appendectomy.default@1.0`, showed Loaded status, and reported no media errors. This verifies the current machine/backend, not every deployment codec or platform. No project lint or type-check command is configured.

## Recommended next increment

Begin C3: add an explicit selected-segment editing context and synchronize selection/navigation across the timeline and segment list before adding precise correction operations.
