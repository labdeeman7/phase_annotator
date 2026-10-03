# Real-Video Validation and Cholecystectomy Training Plan

## Why this is separate from C10

Finishing the application release, exercising it over many real videos, and defining clinical annotation rules answer different questions:

| Workstream | Main question | Output |
| --- | --- | --- |
| C10 release documentation and acceptance | Can a new user install and operate the current software safely? | User/developer/release guides and release candidate |
| Extended real-video validation | Does the application remain correct and usable during sustained work on realistic cases? | Structured findings, defects, timings, and accepted fixes |
| Clinical training and protocol | How should clinicians consistently decide cholecystectomy phase transitions? | Worked examples, practice cases, and an approved protocol |

The recommended sequence is to finish C10 first, then perform extended validation, then finalise training material and the clinical protocol. Severe defects discovered during validation can reopen the application milestone explicitly.

## Dataset boundary

Cholec80 is available for non-commercial research under stated licence terms, but public/research availability is not the same as unrestricted reuse. Before distributing videos, frames, screenshots, or derived annotations, retain and review the exact licence/terms supplied with the local dataset and apply its attribution and share-alike requirements where relevant.

Repository rules:

- Do not commit videos, extracted frames, original labels, converted labels, local/NAS paths, or identifiable reviewer records.
- Keep dataset locations as runtime arguments or ignored local configuration.
- Do not copy the dataset merely to make the converter convenient; choose one authorised source and stage only the needed cases locally when required.
- Cite the Cholec80 source publication in any resulting research or training document that uses it.

## Cohort: 15 videos

Fifteen cases are sufficient for the first structured pass and more achievable than twenty. Select them reproducibly rather than manually cherry-picking them:

1. Inventory the available video IDs and corresponding phase-label files.
2. Sort the eligible IDs.
3. Use a recorded pseudo-random seed to sample 15 unique IDs.
4. Record the selected IDs, seed, selection date, exclusions, and dataset copy/version in a local study manifest.
5. Randomly assign 10 cases to reference walkthrough and 5 cases to blind practice using the same recorded process.

Random sampling limits selection bias but does not guarantee that rare transitions or difficult cases appear. After the random pass, any deliberately selected edge cases must be labelled as a separate targeted cohort rather than quietly added to the random sample.

## Track A: ten reference walkthroughs

Convert the supplied phase labels into application-compatible reference JSON, then load and review them in the packaged application.

This track tests:

- long-video playback and seeking;
- full timelines and large segment lists;
- source/sidecar matching and resume behavior;
- rendering, selection, correction controls, notes, completion, and reopening;
- autosave/history behavior during realistic sessions;
- whether converted boundaries visually correspond to the supplied labels;
- crashes, stalls, confusing feedback, and cumulative usability friction.

These cases are useful worked demonstrations, but loading existing annotations does not test annotation-from-scratch effort.

## Track B: five blind practice annotations

Keep the converted reference answers outside the videos' directories. Open each video without a canonical sidecar and annotate it from scratch.

This track tests:

- learnability and sustained annotation workload;
- hotkey and mouse efficiency;
- correction frequency and Undo/Redo usefulness;
- interruption/resume behavior;
- completion confidence;
- confusing phase or boundary decisions.

Only after the practice annotation is complete should it be compared with the protected reference. Do not copy the reference beside a practice video beforehand: the application would load it as the live canonical annotation and expose the answer.

## Conversion contract

Inspect real source files before implementation; do not assume their exact structure. The converter must then document and test:

- source row/frame semantics and whether endpoints are inclusive;
- actual video duration and FPS provenance;
- frame-to-millisecond rounding and final-interval handling;
- explicit name-based mapping from source labels to configured ontology phase IDs;
- repeated and out-of-order phases;
- unknown labels, gaps, missing files, and duration discrepancies;
- deterministic output and refusal to overwrite by default;
- validation through existing domain/storage rules.

Map by phase name, not by numeric order. The configured application order and a source dataset's label ordering must not be assumed to match.

Every converted reference should have a local manifest record containing source identifier, source annotation filename/format, ontology ID/version, FPS and duration evidence, conversion convention, converter revision, validation result, and review status. Conversion must not pretend that a human created the annotation through the GUI.

## Structured validation record

For each case record:

- cohort and video ID;
- application/artifact version;
- Windows machine and display scale;
- video duration, resolution, codec information available through the application, and FPS provenance;
- session start/end and interruption points;
- pass/fail for open, playback, seek, annotate/load, correct, autosave, resume, complete, and reopen;
- defects with reproduction steps and severity;
- usability friction and frequency;
- ambiguous clinical transitions separately from software defects;
- whether any files required manual recovery.

Do not call this a formal multi-user usability study unless a study design, participants, consent/ethics requirements, outcomes, and analysis plan have been agreed. The first pass is an **extended self-use validation**.

## Training package after validation

The 10 reference cases can supply worked examples. The 5 practice cases can supply exercises and later review discussions. Package references separately from live practice sidecars.

Recommended structure outside this repository:

```text
cholecystectomy_training/
├── worked_examples/
├── practice_videos/
├── reference_answers/
├── manifests/
└── protocol_assets/
```

The actual videos and labels remain governed dataset material. A distributable training package must include the required licence and attribution material and must not be published merely because the source is accessible for research.

## Clinical annotation protocol

Develop the protocol only after reviewing real transitions. For each configured phase, document:

- operational definition;
- observable start and end cues;
- inclusions and exclusions;
- common predecessor/successor phases;
- interruptions, repeated phases, and out-of-order activity;
- when to use Undefined;
- difficult examples with timestamped rationale;
- unresolved questions and the clinical owner who decided them.

Converted source labels are a reference, not automatic proof that every boundary should become the local protocol. Disagreements and uncertain examples should be reviewed with the clinical owner and versioned.

## Execution plan

### V1 — Intake and reproducible selection

- Confirm the exact local dataset terms and source layout.
- Inventory video/label pairs without modifying the source.
- Sample and assign 15 cases using a recorded seed.

### V2 — Converter contract and synthetic tests

- Inspect representative source annotations and video metadata.
- Write expected conversions for boundary edge cases.
- Implement a path-agnostic converter under `scripts/` with synthetic tests and overwrite protection.

### V3 — One-case trial

- Convert one reference case.
- Validate the JSON and inspect several transitions against the source.
- Correct the contract before batch processing.

### V4 — Ten reference walkthroughs

- Convert and review the reference cohort in the packaged application.
- Record application defects and usability findings systematically.

### V5 — Five blind practice cases

- Annotate without adjacent reference sidecars.
- Compare only after completion and record both UI friction and clinical disagreements.

### V6 — Protocol and training material

- Resolve transition questions with the clinical owner.
- Produce worked examples, exercises, approved images, and the versioned protocol.

## Decisions required before V1

1. Confirm whether the intended training distribution is internal research use only.
2. Identify the clinical owner for transition-rule decisions.
3. Decide where the ignored local study manifest and converted references will live.
4. Confirm whether five full blind annotations are feasible or whether a timed subset is more realistic.
5. Decide whether reference comparison is initially manual; an in-application scoring mode is a separate feature and is not assumed.

## First session today

Finish the remaining C10.6 documentation structure first. If time remains, begin V1 with read-only inspection of one chosen dataset source and create the eligible-ID inventory. Do not copy all 15 videos or implement conversion until the real label semantics and local licence file have been checked.
