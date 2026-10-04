# Post-Release Validation and Training Programme

Status: **V3 complete; V4 reference walkthroughs next.** Phase Annotator 0.1.0 has completed C10 release engineering and clean-machine acceptance. The DGX Cholec80 copy has been inventoried read-only, a reproducible 15-case cohort selected, and the converter contract has passed synthetic and one-case visual validation. This programme now asks how the accepted application behaves during sustained use on the remaining real cholecystectomy videos and how reviewed cases should support clinician training.

## The sequence we agreed

```text
V1  Inspect the authorised Cholec80 copy and reproducibly select 15 videos
 ↓
V2  Define and implement the source-label → Phase Annotator JSON converter
 ↓
V3  Trial one converted case and verify boundary semantics visually
 ↓
V4  Infer Cholec80 rules while reviewing 10 reference cases and clips
 ↓
V5  Build the doctor-facing protocol and indexed clip package
 ↓
V6  Annotate 3 Cholec80 cases blindly and score against references
 ↓
V7  Annotate 2 project videos and document local differences
 ↓
V8  Pilot first with Dr Olugbami and revise
 ↓
V9  Begin the 15-video clinical annotation set
```

## Why there are two kinds of testing

The 10 **reference walkthroughs** load converted source labels. They test compatibility, long-video playback, timeline and segment-list behavior, navigation, correction, persistence, and cumulative friction on realistic annotations.

Three of the five seeded **blind practice cases** will begin without a canonical sidecar. They test annotation-from-scratch and support offline comparison with protected Cholec80 references. The other two remain unused reserve cases. Two separate project videos then test adaptation to partial recordings, different instruments, and local workflow without pretending that Cholec80 gold labels exist for them.

This first pass is an **extended self-use validation**, not yet a formal multi-participant usability study. A formal study would additionally require agreed participants, outcomes, procedures, ethics/consent considerations, and an analysis plan.

## Agreed annotation rule

Label only what is observable in the available recording. Every available millisecond must be covered, but every expected surgical phase does not need to appear. Use Undefined for footage that cannot be assigned confidently; never fabricate an absent phase or an unrecorded continuation. A recording may start during a later phase or end before the procedure is complete. Full timeline coverage does not mean full procedure coverage.

## What happens if we find problems

- A reproducible software defect becomes a focused application issue, with severity and data-integrity impact recorded.
- A usability irritation is recorded by frequency and consequence before redesign.
- A disagreement about phase meaning goes to the clinical protocol question log rather than being treated as a software bug.
- A severe defect can explicitly reopen application development and produce a new release candidate; minor observations can remain study findings or backlog items.

## Completed V1

The existing DGX copy was inspected without modifying or copying video. All 80 MP4/TXT pairs passed filename, header, contiguous-frame, and vocabulary checks. Seed `20261003` reproducibly selected 10 reference and 5 blind cases. See [`V1_INTAKE_AND_SELECTION.md`](V1_INTAKE_AND_SELECTION.md) and the machine-readable cohort manifest under `cohorts/`.

## Completed V2–V3 and immediate next session: V4

The exact 25 FPS source-frame to half-open millisecond interval contract, final-duration handling, label-to-ontology mapping, converter provenance, and overwrite/reference separation are implemented and synthetically tested. See [`V2_CONVERSION_CONTRACT.md`](V2_CONVERSION_CONTRACT.md). In V3, `video04` loaded successfully and all six transitions plus final coverage were visually accepted. V4 can now convert and review the remaining nine seeded reference cases.

See [`REAL_VIDEO_VALIDATION_AND_TRAINING_PLAN.md`](REAL_VIDEO_VALIDATION_AND_TRAINING_PLAN.md) for the complete contract, evidence fields, and governance boundaries.

The evolving phase definitions and per-boundary evidence log live in [`INFERRED_CHOLEC80_RULES.md`](INFERRED_CHOLEC80_RULES.md). It is a reverse-engineering notebook, not yet the approved doctor-facing protocol.

V4 case staging, rule inference, clip creation, and per-case review fields are tracked in [`V4_REFERENCE_WALKTHROUGHS.md`](V4_REFERENCE_WALKTHROUGHS.md). The complete protocol/training/practice/pilot/rollout sequence is in [`TRAINING_AND_ANNOTATION_ROLLOUT.md`](TRAINING_AND_ANNOTATION_ROLLOUT.md), and known departures from Cholec80 are being collected separately in [`LOCAL_VIDEO_DIFFERENCES_DRAFT.md`](LOCAL_VIDEO_DIFFERENCES_DRAFT.md).
