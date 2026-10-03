# Phase Annotator

A configurable desktop application for creating and correcting temporal phase annotations in surgical videos. It currently ships with provisional laparoscopic appendectomy and laparoscopic cholecystectomy ontologies, while the annotation engine and UI consume generic ontology configuration.

## Project Goals

* **Research Utility**: Produce deterministic, schema-validated temporal phase annotations for surgical AI research.
* **Data Integrity**: Preserve continuous, validated timeline coverage through transactional editing and atomic JSON repository writes.
* **Flexible Configuration**: Supply phase names, colors, hotkeys, ordering, initial phase, and Undefined role through a versioned ontology.
* **Engineering Rigor**: Keep annotation rules independent of PySide6 and cover important behavior with automated tests.

## Bundled Default Ontology

Default provisional laparoscopic appendectomy ontology:

1. **Identification of the appendix**
2. **Dissection of adhesions of the appendix** *(Optional)*
3. **Coagulation and release of the mesoappendix**
4. **Ligation of the base of the appendix**
5. **Resection/cutting of the appendix**
6. **Retrieval of the appendix specimen**

## Setup & Development

### Linux Prerequisites
On Ubuntu/Debian Linux, Qt 6 requires `libxcb-cursor0`:
```bash
sudo apt update && sudo apt install -y libxcb-cursor0
```

### Installation

Linux/macOS:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Run test suite
QT_QPA_PLATFORM=offscreen python -m pytest -v tests
```

Windows PowerShell:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m ruff format src tests scripts --check
python -m ruff check src tests scripts
python -m mypy
$env:QT_QPA_PLATFORM = "offscreen"
python -m pytest -v tests
Remove-Item Env:QT_QPA_PLATFORM
```

The application entry point is:

```bash
python -m phase_annotator
```

This is an early research prototype with release-engineering milestone C10 complete. Playback, mouse/hotkey annotation, correction tools, undo/redo, media checks, automatic canonical JSON persistence, attribution/history, protected completion/reopening, prominent failures, playback-speed/jump controls, procedure selection, and shortcut help work. The 0.1.0 GitHub Actions artifact passed recorded Windows 11 Sandbox acceptance with documented limitations; broader platform and real-video validation remain planned.

## Documentation

Start with the [documentation map](docs/README.md). It separates clinician guidance, current development/reference material, release evidence, completed milestone history, and the new post-release validation/training programme.

Current entry points:

* [Clinician User Guide](docs/user/USER_GUIDE.md)
* [Developer Guide](docs/development/DEVELOPER_GUIDE.md)
* [Current State](docs/development/CURRENT_STATE.md)
* [0.1.0 Release Evidence](docs/release/versions/0.1.0/CLEAN_MACHINE_ACCEPTANCE.md)
* [Post-Release Validation and Training](docs/studies/README.md)
