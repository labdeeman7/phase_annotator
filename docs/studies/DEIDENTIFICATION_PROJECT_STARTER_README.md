# Surgical Video De-identification Project

## Purpose

This is a separate operational project for preparing surgical videos for human de-identification review. It must not be mixed with the Phase Annotator application or its annotation data.

The immediate goal is to:

1. run CAMMA's out-of-body detector (OoBNet) on a folder of surgical videos;
2. convert the model output into candidate LosslessCut project sidecars;
3. verify the workflow on one video as quickly as possible;
4. batch-process the remaining videos only after that example is accepted; and
5. assemble a simple package that authorised students can review in LosslessCut.

OoBNet output is **not proof that a video is de-identified**. It is a candidate interval generator. Every video must be reviewed completely by an authorised person, corrected where necessary, and quality checked before it is approved for research use.

## Instructions for Codex

Act as the senior software engineer responsible for building and validating this pipeline. Explain the important decisions to the project owner, but do not transfer the core implementation work to them.

Before making functional changes:

1. Read this README completely.
2. Inspect every file in the repository, including the supplied LosslessCut example and any existing scripts or notes.
3. Run `git status --short` and preserve unrelated work.
4. Inspect the current official documentation, code, model requirements, output format and licence of `CAMMA-public/out-of-body-detector`. Do not infer its interface from memory.
5. Inspect the supplied LosslessCut sidecar as the primary local example of the expected project format. Determine whether it describes segments to keep, segments to remove, or both. Preserve fields that are not yet understood.
6. Check the installed Python versions and available GPU/runtime before choosing an environment. OoBNet may have older dependency constraints; do not assume the newest Python version will work.
7. Propose any necessary revision to the plan below before implementation. Explain why, then persist the accepted revision in this README or a focused `docs/` document.

Work in small vertical slices. At the end of each slice, report:

- what now works;
- tests and commands run;
- any privacy or data-integrity risk;
- one short manual acceptance check;
- the next slice.

Do not commit or push without the project owner's approval. Never commit videos, model outputs, LosslessCut projects derived from real videos, absolute source paths, personal information, or packaged reviewer material.

## Expected initial repository contents

The project owner expects to place approximately the following in the new repository:

```text
repository/
├── README.md
├── input_videos/                 # restricted real videos; ignored by Git
└── examples/
    ├── example_video.*           # preferably a non-identifiable test copy
    └── example_losslesscut.*     # accepted LosslessCut project/sidecar
```

The exact video and sidecar extensions must be discovered from the files rather than assumed.

Immediately add protective ignore rules before generating outputs. At minimum, ignore the real input/output directories, common video formats, model weights, predictions, temporary frames, generated reviewer packages, virtual environments and machine-specific configuration. Confirm with `git status --short` that real data are not tracked.

## Safety and data-handling rules

- Treat every original and model-processed video as potentially identifiable.
- Only people authorised to see the original recordings may perform review.
- Do not upload videos, frames or predictions to public services or source control.
- Do not log patient identifiers or embed them in filenames, screenshots or fixtures.
- Do not call a video `deidentified`, `safe`, `approved` or equivalent merely because OoBNet processed it.
- The model must not be the release authority. Human review of the complete video is mandatory.
- False negatives are the principal safety risk: an out-of-body interval missed by the model can expose identifying information.
- Add configurable temporal safety padding around proposed removal intervals. Record the actual value used.
- Preserve source videos unchanged. All generated artifacts must go to separate output directories.
- Do not overwrite the supplied accepted LosslessCut example.
- Use synthetic fixtures in automated tests. Do not copy real video paths, frames or sidecars into committed tests.
- Never invoke an unknown executable from `PATH` without documenting its origin. Record the provenance and licence of OoBNet, FFmpeg and LosslessCut dependencies.
- Packaging for students must use the project's approved secure transfer route, not GitHub or a public file-sharing link.

## Workflow states

Track each video separately using these operational states:

```text
unprocessed
model_processed
candidate_project_created
human_reviewed
quality_checked
approved_for_research
```

Only a designated human quality-control decision may move a video to `approved_for_research`. Store status separately from the video and do not silently infer it from the presence of an output file.

## Implementation plan

### D0 — Handover and environment

Goal: understand the actual files and obtain a reproducible OoBNet runtime.

- Inventory repository contents without exposing sensitive filenames unnecessarily.
- Inspect the LosslessCut example structure and document its time units and segment semantics.
- Inspect the OoBNet repository, paper-linked implementation, dependency constraints, weights and licence.
- Create a local virtual environment named `.venv` unless OoBNet requires an incompatible isolated environment, in which case explain and document the chosen environment name.
- Prefer a standard Python virtual environment. Use Conda only if a dependency genuinely requires it.
- Install dependencies reproducibly and record exact setup commands.
- Add a short environment diagnostic covering Python, PyTorch, CUDA availability and OoBNet import/model loading.
- Run the smallest official smoke test available before processing real video.

Acceptance: the model loads locally and the setup can be recreated from documented commands.

### D1 — One-video OoBNet inference

Goal: run OoBNet on one copied working video and preserve raw predictions.

- Choose one representative video with the project owner.
- Run inference without modifying the source.
- Save raw frame/timestamp scores and all inference parameters in a machine-readable artifact.
- Record model version/commit, weights, threshold, video timing evidence, sampling rate and execution date.
- Confirm whether output timestamps refer to decoded frames, source frame numbers or sampled observations.
- Do not collapse the raw scores irreversibly into intervals.

Acceptance: raw predictions can be inspected and regenerated for the same input.

### D2 — Candidate interval generation

Goal: convert raw scores into conservative proposed out-of-body intervals.

- Define thresholding explicitly.
- Group adjacent positive observations using documented timing rules.
- Apply configurable padding before and after each event.
- Clamp intervals to video bounds.
- Merge overlapping or touching padded intervals.
- Preserve short events; do not discard them merely because they are brief.
- Produce a readable interval report alongside the machine-readable result.
- Add unit tests for empty predictions, first/last-frame events, overlapping padding, adjacent events, timestamp rounding and video-bound clamping.

Acceptance: the project owner can inspect the proposed intervals for the first video before LosslessCut conversion.

### D3 — LosslessCut conversion

Goal: generate a candidate LosslessCut project that behaves like the supplied example.

- Derive the format from the supplied accepted sidecar and, where needed, current official LosslessCut documentation/source.
- Determine whether the review workflow should display proposed removal regions directly or derive complementary keep regions.
- Preserve required metadata and unknown compatible fields from the example.
- Use the exact source-video filename/path convention LosslessCut requires, while preventing machine-specific paths from entering committed fixtures.
- Refuse ambiguous, negative, overlapping or out-of-bounds segments.
- Never overwrite the accepted example or a human-corrected project.
- Add a clear marker in generated metadata or the adjacent manifest that this is an automated candidate requiring full review.

Acceptance: open the generated project in LosslessCut beside the copied test video and confirm that intervals appear at the expected times and have the intended keep/remove meaning.

This is the first major go/no-go gate. Do not batch-process all videos until the owner accepts this manual check.

### D4 — End-to-end one-video review

Goal: prove that a person can correct and return the candidate project.

- Prepare one minimal reviewer folder containing the video, candidate LosslessCut project and concise instructions.
- Have the owner inspect the entire video, not only model-positive intervals.
- Confirm that corrections can be saved without destroying raw predictions or the generated original.
- Decide the naming convention for generated, human-reviewed and quality-checked sidecars.
- Record issues and revise interval/conversion rules before batching.

Acceptance: one complete correction round trip works and the corrected project can be distinguished from the automated candidate.

### D5 — Batch processing

Goal: create review candidates for the remaining authorised videos.

- Add resumable batch processing so one failure does not discard completed work.
- Never overwrite existing human-reviewed files.
- Produce one manifest row per video with a non-identifying case ID, processing state, tool/model version, threshold, padding, candidate interval count and error status.
- Report failures explicitly and continue only where safe.
- Check that every input has either a candidate project or a recorded failure.

Acceptance: expected input count equals successful candidates plus explicit failures, with no silent omissions.

### D6 — Student review package

Goal: assemble a simple, safe package for authorised student reviewers.

The package should be easy to understand:

```text
student_review_package/
├── 00_START_HERE.pdf-or.html
├── LosslessCut/                  # only if redistribution is permitted
├── assignments/
│   ├── CASE-001/
│   │   ├── video.*
│   │   ├── CASE-001.model-candidate.<sidecar-extension>
│   │   └── REVIEW_INSTRUCTIONS.txt
│   └── ...
└── return_reviewed_projects_here/
```

- First verify LosslessCut's licence and preferred distribution method. If bundling is inappropriate, provide an official download/install link and tested version instead.
- Do not require students to install Python or run OoBNet.
- Give every reviewer a small acceptance exercise before assigning real cases.
- Explain how to open the candidate, inspect the full video, add missed intervals, remove false alarms, save without overwriting the candidate, and return the corrected project.
- Include examples of information requiring removal: patient or staff faces, names, hospital numbers, documents, monitor overlays containing identifiers, theatre surroundings and any other identifying out-of-body content.
- State that uncertain material should remain marked for removal and be escalated.
- Package only the cases assigned to each authorised reviewer where practical; do not distribute the entire corpus unnecessarily.
- Generate a file inventory and verify the archive can be opened before transfer.

Acceptance: the owner can follow `00_START_HERE` on a clean machine and open one assigned candidate in LosslessCut without Python or developer knowledge.

### D7 — Review intake and quality control

Goal: receive corrections without confusing them with model output.

- Preserve each returned sidecar unchanged before review.
- Validate its syntax, video association and interval bounds.
- Compare candidate and returned intervals to summarise human corrections without treating absence of corrections as proof of safety.
- Require a second quality-control check according to the project's approved procedure.
- Update status explicitly; never infer approval from filenames alone.

Acceptance: every approved video has identifiable model, human-review and quality-control provenance without containing patient-identifying metadata.

## Required persistent documentation

As implementation progresses, keep these concise documents:

- `README.md`: purpose, safety constraints, setup, commands and current status.
- `docs/ARCHITECTURE.md`: raw predictions → intervals → LosslessCut conversion → review.
- `docs/DATA_MODEL.md`: prediction, interval, manifest and status schemas.
- `docs/REVIEW_PROTOCOL.md`: exact full-video human-review and quality-control procedure.
- `docs/STUDENT_PACKAGE.md`: how packages are assembled and returned.
- `docs/DECISIONS.md`: important choices such as thresholds, padding and keep/remove semantics.

Keep research evaluation optional and separate from the operational pipeline. The immediate objective is safe assisted review, not a publication about OoBNet.

## Minimum provenance

Retain, locally and securely:

- pseudonymous case ID;
- original filename mapping in restricted storage only;
- OoBNet repository commit/version;
- weight identifier and provenance;
- dependency/environment versions;
- threshold and temporal grouping rule;
- padding before and after predictions;
- source timing/FPS evidence;
- generated candidate path;
- assigned reviewer;
- review and quality-control status;
- processing errors and resolutions.

Do not use full video hashes unless a specific operational requirement justifies their computational cost. Never expose absolute paths in shared packages or committed examples.

## Student-facing core instruction

Use this meaning consistently in all generated guidance:

> The automated detector only proposes possible out-of-body sections. It can miss identifying information and can also mark safe footage incorrectly. Review the complete video from beginning to end, correct every interval in LosslessCut, and do not describe the video as de-identified until the required human review and quality-control steps are complete.

## Definition of done for the urgent first delivery

The first-night delivery is complete only when:

- the environment and OoBNet model load reproducibly;
- one candidate has been manually opened and accepted in LosslessCut;
- all remaining inputs have either a generated candidate or an explicit failure;
- no real media or derived sidecar is tracked by Git;
- reviewer instructions clearly require full-video review;
- the student archive opens successfully;
- original videos and model predictions remain preserved separately;
- nothing is labelled approved or de-identified solely because the model processed it.
