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
├── intervals: list[AnnotationInterval]
│   ├── start_ms: int
│   ├── end_ms: int
│   ├── phase_id: int
│   └── notes: str
├── schema_version: str = "1.0"
├── created_at: float (Unix timestamp)
└── updated_at: float (Unix timestamp)
```

`AnnotationInterval` rejects negative starts and requires `start_ms < end_ms`. Its duration is `end_ms - start_ms`. Intervals are treated as half-open `[start_ms, end_ms)`, with adjacent intervals sharing a boundary.

The default ontology contains IDs 1-6. Phase 2 (adhesion dissection) is optional. The ontology, including names and colors, is code-defined in `domain/ontology.py` and is not embedded in session JSON.

## Accepted annotation semantics

- A valid working/final annotation covers the full video without gaps or overlaps.
- `Undefined` is an explicit phase class rather than an absent annotation.
- Phase labels may repeat or appear out of nominal surgical order.
- Moving an internal boundary changes the two adjacent intervals together.
- Delete relabels the selected interval as `Undefined`.
- Merge Left or Merge Right deliberately absorbs the selected interval into that neighbor.
- Adjacent intervals carrying the same phase ID are automatically merged.
- All mutations must be validated transactionally and represented as undoable commands in the application layer.

Once the media duration is known, an empty session is initialized as one Undefined interval covering `[0, duration_ms)`. Selecting a different phase inside a segment splits it at the playhead and relabels only the remainder of that containing segment; established later segments remain intact. Selecting the active phase is a no-op, and transitions at `duration_ms` are invalid because the end boundary is exclusive.

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
