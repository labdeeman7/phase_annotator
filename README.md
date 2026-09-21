# Phase Annotator

A configurable desktop application for creating and correcting temporal phase annotations in surgical videos. It currently ships with a provisional laparoscopic appendectomy ontology, while the annotation engine and UI consume generic ontology configuration.

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
$env:QT_QPA_PLATFORM = "offscreen"
python -m pytest -v tests
Remove-Item Env:QT_QPA_PLATFORM
```

The application entry point is:

```bash
python -m phase_annotator
```

This is an early prototype completed through project milestone C7. Playback, mouse/hotkey annotation, correction tools, undo/redo, media checks, automatic canonical JSON persistence, sequential annotator attribution, changed-run snapshots, and external-write protection work. Explicit completion, distribution, and broader platform validation remain planned.

## Documentation

* [Architecture](docs/ARCHITECTURE.md)
* [Current State and Handover](docs/CURRENT_STATE.md)
* [Project Roadmap](docs/ROADMAP.md)
* [Annotation and Video Workflow](docs/ANNOTATION_WORKFLOW.md)
* [Annotation Data Model](docs/DATA_MODEL.md)
* [Ontology Configuration](docs/ONTOLOGY_CONFIGURATION.md)
* [Media Reliability Contract](docs/C5_MEDIA_RELIABILITY.md)
* [Continuous Persistence Plan](docs/C6_CONTINUOUS_PERSISTENCE.md)
* [Annotator Attribution and History Plan](docs/C7_ATTRIBUTION_AND_HISTORY.md)
* [Architecture Decisions](docs/DECISIONS.md)
* [Software Patterns & Learning Journal](docs/LEARNING_JOURNAL.md)
* [Video Encoding Fundamentals Guide](docs/VIDEO_ENCODING_GUIDE.md)
* [Task Backlog](docs/TASKS.md)
* [Testing Contract](docs/TESTING.md)
