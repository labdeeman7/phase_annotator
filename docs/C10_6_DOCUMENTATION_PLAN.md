# C10.6 Documentation Plan

Status: **Complete.** The clinician, developer, release, limitations, release-notes, and clean-machine acceptance documents are linked from the repository README. The clinician guide contains a repository-safe annotated interface map; governed clinical examples remain part of the separate post-release training work.

## Purpose

C10.6 documents the software and its release. It does not require completion of the proposed Cholec80 evaluation or a clinical annotation protocol. Keeping that boundary allows the application release to finish before the larger research and training work begins.

## Deliverables

### Clinician user guide

Create a concise illustrated guide covering:

- downloading and extracting the complete Windows application folder;
- launching the executable and entering the annotator's first name;
- selecting appendectomy or laparoscopic cholecystectomy;
- opening a video and understanding initial timeline coverage;
- playback, speed, seeking, frame stepping, phase buttons, and hotkeys;
- selecting timeline intervals and segment cards;
- correcting labels and boundaries, converting to Undefined, merging, Undo/Redo, and notes;
- automatic saving, canonical sidecar location, history, resume position, completion, and reopening;
- procedure-mismatch and invalid-sidecar messages;
- keeping the video and its JSON sidecar together;
- privacy, supported-environment, collaboration, frame-estimation, codec, and prototype limitations.

Use annotated screenshots with numbered callouts and short task-oriented explanations. General UI screenshots should use synthetic or disposable media. Clinically derived screenshots can be added later only under the applicable dataset terms and project governance.

### Developer guide

- supported Python environment and editable installation;
- repository architecture and entry points;
- validation commands and test boundaries;
- ontology/resource configuration;
- persistence and data-integrity constraints;
- how to make and validate a focused change.

### Release guide

- clean CPython and PyInstaller build procedure;
- GitHub Actions validation and manually dispatched artifact build;
- artifact download, versioning, release notes, and ZIP preparation;
- clean-machine acceptance procedure;
- release checklist and rollback/known-failure recording.

### Known limitations

Maintain one clear list of supported and unsupported behavior, including Windows/media scope, approximate frame conversion, VFR limitations, sequential rather than concurrent annotators, local sidecars/history, prototype audit limitations, and deferred exports/installers/platforms.

## Screenshot rules

- Capture the release-candidate UI at a consistent display scale and window size.
- Use callout numbers and captions rather than dense prose over the interface.
- Do not show names, local absolute paths, patient information, or real canonical sidecars.
- Keep source images separate from rendered documentation so callouts can be updated.
- Record the application version used for the screenshots.

## Exit gate

- A first-time clinician can extract, launch, annotate, correct, resume, and complete a disposable case using only the user guide.
- A developer can reconstruct and validate the project from a clean checkout.
- A release operator can reproduce the Windows artifact and its acceptance checks.
- Limitations are visible rather than implied.

## Reading and review order

1. Review the user-guide outline and terminology.
2. Capture the required screenshots from the current release candidate.
3. Walk through the draft as a new user and correct missing steps.
4. Consolidate developer/release material already present across repository documents.
5. Complete C10.7 against the exact documented artifact.

The separate real-video evaluation and clinical training/protocol work is planned in `REAL_VIDEO_VALIDATION_AND_TRAINING_PLAN.md`.
