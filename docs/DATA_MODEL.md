# Annotation Data Model

## In-memory schema

`AnnotationSession` is the aggregate serialized by `JsonSessionRepository`:

```text
AnnotationSession
├── video_info: VideoInfo
│   ├── video_id: str
│   ├── duration_ms: int
│   ├── fps: float = 30.0
│   ├── width: int | null
│   └── height: int | null
├── annotator_id: str
├── ontology_id: str
├── ontology_version: str
├── intervals: list[AnnotationInterval]
│   ├── start_ms: int
│   ├── end_ms: int
│   ├── phase_id: int
│   └── notes: str
├── schema_version: str = "1.0"
├── created_at: float (Unix timestamp)
└── updated_at: float (Unix timestamp)
```

`notes` is committed annotation data, while text being typed in the modal note dialog is transient UI state. `AnnotationEditor.update_notes()` replaces the selected interval with an otherwise identical interval only after validating the existing and candidate coverage; it then commits once and updates the session timestamp.

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

## Planned lifecycle and progress fields

Full interval coverage does not prove full human review because the current phase provisionally extends into unwatched footage. The persisted session model will therefore distinguish:

- `status`: `draft` or `completed`;
- `completed_at`: nullable completion timestamp;
- `resume_position_ms`: last saved playhead position for convenience;
- `reviewed_until_ms`: furthest contiguously reviewed position.

Forward seeking must not falsely advance `reviewed_until_ms`. Completion is an explicit validated action. Undefined footage is summarized for confirmation rather than automatically blocking completion. Editing a completed session returns it to draft after confirmation.

## Persisted JSON

Persistence is a direct `dataclasses.asdict()` representation. Loading reconstructs known fields and defaults missing `schema_version`, `created_at`, and `updated_at`; it does not preserve unknown fields or perform an explicit schema migration. Example:

```json
{
  "video_info": {
    "video_id": "synthetic_case_01.mp4",
    "duration_ms": 120000,
    "fps": 30.0,
    "width": 1920,
    "height": 1080
  },
  "annotator_id": "annotator_01",
  "ontology_id": "laparoscopic_appendectomy.default",
  "ontology_version": "1.0",
  "intervals": [
    {"start_ms": 0, "end_ms": 15000, "phase_id": 1, "notes": ""}
  ],
  "schema_version": "1.0",
  "created_at": 0.0,
  "updated_at": 0.0
}
```

## Integrity requirements for future work

Before UI-integrated persistence or export, make these policies explicit and tested:

- how an unfinished/final interval is represented;
- phase-ID and video-bound validation;
- source-video identity and relocation behavior;
- schema migration and unknown-field behavior;
- crash recovery, backup, concurrent writer, and stale-temp handling;
- timestamp/frame semantics for CFR and VFR media.

Session fixtures and documentation must use synthetic identifiers. Do not store patient identifiers or real clinical metadata in the repository.
