# Architecture Overview

The implemented application is a small three-package desktop prototype. It follows the intended dependency direction at the domain boundary, but it does not yet have the documented presenter/controller layer.

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

- `models.py`: `VideoInfo`, `AnnotationInterval`, and `AnnotationSession` dataclasses.
- `ontology.py`: `Phase` and the code-defined provisional six-phase ontology.
- `validation.py`: opt-in overlap detection only; it does not enforce gaps, bounds, or phase IDs.
- `time_utils.py`: constant-FPS timestamp/frame arithmetic and timecode formatting.

The domain package currently has no Qt or IO imports. Preserve that boundary.

### Storage (`src/phase_annotator/storage/`)

- `json_repo.py`: direct dataclass-to-JSON serialization and loading. Save writes a same-directory temporary file and atomically replaces the destination.

There is no repository interface, GUI integration, CSV exporter, autosave, backup, migration layer, or recovery coordinator yet.

### UI (`src/phase_annotator/ui/`)

- `main_window.py`: constructs the window and controls, owns session state, connects signals, and performs phase-transition mutation.
- `player_widget.py`: wraps `QMediaPlayer`, `QAudioOutput`, and `QVideoWidget`.
- `timeline_widget.py`: paints phase intervals and a playhead; mouse clicks emit seek timestamps.
- `segment_list_widget.py`: active `QListWidget`-based custom segment cards.
- `table_widget.py`: unused duplicate/experimental M3 implementation; despite its name, it also uses a list rather than a table.

See `ANNOTATION_WORKFLOW.md`, `DATA_MODEL.md`, and `CURRENT_STATE.md` for behavior and limitations.
