# V4 Reference Walkthroughs

Status: **Complete for the initial inferred protocol.** All ten reference cases were staged, converted, and reviewed; all 58 source-boundary clips were generated and indexed. The resulting rules are ready for clinical review, not yet formal clinical approval.

## Purpose

V4 reconstructs the phase and boundary convention demonstrated by Cholec80 while also exercising the locally accepted 0.1.1 packaged application. It is not a blind accuracy study: each case intentionally loads the converted Cholec80 reference, and that supplied boundary is the reference decision to explain rather than replace.

For every case:

1. stage only the selected MP4 and matching phase TXT in the ignored study workspace;
2. obtain duration through the application's Qt media pipeline;
3. convert into the protected reference-answer directory;
4. copy the generated canonical sidecar beside the walkthrough video;
5. open it with the packaged 0.1.1 cholecystectomy application;
6. inspect every transition through its one-minute boundary clip and update `INFERRED_CHOLEC80_RULES.md` with before/after activity and the inferred source convention;
7. record software defects separately from clinical interpretation questions.

The watching and protocol-inference tasks happen together, one case at a time. Do not watch all ten full videos and later rewatch all ten to locate transitions again.

## Case tracker

| Order | Case | Known cohort characteristic | Staged | Converted | Clips | Walkthrough | Rule evidence |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `video04` | Nominal seven-phase order; V3 trial | Yes | Yes | 6 | Complete | Initial working generalisations |
| 2 | `video79` | Cleaning/coagulation precedes Packaging | Yes | Yes | 6 | Complete | Task-based order; unused-instrument caveat |
| 3 | `video01` | Nominal seven-phase order | Yes | Yes | 6 | Complete | Instrument and next-task cues |
| 4 | `video44` | Nominal seven-phase order | Yes | Yes | 6 | Complete | Variable source timing around task changes |
| 5 | `video19` | Starts at P2; Preparation absent | Yes | Yes | 5 | Complete | Partial-recording rule |
| 6 | `video64` | Cleaning/coagulation precedes Packaging | Yes | Yes | 6 | Complete | Task-based order; confirmation after cutting |
| 7 | `video37` | Cleaning/coagulation precedes Packaging | Yes | Yes | 6 | Complete | Distinct P6 before packaging |
| 8 | `video68` | Nominal seven-phase order | Yes | Yes | 6 | Complete | Purposeful-instrument and task-completion cues |
| 9 | `video14` | Retraction precedes Cleaning/coagulation; ends P6 | Yes | Yes | 6 | Complete | Non-nominal P7-to-P6 order |
| 10 | `video50` | Cleaning/coagulation absent | Yes | Yes | 5 | Complete | Absent-phase rule and extraction cue |

## Batch-conversion evidence

- Exactly nine selected MP4s and nine matching source TXT files were staged; combined video size was 11.26 GB.
- Qt successfully opened every video and reported 25 FPS.
- Every label-derived duration exactly matched Qt's duration; no final-endpoint adjustment was required.
- The converter produced nine canonical sidecars and nine provenance manifests.
- `SessionPersistenceCoordinator.inspect()` returned `loaded` for every staged video.
- Every imported session is `completed` with machine-import attribution and the Cholec80 reference video note.
- `video19` and `video50` correctly contain six phase runs; the other seven cases contain seven.

## Clip-generation evidence

- Exactly one clip was generated for each internal source boundary: 58 clips across 10 cases.
- Every default clip is centered on the exact Cholec80 boundary with 30 seconds before and after, except when a video edge requires clamping. A phase-coloured label appears in the top-right of every frame and changes at the exact reference boundary.
- Clips were re-encoded with an explicitly selected offline FFmpeg binary rather than coarse keyframe copying; extraction settings and boundary metadata are stored in one ignored manifest per case.
- The clip library is approximately 973 MB. Qt successfully opened sampled 480p and 1080p outputs as 25 FPS, 60-second MP4 videos.
- Clip IDs and filenames identify case, boundary order, source phase, and destination phase.

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
- Additional non-boundary clip requests: Pending

## Separation rules

- Do not stage or convert the five blind-practice cases as part of V4.
- Keep protected reference answers outside blind-video directories.
- Do not commit videos, source labels, converted sidecars, clips, or absolute dataset paths.
- A surprising supplied boundary is an interpretation question, not automatically a software defect or a reason to move the reference.
- Do not modify a completed reference while reconstructing Cholec80's convention.
