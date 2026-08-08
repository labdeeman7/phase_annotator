# Architecture Decision Records (ADRs)

## ADR 001: Video Playback Engine Selection
* **Date**: 2026-08-08
* **Status**: Accepted
* **Context**: Surgical video annotation requires smooth playback, seeking, and clean cross-platform bundling (Linux dev, Windows target annotators).
* **Decision**: Selected **PySide6 (`QMediaPlayer` + `QVideoWidget`)** as the primary playback engine instead of native libVLC bindings or raw OpenCV rendering.
* **Rationale**: PySide6 integrates directly with Qt event loops, has native cross-platform backend support, and simplifies PyInstaller executable bundling.

## ADR 002: Pure Python Domain Layer Isolation
* **Date**: 2026-08-08
* **Status**: Accepted
* **Context**: Annotation rules, interval validation, and session persistence must be 100% reliable and easy to unit test.
* **Decision**: Isolate all domain entities (`src/phase_annotator/domain`) into pure Python with zero GUI dependencies.
* **Rationale**: Enables millisecond pytest suite execution without spinning up Qt application contexts during unit testing.

## ADR 003: Atomic Session File Writes
* **Date**: 2026-08-08
* **Status**: Accepted
* **Context**: Research data loss from application crashes or partial saves is intolerable.
* **Decision**: All file saves write to a temporary file (`.session.json.tmp`) before calling `os.replace()` to atomically swap the target file.
* **Rationale**: Ensures session files are never left in a corrupted/half-written state.
