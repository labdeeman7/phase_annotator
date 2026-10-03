# Post-Release Validation and Training Programme

Status: **Ready to begin V1.** Phase Annotator 0.1.0 has completed C10 release engineering and clean-machine acceptance. This programme now asks how the accepted application behaves during sustained use on real cholecystectomy videos and how reviewed cases should support clinician training.

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

## What happens if we find problems

- A reproducible software defect becomes a focused application issue, with severity and data-integrity impact recorded.
- A usability irritation is recorded by frequency and consequence before redesign.
- A disagreement about phase meaning goes to the clinical protocol question log rather than being treated as a software bug.
- A severe defect can explicitly reopen application development and produce a new release candidate; minor observations can remain study findings or backlog items.

## Immediate next session: V1

1. Choose one authorised source copy (DGX or NAS) for read-only inventory.
2. Locate and retain the exact dataset terms accompanying that copy.
3. Inspect actual video and phase-label filenames and file format; do not assume the format from memory.
4. Identify valid video/label pairs and exclusions.
5. Sample 15 unique cases from the sorted eligible IDs using a recorded random seed.
6. Assign 10 to reference walkthrough and 5 to blind practice, and save only the non-patient case IDs plus selection metadata in a local study manifest.

Do not copy all 15 videos or write the converter until V1 establishes the real source layout and V2 defines frame/timestamp boundary semantics.

See [`REAL_VIDEO_VALIDATION_AND_TRAINING_PLAN.md`](REAL_VIDEO_VALIDATION_AND_TRAINING_PLAN.md) for the complete contract, evidence fields, and governance boundaries.
