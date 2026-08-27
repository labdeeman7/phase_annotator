# Current State and Handover

Last verified against commit `141d6df` on 2026-08-13. The worktree was clean before this documentation pass.

## What the application currently does

The application starts a PySide6 desktop window, lets the user choose a local video, and delegates playback to Qt Multimedia. The user can play/pause, seek with a slider or timeline, click a segment card to seek, and step by an approximate frame duration. Pressing `1` through `6` records a phase transition in the in-memory session and refreshes a colored timeline and segment-card list.

The pure-Python layer provides the six-phase provisional appendectomy ontology, session/video/interval dataclasses, millisecond/frame formatting helpers, overlap detection, and JSON round-trip persistence through a stateless repository.

The first Codex C0 slice adds a pure-Python transactional `AnnotationEditor`. It initializes full-video Undefined coverage and safely applies playhead transitions using half-open intervals, validation, same-class no-ops, backward-local splitting, and adjacent-label coalescing. It is tested but not yet connected to `MainWindow`.

## What is only partial or unsafe

- Annotation state exists only in `MainWindow._session`; opening another video replaces it without a dirty-state warning.
- The UI never calls `JsonSessionRepository`. There is no manual save, session-open flow, autosave, crash recovery, or close protection.
- `record_phase_transition()` still directly reaches into `VideoPlayerWidget._player` and uses the inherited unsafe mutation path. The tested `AnnotationEditor` exists to replace it in the next C0 slice but is not yet wired to the GUI.
- The first recorded interval starts at the current playhead, so video time before it is an implicit gap. Every newly created interval initially extends to the video end; the last interval is therefore provisional.
- Phase IDs are not validated by `AnnotationSession.add_interval()`, intervals are not checked against video duration, and overlap validation is opt-in rather than enforced.
- FPS remains the hard-coded 30.0 default unless code sets it manually. No media metadata is extracted. Frame stepping is millisecond seeking, not decoder-accurate frame navigation.
- Only the video basename is stored as `video_id`; there is no path, hash, size, or other identity check for reconnecting sessions to source media.
- JSON saving uses a same-directory dot-prefixed temporary file and `os.replace`, but does not fsync, clean stale temp files, lock concurrent writers, validate schema, or create the `.bak` backup claimed by historical rules.
- GUI tests instantiate widgets and check simple state/population. They do not cover real media playback, hotkeys, transition edge cases, signal-based seeking, or a complete GUI workflow.

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
- `validation.py` retains a “TODO: implement” comment even though overlap detection is implemented.
- Several imports are unused, and no lint/type-check configuration exists to catch them.
- The README's installation example was Unix-only even though Windows is a target.

## Git evolution and latest Antigravity work

The six commits form a linear milestone history:

1. M0 created the layout, documentation contracts, and `.gemini/rules/`.
2. M1 added models, ontology, overlap validation, atomic JSON persistence, and tests.
3. Documentation added the learning journal/backlog.
4. M2 added the PySide6/Qt Multimedia shell and time utilities.
5. M3 (`141d6df`, 2026-08-10) added the painted timeline, segment-card list, colored ontology, splitter layout, click-to-seek wiring, and keyboard transitions/frame controls.

The stated next milestone was M4: manual saving, periodic autosave, crash recovery, and a learning exercise. No M4 implementation is present.

## Validation baseline

On 2026-08-14, the repository-local Python 3.11.5 environment passed all 31 tests with PySide6/Qt 6.11.1, pytest 9.1.1, and pytest-qt 4.5.0. `python -m compileall -q src tests` also passed. The earlier offscreen smoke test showed `MainWindow`, ran the Qt event loop for 1.5 seconds, and exited cleanly. Real video decoding and interactive playback with a representative file have not yet been verified. No project lint or type-check command is configured.

## Recommended next increment

First stabilize the annotation state transition boundary with tests: define transition/gap/end semantics, enforce ontology and duration invariants without partial mutation, and move orchestration out of direct access to private Qt player state. Then implement manual save/load with an explicit session path and dirty-state behavior. Autosave/recovery should build on that tested lifecycle; CSV export should follow only after the persisted schema and interval policy are settled.
