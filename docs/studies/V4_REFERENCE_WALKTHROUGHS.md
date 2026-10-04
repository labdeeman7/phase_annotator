# V4 Reference Walkthroughs

Status: **In progress.** All nine remaining reference cases are staged, converted, and structurally validated; packaged-application walkthroughs remain.

## Purpose

V4 exercises the locally accepted 0.1.1 packaged application over realistic long annotations and gathers evidence for the working clinical protocol. It is not a blind accuracy study: each case intentionally loads the converted Cholec80 reference.

For every case:

1. stage only the selected MP4 and matching phase TXT in the ignored study workspace;
2. obtain duration through the application's Qt media pipeline;
3. convert into the protected reference-answer directory;
4. copy the generated canonical sidecar beside the walkthrough video;
5. open it with the packaged 0.1.1 cholecystectomy application;
6. inspect every transition and update `protocol.md` with supporting evidence, a counterexample, or a disagreement;
7. record software defects separately from clinical interpretation questions.

## Case tracker

| Order | Case | Known cohort characteristic | Staged | Converted | Walkthrough | Protocol evidence |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `video04` | Nominal seven-phase order; V3 trial | Yes | Yes | Complete | Initial working generalisations |
| 2 | `video79` | Cleaning/coagulation precedes Packaging | Yes | Yes | Pending | Pending |
| 3 | `video01` | Nominal seven-phase order | Yes | Yes | Pending | Pending |
| 4 | `video44` | Nominal seven-phase order | Yes | Yes | Pending | Pending |
| 5 | `video19` | Starts at P2; Preparation absent | Yes | Yes | Pending | Pending |
| 6 | `video64` | Cleaning/coagulation precedes Packaging | Yes | Yes | Pending | Pending |
| 7 | `video37` | Cleaning/coagulation precedes Packaging | Yes | Yes | Pending | Pending |
| 8 | `video68` | Nominal seven-phase order | Yes | Yes | Pending | Pending |
| 9 | `video14` | Retraction precedes Cleaning/coagulation; ends P6 | Yes | Yes | Pending | Pending |
| 10 | `video50` | Cleaning/coagulation absent | Yes | Yes | Pending | Pending |

## Batch-conversion evidence

- Exactly nine selected MP4s and nine matching source TXT files were staged; combined video size was 11.26 GB.
- Qt successfully opened every video and reported 25 FPS.
- Every label-derived duration exactly matched Qt's duration; no final-endpoint adjustment was required.
- The converter produced nine canonical sidecars and nine provenance manifests.
- `SessionPersistenceCoordinator.inspect()` returned `loaded` for every staged video.
- Every imported session is `completed` with machine-import attribution and the Cholec80 reference video note.
- `video19` and `video50` correctly contain six phase runs; the other seven cases contain seven.

## Per-case record

Copy this section for each walkthrough.

### `videoXX`

- Application build/version: 0.1.1 local artifact
- Open/play/seek: Pending
- Timeline and segment list: Pending
- Completed-reference protection: Pending
- Close/reopen: Pending
- Software defects: None recorded yet
- Usability friction: None recorded yet
- Supplied boundaries accepted: Pending
- Protocol support/counterexamples: Pending
- Clip/image candidates: Pending

## Separation rules

- Do not stage or convert the five blind-practice cases as part of V4.
- Keep protected reference answers outside blind-video directories.
- Do not commit videos, source labels, converted sidecars, clips, or absolute dataset paths.
- A supplied boundary disagreement is a protocol finding, not automatically a software defect.
- Do not modify a completed reference merely to record disagreement; record the proposed boundary in `protocol.md`.
