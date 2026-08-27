# Testing Strategy & Contracts

## TDD Workflow

All domain rules and storage operations follow the TDD loop:

```
1. Write failing test in tests/unit/ (Red)
2. Run `pytest` to confirm failure
3. Implement minimal code in src/phase_annotator/ (Green)
4. Run `pytest` to confirm pass
5. Refactor code & tests cleanly
```

## Running Tests

Use Python 3.10 or newer and install the editable development dependencies first:

```powershell
python -m pip install -e ".[dev]"
$env:QT_QPA_PLATFORM = "offscreen"

# Run all unit tests
python -m pytest -v tests/unit/

# Run all integration tests
python -m pytest -v tests/integration/

# Run complete suite
python -m pytest -v tests/

# Syntax/import-independent compilation check
python -m compileall -q src tests
```

On Linux, use `QT_QPA_PLATFORM=offscreen python -m pytest -v tests` for headless Qt tests. There is currently no configured linter, formatter, type checker, coverage threshold, or CI job.

## Testing Contracts

1. **Domain isolation**: Domain tests must never instantiate Qt widgets or depend on display servers. Existing GUI widget tests also live under `tests/unit/` and require PySide6 plus pytest-qt.
2. **Deterministic Inputs**: Tests must use fixed timestamps/frames and mock video metadata.
3. **Storage Isolation**: Storage tests must use temporary directories (`tmp_path` fixture) to isolate file IO.

## Current coverage gaps

There are no tests for real playback/codec behavior, phase hotkey transitions, invalid transition rollback, timeline/card seek signals, save failures, backup/recovery, schema compatibility, or a complete GUI workflow. See `CURRENT_STATE.md` before interpreting a green suite as production readiness.
