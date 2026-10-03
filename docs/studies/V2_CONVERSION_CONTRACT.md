# V2 Cholec80 Conversion Contract

Status: **Implemented; synthetic validation complete.** Acceptance still requires the V3 one-case visual trial.

## Purpose and safety boundary

`scripts/convert_cholec80_phase.py` converts Cholec80's frame-level phase TXT into a schema-1.4 Phase Annotator session. It does not discover datasets, copy videos, infer missing labels, or certify clinical correctness. Generated files are marked `completed` reference imports so accidental edits trigger the application's explicit archive-and-reopen confirmation. Their machine attribution and provenance note distinguish this protection state from human completion.

Keep converted references outside this repository and outside blind-practice video directories. Copy a canonical sidecar beside a reference video only for an intentional walkthrough.

## Source and timing semantics

- Require the exact `Frame<TAB>Phase` header and every integer frame from zero.
- Treat each row as one source frame at Cholec80's documented 25 FPS (40 ms).
- Convert inclusive frames `a` through `b` to `[a × 40 ms, (b + 1) × 40 ms)`.
- Coalesce equal adjacent labels and preserve repeated or out-of-order runs.
- Require the video's Qt duration. Adjust only the final endpoint and only within the application's existing 100 ms tolerance; otherwise fail visibly.

Unknown labels fail. The explicit token-to-ID mapping is: `Preparation` 1, `CalotTriangleDissection` 2, `ClippingCutting` 3, `GallbladderDissection` 4, `GallbladderPackaging` 5, `CleaningCoagulation` 6, and `GallbladderRetraction` 7.

## Provenance and output

For `video04.mp4`, the output directory receives `video04.mp4.phase-annotations.json` and `video04.mp4.conversion.json`. The session identity and completer are `cholec80_reference_import`, its note says it was not produced by a human GUI annotator, and its creation/completion timestamps are zero because the dataset supplies no truthful annotation-session timestamps. The manifest records filenames (not absolute paths), timing evidence and adjustment, mapping, ontology, validation, and pending visual review.

Outputs are deterministic for unchanged inputs and duration. Conversion refuses to overwrite either output unless `--overwrite` is deliberately supplied. The session is validated through the application's persistence coordinator before writing.

## Usage

```powershell
python scripts/smoke_test_media.py C:\study\worked_examples\video04.mp4
python scripts/convert_cholec80_phase.py `
  C:\study\source_labels\video04-phase.txt `
  C:\study\worked_examples\video04.mp4 `
  C:\study\reference_answers `
  --video-duration-ms <duration-printed-by-smoke-test>
```

## V3 acceptance checks

Stage one reference video and TXT outside the repository, record its Qt duration, convert it, and load the sidecar beside the staged video. Inspect the first boundary, at least two internal boundaries, and the final endpoint; then confirm ontology identity and clean reload. Any timing failure reopens this contract before batch conversion.
