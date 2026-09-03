# Annotation and Video Workflow

## Current UI flow

1. `python -m phase_annotator` creates `QApplication` and `MainWindow`.
2. **Open Video** selects a local MP4/AVI/MKV/MOV file. `QMediaPlayer.setSource()` receives its local URL.
3. `MainWindow` creates a fresh in-memory `AnnotationSession` using the file basename, a hard-coded `surgeon_01` annotator, duration 0, and the player's default 30 FPS. The status bar shows **Loading**.
4. A positive Qt duration signal updates the slider/timeline/session, initializes one interval using the ontology's configured `initial_phase_id` (Phase 1 for appendectomy) over `[0, duration_ms)`, refreshes both annotation views, and changes status to **Loaded**.
5. Play/pause is available through the state-aware Play/Pause button or Space. Left/Right seek by `int(1000 / fps)` milliseconds. The slider and painted timeline seek in milliseconds.
6. The always-visible phase palette is built from the configured ontology. Clicking a phase or pressing its configured window shortcut (including `U`) calls the same `record_phase_transition()` method, which delegates interval changes to the transactional `AnnotationEditor`. Phase shortcuts are disabled while a text-entry control or the segment list has keyboard focus; clicking the timeline restores the normal annotation context.
7. The palette highlights the phase under the playhead. The timeline and segment cards are rebuilt from the same validated session interval sequence. A white outline identifies the segment under the playhead; a cyan outline identifies the explicitly selected segment. Single-clicking a card selects it and seeks to its start. Clicking within a timeline interval selects it and seeks to that position. Selection persists while the playback slider moves, but is cleared when a phase transition changes the interval structure.

There is currently no selected-segment editing/deleting/notes UI, undo/redo, save/load, dirty-state indicator, persistent error display, or export action.

## Qt ownership and signal flow

- `MainWindow` owns `VideoPlayerWidget`, `TimelineWidget`, `PhasePaletteWidget`, and `SegmentListWidget`.
- `VideoPlayerWidget` wraps `QMediaPlayer`, `QAudioOutput`, and `QVideoWidget`, forwarding position, duration, and simplified playing/not-playing signals. It exposes public `position_ms`, `duration_ms`, and `is_playing` properties.
- Player position updates the slider (unless it is being dragged), timeline playhead, and time label.
- Timeline and segment-list `seek_requested(int)` signals connect directly to `VideoPlayerWidget.seek_ms()`.
- `MainWindow` still performs presenter/controller coordination, but annotation mutation belongs to the pure-Python `AnnotationEditor`; it no longer reaches into the private Qt player for position or duration.

## Video accuracy limitations

Qt Multimedia chooses the platform media backend and codec support is environment-dependent. This repository contains no media probing, codec fallback, sample video, or playback integration test. FPS is assumed to be 30.0; source FPS, variable frame rate, time bases, keyframes, rotation, and stream errors are not handled. Consequently, displayed frame numbers and frame-step controls are estimates based on timestamps, not guaranteed decoded-frame indices.

Milliseconds are the authoritative annotation unit today. Do not derive a claim of VFR frame accuracy from `ms_to_frame()` or `frame_to_ms()`; both are simple constant-rate arithmetic.
