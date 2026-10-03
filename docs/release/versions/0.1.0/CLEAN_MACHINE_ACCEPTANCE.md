# C10.7 Clean-Machine Acceptance Record

Status: **Passed on 2026-10-03 with accepted limitations.**

Test the exact GitHub Actions artifact produced from the intended release commit. A clean machine means a Windows computer or fresh VM without this repository, its virtual environments, or a developer Python installation being used by the application.

## Release identity

| Field | Record |
| --- | --- |
| Application version | 0.1.0 |
| Git commit SHA | 4fce4f55300c99bb748ea8ff845ea8dc8b2472ad |
| GitHub workflow run | [Windows quality and release artifact #4](https://github.com/labdeeman7/phase_annotator/actions/runs/37133363159) |
| Artifact name | PhaseAnnotator-windows-4fce4f55300c99bb748ea8ff845ea8dc8b2472ad |
| Test date/reviewer | 2026-10-03 ; Tosin |
| Windows edition/version/build | Windows 11 Sandbox; version 24H2 (OS build 26100.9457) |
| Display resolution/scaling | 1920x1080; 100% |
| Test-video container/codec/resolution/FPS source | MP4 / H.264 (AVC) / 720 × 576 / 24.99 FPS (metadata source not recorded) |

Use disposable/de-identified representative media. Do not record a patient identifier or local clinical path in this document.

## Installation and startup

- [x] Download the artifact on the clean machine.
- [x] Extract the complete folder; do not run inside the ZIP.
- [x] Record whether SmartScreen shows **Windows protected your PC / Unknown publisher**; for the approved unsigned 0.1.0 artifact, confirm **More info → Run anyway** remains available. Treat a named malware detection or quarantine as a separate blocking failure.
- [x] Launch `PhaseAnnotator.exe` without Python or administrator rights.
- [x] Enter a first name and confirm it appears lowercase in the title.
- [x] Select appendectomy and confirm the correct phase palette/title.
- [x] Restart, select laparoscopic cholecystectomy, and confirm its seven phases plus Undefined.
- [x] Open **Help → Shortcuts and controls...** and confirm it is readable at the recorded display scale.

## Media and annotation

- [x] Open representative media and obtain visible playback/audio behavior expected for that file.
- [x] Play/pause, seek slider, timeline seek, ±5 seconds, estimated frame steps, and 1×/2×/4×/8×/12× work.
- [x] Record phases using a hotkey and a palette click.
- [x] Select using timeline and segment card; confirm cyan selection and white playhead distinctions.
- [x] Change phase, move a boundary by action and drag, edit a segment note, and use Delete → Undefined.
- [x] Undo and Redo restore the expected annotation.
- [x] Invalid boundary movement is rejected without corrupting coverage.

## Persistence and lifecycle

- [x] Confirm the canonical adjacent sidecar appears and updates automatically.
- [x] Pause/close/reopen and confirm resume position and annotation recovery.
- [x] Add a video note, mark complete, and confirm editing is protected.
- [x] Reopen for editing and confirm the completed record is archived.
- [x] Change annotation, close, and confirm one appropriate history snapshot.
- [x] Reopen without annotation changes and confirm no new annotation-change snapshot.
- [x] Attempt the other procedure against the existing sidecar; confirm loading is blocked and JSON is unchanged.
- [ ] If practical, exercise an unwritable location and confirm `[UNSAVED]`/retry-discard-cancel handling without silent loss. **Not exercised:** not practical in this Windows Sandbox pass.

## Artifact integrity

- [x] The application contains and loads both packaged ontologies.
- [x] No repository, virtual environment, build output, test video, annotation sidecar, or local identity is bundled.
- [x] `PhaseAnnotator.exe` remains with `_internal` throughout testing.
- [x] The user guide, release notes, and limitations match observed behavior.

## Result

| Item | Record |
| --- | --- |
| Overall result | PASS WITH ACCEPTED LIMITATIONS |
| Blocking defects | None |
| Accepted limitations | Unsigned executable triggered expected SmartScreen warning; unwritable-location test not exercised |
| Annotation-data integrity preserved | Yes |
| Exact artifact approved | Yes |

Any code, configuration, dependency, spec, or bundled-resource change creates a new candidate and requires relevant checks again. Documentation-only corrections need review but do not necessarily require repeating every media operation.
