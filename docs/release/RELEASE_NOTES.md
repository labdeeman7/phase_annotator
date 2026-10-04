# Release Notes

## 0.1.1 — Locally accepted patch (2026-10-04)

This usability patch is accepted for local project use. It has not undergone fresh clean-machine acceptance.

### Changed

- Show the selected video filename above the video and in the window title.
- Toggle Play/Pause by clicking the video surface, matching a familiar media-player interaction.
- Protect imported Cholec80 training references as Completed while retaining explicit machine-import attribution and provenance.
- Add the tested Cholec80 conversion contract and a structured working clinical-protocol evidence log.

### Acceptance

Source validation, the standard-CPython/PyInstaller build, packaged smoke test, and focused local manual checks passed. The executable launched, loaded and played the representative video, displayed annotator/video identity, toggled playback from the video surface, and protected the completed imported reference. Fresh clean-machine acceptance was explicitly skipped for time; see `versions/0.1.1/LOCAL_ACCEPTANCE.md`.

## 0.1.0 — Accepted release candidate (2026-10-03)

Phase Annotator 0.1.0 is the first Windows release candidate of the configurable surgical phase annotation prototype.

### Included

- Packaged provisional appendectomy and laparoscopic cholecystectomy procedures.
- Qt video playback, seek, speed, jump, and estimated frame-step controls.
- Mouse and ontology-configured hotkey phase transitions.
- Coloured continuous timeline and synchronized segment cards.
- Relabel, boundary correction/dragging, notes, Undefined conversion, merge, Undo, and Redo.
- Automatic adjacent JSON saving, resume checkpoints, local history snapshots, and external-change protection.
- Sequential annotator attribution, Draft/Completed lifecycle, protected reopening, and procedure-mismatch safety.
- High-visibility actionable error banner and in-application shortcut reference.
- Reproducible PyInstaller one-folder build and clean Windows GitHub Actions validation/artifact workflow.

### Important limitations

- Millisecond boundaries are authoritative; displayed frames are estimates.
- Windows codec support varies by machine and encoding.
- Ontologies remain provisional and require clinical governance.
- No concurrent collaboration, CSV export, persisted Undo/Redo, installer, signing, or automatic updates.
- This remains research software, not a regulated clinical system.

See `../user/LIMITATIONS.md` and `../user/USER_GUIDE.md` before use.

### Acceptance

The exact GitHub Actions artifact for commit `4fce4f55300c99bb748ea8ff845ea8dc8b2472ad` passed Windows 11 Sandbox acceptance. The unsigned executable produced the expected SmartScreen warning, and the optional unwritable-location scenario was not manually exercised. Full evidence is in `versions/0.1.0/CLEAN_MACHINE_ACCEPTANCE.md`.
