# Architecture Decision Log (ADR)

## ADR 001: Separation of Domain and UI
- **Status**: Approved
- **Context**: Surgical video annotation requires strict data validation (no overlaps, gap handling) independent of UI rendering.
- **Decision**: Keep domain logic in pure Python data classes and services with zero PySide6 dependencies. UI components consume domain models. A dedicated MVP presenter is not required by this decision and has not yet been extracted.

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

## ADR 007: Draft/Completed Lifecycle and Resume Position

- **Status**: Approved
- **Context**: Full coverage can contain automatically assigned provisional labels, so coverage validity alone cannot demonstrate completion. The application also needs a convenient place to resume without claiming that every preceding timestamp was reviewed.
- **Decision**:
  - Sessions have an explicit lifecycle status, initially `draft` and later `completed` through a deliberate completion action.
  - Persist nullable `completed_at` and non-negative `resume_position_ms`.
  - Restoring or seeking to a resume position does not prove review progress.
  - Defer `reviewed_until_ms` until the product has a concrete, trustworthy definition of reviewed footage.
  - Completion validates video association, ontology identity, interval coverage/bounds, and phase IDs.
  - Undefined intervals are summarized and require informed confirmation but do not necessarily prohibit completion.
  - Editing a completed session requires confirmation and returns it to draft; C7 historical snapshots retain the prior completed state when that changed run ends.
- **Consequences**: The application can resume work without confusing playhead position with proof of review. C6 persists the fields; C8 owns the explicit completion workflow.

## ADR 008: Lightweight Media Descriptor Without Content Hashing

- **Status**: Approved
- **Context**: Sessions need enough source evidence to warn about an obviously wrong video, but clinical videos may be large and the target computers are not suited to repeated full-file hashing.
- **Decision**:
  - Never hash video contents, including full or sampled SHA-256.
  - Store the basename plus optional absolute last-known path, byte size, modification time, duration, dimensions, FPS provenance, and CFR/VFR knowledge.
  - Treat these fields as a source descriptor and comparison evidence, never as globally unique identity.
  - Keep the absolute path in local session JSON for convenient reopening, but exclude it from research exports and avoid exposing it in logs, screenshots, fixtures, or examples.
  - A session creation timestamp describes the annotation session and is not evidence about the video.
  - C5 uses metadata exposed by the already packaged PySide6/Qt stack and does not invoke or bundle a separate `ffprobe`. Reconsideration belongs to future distribution work and requires verified binary provenance, licensing compliance, supported-platform builds, and installer integration. Never require an executable installed on `PATH`.
- **Consequences**: Metadata checks remain fast and practical, but relocation needs an explicit user confirmation workflow and no combination of descriptor fields can mathematically prove that two files have identical content.

## ADR 009: Generic Phase Annotator With a Bundled Appendectomy Default

- **Status**: Approved
- **Context**: Phase definitions, hotkeys, colors, expected order, initial phase, and Undefined role are already supplied through an injected ontology. Naming the product after appendectomy incorrectly suggests that the reusable application logic is tied to one procedure.
- **Decision**:
  - Name the product **Phase Annotator**.
  - Continue shipping the provisional laparoscopic appendectomy ontology as the current startup default.
  - Keep procedure selection at the composition root and keep reusable domain/UI components independent of appendectomy-specific loaders and phase IDs.
  - Retain appendectomy terminology in ontology identifiers, configuration files, clinical decisions, and tests that specifically describe that default.
- **Consequences**: Other phase ontologies can use the same application architecture, but user-facing ontology selection is still future work and the bundled appendectomy phase set remains provisional until clinically reviewed.

## ADR 010: Automatic Canonical Sidecar Persistence

- **Status**: Approved
- **Context**: Annotation normally happens on one computer against one local video. Routine Save, Save As, manual session opening, periodic autosave copies, and recovery artifacts would add interaction and state that the current workflow does not need.
- **Decision**:
  - Use `<video filename>.phase-annotations.json` beside the video as its deterministic canonical sidecar.
  - Automatically create it after valid duration initialization, load it when the video opens, and atomically save after every successful annotation mutation.
  - Keep valid in-memory work after a write failure and define dirty state as divergence from the last successful canonical write.
  - Prompt on close/video replacement only when a persistence failure has left dirty work.
  - Use C5 source evidence before attaching an existing sidecar. A mismatch blocks loading; unknown evidence requires confirmation.
  - Treat read-only-directory fallback as an exceptional later C6 slice; do not introduce ordinary Save As behavior into the core workflow.
  - Keep JSON canonical and defer CSV until a demonstrated consumer requires it.
- **Consequences**: The normal workflow has no save ceremony and minimizes crash exposure. Videos and annotations remain easy to move together. Read-only media locations need an explicit fallback policy, and immediate persistence failures must be highly visible.

## ADR 011: One Annotator Per Launch and Changed-Run Snapshots

- **Status**: Approved for C7 planning
- **Context**: A supervisor requested annotator identification and retained historical JSON states. A first work-session UI felt like bloat in manual use. Current deployment assumes one surgeon per application launch, usually on separate computers.
- **Decision**:
  - Require an annotator ID at every application startup and retain it across videos during that run.
  - Do not remember the previous ID or allow in-application identity switching.
  - Preserve legacy `annotator_id`; distinguish creator, last editor, and C8's future completer without embedded work-session records.
  - Keep one shared resume position per video. It is navigation convenience, not per-user review progress.
  - On clean close or video replacement, create one validated historical snapshot only when annotation data changed since that video was opened.
  - Store snapshots in `<video filename>.phase-annotations-history/` with collision-safe UTC filenames; keep annotator identifiers inside JSON rather than filenames.
  - Keep canonical dirty state, changed-since-open state, and resume-only changes separate.
  - Detect an externally changed canonical sidecar before overwrite and block rather than merge automatically.
- **Consequences**: Sequential users gain useful attribution and a lightweight local trail without an account/session-management interface. The trail is not tamper-proof and simultaneous editing remains unsupported.
