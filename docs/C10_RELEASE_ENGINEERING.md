# C10 — Release Engineering and Windows Distribution

## Purpose

C10 turns the tested source repository into a repeatable Windows release that a clinician can run without installing Python or using a terminal. Packaging is only one part of that outcome: the delivered artifact must contain its resources, preserve the annotation-data contract, pass clean-machine acceptance, and be reproducible from documented commands.

This is a learning milestone. Work should proceed in small slices, with the build and release concepts explained before automation hides them.

## C10.1 release contract

Status: **Agreed and documented.** Implementation and acceptance remain pending.

The first supported release will have these properties:

- **Supported target:** 64-bit Windows. Other platforms remain development environments until separately built and tested.
- **Distribution:** a versioned ZIP containing a portable one-folder application.
- **Launch:** the clinician extracts the complete folder and runs `PhaseAnnotator.exe`; Python, a virtual environment, and administrator access must not be required.
- **Installation:** no installer, registry changes, file associations, automatic updater, or Start-menu integration in the first release.
- **Procedures:** both packaged laparoscopic appendectomy and laparoscopic cholecystectomy ontologies must be usable from the artifact.
- **Data location:** videos are opened in place and are never bundled or copied. The canonical annotation remains `<video filename>.phase-annotations.json` beside the video, with the existing adjacent history-directory policy.
- **Permissions:** the application must clearly report when the video directory cannot be written. Packaging must not redirect annotations into the application folder or silently choose another location.
- **Privacy:** the release contains no clinical video, annotation, identity, or patient data. The ZIP and documentation use synthetic examples only.
- **Version:** the application, package metadata, release artifact, and release notes must report one consistent version. The prototype begins at `0.1.0`; any later version change is an explicit release decision.
- **Console:** the clinician-facing executable should not open a terminal window. Build and diagnostic failures must still be observable through documented logs or a separate controlled diagnostic method.
- **Media:** the release bundles application/Qt dependencies but does not claim universal codec support. Representative project videos must be tested on the supported Windows environment.
- **Trust:** an unsigned prototype may trigger Windows SmartScreen or antivirus warnings. Code signing is a separate deployment decision and must not be implied by successful packaging.

### Why one-folder first

A one-folder build makes runtime libraries, Qt plugins, and packaged ontology resources inspectable. It is normally easier to diagnose and avoids the extraction behavior and slower startup associated with one-file bundles. The entire folder is the application: users must not move only the `.exe` out of it.

PyInstaller also creates an executable under `build/pyinstaller/PhaseAnnotator/` while assembling the application. That is an intermediate build object, not a runnable or distributable application; it does not have the collected `_internal` runtime beside it and may fail with a missing `python311.dll` message. Run only `dist/PhaseAnnotator/PhaseAnnotator.exe`, and distribute the complete `dist/PhaseAnnotator/` folder.

The folder will be distributed as a ZIP for convenient transfer. A one-file executable or graphical installer may be evaluated later only if deployment evidence shows that it improves the clinician workflow enough to justify the additional complexity.

## Milestone slices

### C10.1 — Release contract and plan

Status: **Complete.**

- Agree the supported platform, artifact form, data-location behavior, privacy boundary, and explicit non-goals.
- Keep packaging choices subordinate to the data-integrity contract.
- Record the learning and acceptance workflow before implementation.

Learning focus: the difference between building software and defining a releasable product.

### C10.2 — Minimal engineering-quality toolchain

Status: **Complete.** Ruff provides an explicit conservative formatting/lint baseline, and the repository is formatter-clean. Mypy gates configuration, domain, media, and storage; UI typing findings remain visible future hardening work rather than being suppressed. All configured checks and 184 tests passed when the baseline was introduced.

- Inspect existing code before choosing lint/format/type rules.
- Add a deliberately small formatter and linter configuration, expected to use Ruff unless repository findings give a reason not to.
- Evaluate type checking separately. Do not enable a noisy whole-project strict policy merely to tick a box; establish a useful scope and baseline first.
- Add commands to developer documentation and run them locally.
- Fix findings by understanding them; never change annotation behavior merely to silence a tool.

Exit gate: a fresh development environment can run documented formatting/lint checks, tests, and compilation checks with deterministic results.

Learning focus: the distinct roles of formatting, linting, static typing, compilation checks, and behavioral tests.

### C10.3 — PyInstaller one-folder build and maintained recipe

Status: **Complete.** An exploratory Miniconda-derived build exposed unresolved DLL warnings and was rejected as a release candidate. A separate `.release-venv` based on official 64-bit CPython 3.13.15 passed Ruff, scoped Mypy, compilation, and all 184 tests. PyInstaller 6.22.3 then produced a 242-file, 131.6 MiB one-folder artifact with no unresolved Windows DLL warnings. The build script verified the executable and both ontologies, and the packaged GUI passed a controlled startup probe. C10.4 owns deeper packaged workflow/media acceptance.

- Use PyInstaller as the primary packaging path. It is a widely used freezing tool, supports one-folder applications, and exposes dependency/resource decisions through an inspectable Python `.spec` file.
- Begin with a minimal exploratory build, inspect what PyInstaller detects, and then convert the successful configuration into a maintained `.spec` recipe. Do not start by hiding the process behind additional deployment automation.
- Verify PySide6/Qt Multimedia support, resource inclusion, output size/startup, licensing implications, reproducibility, and CI suitability on this application.
- Keep Qt's `pyside6-deploy` as a documented fallback, not a parallel implementation. Reconsider it only if PyInstaller presents a concrete unresolved Qt deployment problem.
- Record the packaging decision and fallback in `DECISIONS.md`.
- Add the selected build dependency in an explicit packaging/release dependency group.
- Create a maintained build recipe and PowerShell build script; do not rely on an undocumented command from shell history.
- Reject Conda-derived release environments by default because the exploratory build exposed unresolved base-interpreter DLLs; retain an explicitly named exploration-only override that cannot be mistaken for release approval.
- Produce a windowed `PhaseAnnotator.exe` in a one-folder output.
- Explicitly verify that both ontology JSON resources are present and loadable.
- Keep generated `build/`, `dist/`, and release ZIP files out of source control.

Official references to use during implementation:

- [Qt for Python and PyInstaller](https://doc.qt.io/qtforpython-6/deployment/deployment-pyinstaller.html)
- [PyInstaller operating modes](https://pyinstaller.org/en/stable/operating-mode.html)
- [PyInstaller specification files](https://pyinstaller.org/en/stable/spec-files.html)

Exit gate: one documented command produces an inspectable Windows application folder from a clean release environment, and an automated artifact check proves both procedure resources are loadable.

Learning focus: freezing Python, import analysis, native libraries, Qt plugins, data resources, entry points, and build recipes.

### C10.4 — Packaged-artifact testing

Status: **Complete.** The frozen executable's noninteractive smoke mode loads every registered ontology through packaged resources, validates its identity, constructs the real `MainWindow`, and exits successfully. Source coverage is now 187 passing tests. Manual acceptance on 2026-09-23 used the clean CPython 3.13 artifact and an ignored disposable representative video. Both procedure startups, packaged decoding/playback, keyboard and mouse annotation, correction, Undo/Redo, automatic persistence/resume, notes, completion/reopening, history, and wrong-procedure blocking worked as specified. Inspection confirmed one canonical adjacent sidecar and one adjacent history directory; no procedure-specific parallel sidecar appeared.

- Add an automated smoke check that launches or probes the packaged artifact without relying on the source checkout being importable.
- Ensure every command, guide, and acceptance check points to `dist/PhaseAnnotator/PhaseAnnotator.exe`, never the intermediate executable under `build/`.
- Verify startup identity and procedure selection, both ontology resources, and application version.
- Manually test representative H.264/AAC project media through the packaged Qt Multimedia backend.
- Exercise annotation, correction, undo/redo, automatic save, close/reopen resume, history, completion/reopening, malformed sidecars, and wrong-procedure protection.
- Confirm all writes still follow the canonical adjacent-sidecar policy.

Exit gate: the artifact—not only the source environment—passes the critical workflow checklist without annotation loss or procedure confusion.

Learning focus: why source tests cannot prove that a packaged resource or native runtime was shipped.

#### C10.4 manual packaged acceptance

Use only `dist/PhaseAnnotator/PhaseAnnotator.exe` and the ignored disposable copy at `test_dataset/packaged_acceptance/packaged-acceptance.mp4`. Do not open the original representative video's existing sidecar during this test.

1. Launch, enter a synthetic first name, select laparoscopic cholecystectomy, confirm its seven phases appear, then close without opening media.
2. Relaunch with laparoscopic appendectomy and open the disposable video. Confirm Loaded state, positive duration, visible decoded frames, usable audio if expected, timeline coverage, and responsive play/pause plus speed/jump controls.
3. Create transitions once by hotkey and once by clicking the palette. Confirm timeline and segment cards describe the same normalized intervals.
4. Select a segment; add/cancel/save a note, relabel it, move one boundary, drag another boundary, convert one segment to Undefined with Delete, then exercise Undo/Redo. Confirm selection and both views remain synchronized.
5. Pause at a recognizable location, close cleanly, and confirm the canonical adjacent JSON and history directory appear beside the disposable video.
6. Relaunch appendectomy, reopen the video, and confirm intervals, note, status, attribution, and resume position restore. Add a video note and complete the annotation after reviewing the summary.
7. Confirm completed work is protected, deliberately reopen it for editing, and verify the completed version was archived before the session returned to Draft.
8. Close and relaunch with cholecystectomy, then open the same disposable video. Confirm the procedure-mismatch banner names both procedures, says nothing changed, and blocks annotation. Do not create a second sidecar.
9. Report any visual, playback, persistence, or error-message discrepancy. After the run, inspect the sidecar/history filenames and JSON structure without committing them.

### C10.5 — Continuous integration

Status: **Complete.** `.github/workflows/windows-ci.yml` validates every push, pull request, and manual run on 64-bit CPython 3.13.15. A packaging job runs only on manual dispatch after validation, builds through the maintained PowerShell recipe, executes the frozen-artifact smoke test, and uploads the complete application folder for 14 days. On 2026-09-23, the first push-triggered validation and manually dispatched validation/package jobs all passed on GitHub's clean Windows runner, including artifact upload.

- Add GitHub Actions for a clean Windows checkout and the supported Python version.
- Install declared dependencies; run formatting/lint checks, the complete test suite with headless Qt, and compilation checks.
- Add a deliberate Windows packaging job or manually triggered release workflow after the local recipe is stable.
- Upload the application folder/ZIP as a workflow artifact when packaging succeeds.
- Prefer clear jobs and logs over premature matrix complexity or cache tuning.

Exit gate: CI proves a clean checkout can validate and build the project without undeclared local state.

Learning focus: workflow triggers, runners, jobs, steps, clean environments, caches, and artifacts.

### C10.6 — User, developer, and release documentation

Status: **Complete.** `USER_GUIDE.md`, `DEVELOPER_GUIDE.md`, `RELEASE_GUIDE.md`, `LIMITATIONS.md`, `RELEASE_NOTES.md`, and `CLEAN_MACHINE_ACCEPTANCE.md` cover their distinct audiences and are linked from the README. The user guide includes a repository-safe annotated interface map. Extended Cholec80 validation and clinical training/protocol development remain separate post-release work in `REAL_VIDEO_VALIDATION_AND_TRAINING_PLAN.md`.

- Write a short clinician guide covering extraction, launch, identity/procedure choice, annotation, corrections, autosave, completion, and common errors.
- Document where canonical JSON and history live and how they must travel with the video.
- Document supported Windows/media scope, privacy constraints, and the absence of simultaneous collaboration.
- Write clean developer setup/build instructions.
- Add versioned release notes and a release checklist.
- Keep clinician instructions separate from implementation detail.

Exit gate: a first-time clinician can operate the artifact without repository knowledge, and a developer can reproduce it from a clean checkout.

Learning focus: writing for users, maintainers, and release operators as distinct audiences.

### C10.7 — Clean-machine acceptance and release candidate

Status: **Ready for manual execution.** The exact-artifact checklist and evidence record are in `CLEAN_MACHINE_ACCEPTANCE.md`. Automated clean-runner validation, packaging, frozen-resource/window smoke testing, and local representative-media lifecycle acceptance pass; the final exact downloaded artifact still requires the recorded GUI/media run on a clean Windows machine or VM.

- Copy only the versioned release ZIP to another Windows machine or clean VM that does not have the repository or project virtual environment.
- Extract the whole folder and launch without Python or administrator privileges.
- Run the end-to-end checklist for both procedures with disposable representative media.
- Confirm save/resume, history, completion, failure feedback, and procedure-mismatch safety.
- Record Windows version, artifact version, test media characteristics, outcomes, and known limitations.
- Do not call the artifact released until failures are resolved or explicitly documented and accepted.

Exit gate: CI is green and the exact versioned artifact passes the recorded clean-machine checklist.

Learning focus: release candidates, acceptance evidence, reproducibility, and the meaning of “works on my machine.”

## Constraints that packaging must not violate

- Do not change domain semantics, the JSON schema, or canonical sidecar naming merely to simplify packaging.
- Do not bundle representative clinical videos, generated annotation files, annotator names, or local absolute paths.
- Do not invoke untracked executables from `PATH`. Any bundled binary requires documented source, version, license, and platform validation.
- Do not add video hashing or a hidden fallback save location.
- Do not assume that bundling Qt guarantees support for every codec or Windows version.
- Do not commit generated build output.
- Do not treat a successful packaging command as release acceptance.

## Validation layers

| Layer | Question answered |
| --- | --- |
| Formatter/linter | Is the source consistently structured and free of selected suspicious patterns? |
| Type checker, if adopted | Are declared types used consistently within the chosen scope? |
| Unit/integration tests | Does source behavior satisfy the tested contracts? |
| Packaging build | Can declared source and dependencies be assembled into an artifact? |
| Artifact smoke test | Did the bundle contain the entry point, resources, and runtime components needed to start? |
| Representative-media test | Does the packaged Qt backend handle the videos expected in practice? |
| Clean-machine acceptance | Can a real recipient use the exact release without developer state? |

No single layer replaces the others.

## Learning-mode reading map

Read closely:

1. `pyproject.toml` dependency groups and tool configuration.
2. The selected packaging recipe/specification and its resource declarations.
3. The build script's clean inputs and outputs.
4. The CI workflow's job boundaries.
5. The release checklist and recorded clean-machine result.

Skim generated packaging logs after learning their main phases. Do not study generated `build/` or `dist/` contents line by line; inspect them to answer specific questions about resources, native libraries, or size.

## Collaboration and acceptance responsibilities

Codex owns implementation, tests, documentation, and explanation. The user participates in three high-value decisions/checks:

1. Confirm the C10.1 clinician-facing release contract.
2. Review the C10.3 PyInstaller recipe and its explicit resource/runtime choices with Codex.
3. Run or observe the C10.7 clean-machine acceptance using disposable media.

Each slice should end with validation evidence, a short reading map, and one focused manual check before its commit unless the user asks to combine work.
