# Annotation Data Model

## In-memory schema

`AnnotationSession` is the aggregate serialized by `JsonSessionRepository`:

```text
AnnotationSession
├── video_info: VideoInfo
│   ├── video_id: str
│   ├── duration_ms: int
│   ├── fps: float | null
│   ├── width: int | null
│   ├── height: int | null
│   ├── source_path: str | null (absolute last-known local path)
│   ├── file_size_bytes: int | null
│   ├── file_modified_ns: int | null
│   ├── fps_source: unknown | assumed | qt | ffprobe
│   └── frame_rate_mode: unknown | cfr | vfr
├── annotator_id: str (legacy field retained for compatibility)
├── created_by: str
├── last_edited_by: str | null
├── ontology_id: str
├── ontology_version: str
├── intervals: list[AnnotationInterval]
│   ├── start_ms: int
│   ├── end_ms: int
│   ├── phase_id: int
│   └── notes: str
├── status: draft | completed = "draft"
├── completed_at: float | null
├── completed_by: str | null
├── session_notes: str = ""
├── resume_position_ms: int = 0
├── schema_version: str = "1.4"
├── created_at: float (Unix timestamp)
└── updated_at: float (Unix timestamp)
```

`notes` is committed annotation data, while text being typed in the modal note dialog is transient UI state. `AnnotationEditor.update_notes()` replaces the selected interval with an otherwise identical interval only after validating the existing and candidate coverage; it then commits once and updates the session timestamp.

`AnnotationEditor.relabel_interval()` changes the phase of one complete interval, preserves its note, and coalesces adjacent intervals that now share a phase. Coalescing combines non-empty notes from left to right with newline separators so correction never silently drops annotation context.

`AnnotationEditor.move_boundary()` identifies an internal boundary by the index of the interval on its right. It replaces the left interval's end and right interval's start in one validated candidate, preserving their phases and notes. The strict bounds `left.start_ms < position_ms < right.end_ms` guarantee both resulting intervals have positive duration.

Removal is modeled as resolution rather than physical deletion: `convert_to_undefined()` relabels the interval, while `merge_left()` and `merge_right()` adopt the selected neighbour's phase and coalesce. All three preserve full coverage and combine notes chronologically instead of dropping them.

`AnnotationHistory` stores copied before/after interval tuples for up to 100 successful annotation commands. Entries also retain a description and temporal anchor for UI feedback and safe selection relocation. Snapshots are not serialized. Undo/redo verifies that the current intervals match the expected side of the entry, then calls `AnnotationEditor.restore_intervals()` so restored phase IDs and coverage are validated before the session is committed.

`AnnotationInterval` rejects negative starts and requires `start_ms < end_ms`. Its duration is `end_ms - start_ms`. Intervals are treated as half-open `[start_ms, end_ms)`, with adjacent intervals sharing a boundary.

The packaged default ontology contains IDs 1-6 plus Undefined (ID 0). Phase 2 (adhesion dissection) is optional. Names, colors, hotkeys, expected order, initial phase, and Undefined role come from the validated packaged JSON described in `ONTOLOGY_CONFIGURATION.md`. Sessions store ontology identity/version so interval IDs remain interpretable.

## Accepted annotation semantics

- A valid working/final annotation covers the full video without gaps or overlaps.
- `Undefined` is an explicit phase class rather than an absent annotation.
- Phase labels may repeat or appear out of nominal surgical order.
- Moving an internal boundary changes the two adjacent intervals together.
- Delete opens an explicit resolution choice: convert to Undefined, merge into the previous segment, merge into the next segment, or cancel.
- Adjacent intervals carrying the same phase ID are automatically merged.
- All mutations must be validated transactionally and represented as undoable commands in the application layer.

Once media duration is known, an empty session is provisionally covered by the ontology's explicit `initial_phase_id`. For the default appendectomy ontology this is Phase 1, not Undefined. Selecting a different phase inside a segment splits it at the playhead and relabels only the remainder of that containing segment; established later segments remain intact. Selecting the active phase is a no-op, and transitions at `duration_ms` are invalid because the end boundary is exclusive.

Expected phase order is display/clinical guidance only. Repeated and out-of-order phase transitions remain valid.

## Lifecycle and resume fields

Full interval coverage does not prove completion because the current phase provisionally extends into unwatched footage. The persisted session model therefore includes:

- `status`: `draft` or `completed`;
- `completed_at`: nullable completion timestamp;
- `completed_by`: nullable identity of the annotator who explicitly completed it;
- `session_notes`: optional note about the video/session as a whole, distinct from interval notes;
- `resume_position_ms`: last checkpointed playhead position for convenience.

Draft sessions require both completion fields to be null; completed sessions require a valid timestamp and non-empty completer. Resume position is not proof of review. `reviewed_until_ms` is deferred until a trustworthy definition is needed. The explicit completion action summarizes Undefined footage for confirmation rather than automatically blocking completion. Editing a completed session requires confirmation and archives the completed record before returning it to draft.

## C7 attribution and historical snapshots

Schema 1.3 preserves legacy `annotator_id` and adds these explicit concepts:

- `created_by`: who created the annotation session;
- `last_edited_by`: who made the latest annotation-data mutation;
- active annotator: application state, entered at every startup and retained across opened videos for that launch;
- `completed_by`: added in schema 1.4 for C8 explicit completion.

The rejected pre-commit C7 prototype briefly emitted `work_sessions`. The loader preserves that field opaquely when encountered so a trial sidecar can round trip without data loss, but new sessions do not create or use it.

Seeking and resume checkpoints do not change annotation attribution. Resume remains one shared position per video rather than a per-annotator progress record. Historical files are complete validated session JSON snapshots created once when a changed video is closed or replaced and remain independently loadable.

## Persisted JSON

Persistence is a direct `dataclasses.asdict()` representation. Schema 1.1 added optional media fields, schema 1.2 lifecycle/resume fields, schema 1.3 creator/last-editor attribution, and schema 1.4 completion attribution plus video-level notes. Older known schemas remain loadable through explicit defaults. Unknown fields are rejected rather than silently erased on the next write; there is not yet a general migration framework. Example:

```json
{
  "video_info": {
    "video_id": "synthetic_case_01.mp4",
    "duration_ms": 120000,
    "fps": 30.0,
    "width": 1920,
    "height": 1080,
    "source_path": "C:/synthetic-media/synthetic_case_01.mp4",
    "file_size_bytes": 123456,
    "file_modified_ns": 1700000000000000000,
    "fps_source": "qt",
    "frame_rate_mode": "unknown"
  },
  "annotator_id": "annotator_01",
  "created_by": "annotator_01",
  "last_edited_by": "annotator_01",
  "ontology_id": "laparoscopic_appendectomy.default",
  "ontology_version": "1.0",
  "intervals": [
    {"start_ms": 0, "end_ms": 15000, "phase_id": 1, "notes": ""}
  ],
  "status": "draft",
  "completed_at": null,
  "completed_by": null,
  "session_notes": "",
  "resume_position_ms": 0,
  "schema_version": "1.4",
  "created_at": 0.0,
  "updated_at": 0.0
}
```

The media fields form a lightweight **source descriptor**, not guaranteed identity. No content hash is stored. `source_path` is a convenient last-known locator but can become stale after a move and may reveal local directory or user names; exclude it from research exports, logs, screenshots, fixtures, and committed examples. File size and modification time can support later mismatch warnings but cannot prove equality. `frame_numbers_are_estimated` remains true unless a measured FPS and known CFR mode are both available.

Source comparison returns `match`, `mismatch`, or `unknown` with per-field evidence. Filename agreement alone is unknown; at least one other descriptor must agree. Conflicting filename, size, modification time, duration, or dimensions is a mismatch. A different absolute path is reported but treated as relocation rather than a conflict when the remaining evidence agrees. Duration comparison allows a small backend-rounding tolerance. No result proves byte-for-byte identity.

## Remaining integrity work

Before production use, continue strengthening these policies:

- how an unfinished/final interval is represented;
- phase-ID and video-bound validation;
- source-video identity and relocation behavior;
- schema migration and unknown-field behavior;
- write failure/retry, concurrent writer, and stale-temp behavior;
- timestamp/frame semantics for CFR and VFR media.

Session fixtures and documentation must use synthetic identifiers. Do not store patient identifiers or real clinical metadata in the repository.
