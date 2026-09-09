# C5 Media Metadata and Playback Reliability

## Outcome

C5 makes the application's timing claims explicit, provides enough lightweight source evidence to detect common video mismatches, and turns media/backend failures into actionable feedback. Millisecond timestamps remain the authoritative annotation coordinate.

## Approved constraints and tradeoffs

- **Never hash video contents.** Full or sampled content hashes are outside this project's identity strategy because large surgical videos and modest annotation computers make that cost undesirable.
- A video has a **source descriptor**, not a cryptographically unique identity. Filename, last-known absolute path, file size, modification time, duration, and dimensions can identify obvious mismatches but cannot prove that two files have identical content.
- Store the absolute path as the last-known location for convenient same-machine reopening. It is location, not identity, and C6 must support relocation when the file moves.
- Absolute paths may contain usernames or sensitive directory names. Keep them in session files only; do not include them in research CSV exports, logs, screenshots, committed fixtures, or user-facing examples.
- Session `created_at` records when annotation began. It must not be used as evidence of source-video identity.
- C5 uses Qt/platform metadata only. Do not invoke an `ffprobe` found on `PATH`. Bundling can be reconsidered during distribution work only if its executable provenance, licensing obligations, supported platforms, invocation, and installer integration are deliberately owned.
- Never infer CFR merely because one FPS number is available. VFR/CFR classification requires explicit evidence; otherwise frame numbers remain estimated.

## C5.1 — Metadata contract

Status: **Complete.**

Extend `VideoInfo` with optional source path, file size, modification timestamp, FPS provenance, and frame-rate mode. Retain backward loading of older JSON sessions with missing fields, and version the new session schema explicitly. New UI sessions record the absolute last-known path and mark the current 30 FPS player value as assumed rather than measured.

## C5.2 — Probe adapter and bundling decision

Status: **Complete.**

- `MediaMetadata` and `MediaProbeFailure` are frozen, UI-independent result types.
- `probe_local_file()` reads only path, byte size, and nanosecond modification time; it never opens or hashes content.
- `read_qt_media_metadata()` translates backend-dependent Qt duration, resolution, and frame-rate values into the neutral result.
- `VideoPlayerWidget` emits late metadata snapshots; `MainWindow` rejects snapshots that do not belong to the current source.
- Qt does not establish CFR/VFR status, so `frame_rate_mode` remains `unknown` and frame numbers remain estimated even when Qt reports FPS.
- Decision: use the already packaged PySide6/Qt stack. Do not bundle or invoke a separate `ffprobe` in the current application.

## C5.3 — Lightweight source matching

Status: **Complete.**

- `compare_video_source()` returns an explainable `match`, `mismatch`, or `unknown` result plus per-field evidence.
- Conflicting filename, size, modification time, duration, or dimensions produces `mismatch`. Duration allows 100 ms of backend rounding by default.
- A matching filename alone is insufficient and returns `unknown`; it needs at least one agreeing descriptor field.
- A changed absolute path is reported as relocation evidence but does not by itself make otherwise matching media conflict.
- These results remain warning evidence, not proof that file contents are identical. C6 will use them when opening and relocating saved sessions.

## C5.4 — Honest timing UI

Status: **Complete.**

- The main time label leads with millisecond timecodes and uses the compact `Frame N` presentation.
- Segment cards show seconds and a compact frame count; repeated milliseconds, FPS, and provenance were removed as visual noise.
- Frame-step buttons retain the familiar `-1 Frame` and `+1 Frame` labels.
- Qt-reported FPS refreshes the time label, frame-step presentation, and segment-card estimates consistently.
- Internal provenance and uncertainty remain intact. One unobtrusive tooltip explains timestamp-derived frame values while CFR is unconfirmed.

## C5.5 — Playback and codec errors

Status: **Complete.**

- Missing/unreadable paths fail before Qt loading and receive a filename-scoped status message.
- `VideoPlayerWidget` translates Qt resource, format/codec, network, and permission errors into actionable text without exposing Qt enums to `MainWindow`.
- A failed load pauses playback and disables play, frame-step, seek, palette, and annotation shortcuts.
- Opening another video resets the failure state. Routine Loading/Loaded and failure feedback remain in the status bar; the polished notification component stays deferred.

## C5.6 — Integration validation

Status: **Planned.**

- Unit-test optional/missing metadata, source descriptors, compatibility, and failure mapping.
- Test a small generated synthetic CFR asset where practical without committing clinical or large media.
- Manually test representative project media and document backend/platform limits.

## Learning-mode reading map

For C5.5, focus on `VideoPlayerWidget._forward_media_error()`, `MainWindow._on_media_error()`, and the early failure branch in `_load_video()`. Skim the Qt error-message mapping and repeated control assertions.
