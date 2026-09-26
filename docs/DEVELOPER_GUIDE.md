# Developer Guide

## Supported development baseline

Use Python 3.10 or newer. Release artifacts use standard 64-bit CPython 3.13 rather than a Conda-derived interpreter.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the application with:

```powershell
python -m phase_annotator
```

On Ubuntu/Debian, Qt may require `libxcb-cursor0`. macOS and Linux packaging/playback are not release-validated.

## Architecture map

- `__main__.py` is the composition root: identity, procedure selection, ontology loading, and `MainWindow` construction.
- `domain/` contains pure-Python models, validation, annotation editing, history, completion, and time conversion.
- `config/` contains validated packaged ontology JSON and the registry/loader.
- `media/` converts Qt metadata into lightweight descriptors and source-comparison evidence.
- `storage/` owns schema conversion, validation, atomic JSON replacement, canonical sidecar policy, history snapshots, and dirty-state coordination.
- `ui/` owns PySide6 widgets and orchestration. `MainWindow` still combines view and controller/presenter responsibilities.

Read `ARCHITECTURE.md`, `DATA_MODEL.md`, and `ANNOTATION_WORKFLOW.md` before changing domain behavior.

## Quality gates

```powershell
python -m ruff format src tests scripts --check
python -m ruff check src tests scripts
python -m mypy
$env:QT_QPA_PLATFORM = "offscreen"
python -m pytest -v tests
python -m compileall -q src tests
git diff --check
```

Mypy currently gates configuration, domain, media, and storage—not the Qt UI. Tests do not replace representative media or packaged GUI checks.

## Change discipline

1. Check `git status --short` and preserve unrelated changes.
2. Inspect the implementation and tests rather than relying on roadmap prose.
3. Resolve product semantics before architecture and implementation.
4. Put annotation meaning in the domain layer, not only in widgets.
5. Validate proposed interval/session changes before committing them.
6. Add narrow failure-path tests, then run the complete gate.
7. Update current-state, workflow/schema, user, and limitation documentation when behavior changes.

Do not hash videos, silently migrate/discard unknown data, introduce hidden save locations, invoke system `ffprobe`, or hard-code procedure phases in reusable UI/domain code.

## Persistence contract

The canonical JSON is adjacent to the video and is replaced atomically using a same-directory temporary file plus `os.replace`. Milliseconds and continuous non-overlapping coverage are authoritative. One procedure-neutral sidecar exists per video; ontology mismatch blocks loading rather than creating parallel annotations.

Changes to schema, canonical naming, ontology IDs/versions, interval semantics, lifecycle, or source identity require a compatibility plan and tests. Never place real clinical data or absolute dataset paths in source control.

## Adding or changing an ontology

Ontology files configure IDs, display names, order, colours, hotkeys, initial phase, and Undefined. Keep procedure selection at the composition root and inject `PhaseOntology`. Validate hotkey uniqueness and lifecycle compatibility. Existing sidecars retain ontology identity/version, so incompatible ontology edits require an explicit migration decision.

## Useful starting points

- `tests/unit/`: domain, media, storage, and conversion behavior.
- `tests/integration/`: lightweight persistence/UI flows.
- `scripts/smoke_test_media.py`: local media pipeline check.
- `scripts/build_windows.ps1`: supported Windows package orchestration.
- `scripts/test_packaged_windows.ps1`: frozen executable/resource smoke test.
- `.github/workflows/windows-ci.yml`: clean Windows validation and artifact production.
