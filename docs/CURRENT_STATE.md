# Current State and Handover

Last verified on 2026-09-21 after implementation of C9, based on C8.7 commit `010441f`.

## What Phase Annotator currently does

Milliseconds remain authoritative internally and lead the main time display. Frame labels and segment cards stay compact; one time-label tooltip carries the timestamp-derived-frame caveat while FPS provenance remains internal.

The application starts a PySide6 desktop window, lets the user choose a local video, and delegates playback to Qt Multimedia. The user can play/pause with a state-aware button, seek with a slider or timeline, click a segment card to select it and seek to its start, and step by an approximate frame duration. Timeline and list selection are synchronized. Selected segments use a cyan outline, while the independently playhead-active segment uses white; slider seeking preserves selection. The status bar reports Loading/Loaded state. An always-visible configured phase palette shows each color, name, hotkey, and optional status. Clicking a phase or pressing its configured hotkey, including `U`, records the same validated transition and refreshes the palette, colored timeline, and segment-card list.

The segment-card action menu is available through right-click and a discoverable **⋮** button. **Edit note...** opens a modal Save/Cancel dialog, and cards with notes show a compact indicator and full-note tooltip. **Change phase** exposes every configured ontology phase and relabels the complete selected segment. Relabeling preserves notes, coalesces equal neighbours, and keeps the resulting interval selected. **Set start to playhead** and **Set end to playhead** move the appropriate shared boundary atomically while preserving positive adjacent durations. **Remove / merge** offers Convert to Undefined, Merge left, and Merge right; unavailable directions are disabled and closing the menu cancels. Visible Undo/Redo buttons and `Ctrl+Z`, `Ctrl+Shift+Z`, and `Ctrl+Y` restore validated interval snapshots for every annotation mutation. Internal timeline boundaries have subtle handles, an emphasized cyan hover state, a resize cursor, and deterministic nearest-boundary hit testing. Dragging a handle seeks and previews without mutating data; one valid release creates one history command, while invalid/Escape cancellation restores the original playhead. The earlier permanent inspector prototype was rejected and removed because notes are infrequent and should not consume persistent sidebar space.

The pure-Python layer provides Undefined plus the six provisional appendectomy phases, session/video/interval dataclasses, millisecond/frame formatting helpers, coverage/overlap validation, and JSON persistence. Schema 1.2 adds draft/completed lifecycle fields and a bounded resume checkpoint while retaining known legacy defaults. A persistence coordinator now owns deterministic adjacent-sidecar naming, validation, source decisions, and dirty state above the stateless atomic JSON repository. C5 supplies lightweight media probing and explainable match/mismatch/unknown source comparison without hashing.

C6 connects persistence to the GUI. Once duration is known, a new valid session is written to `<video filename>.phase-annotations.json`; every annotation mutation, undo, and redo saves immediately. Matching sidecars load automatically, unknown source evidence requires confirmation, and invalid or mismatching sidecars disable annotation. Resume is checkpointed on edits, pause, periodically during playback, and before clean close/replacement. A persistent `[UNSAVED]` title marker and retry/discard/cancel guard appear only when a write failure leaves memory ahead of disk.

C7 asks for an annotator ID on every launch, keeps it fixed across videos for that run, and shows it in the window title. Schema 1.3 introduced creator and last-editor attribution while preserving legacy `annotator_id`. Clean close or video replacement creates one atomic timestamped JSON snapshot in a per-video history directory only when annotation data changed; resume-only use creates none. Lightweight sidecar revision evidence blocks silent external overwrite.

C8 advances the persisted model to schema 1.4. It adds optional video-level `session_notes` and explicit `completed_by`, and enforces the lifecycle invariant that a completed session has both completion timestamp and completer while a draft has neither. Known older schemas load with compatible defaults. A compact **Annotation** menu edits the video note, validates and summarizes work before explicit completion, and safely reopens completed annotations. Completed work is navigable but every mutation is guarded; reopening verifies the canonical sidecar and archives the completed record before returning to Draft.

C8.7 pulls visual consistency forward from C9. `ui/theme.py` gives the application shell, menu, controls, dialogs, status bar, splitter, tooltips, and scrollbars one dark high-contrast workstation theme. Existing phase colors and selected/playhead distinctions remain intact.

C9 adds a dismissible high-visibility banner for actionable media/persistence failures, fixed playback rates of 1×, 2×, 4×, 8×, and 12×, ±5-second jumps, and a structured in-application shortcut reference. Delete converts the selected segment to Undefined through the existing undoable resolution command. A trial timeline zoom was removed after manual feedback because its multiplier controls were confused with playback speed. These controls do not alter annotation timestamps or schema data.

C9.6 exposes the generic ontology architecture at startup. After entering a lowercase first name, the annotator chooses packaged laparoscopic appendectomy or laparoscopic cholecystectomy. The selected procedure appears in the window title, drives all phase metadata, and remains protected by persisted ontology identity/version checks. The cholecystectomy JSON contains the supplied seven classes plus Undefined.

C9.7 retains one procedure-neutral canonical sidecar per video. If the operator selects a different procedure from the sidecar's stored ontology, loading is blocked with both friendly procedure names, confirmation that nothing changed, and an instruction to restart with the saved procedure. The application never silently creates a second wrong-procedure annotation.

Codex milestone C0 adds a pure-Python transactional `AnnotationEditor`. It initializes full-video coverage and safely applies playhead transitions using half-open intervals, validation, same-class no-ops, backward-local splitting, and adjacent-label coalescing. `MainWindow` now uses it and refreshes the timeline and segment list from the same normalized session state.

Codex milestone C1 replaces hard-coded ontology construction with a validated packaged JSON configuration. The default explicitly uses Phase 1 as its provisional initial phase, orders phases 1-6 as expected clinical guidance, places Undefined (`U`) last, and records ontology identity/version in sessions.

## What is only partial or unsafe

- Annotation state lives in `MainWindow._session` and is mirrored immediately to the canonical sidecar. History remains process-local and is not restored.
- Resume position is shared session convenience, not per-annotator progress or evidence of review.
- `MainWindow` still combines view construction and presenter/controller coordination; a dedicated presenter has not been extracted.
- C3 and C4 are complete, with the user-visible correction, dragging, and undo/redo workflows manually accepted. History is not persisted across application or video loads.
- The GUI begins with 30.0 FPS explicitly marked `assumed`, then adopts a positive FPS reported by Qt and labels its source `qt`. File size/modification time and available Qt duration/resolution are populated. Qt does not establish CFR/VFR status, so frame stepping remains estimated millisecond seeking rather than decoder-accurate navigation.
- Missing/unreadable files fail before backend loading. Qt resource, format/codec, network, and permission errors produce actionable banner messages and disable playback, seeking, and annotation controls for that failed load.
- New GUI sessions record the absolute last-known source path as well as the basename. The C5.3 comparison engine exists, but session loading and relocation do not yet call it. Video hashing is intentionally prohibited for this project.
- JSON saving uses a same-directory dot-prefixed temporary file and `os.replace`, with coordinator validation and visible dirty failure state. It does not fsync, clean stale temp files, lock concurrent writers, create backups, or support read-only source directories.
- GUI and coordinator tests cover initial save, immediate mutation/undo persistence, matching reload, source outcomes, invalid data, legacy defaults, and write-failure dirty retention. Packaged cross-platform playback and crash/concurrent-writer behavior remain untested.

## Planned but absent

- Distribution/installer work and Windows/Linux media-backend verification.
- Continuous integration.
- A real presenter/controller layer. `MainWindow` currently combines orchestration, session creation, and annotation mutations.
- User-configurable ontology/configuration loading.

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

Codex then stabilized and extended the application through C0-C7. The historical M4 persistence proposal has been superseded by C6 continuous sidecars and C7 sequential attribution/history.

## Validation baseline

On 2026-09-23, both the repository-local Miniconda-derived Python 3.11.5 development environment and the standard-CPython 3.13.15 release environment passed the configured checks. The current suite has 187 passing tests; Ruff lint/format, scoped Mypy over 16 configuration/domain/media/storage source files, compilation, and `git diff --check` pass. UI typing is not yet enforced. The CPython 3.13/PyInstaller 6.22.3 recipe produced a 242-file, 131.6 MiB one-folder artifact without the earlier Conda DLL warnings. Automated frozen-artifact checks loaded both ontologies and constructed both procedure windows. Manual disposable-media acceptance passed packaged decoding/playback, annotation/correction, Undo/Redo, persistence/resume, notes, completion/reopening, history, and mismatch protection. This verifies the current machine and representative media, not every target computer or codec.

## Recommended next increment

C10.1–C10.6 are complete. The release contract and staged plan are in `C10_RELEASE_ENGINEERING.md`; the quality baseline, clean standard-CPython build, automated artifact smoke test, manual packaged lifecycle acceptance, clean Windows CI/build-artifact workflow, and audience-specific documentation pass. On 2026-09-23, GitHub's Windows runner passed both the push validation and manually dispatched package/smoke-test/artifact-upload jobs. C10.7 is reduced to executing and recording `CLEAN_MACHINE_ACCEPTANCE.md` against the exact downloaded artifact on a clean Windows machine or VM. The larger Cholec80 extended-validation and clinical training/protocol work remains separate in `REAL_VIDEO_VALIDATION_AND_TRAINING_PLAN.md`.
