# C6 Continuous Sidecar Persistence

## Outcome

Opening a video automatically resumes its annotation sidecar when safe, or creates one when none exists. Every successful annotation edit is written atomically without requiring routine Save or Save As actions. Persistence failures remain visible and cannot be mistaken for saved work.

## Approved product contract

- The canonical annotation is JSON named `<video filename>.phase-annotations.json` beside the video; for example `case.mp4.phase-annotations.json`.
- The application automatically looks for that exact sidecar when a video is opened. There is no ordinary Save, Save As, or Open Session workflow.
- A new sidecar is created only after Qt supplies a positive duration and the initial full-coverage interval is valid.
- Every successful annotation mutation saves immediately: phase transitions, notes, whole-segment relabeling, boundary edits, removal/merge, undo, and redo.
- JSON remains the canonical research artifact. CSV export is not required unless a real downstream consumer later needs it.
- Save uses the existing same-directory temporary file plus `os.replace`; no video content is hashed.
- The first implementation targets writable video directories. The exceptional read-only-directory fallback is a later C6 sub-slice and must not weaken the core save/load behavior.

## Dirty-state semantics

`dirty` means the current in-memory session differs from the last successfully written canonical sidecar. It is not a synonym for “the user has edited something.”

- A successful write clears dirty state.
- A failed write preserves the valid in-memory session, marks it dirty, displays an actionable error, and allows a later retry.
- Replacing the video or closing the application prompts only when dirty work remains.
- Annotation state is never rolled back merely because disk persistence failed.

## Loading and source safety

An existing sidecar is parsed and validated before its intervals replace the current session. Loading must check supported schema, ontology identity, phase IDs, timestamp ordering, contiguity, and video bounds. C5 source comparison supplies the media decision:

- `match`: load automatically. A path-only difference is relocation; update the last-known path after successful loading.
- `mismatch`: do not attach the annotations to the video.
- `unknown`: require explicit user confirmation; never silently treat missing legacy evidence as a match.

Annotation controls stay disabled while an existing sidecar is unresolved or invalid.

## Resume and lifecycle

C6 persists `resume_position_ms`, but does not write on every Qt position signal. Save it with annotation edits, on pause, at a modest periodic checkpoint during playback, and on clean close/video replacement. Restoring the playhead does not imply that footage was reviewed.

The session schema will add:

- `status`: `draft` or `completed`, default `draft`;
- `completed_at`: nullable Unix timestamp;
- `resume_position_ms`: non-negative millisecond position.

C6 persists these fields but does not add the completion action. C8 owns completion validation and UI. `reviewed_until_ms` is deferred until a concrete, trustworthy review-progress definition is needed.

## Sub-slices

### C6.1 — Contract and schema plan

Status: **Complete.** This document, ADR 007/010, the roadmap, and data-model plan record the agreed behavior.

### C6.2 — Persistence coordinator and schema fields

Status: **Complete.** Schema 1.2 adds lifecycle/resume fields, and the UI-independent coordinator owns naming, validation, source decisions, saving, and dirty state.

### C6.3 — Automatic new-session saving

Status: **Complete.** The first valid full-coverage session is saved after duration initialization, and annotation commands save immediately.

### C6.4 — Automatic existing-session loading

Status: **Complete.** Matching sessions load automatically, mismatch/invalid files block annotation, and unknown legacy source evidence requires confirmation.

### C6.5 — Resume checkpoints

Status: **Complete.** Resume is saved with edits, on pause, periodically during playback, and before clean replacement/close; it is restored on load.

### C6.6 — Dirty close/replacement and unwritable folders

Status: **Complete.** Close/replacement prompts only when failed persistence leaves dirty work. No alternate annotation folder was added: deterministic adjacent sidecars remain the sole lookup rule until representative read-only use demonstrates a need.

### C6.7 — Failure and round-trip validation

Status: **Complete.** Tests cover legacy defaults, unknown-field rejection, validation/source outcomes, write failure and dirty retention, initial save, immediate edit/undo persistence, and matching-sidecar reload. Retry/discard/cancel uses the same tested coordinator state and a small UI decision boundary.

## Learning-mode reading map

For C6.2, focus on the new coordinator boundary, the additive session-schema fields, and failure-path tests. The central engineering idea is that a repository reads/writes JSON, while an application persistence coordinator decides **when**, **where**, and **whether** a session may be loaded or considered saved.
