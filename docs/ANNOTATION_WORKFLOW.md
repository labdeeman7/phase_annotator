# Annotation and Video Workflow

## Current UI flow

1. `python -m phase_annotator` creates `QApplication` and `MainWindow`.
2. **Open Video** selects a local MP4/AVI/MKV/MOV file. `QMediaPlayer.setSource()` receives its local URL.
3. `MainWindow` creates a fresh in-memory `AnnotationSession` using the file basename, a hard-coded `surgeon_01` annotator, duration 0, and the player's default 30 FPS.
4. Qt's duration signal updates the slider, timeline duration, and `VideoInfo.duration_ms`.
5. Play/pause is available through the button or Space. Left/Right seek by `int(1000 / fps)` milliseconds. The slider and painted timeline seek in milliseconds.
6. Keys `1`-`6` call `record_phase_transition()`. The prior interval's end becomes the current position and a new interval begins there, provisionally ending at media duration.
7. Timeline blocks and segment cards are rebuilt from the session list. Clicking a card seeks to that interval's start.

There is currently no onscreen phase palette, selected-phase state, editing/deleting/notes UI, undo/redo, save/load, dirty-state indicator, error display, or export action.

## Qt ownership and signal flow

- `MainWindow` owns `VideoPlayerWidget`, `TimelineWidget`, and `SegmentListWidget`.
- `VideoPlayerWidget` wraps `QMediaPlayer`, `QAudioOutput`, and `QVideoWidget`, forwarding position and duration signals.
- Player position updates the slider (unless it is being dragged), timeline playhead, and time label.
- Timeline and segment-list `seek_requested(int)` signals connect directly to `VideoPlayerWidget.seek_ms()`.
- `MainWindow` currently accesses the player's private `_player` for position and duration. Prefer a public wrapper or controller boundary when this behavior is revised.

## Video accuracy limitations

Qt Multimedia chooses the platform media backend and codec support is environment-dependent. This repository contains no media probing, codec fallback, sample video, or playback integration test. FPS is assumed to be 30.0; source FPS, variable frame rate, time bases, keyframes, rotation, and stream errors are not handled. Consequently, displayed frame numbers and frame-step controls are estimates based on timestamps, not guaranteed decoded-frame indices.

Milliseconds are the authoritative annotation unit today. Do not derive a claim of VFR frame accuracy from `ms_to_frame()` or `frame_to_ms()`; both are simple constant-rate arithmetic.
