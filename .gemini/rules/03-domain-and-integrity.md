# Rule 03: Domain Isolation & Data Integrity

## Architecture & Data Safety

1. **Domain Isolation**:
   * Core domain logic (`src/phase_annotator/domain`) MUST remain pure Python with ZERO imports from `PySide6`, `Qt`, or IO frameworks.
   * Domain rules must be 100% executable under pure `pytest`.
2. **Data Persistence Safety**:
   * Session file writes MUST be atomic (`.tmp` write followed by `os.replace`).
   * Never overwrite an existing session without creating a `.bak` backup copy or using atomic replacement.
   * Preserve annotation metadata (annotator ID, timestamps, video identifier, version schema).
