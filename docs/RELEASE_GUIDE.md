# Windows Release Guide

## Release target

The current target is a versioned ZIP containing the complete 64-bit Windows one-folder application. It requires neither administrator rights nor an installed Python, but `PhaseAnnotator.exe` must remain beside `_internal`.

One-file packaging, an installer, signing, automatic updates, and non-Windows releases are deferred.

## Prepare the release

1. Confirm the intended version in `pyproject.toml` and `src/phase_annotator/__init__.py` matches the release notes and window title.
2. Ensure the working tree contains only intended changes.
3. Run all source quality gates from `DEVELOPER_GUIDE.md`.
4. Use a standard 64-bit CPython 3.13 environment—not the Conda-derived development environment.

Create or refresh the release environment:

```powershell
py -3.13 -m venv .release-venv
.\.release-venv\Scripts\python.exe -m pip install --upgrade pip
.\.release-venv\Scripts\python.exe -m pip install -e ".[release]"
```

## Build and smoke-test locally

```powershell
.\scripts\build_windows.ps1
.\scripts\test_packaged_windows.ps1
```

The build script cleans PyInstaller analysis output and verifies:

- `dist\PhaseAnnotator\PhaseAnnotator.exe`;
- packaged appendectomy ontology;
- packaged cholecystectomy ontology.

The smoke test starts the frozen executable in noninteractive mode, loads every registered ontology, and constructs the real main window. It does not prove codec playback or clinician workflow.

## Build through GitHub Actions

1. Push the reviewed commit and confirm the automatic **Validate source on CPython 3.13** job is green.
2. Open **Actions → Windows quality and release artifact**.
3. Choose **Run workflow** on the release branch.
4. Confirm validation and **Build and smoke-test Windows artifact** are green.
5. Download `PhaseAnnotator-windows-<commit SHA>` before its 14-day retention expires.

GitHub's artifact is the preferred release-candidate input because it was reconstructed from a clean checkout. Record the commit SHA and workflow-run link in the acceptance record.

## Prepare the distributable ZIP

1. Extract the GitHub artifact.
2. Confirm the top-level application folder contains `PhaseAnnotator.exe` and `_internal`.
3. Add only the approved user guide, release notes, and any required notices outside the generated application folder.
4. Name the ZIP with product, version, platform, and architecture, for example `PhaseAnnotator-0.1.0-windows-x64.zip`.
5. Do not add videos, sidecars, histories, annotator names, local paths, or build directories.

The project intentionally does not hash source videos. Release-file checksums, if later desired for download integrity, are a different concern and need an explicit release decision.

## Acceptance and release

Use `CLEAN_MACHINE_ACCEPTANCE.md` on a Windows machine or VM without the repository, virtual environment, or developer tools. Test the exact extracted GitHub artifact, not a later local rebuild. Record failures; fix them or accept them explicitly in `LIMITATIONS.md`, then rebuild and restart acceptance if the artifact changes.

After acceptance:

1. finalise versioned release notes;
2. tag the accepted commit;
3. publish the exact accepted ZIP through the approved project channel;
4. retain the acceptance record and source commit reference.

Do not call a build released merely because PyInstaller completed or the executable opened once.
