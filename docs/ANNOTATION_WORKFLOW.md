# Annotation and Video Workflow

## Current UI flow

1. `python -m phase_annotator` creates `QApplication`, asks for a first name, then asks for packaged laparoscopic appendectomy or laparoscopic cholecystectomy. Cancelling either prompt exits. The lowercase identity and selected procedure are fixed for that launch and shown unobtrusively in the window title.
2. **Open Video** selects a local MP4/AVI/MKV/MOV file. `QMediaPlayer.setSource()` receives its local URL.
   If its canonical sidecar belongs to the other procedure, annotation is blocked, both procedures are named, and the operator is told to restart with the saved procedure. The JSON is not changed and no second sidecar is created.
3. `MainWindow` creates a fresh in-memory `AnnotationSession` using the file basename, resolved absolute last-known path, confirmed active annotator, duration 0, and the player's 30 FPS value explicitly marked as assumed with unknown CFR/VFR status. Existing valid sidecars retain creator/last-editor attribution. The status bar shows **Loading**.
4. A positive Qt duration signal updates the slider/timeline/session, initializes one interval using the ontology's configured `initial_phase_id` (Phase 1 for appendectomy) over `[0, duration_ms)`, refreshes both annotation views, and changes status to **Loaded**.
5. Play/pause is available through the state-aware Play/Pause button or Space. Left/Right seek by `int(1000 / fps)` milliseconds. The slider and painted timeline seek in milliseconds.
6. The always-visible phase palette is built from the configured ontology. Clicking a phase or pressing its configured window shortcut (including `U`) calls the same `record_phase_transition()` method, which delegates interval changes to the transactional `AnnotationEditor`. Phase shortcuts are disabled while a text-entry control or the segment list has keyboard focus; clicking the timeline restores the normal annotation context.
7. The palette highlights the phase under the playhead. The timeline and segment cards are rebuilt from the same validated session interval sequence. A white outline identifies the segment under the playhead; a cyan outline identifies the explicitly selected segment. Single-clicking a card selects it and seeks to its start. Clicking within a timeline interval selects it and seeks to that position. Selection persists while the playback slider moves, but is cleared when a phase transition changes the interval structure.
8. The annotator can right-click a segment or use its visible **⋮** button and choose **Edit note...**. A modal dialog owns the temporary draft; Save invokes `AnnotationEditor.update_notes()`, while Cancel leaves committed annotation data unchanged. A compact indicator identifies segments with notes.
9. **Change phase** in the same menu relabels the complete selected interval, unlike palette/hotkey transitions at the playhead. Equal neighbouring phases coalesce, their notes are combined in order, and the resulting interval remains selected.
10. **Set start to playhead** moves the boundary shared with the previous segment; **Set end to playhead** moves the boundary shared with the next segment. The unavailable external-video boundary action is disabled, and an invalid playhead position leaves both intervals unchanged.
11. **Remove / merge** never creates an uncovered hole. Convert to Undefined relabels the selected interval; Merge left/right adopts the chosen neighbour's phase and coalesces. Edge directions are disabled, and closing the menu is Cancel.
    Pressing Delete while a segment is selected is a shortcut for Convert to Undefined; it uses the same validated, undoable command and never removes timeline coverage.
12. Every successful annotation mutation enters a 100-command in-memory history. Undo/Redo buttons and `Ctrl+Z`, `Ctrl+Shift+Z`, or `Ctrl+Y` restore exact validated snapshots. Failed operations, no-ops, playback, seeking, and selection are not recorded; loading another video clears history.
13. Internal timeline boundaries display subtle handles. Hovering within eight pixels emphasizes the nearest handle and changes the cursor; ordinary clicks outside that area retain select/seek behavior. Pressing a handle begins a drag preview rather than immediately mutating data.
14. Pressing and dragging a boundary displays a cyan valid or red invalid preview and seeks the video without changing intervals. One valid release invokes the shared boundary command once; invalid release or Escape restores the original playhead and records no history entry.

Draggable boundaries, correction, and in-memory undo/redo are available. The canonical adjacent JSON sidecar loads and saves automatically with resume checkpoints and visible dirty-state failure handling. Clean close or video replacement creates one history snapshot only when annotation data changed since opening that video. External sidecar changes block overwrite. The **Annotation** menu provides an optional video-level note and an explicit completion declaration with an Undefined-footage summary. Completed annotations remain navigable; editing requires confirmation and archives the completed JSON before returning to Draft. Persisted command history is not implemented.

The playback toolbar provides approximate frame steps, ±5-second jumps, and 1×/2×/4×/8×/12× playback rates. The timeline remains a single full-width overview. **Help → Shortcuts and controls...** opens a structured visual reference for phase, playback, correction, and history interactions. Actionable media/persistence failures appear in the dismissible top banner, while routine feedback stays in the status bar.

## Qt ownership and signal flow

- `MainWindow` owns `VideoPlayerWidget`, `TimelineWidget`, `PhasePaletteWidget`, and `SegmentListWidget`.
- `VideoPlayerWidget` wraps `QMediaPlayer`, `QAudioOutput`, and `QVideoWidget`, forwarding position, duration, and simplified playing/not-playing signals. It exposes public `position_ms`, `duration_ms`, and `is_playing` properties.
- Player position updates the slider (unless it is being dragged), timeline playhead, and time label.
- Timeline and segment-list selection requests carry segment intent to `MainWindow`, which synchronizes selection and seeking. Modal note editing does not leave a draft behind for navigation actions to resolve.
- `MainWindow` still performs presenter/controller coordination, but annotation mutation belongs to the pure-Python `AnnotationEditor`; it no longer reaches into the private Qt player for position or duration.

## Video accuracy limitations

Qt Multimedia chooses the platform media backend and codec support is environment-dependent. C5 records cheap filesystem evidence and available Qt duration, resolution, and reported FPS, with a reusable local-media smoke script. There is no codec fallback or automated decoded-video test. Variable frame rate, time bases, keyframes, and rotation are not resolved, so displayed frame numbers and frame-step controls remain timestamp-derived rather than guaranteed decoded-frame indices.

Milliseconds are the authoritative annotation unit today. Frame labels stay compact for the clinical workflow, with the uncertainty retained in metadata and disclosed through the main time-label tooltip. Do not derive a claim of VFR frame accuracy from `ms_to_frame()` or `frame_to_ms()`; both are simple constant-rate arithmetic.

Missing/unreadable files are rejected before media loading. If Qt reports a resource, format/codec, network, or permission error, playback and annotation controls are disabled and the status bar explains the failure. Opening a new source begins a fresh load attempt.
