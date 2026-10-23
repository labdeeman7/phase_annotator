# Phase Annotator to Dataset Curator Handover

Status: **Migration instructions — copy, verify, confirm, then remove**

Date prepared: 18 October 2026

## Purpose

The Phase Annotator repository began as a desktop annotation application, but it gradually accumulated clinical-protocol work, dataset registries, training material, study planning, presentations, conversion utilities, and clinician-package generation. Those responsibilities now belong in the OAUTHC dataset-curation repository.

This document is written for the Codex session taking over the curator repository. It should be usable without access to the conversation that produced it.

The migration must be performed in four explicit stages:

1. **Copy** the listed material into a coherent curator-owned structure.
2. **Verify** that source documents, scripts, manifests, links, and generated outputs still work.
3. **Confirm** the completed inventory and validation results with Tosin.
4. **Remove** the transferred originals from Phase Annotator only after that confirmation, in a separate cleanup commit.

Do not combine the copy and deletion into one operation. Do not delete the only copy of any document, annotation, registry, video, clip, PDF, presentation, or generated package.

## Ownership boundary

### Dataset curator owns

- the clinical definition of each phase and its boundaries;
- OAUTHC-specific adaptations to Cholec80;
- unusual or candidate activities such as gallbladder drainage;
- annotation protocols, training manuals, transition examples, and clinician instructions;
- case registries, cohort selection, aliases, provenance, and annotation status;
- original/deidentified/working-copy relationships;
- deidentification records and methods;
- annotator assignment, returned sidecars, review status, and consensus status;
- Cholec80 conversion, reference cases, clips, and protocol evidence;
- study batches, clinician packages, presentations, and research planning.

### Phase Annotator continues to own

- the desktop application and its source code;
- the canonical annotation-sidecar schema and validation behavior;
- generic annotation editing, undo/redo, completion, attribution, and persistence;
- the machine-readable ontology resource format and ontology loader;
- packaged ontology resources used by released application versions;
- the canonical application user guide and application limitations;
- application tests, CI, release engineering, and Windows packaging.

The curator may propose an ontology change. For example, it may recommend adding `Gallbladder drainage` after reviewing prevalence and boundary reliability. The curator must document and approve the clinical change first. Phase Annotator should then receive a versioned ontology/configuration request and implement compatibility deliberately; the curator must not silently edit the application schema.

## Current annotation decisions that must survive the handover

1. Label the dominant visible operative task, not merely the instrument present.
2. At the P1-to-P2 boundary, hook appearance alone does not establish Calot triangle dissection. P2 begins when focused dissection of the hepatocystic triangle becomes the sustained operative objective.
3. Complex operations are not required to pass through P1-P7 once in order. Genuine recurrence such as `P1 → P2 → P1 → P2`, repeated P4, or repeated P6 must be preserved.
4. Partial recordings do not need to begin at P1 or end at P7. Annotate only what is visible while covering the complete available recording.
5. Do not remove inactive periods from historical recordings. If operative context remains clear, retain the surrounding phase; note important prolonged inactivity. Future recording practice is a separate clinical decision.
6. Purposeful gallbladder drainage is currently an **interim candidate phase**. Label the complete episode `Undefined`, add the exact note `Gallbladder drainage — candidate phase`, and resume the appropriate seven-class phase when drainage ends. This does not mean the clinical action is unknown. Do not use this rule for incidental puncture or leakage.
7. The drainage decision must be reviewed after measuring its case frequency, episode count, duration, boundary reliability, and intended model use.
8. Keep patient-identifying information out of Git, filenames used in publications, fixtures, logs, screenshots, and example annotations.

The important supporting paper is:

> Kirtac K, Aydin N, Lavanchy JL, et al. *Surgical Phase Recognition: From Public Datasets to Real-World Data*. Applied Sciences. 2022;12(17):8746. https://doi.org/10.3390/app12178746

The local PDF is presently `papers/surgical phase recognition from public datasets to real world data.pdf`. Confirm redistribution rights and repository policy before committing a copied PDF; a citation and DOI may be preferable.

## Recommended curator-repository layout

Adapt this layout to existing curator conventions rather than creating duplicate roots:

```text
docs/
  protocol/
    cholecystectomy/
      source/
      rendered/
      evidence/
  training/
  studies/
    pilot/
    shared_annotation/
  presentations/
  research_plans/
data_registry/
  cohorts/
  annotation_batches/
  schemas/
scripts/
  conversion/
  clips/
  packages/
  presentations/
private_working_data/        # ignored; never committed
generated_packages/         # ignored unless policy says otherwise
```

Preserve Git-friendly source files separately from generated PDFs, HTML, PowerPoint files, clips, ZIP files, and videos.

## Copy unchanged or with only path updates

### Protocol and training sources

- `docs/studies/CHOLEC80_DERIVED_TRAINING_MANUAL.md`
- `docs/studies/OAUTHC_CHOLECYSTECTOMY_TRAINING_MANUAL.md`
- `docs/studies/cholecystectomy_protocol/`
- `docs/studies/evidence/ROUGH_CHOLEC80_REVIEW_NOTES_2026-10-04.md`
- `docs/studies/LOCAL_VIDEO_DIFFERENCES_DRAFT.md`

The Markdown manuals are editable sources. The HTML protocol is generated material plus a small README. After migration, identify the generator as the source of truth and do not hand-edit generated pages without also updating the generator.

### Study and clinician-workflow documents

- `docs/studies/CLINICIAN_PACKAGE_START_HERE.md`
- `docs/studies/REAL_VIDEO_VALIDATION_AND_TRAINING_PLAN.md`
- `docs/studies/TRAINING_AND_ANNOTATION_ROLLOUT.md`
- `docs/studies/SHARED_ANNOTATION_STUDY_INSTRUCTIONS.md`
- `docs/studies/LOCAL_PILOT_COHORT.md`
- `docs/studies/LOCAL_STUDY_WORKSPACE.md`
- `docs/studies/V1_INTAKE_AND_SELECTION.md`
- `docs/studies/V2_CONVERSION_CONTRACT.md`
- `docs/studies/V3_ONE_CASE_TRIAL.md`
- `docs/studies/V4_REFERENCE_WALKTHROUGHS.md`
- `docs/studies/V7_CLINICIAN_PILOT_REVIEW.md`
- `docs/studies/TASKS.md`
- `docs/studies/README.md`

Some of these record superseded plans. Preserve their status and dates rather than rewriting history as if every plan remained active. Create a curator documentation map that identifies current instructions, historical evidence, and superseded plans.

### Registries and manifests

- `docs/studies/cohorts/cholec80_15_seed_20261003.json`
- `docs/presentations/2026-10-17_oauthc_annotation_meeting/annotation_batch_03_cholecystectomy.json`
- the seven-case registry if it exists in either working tree;
- conversion manifests, transition-clip manifests, package manifests, and returned-sidecar intake records found in ignored working directories.

Do not assume a registry is correct merely because it is JSON. Reconcile it against the master Excel sheet, actual storage, sidecar filenames, and known pilot/shared-study aliases. The master Excel sheet is the first curation authority to inspect, but discrepancies must be recorded rather than silently overwritten.

### Presentation material

- `docs/presentations/2026-10-17_oauthc_annotation_meeting/`
- `scripts/build_annotation_meeting_presentation.py`

The PowerPoint is generated from the script and external/local assets. Preserve `FIGURE_SOURCES.md` and `SPEAKER_NOTES.md`. After copying, replace Phase Annotator-relative asset paths with curator-relative configuration rather than embedding another developer's absolute path.

### Research and adjacent-project planning

- `docs/studies/DEIDENTIFICATION_PROJECT_STARTER_README.md`
- `docs/studies/ISBI_TECNO_HMM_PROJECT_STARTER_README.md`
- `docs/studies/ISBI_EXPERT_PROMPTED_PROJECT_STARTER_README.md`

These may ultimately move again into dedicated experiment/deidentification repositories. Until then, the curator repository is the better index because it owns dataset provenance and approved splits. Mark them as plans, not completed evidence.

## Copy, then adapt before running

### `scripts/convert_cholec80_phase.py`

Purpose: converts Cholec80 phase TXT labels and a matching video into a Phase Annotator JSON sidecar plus a conversion manifest.

Current interface:

```powershell
python scripts/convert_cholec80_phase.py LABELS_TXT VIDEO_MP4 OUTPUT_DIR [options]
```

It imports Phase Annotator domain/storage code. During migration, either:

1. install the Phase Annotator repository as an editable dependency; or
2. later extract a small, versioned interchange/schema package.

Do not duplicate the domain models informally. Record the Phase Annotator release/schema version used for every conversion. The converter refuses to overwrite existing output unless explicitly instructed; preserve that safety behavior.

### `scripts/extract_transition_clips.py`

Purpose: extracts clips around annotation boundaries and overlays the active phase name and configured colour on every frame.

Current interface:

```powershell
python scripts/extract_transition_clips.py VIDEO SESSION_JSON OUTPUT_DIR `
  --ffmpeg-path PATH_TO_FFMPEG `
  --font-path PATH_TO_FONT `
  [--context-seconds 30] [--case-id ID] [--allow-draft] [--overwrite]
```

Important behavior:

- completed annotations are required unless `--allow-draft` is deliberately used;
- FFmpeg must be supplied explicitly; never invoke an unknown executable from `PATH`;
- a manifest records clip boundaries and FFmpeg version;
- existing outputs are protected unless overwrite is explicit;
- clinical videos and generated clips must remain ignored/private.

For the current clinician protocol, transition-centred examples are preferred over isolated representative clips.

### `scripts/build_cholecystectomy_protocol_site.py`

Purpose: generates the multi-page offline HTML protocol and validates that all referenced clips exist.

Current interface:

```powershell
python scripts/build_cholecystectomy_protocol_site.py `
  --output-dir GENERATED_PROTOCOL_DIR `
  --clip-dir EXISTING_CLIP_DIR
```

The generator copies the clip directory when the source and destination differ. Review destination paths before running because an existing destination `clips/` directory is replaced. Generated `.htm` and CSS files should be rebuilt from the generator after protocol changes.

### `scripts/build_clinician_pilot_package.py`

Purpose: assembles the older two-case clinician pilot package, renders Markdown to PDF through Qt/Chromium, copies the application and selected clips/videos, and creates a ZIP.

Current interface:

```powershell
python scripts/build_clinician_pilot_package.py `
  --repository PATH_TO_PHASE_ANNOTATOR `
  --output-dir DEDICATED_OUTPUT_DIR `
  --zip-path OUTPUT_ZIP `
  --browser-path PATH_TO_EDGE_OR_CHROMIUM
```

This script reflects the earlier pilot layout (`01_Application`, `02_Guides_and_Protocol`, `03_Example_Clips`, `04_Local_Study`). It is historical and must not automatically be treated as the current shared-study builder. It deletes and recreates its dedicated output directory. Read it completely and update its layout/configuration before using it for a new batch.

### `scripts/validate_clinician_pilot_package.py`

Purpose: validates the older pilot directory, ZIP structure, clip links, video count, and required files.

Current interface:

```powershell
python scripts/validate_clinician_pilot_package.py PACKAGE_DIR ZIP_PATH PREVIEW_DIR
```

Keep validation coupled to the package version it understands. Create a new validator or versioned configuration for materially different shared-study packages rather than weakening checks until they pass.

### `scripts/build_oauthc_training_material.py`

Purpose: builds phase-organised OAUTHC/Cholec80 training examples, an HTML index, a PDF manual, and a manifest.

Current interface:

```powershell
python scripts/build_oauthc_training_material.py `
  --repository REPOSITORY `
  --output-dir DEDICATED_OUTPUT_DIR `
  --ffmpeg-path PATH_TO_FFMPEG `
  --font-path PATH_TO_FONT `
  --browser-path PATH_TO_EDGE_OR_CHROMIUM
```

This was superseded for the distributed material because its representative-phase examples were less useful than transition-centred examples. Preserve it as experimental/history until the curator decides whether to redesign or retire it. It deletes and recreates its output directory, so inspect the resolved target before running.

## Private and ignored working material

Phase Annotator ignores:

- video files (`*.mp4`, `*.avi`, `*.mkv`, `*.mov`);
- live annotation sidecars (`*.phase-annotations.json`);
- annotation-history directories;
- everything under `test_dataset/` except `.gitkeep`;
- build and distribution directories.

Therefore `git clone` or ordinary Git copying is not enough. On the source workstation, inspect the ignored working tree separately. Likely material includes:

- `test_dataset/reference_cases/`;
- Cholec80 TXT labels and converted sidecars;
- transition clips and their manifests;
- the two-case clinician pilot package;
- `test_dataset/shared_study/OAUTHC_Cholecystectomy_Shared_Study_0.1/`;
- its application copy, PDFs, HTML protocol, 18 reference clips, five study videos, and return folder;
- returned OAUTHC annotations and historical snapshots;
- any generated ZIP files.

Never add these wholesale to Git. Place them in curator-controlled private storage and keep a safe manifest in Git. Do not expose patient identifiers, source absolute paths, or clinical media in commits, logs, screenshots, or example JSON.

Do not hash full videos merely for this transfer. Verification should use expected filenames/case IDs, file counts, byte sizes, readable media metadata, sidecar validation, and manual spot checks. If a separate governance policy later requires checksums, decide that explicitly rather than adding expensive hashing casually.

## Application dependency and interchange contract

The curator repository should not copy `src/phase_annotator` wholesale. Initially, use a documented local/editable dependency on a known Phase Annotator revision when conversion or validation scripts need its models:

```powershell
python -m pip install -e "C:\path\to\phase_annotator"
```

Record at least:

- Phase Annotator application version;
- sidecar schema version;
- ontology ID and version;
- converter script revision;
- whether the sidecar is imported reference material, independent annotation, adjudicated annotation, or model output.

Longer term, consider moving schema-only validation into a small shared package. Do not create two diverging implementations of interval validity.

The application currently uses one procedure-neutral sidecar name beside each video. A sidecar with a different persisted ontology is deliberately rejected. Preserve that safety behavior when arranging datasets.

## Migration procedure

### Stage 1 — inventory before copying

1. Read this handover and the existing curator repository instructions.
2. Run `git status --short` in both repositories.
3. Record the Phase Annotator branch and commit from which the migration begins.
4. Inventory tracked files listed above.
5. Inventory ignored/private directories by filename, case ID, count, and byte size without exposing clinical content.
6. Identify user changes and uncommitted files. Do not discard or overwrite them.
7. Decide the curator destination for each item and create a migration manifest with `source`, `destination`, `kind`, `status`, and `verification` fields.

### Stage 2 — copy

1. Copy documents and registries first.
2. Copy scripts second and update their repository-relative paths/configuration.
3. Copy private/generated artifacts into ignored curator storage.
4. Preserve original filenames and manifests during the first copy. Rename only through a recorded mapping.
5. Do not modify or delete the Phase Annotator originals during this stage.
6. Commit the tracked curator sources as a dedicated handover commit.

### Stage 3 — verify and confirm

At minimum:

- compare the source/destination inventory and explain every difference;
- parse every migrated JSON file;
- validate every copied annotation sidecar with the Phase Annotator validator;
- confirm all case IDs and aliases against the master Excel sheet;
- run `python -m py_compile` on copied Python scripts;
- run relevant unit tests or move their supporting tests with the scripts;
- regenerate the HTML protocol into a temporary directory;
- open the start page and confirm navigation and video links;
- extract text from generated PDFs and check current protocol phrases;
- open the PowerPoint and check linked/embedded media behavior;
- validate clinician-package directory and ZIP contents with the matching validator;
- manually open representative videos, clips, sidecars, HTML pages, PDFs, and the packaged application;
- confirm that no patient identifiers, private absolute paths, or clinical media entered Git.

Send Tosin a migration report containing:

- copied items;
- destination paths;
- validation commands and results;
- missing or intentionally excluded items;
- unresolved discrepancies;
- proposed list of Phase Annotator paths to remove;
- curator commit ID establishing the verified new copies.

Do not proceed to deletion until Tosin explicitly confirms this report.

### Stage 4 — remove from Phase Annotator

After confirmation only:

1. Recheck both repositories and the migration manifest.
2. Remove only the confirmed transferred paths from Phase Annotator.
3. Keep a short `docs/studies/README.md` pointer stating that protocol, cohort, and study authority moved to the curator repository.
4. Keep any minimal compatibility fixtures required by application tests, but make them synthetic and document why they remain.
5. Update Phase Annotator's `AGENTS.md`, `docs/README.md`, and any broken links.
6. Run Phase Annotator's full validation suite.
7. Commit source-repository cleanup separately from the curator import.
8. Report exactly what was deleted and where the recoverable copies live.

## What must remain in Phase Annotator after cleanup

- `src/phase_annotator/`
- `tests/`
- `.github/workflows/`
- `PhaseAnnotator.spec`
- `pyproject.toml`
- `docs/development/`
- `docs/release/`
- `docs/user/`
- `scripts/build_windows.ps1`
- `scripts/test_packaged_windows.ps1`
- `scripts/smoke_test_media.py`
- a concise studies pointer and any synthetic integration fixtures actually required by tests.

The canonical user guide remains in Phase Annotator because it explains the application itself. The curator should copy a released/versioned PDF into clinician packages, not fork and independently maintain the application's behavior documentation. Study-specific additions belong in the curator's `START HERE` and protocol documents.

## Open decisions for the curator

1. Whether purposeful gallbladder drainage is frequent and reliable enough to become an eighth OAUTHC phase.
2. Whether to retain both a Cholec80-compatible seven-class view and an extended OAUTHC view.
3. How to represent candidate events without overloading `Undefined` permanently.
4. How the master Excel sheet, JSON case registry, physical storage, and annotation batches remain synchronized.
5. How independent annotation, clinical correction, adjudication, and final ground truth are versioned.
6. Which 26 cholecystectomy videos enter each annotation batch and which cases are reserved for agreement or evaluation.
7. How appendectomy and cholecystectomy releases remain separate while sharing governance and tooling.

Until those decisions are approved, preserve raw evidence and avoid irreversible schema or ontology changes.

