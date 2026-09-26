# Release Notes

## 0.1.0 — Release candidate

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

See `LIMITATIONS.md` and `USER_GUIDE.md` before use.
