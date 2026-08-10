# Architecture Decision Log (ADR)

## ADR 001: Separation of Domain and UI via MVP Pattern
- **Status**: Approved
- **Context**: Surgical video annotation requires strict data validation (no overlaps, gap handling) independent of UI rendering.
- **Decision**: Keep domain logic in pure Python data classes (`models.py`, `ontology.py`, `validation.py`) with zero PySide6 dependencies. UI components consume domain models.

## ADR 002: Atomic Data Persistence Strategy
- **Status**: Approved
- **Context**: Application crashes must never result in corrupted `.json` session files.
- **Decision**: `JsonSessionRepository.save()` writes to a `.tmp` file in the same directory before calling `os.replace()` for atomic replacement across Linux and Windows.

## ADR 003: PySide6 (Qt 6) Desktop Shell & Qt Multimedia
- **Status**: Approved
- **Context**: Need a cross-platform desktop video playback engine supported on both Windows and Linux without third-party app dependencies.
- **Decision**: Use PySide6 `QMediaPlayer`, `QVideoWidget`, and `QAudioOutput`.

## ADR 004: Dual Interval Visualization (Timeline + Segment Table View)
- **Status**: Approved
- **Context**: Annotators need both a visual timeline bar and a structured list view of labeled surgical segments (similar to LosslessCut).
- **Decision**: Implement both a custom painted `TimelineWidget` and a `QTableWidget` (`IntervalTableView`) side-by-side. Clicking any row in the table jumps playback to that segment's start timestamp.
