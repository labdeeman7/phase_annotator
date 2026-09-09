# Current State and Handover

Last verified on 2026-09-09 against the post-C5 documentation cleanup based on `main` at `e5fd3b9`.

## What Phase Annotator currently does

Milliseconds remain authoritative internally and lead the main time display. Frame labels and segment cards stay compact; one time-label tooltip carries the timestamp-derived-frame caveat while FPS provenance remains internal.

The application starts a PySide6 desktop window, lets the user choose a local video, and delegates playback to Qt Multimedia. The user can play/pause with a state-aware button, seek with a slider or timeline, click a segment card to select it and seek to its start, and step by an approximate frame duration. Timeline and list selection are synchronized. Selected segments use a cyan outline, while the independently playhead-active segment uses white; slider seeking preserves selection. The status bar reports Loading/Loaded state. An always-visible configured phase palette shows each color, name, hotkey, and optional status. Clicking a phase or pressing its configured hotkey, including `U`, records the same validated transition and refreshes the palette, colored timeline, and segment-card list.

The segment-card action menu is available through right-click and a discoverable **⋮** button. **Edit note...** opens a modal Save/Cancel dialog, and cards with notes show a compact indicator and full-note tooltip. **Change phase** exposes every configured ontology phase and relabels the complete selected segment. Relabeling preserves notes, coalesces equal neighbours, and keeps the resulting interval selected. **Set start to playhead** and **Set end to playhead** move the appropriate shared boundary atomically while preserving positive adjacent durations. **Remove / merge** offers Convert to Undefined, Merge left, and Merge right; unavailable directions are disabled and closing the menu cancels. Visible Undo/Redo buttons and `Ctrl+Z`, `Ctrl+Shift+Z`, and `Ctrl+Y` restore validated interval snapshots for every annotation mutation. Internal timeline boundaries have subtle handles, an emphasized cyan hover state, a resize cursor, and deterministic nearest-boundary hit testing. Dragging a handle seeks and previews without mutating data; one valid release creates one history command, while invalid/Escape cancellation restores the original playhead. The earlier permanent inspector prototype was rejected and removed because notes are infrequent and should not consume persistent sidebar space.

The pure-Python layer provides Undefined plus the six provisional appendectomy phases, session/video/interval dataclasses, millisecond/frame formatting helpers, coverage/overlap validation, and JSON round-trip persistence through a stateless repository. C5.1 extends new sessions to schema 1.1 with optional lightweight media descriptors and explicit FPS provenance/frame-rate knowledge; schema 1.0 JSON remains loadable. C5.2 adds a neutral media-result/failure contract, cheap filesystem probing, and a Qt adapter for late duration, resolution, and reported-FPS metadata. C5.3 adds explainable match/mismatch/unknown source comparison without hashing.

Codex milestone C0 adds a pure-Python transactional `AnnotationEditor`. It initializes full-video coverage and safely applies playhead transitions using half-open intervals, validation, same-class no-ops, backward-local splitting, and adjacent-label coalescing. `MainWindow` now uses it and refreshes the timeline and segment list from the same normalized session state.

Codex milestone C1 replaces hard-coded ontology construction with a validated packaged JSON configuration. The default explicitly uses Phase 1 as its provisional initial phase, orders phases 1-6 as expected clinical guidance, places Undefined (`U`) last, and records ontology identity/version in sessions.

## What is only partial or unsafe

- Annotation state exists only in `MainWindow._session`; opening another video replaces it without a dirty-state warning.
- The UI never calls `JsonSessionRepository`. There is no manual save, session-open flow, autosave, crash recovery, or close protection.
- `MainWindow` still combines view construction and presenter/controller coordination; a dedicated presenter has not been extracted.
- C3 and C4 are complete, with the user-visible correction, dragging, and undo/redo workflows manually accepted. History is not persisted across application or video loads.
- The GUI begins with 30.0 FPS explicitly marked `assumed`, then adopts a positive FPS reported by Qt and labels its source `qt`. File size/modification time and available Qt duration/resolution are populated. Qt does not establish CFR/VFR status, so frame stepping remains estimated millisecond seeking rather than decoder-accurate navigation.
- Missing/unreadable files fail before backend loading. Qt resource, format/codec, network, and permission errors produce actionable status-bar messages and disable playback, seeking, and annotation controls for that failed load.
- New GUI sessions record the absolute last-known source path as well as the basename. The C5.3 comparison engine exists, but session loading and relocation do not yet call it. Video hashing is intentionally prohibited for this project.
- JSON saving uses a same-directory dot-prefixed temporary file and `os.replace`, but does not fsync, clean stale temp files, lock concurrent writers, validate schema, or create the `.bak` backup claimed by historical rules.
- GUI tests cover transition, selection, correction menus, notes, relabeling, boundary edits, removal/merge, undo/redo, dragging, timing presentation, media metadata, errors, and focus protection. They do not yet cover save/recovery, packaged cross-platform playback, or a complete persisted GUI workflow.

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
- Package metadata, `phase_annotator.__version__`, and the window title now consistently report `0.1.0`; release versioning remains manual.
- Historical docs described Clean Architecture/MVP and a storage/export layer more fully than implemented. There is no presenter, repository interface, or CSV adapter yet.
- Several imports are unused, and no lint/type-check configuration exists to catch them.

## Git evolution and latest Antigravity work

Antigravity established the original M0-M3 foundation:

1. M0 created the layout, documentation contracts, and `.gemini/rules/`.
2. M1 added models, ontology, overlap validation, atomic JSON persistence, and tests.
3. Documentation added the learning journal/backlog.
4. M2 added the PySide6/Qt Multimedia shell and time utilities.
5. M3 (`141d6df`, 2026-08-10) added the painted timeline, segment-card list, colored ontology, splitter layout, click-to-seek wiring, and keyboard transitions/frame controls.

Codex then stabilized and extended the application through C0-C5. The historical M4 persistence proposal has been superseded by the more explicit C6 session lifecycle and C7 recovery milestones.

## Validation baseline

On 2026-09-09, the repository-local Python 3.11.5 environment passed all 142 tests with PySide6/Qt 6.11.1, pytest 9.1.1, and pytest-qt 4.5.0. `python -m compileall -q src tests` and `git diff --check` also passed. An earlier offscreen smoke test loaded the local ignored representative H.264/AAC MP4, obtained a positive duration, initialized exactly one Phase 1 interval over the full duration, stored `laparoscopic_appendectomy.default@1.0`, showed Loaded status, and reported no media errors. This verifies the current machine/backend, not every deployment codec or platform. No project lint or type-check command is configured.

## Recommended next increment

Begin C6 manual session save, load, and dirty-state safety. Improving status-bar errors into prominent top-of-window notifications remains deferred to the beautification backlog.
