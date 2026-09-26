# C10.7 Clean-Machine Acceptance Record

Status: **Ready to execute; final manual clean-machine result pending.**

Test the exact GitHub Actions artifact produced from the intended release commit. A clean machine means a Windows computer or fresh VM without this repository, its virtual environments, or a developer Python installation being used by the application.

## Release identity

| Field | Record |
| --- | --- |
| Application version | 0.1.0 |
| Git commit SHA | _pending_ |
| GitHub workflow run | _pending_ |
| Artifact name | _pending_ |
| Test date/reviewer | _pending_ |
| Windows edition/version/build | _pending_ |
| Display resolution/scaling | _pending_ |
| Test-video container/codec/resolution/FPS source | _pending_ |

Use disposable/de-identified representative media. Do not record a patient identifier or local clinical path in this document.

## Installation and startup

- [ ] Download the artifact on the clean machine.
- [ ] Extract the complete folder; do not run inside the ZIP.
- [ ] Launch `PhaseAnnotator.exe` without Python or administrator rights.
- [ ] Enter a first name and confirm it appears lowercase in the title.
- [ ] Select appendectomy and confirm the correct phase palette/title.
- [ ] Restart, select laparoscopic cholecystectomy, and confirm its seven phases plus Undefined.
- [ ] Open **Help → Shortcuts and controls...** and confirm it is readable at the recorded display scale.

## Media and annotation

- [ ] Open representative media and obtain visible playback/audio behavior expected for that file.
- [ ] Play/pause, seek slider, timeline seek, ±5 seconds, estimated frame steps, and 1×/2×/4×/8×/12× work.
- [ ] Record phases using a hotkey and a palette click.
- [ ] Select using timeline and segment card; confirm cyan selection and white playhead distinctions.
- [ ] Change phase, move a boundary by action and drag, edit a segment note, and use Delete → Undefined.
- [ ] Undo and Redo restore the expected annotation.
- [ ] Invalid boundary movement is rejected without corrupting coverage.

## Persistence and lifecycle

- [ ] Confirm the canonical adjacent sidecar appears and updates automatically.
- [ ] Pause/close/reopen and confirm resume position and annotation recovery.
- [ ] Add a video note, mark complete, and confirm editing is protected.
- [ ] Reopen for editing and confirm the completed record is archived.
- [ ] Change annotation, close, and confirm one appropriate history snapshot.
- [ ] Reopen without annotation changes and confirm no new annotation-change snapshot.
- [ ] Attempt the other procedure against the existing sidecar; confirm loading is blocked and JSON is unchanged.
- [ ] If practical, exercise an unwritable location and confirm `[UNSAVED]`/retry-discard-cancel handling without silent loss.

## Artifact integrity

- [ ] The application contains and loads both packaged ontologies.
- [ ] No repository, virtual environment, build output, test video, annotation sidecar, or local identity is bundled.
- [ ] `PhaseAnnotator.exe` remains with `_internal` throughout testing.
- [ ] The user guide, release notes, and limitations match observed behavior.

## Result

| Item | Record |
| --- | --- |
| Overall result | _PASS / FAIL / PASS WITH ACCEPTED LIMITATIONS_ |
| Blocking defects | _pending_ |
| Accepted limitations | _pending_ |
| Annotation-data integrity preserved | _pending_ |
| Exact ZIP/archive approved | _pending_ |

Any code, configuration, dependency, spec, or bundled-resource change creates a new candidate and requires relevant checks again. Documentation-only corrections need review but do not necessarily require repeating every media operation.
