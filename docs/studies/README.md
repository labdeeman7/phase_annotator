# Post-Release Validation and Training Programme

Status: **V2 implemented; V3 one-case trial next.** Phase Annotator 0.1.0 has completed C10 release engineering and clean-machine acceptance. The DGX Cholec80 copy has been inventoried read-only, a reproducible 15-case cohort selected, and a provenance-preserving converter tested synthetically. This programme now asks how the accepted application behaves during sustained use on those real cholecystectomy videos and how reviewed cases should support clinician training.

## The sequence we agreed

```text
V1  Inspect the authorised Cholec80 copy and reproducibly select 15 videos
 ↓
V2  Define and implement the source-label → Phase Annotator JSON converter
 ↓
V3  Trial one converted case and verify boundary semantics visually
 ↓
V4  Review 10 converted reference cases in the packaged application
 ↓
V5  Annotate 5 cases blindly, then compare with protected references
 ↓
V6  Turn reviewed examples into training material and a clinical protocol
```

## Why there are two kinds of testing

The 10 **reference walkthroughs** load converted source labels. They test compatibility, long-video playback, timeline and segment-list behavior, navigation, correction, persistence, and cumulative friction on realistic annotations.

The 5 **blind practice cases** begin without a canonical sidecar. They test the real annotation-from-scratch experience: learnability, speed, corrections, interruption/resume, completion confidence, and ambiguous transition decisions. Reference answers remain separate until each practice annotation is complete.

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

## Completed V2 and immediate next session: V3

The exact 25 FPS source-frame to half-open millisecond interval contract, final-duration handling, label-to-ontology mapping, converter provenance, and overwrite/reference separation are implemented and synthetically tested. See [`V2_CONVERSION_CONTRACT.md`](V2_CONVERSION_CONTRACT.md). V3 stages only one reference case, obtains its Qt duration, converts it, and visually checks real boundaries before any batch conversion.

See [`REAL_VIDEO_VALIDATION_AND_TRAINING_PLAN.md`](REAL_VIDEO_VALIDATION_AND_TRAINING_PLAN.md) for the complete contract, evidence fields, and governance boundaries.

The evolving phase definitions and per-boundary evidence log live in [`protocol.md`](protocol.md). It is an observational working draft, not yet an approved student protocol.
