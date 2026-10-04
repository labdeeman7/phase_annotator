# Phase Annotator 0.1.1 Local Acceptance

Date: 2026-10-04  
Result: **PASS FOR LOCAL PROJECT USE WITH ACCEPTED LIMITATION**

## Candidate

- Version: 0.1.1
- Build environment: standard 64-bit CPython 3.13.15 on Windows 11
- PyInstaller: 6.22.3
- Output: one-folder `dist/PhaseAnnotator/` artifact
- Artifact inventory: 242 files, 131.6 MiB

## Evidence completed

- Ruff format and lint passed.
- Scoped Mypy passed over the configured 16 source files.
- All 196 pytest tests passed.
- Python compilation check passed.
- Build script verified the executable and both packaged ontology resources.
- The frozen executable's noninteractive artifact smoke test passed for both configured procedures and real `MainWindow` construction.
- The built executable launched successfully on the development machine.
- Manual inspection confirmed the annotator name and selected video filename were visible in the title bar.
- The representative `video04` reference loaded and played successfully in the local build.
- Earlier focused manual checks confirmed video-click Play/Pause and completed-reference edit protection.

## Accepted limitation

The 0.1.1 artifact did **not** undergo a fresh Windows Sandbox or other clean-machine acceptance run. This was an explicit time-based decision, not evidence that clean-machine behavior was tested. Version 0.1.0 retains the stronger recorded clean-machine acceptance baseline.

The local `dist/` output is not committed. Any separately rebuilt or GitHub-generated artifact must run its automated packaged smoke test; it should not inherit this local artifact's manual evidence as though it were byte-identical.
