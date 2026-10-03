# Known Limitations

This document describes the current Phase Annotator 0.1.0 prototype. It should accompany user and release documentation.

## Platform and media

- The supported release target is 64-bit Windows using the packaged Qt multimedia backend.
- Codec support depends on the target Windows/Qt environment. Not every MP4/AVI/MKV/MOV encoding is guaranteed.
- Linux and macOS source execution may work but are not release-validated.
- Video metadata comes from Qt; the application does not bundle or invoke `ffprobe`.
- Frame numbers and frame-step controls are estimates derived from milliseconds and reported FPS. Variable-frame-rate video is not frame-accurate.
- Seeking may land near a requested time because compressed video uses keyframes and platform decoding.

## Annotation and workflow

- Milliseconds, not decoded frame indices, are authoritative.
- Appendectomy and cholecystectomy ontologies are provisional and require clinical governance.
- Expected phase order is guidance, not a constraint preventing repeated or out-of-order phases.
- Undo/Redo history is limited to 100 commands and is not restored across video loads or application restarts.
- Completion is a user declaration, not independent verification of clinical correctness.
- The application has no gold-label comparison, scoring, or inter-rater agreement workflow.
- CSV/research export is deferred; canonical data is JSON.
- User-supplied ontology loading is not available; two packaged procedures are selectable.

## Persistence and collaboration

- The application requires a writable directory beside the video and has no hidden fallback save location.
- Atomic replacement reduces partial-write risk but does not fsync, lock concurrent writers, or clean every stale temporary file.
- Do not edit the same sidecar simultaneously on multiple computers. External revision evidence can block an overwrite but does not provide collaborative merging.
- Resume position is shared session convenience, not per-annotator progress or evidence of review.
- History snapshots are local recovery/trail files, not tamper-proof or regulated audit records.
- Absolute last-known source paths and annotator attribution are stored in canonical JSON; keep these files within the approved research environment.
- Relocating a video/sidecar is not fully mediated by the existing source-comparison engine.

## Architecture and quality

- `MainWindow` still combines UI construction and controller/presenter coordination.
- Mypy gates non-UI layers only; the Qt UI is not statically type-checked as a whole.
- No coverage threshold is configured.
- Automated tests and frozen smoke tests do not replace long-video, codec, display-scaling, or clinical workflow testing.
- `ui/table_widget.py` is an unused historical duplicate and is not the active segment list.

## Distribution

- The release is a portable one-folder ZIP, not an installer.
- The executable is not currently code-signed; Windows reputation warnings may occur.
- Automatic updates, crash reporting, telemetry, and central backup are absent.
- The application has not yet been validated across a documented matrix of Windows versions, machines, displays, and codecs.

Report a limitation encountered in practice with the application version, operating system, video characteristics, reproduction steps, and whether annotation data remained intact. Do not include patient-identifying information.
