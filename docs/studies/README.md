# Post-Release Validation and Training Programme

Status: **Two finished clinician pilot annotations returned; V7 boundary review ready.** Ten Cholec80 reference cases produced 58 labelled transition clips and an initial clinician-review protocol. Both local pilot sidecars pass automated validation in Phase Annotator 0.1.2. They remain technically marked Draft because the separate completion action was missed; the project lead confirms the annotation work was finished. Structured clinician feedback is still pending.

## Current sequence

```text
V1  Inspect Cholec80 and reproducibly select the reference cohort       Complete
 ↓
V2  Implement the Cholec80 label-to-Phase-Annotator converter          Complete
 ↓
V3  Validate one converted case visually                               Complete
 ↓
V4  Infer rules from 10 reference cases and create labelled clips      Complete
 ↓
V5  Assemble application, user guide, draft protocol, and pilot files  Complete
 ↓
V6  Clinician returns 2 annotations; completion/feedback pending        Partial
 ↓
V7  Intake, jointly review annotations, and revise protocol/application Active
 ↓
V8  Approve and begin the 15-video clinical annotation set
```

## Current pilot decision

The previous plan for three blind Cholec80 annotations and two researcher-annotated local cases has been cancelled. Instead, the first clinician reviewer will annotate two selected local videos from scratch. This is a faster and more relevant test of whether the draft convention transfers to local instruments, recording coverage, and workflow.

Because the local videos have no Cholec80 gold labels, this pilot produces clinical review evidence rather than a Cholec80 accuracy score. The first returned labels are not automatically final ground truth; they must be reviewed with the clinician.

The pilot package contains:

- the approved Phase Annotator Windows application folder;
- the Phase Annotator User Guide;
- the draft Laparoscopic Cholecystectomy Phase Annotation Protocol;
- the consolidated `START HERE` pilot instructions;
- `LOCAL-01` / `20260505_221257.mp4`;
- `LOCAL-02` / `20260519_215628.mp4`.

The clinician must choose **Cholecystectomy** when the application starts.

## Agreed annotation rule

Label only what is observable in the available recording. Every available millisecond must be covered, but every expected surgical phase does not need to appear. Use Undefined for footage that cannot be assigned confidently; never fabricate an absent phase or an unrecorded continuation. A recording may start during a later phase or end before the procedure is complete. Full timeline coverage does not mean full procedure coverage.

## How findings are handled

- A reproducible software defect becomes a focused application issue with data-integrity impact recorded.
- A usability irritation is recorded by frequency and consequence before redesign.
- A disagreement about phase meaning is a protocol/clinical-review issue, not automatically a software bug.
- A severe defect can explicitly reopen application development; minor findings may remain study observations or backlog items.
- Returned pilot JSON must be preserved before any reviewed correction is made.

## Documents and evidence

- [`CHOLEC80_DERIVED_TRAINING_MANUAL.md`](CHOLEC80_DERIVED_TRAINING_MANUAL.md): preserved operational convention inferred from ten Cholec80 reference cases.
- [`OAUTHC_CHOLECYSTECTOMY_TRAINING_MANUAL.md`](OAUTHC_CHOLECYSTECTOMY_TRAINING_MANUAL.md): current OAUTHC clinical adaptation and primary instruction for the next review stage.
- [`evidence/ROUGH_CHOLEC80_REVIEW_NOTES_2026-10-04.md`](evidence/ROUGH_CHOLEC80_REVIEW_NOTES_2026-10-04.md): archived case-by-case reasoning and uncertainty; not annotation instructions.
- [`V4_REFERENCE_WALKTHROUGHS.md`](V4_REFERENCE_WALKTHROUGHS.md): conversion, clip, and walkthrough evidence.
- [`LOCAL_PILOT_COHORT.md`](LOCAL_PILOT_COHORT.md): stable record of the two local pilot videos.
- [`CLINICIAN_PACKAGE_START_HERE.md`](CLINICIAN_PACKAGE_START_HERE.md): consolidated pilot purpose, package guide, annotation steps, feedback, return, and support instructions.
- [`LOCAL_VIDEO_DIFFERENCES_DRAFT.md`](LOCAL_VIDEO_DIFFERENCES_DRAFT.md): local differences to revise from pilot evidence.
- [`V7_CLINICIAN_PILOT_REVIEW.md`](V7_CLINICIAN_PILOT_REVIEW.md): controlled intake, joint-review questions, outputs, and rollout gate for the returned pilot annotations.
- [`TRAINING_AND_ANNOTATION_ROLLOUT.md`](TRAINING_AND_ANNOTATION_ROLLOUT.md): current packaging, pilot, review, and wider-rollout workflow.
- [`REAL_VIDEO_VALIDATION_AND_TRAINING_PLAN.md`](REAL_VIDEO_VALIDATION_AND_TRAINING_PLAN.md): detailed historical study contract; superseded sections are identified within it.

The editable source documents are Markdown. Distribute versioned PDFs to clinicians so page content cannot be accidentally modified. HTML may be added later for a searchable clip index, but it is not required for this first pilot.
