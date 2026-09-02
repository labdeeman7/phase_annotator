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

The code does not yet settle media identity, frame accuracy, or schema migration. Decide and test these before treating the persisted format as stable or implementing CSV export.

## ADR 005: Continuous Coverage, Undefined, Delete, and Merge Semantics

- **Status**: Approved
- **Context**: Surgical phase annotations form a temporal partition rather than independent clips. Editing must not create hidden gaps or silently assign uncertain footage to a neighboring phase.
- **Decision**:
  - The full video timeline is covered by annotation segments.
  - `Undefined` is a real configured class, selected with `U`, and represents footage without a confident phase label.
  - Gaps and overlaps are invalid.
  - Adjacent segments share a boundary; moving it lengthens one segment and shortens the other.
  - Phases may repeat or appear outside nominal ontology order because real procedures are not strictly linear.
  - Delete does not silently choose a replacement. It opens a resolution choice: convert to `Undefined`, merge into the previous segment, merge into the next segment, or cancel. Neighbor options are disabled when no such neighbor exists.
  - Adjacent segments with the same class are automatically coalesced.
  - Annotation mutations must be undoable and validated before replacing the current session state.
- **Consequences**: Segment removal is explicit and reversible, exports have complete coverage, and boundary edits cannot produce ambiguity.

## ADR 006: Expected Order and Configurable Initial Phase

- **Status**: Approved
- **Context**: Appendectomy phases normally follow a clinical sequence, and requiring an annotator to mark Phase 1 at exactly `0ms` is awkward. However, real procedures may repeat or deviate from the expected order.
- **Decision**:
  - Each ontology defines an expected display order as guidance, not a transition constraint.
  - Each ontology explicitly defines `initial_phase_id`; it is not inferred from the smallest ID or list position.
  - The default appendectomy ontology uses Phase 1 (Identification of the appendix) as its initial phase.
  - Undefined remains a configured exception class with hotkey `U` and appears separately after the expected surgical phases.
  - New media loads paused at `0ms`; once duration is known, the initial phase provisionally covers `[0, duration_ms)`.
  - Other ontologies may choose a different initial phase, including Undefined.
- **Consequences**: Sequential annotation starts naturally, while unusual footage can still be relabeled Undefined at zero. Automatically populated future coverage is provisional and cannot be interpreted as proof of review.

## ADR 007: Draft/Completed Lifecycle and Review Progress

- **Status**: Approved
- **Context**: Full coverage can contain automatically assigned provisional labels, so coverage validity alone cannot demonstrate that an annotator reviewed the whole video or indicate where unfinished work should resume.
- **Decision**:
  - Sessions have an explicit lifecycle status, initially `draft` and later `completed` through a deliberate completion action.
  - Persist `completed_at` (and completion identity if required by the workflow), `resume_position_ms`, and `reviewed_until_ms` as distinct concepts.
  - Seeking forward changes resume position but must not automatically advance contiguous review progress.
  - Completion validates video identity, ontology identity, interval coverage/bounds/phase IDs, and review progress.
  - Undefined intervals are summarized and require informed confirmation but do not necessarily prohibit completion.
  - Editing a completed session requires confirmation and returns it to draft for the first release; revision history is deferred.
- **Consequences**: The application can resume work without confusing playhead position, provisional coverage, and human-reviewed progress. Lifecycle/progress fields must be designed before session persistence is treated as stable; the full tracking and completion UI remain planned for C6-C8.
