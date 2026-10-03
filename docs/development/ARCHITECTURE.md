# Architecture Overview

The implemented application is a small layered desktop prototype. It follows the intended dependency direction at the domain boundary, but it does not yet have a dedicated presenter/controller layer.

```text
__main__.py
    └── MainWindow (UI orchestration + in-memory session state)
        ├── VideoPlayerWidget ── Qt Multimedia
        ├── TimelineWidget ───── domain intervals + ontology
        ├── SegmentListWidget ── domain intervals + ontology
        └── domain models/time helpers

JsonSessionRepository ────────── domain models (not connected to MainWindow)
```

## Components

### Domain (`src/phase_annotator/domain/`)

- `models.py`: `VideoInfo`, `AnnotationInterval`, and `AnnotationSession` dataclasses. `VideoInfo` separates optional media values from their provenance and records a lightweight, non-cryptographic source descriptor.
- `ontology.py`: generic `Phase`/`PhaseOntology` models and validation from decoded configuration.
- `validation.py`: overlap detection and ordered, contiguous full-coverage validation. `AnnotationEditor` additionally enforces configured phase IDs and playhead bounds.
- `time_utils.py`: constant-FPS timestamp/frame arithmetic and timecode formatting.
- `annotation_editor.py`: transactional full-coverage initialization and phase-transition editing, including validation and adjacent-label coalescing.

The domain package currently has no Qt or IO imports. Preserve that boundary.

### Configuration (`src/phase_annotator/config/`)

- `default_appendectomy.json` and `cholec80_cholecystectomy.json`: versioned bundled ontologies with expected order, hotkeys, colors, and explicit initial/Undefined roles.
- `__init__.py`: generic packaged-resource/path JSON adapters that pass decoded data to the pure `PhaseOntology.from_config()` validator.

`__main__.py` is the composition root: it asks for a packaged procedure, loads its registry-selected ontology, and injects one instance into `MainWindow`, which passes that same instance to the annotation views and phase palette. UI components depend on `PhaseOntology`, not on procedure-specific loader names or resources.

The `PhasePaletteWidget` renders the configured phase order, names, colors, hotkeys, and optional flags. It emits only a phase ID. `MainWindow` routes that signal and configured window-scoped `QShortcut` objects through the same `record_phase_transition()` command, then derives the active palette selection from the interval under the playhead. Shortcut availability follows keyboard focus: text inputs and the segment list reserve their keys, while clicking the focusable timeline returns to annotation mode.

`MainWindow` also owns transient selected-segment state as an interval index and synchronizes it into `TimelineWidget` and `SegmentListWidget`. Playhead-active state is independently derived from session intervals and the current position. Because indexes can change meaning when an edit splits or coalesces intervals, playhead transitions clear selection rather than risking selection of the wrong segment. Segment-card context-menu actions route through `MainWindow`, while the modal note dialog owns its temporary draft until Save or Cancel.

### Storage (`src/phase_annotator/storage/`)

- `json_repo.py`: direct dataclass-to-JSON serialization and loading. Save writes a same-directory temporary file and atomically replaces the destination.
- `session_persistence.py`: deterministic sidecar/history naming, load validation, C5 source-comparison decisions, saved/dirty/changed-session state, atomic snapshots, and optimistic external-change detection.

`MainWindow` uses the coordinator to create/load `<video filename>.phase-annotations.json`, save every annotation command, checkpoint resume position, and create one history snapshot when a changed video is closed or replaced. External revision evidence blocks silent overwrite. There is no automatic merge, OS file lock, general migration framework, or alternate read-only-directory location. CSV is not required by the current roadmap.

### Media (`src/phase_annotator/media/`)

- `metadata.py`: frozen toolkit-neutral metadata/failure results and cheap filesystem descriptor probing.
- `qt_metadata.py`: translates backend-dependent Qt metadata without claiming CFR/VFR knowledge.
- `matching.py`: produces explainable source match/mismatch/unknown evidence without treating the path as content identity.

The media layer never hashes video contents or searches `PATH` for external executables. `VideoPlayerWidget` emits translated snapshots, and `MainWindow` applies them only when their source still matches the current video.

### UI (`src/phase_annotator/ui/`)

- `main_window.py`: constructs the window and controls, owns session/selection state, delegates annotation mutation to `AnnotationEditor`, and refreshes the synchronized views.
- `annotator_identity.py`: asks for one first name per launch and normalizes it to lowercase for attribution; no identity is remembered between launches.
- `domain/annotation_history.py`: Qt-free bounded command history. It captures isolated before/after interval snapshots around successful mutations and restores them through `AnnotationEditor` validation.
- `player_widget.py`: wraps `QMediaPlayer`, `QAudioOutput`, and `QVideoWidget`.
- `timeline_widget.py`: paints phase intervals, selection, playhead, internal-boundary handles, and transient drag preview; it emits preview seek, commit, and cancellation intent but never mutates the annotation session.
- `segment_list_widget.py`: active `QListWidget`-based custom segment cards and combined selection/seek requests.
- `segment_note_dialog.py`: modal editor for one optional segment note; it exposes the accepted text but does not mutate the session.
- `table_widget.py`: unused duplicate/experimental M3 implementation; despite its name, it also uses a list rather than a table.

See `ANNOTATION_WORKFLOW.md`, `DATA_MODEL.md`, and `CURRENT_STATE.md` for behavior and limitations.
