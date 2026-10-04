# Training and Annotation Rollout

## Goal

Reconstruct the annotation convention demonstrated by Cholec80, turn it into a lightweight clinician training package, test that package internally, adapt it explicitly to the project's partial and instrument-variable videos, review it first with Dr Olugbami, and only then begin the 15-video clinical annotation set.

## Workstreams in order

### V4 — Infer Cholec80 rules while creating clips

Review the ten converted reference cases once. For every supplied transition, use a one-minute clip containing 30 seconds before and 30 seconds after the exact Cholec80 boundary. While watching, update `INFERRED_CHOLEC80_RULES.md` with the visible before/after activity and the rule that appears to explain Cholec80's decision. Additional non-boundary clips may be requested for clear within-phase activity, exceptions, missing phases, or unusual order.

Output: an evidence draft plus an indexed reference clip library. The source boundary remains authoritative for this reconstruction exercise.

### V5 — Build the first clinician package

Create a separate doctor-facing `ANNOTATION_PROTOCOL.md` from the accumulated evidence. Package:

- Phase Annotator 0.1.1 or its approved successor;
- the software user guide;
- the annotation protocol with class definitions, boundary rules, Undefined use, and partial-video rules;
- an indexed folder of short transition clips referenced by clip ID;
- a short local-differences guide;
- practice instructions and scoring instructions.

The primary format should be a concise PDF/HTML document plus ordinary video files in an indexed folder. Do not embed approximately 20 clips in the primary PowerPoint: it creates a large, fragile file and makes clip replacement/versioning harder. A small presentation may be produced later for a live teaching session, but it is not the source of truth.

### V6 — Internal blind rehearsal on three Cholec80 cases

Use three of the five seeded blind cases, reduced from the earlier five-case plan. Keep their protected Cholec80 references inaccessible while annotating. Afterwards, compare the application JSON with the reference using a reproducible offline scoring report.

Use the first three cases from the reproducible blind assignment: `video67`, `video39`, and `video07`. Retain `video03` and `video61` untouched as reserve cases. This preserves a documented selection rule instead of choosing exercises after seeing their difficulty.

The scoring contract must be agreed before implementation. At minimum it should report duration-weighted/framewise phase agreement and transition-boundary differences with stated tolerances; a single unexplained score is insufficient. Use errors to clarify the protocol and training clips, not to rewrite the source reference.

Retain the other two Cholec80 blind cases as unused reserve material rather than quietly converting them into training examples.

### V7 — Local adaptation on two project videos

Annotate two representative project videos after the Cholec80 rehearsal. These are not Cholec80-scored because no Cholec80 gold label exists. Use them to document where project data differs:

- recordings may begin or end mid-procedure;
- every expected phase may not be present;
- instruments may differ from Cholec80 examples;
- visual quality, camera position, or workflow may differ;
- Undefined may be needed for unclassifiable footage.

Review these two annotations and the differences guide with Dr Olugbami. The key adaptation remains: annotate only observable footage, cover the available timeline, and never invent absent or unrecorded phases.

### V8 — Dr Olugbami pilot and clinical review

Send the package to Dr Olugbami first. Ask for review of clinical terminology, inferred transition rules, local differences, clip usefulness, installation/usability, and exercise clarity. Record requested changes and publish a versioned protocol/package revision before wider use.

### V9 — Fifteen-video clinical annotation set

After the pilot is accepted, provide doctors with the application, user guide, approved protocol, clip library, local-differences guide, and any agreed practice/scoring material. The 15 project videos are the real annotation task, not additional training examples. Define assignment, completion, support, data-return, and quality-review procedures before distribution.

## Package layout

```text
clinician_package/
├── application/
├── user_guide/
├── protocol/
│   ├── annotation_protocol.pdf
│   └── local_video_differences.pdf
├── clip_library/
│   ├── index.html
│   └── clips/
├── exercises/
│   ├── instructions.pdf
│   └── scoring_guide.pdf
└── licence_and_attribution/
```

Dataset-derived clips remain subject to Cholec80's terms. Confirm that the intended recipients and distribution method comply before sending the package.
