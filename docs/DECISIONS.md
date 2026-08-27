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

## ADR 004: Dual Interval Visualization (Timeline + Segment Card View)
- **Status**: Approved
- **Context**: Annotators need both a visual timeline bar and a structured list view of labeled surgical segments (similar to LosslessCut).
- **Decision**: Implement both a custom painted `TimelineWidget` and custom segment cards hosted by a `QListWidget` side-by-side. Clicking a card jumps playback to that segment's start timestamp.
- **Implementation note**: `SegmentListWidget` is the active view. `table_widget.py` is an unused duplicate from M3 and is not evidence of a second table-based UI.

## Proposed decisions still required

The code does not yet settle unfinished interval representation, media identity, frame accuracy, or schema migration. Decide and test these before treating the persisted format as stable or implementing CSV export.

## ADR 005: Continuous Coverage, Undefined, Delete, and Merge Semantics

- **Status**: Approved
- **Context**: Surgical phase annotations form a temporal partition rather than independent clips. Editing must not create hidden gaps or silently assign uncertain footage to a neighboring phase.
- **Decision**:
  - The full video timeline is covered by annotation segments.
  - `Undefined` is a real configured class, selected with `U`, and represents footage without a confident phase label.
  - Gaps and overlaps are invalid.
  - Adjacent segments share a boundary; moving it lengthens one segment and shortens the other.
  - Phases may repeat or appear outside nominal ontology order because real procedures are not strictly linear.
  - Delete converts the selected segment to `Undefined`.
  - Merge Left and Merge Right explicitly assign the selected region to the corresponding neighbor.
  - Adjacent segments with the same class are automatically coalesced.
  - Annotation mutations must be undoable and validated before replacing the current session state.
- **Consequences**: Deletion is safe and reversible, exports have explicit coverage, and boundary edits cannot produce ambiguity. Initial session creation and unfinished/final interval behavior still require an implementation-level decision in C0.
