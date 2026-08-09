# Appendectomy Phase Annotation Tool

A lightweight, high-reliability desktop application for annotating temporal surgical phases in laparoscopic appendectomy videos.

## Project Goals

* **Research Utility**: Produce deterministic, schema-validated temporal phase annotations for surgical AI research.
* **Data Integrity**: Fail-safe persistence via atomic writes, session recovery, and clear error boundaries.
* **Engineering Rigor**: Built using Test-Driven Development (TDD), Clean Architecture, and clear domain isolation.

## Surgical Phase Ontology

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
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Run test suite
pytest -v tests/
```

## Documentation

* [Architecture](docs/ARCHITECTURE.md)
* [Architecture Decisions](docs/DECISIONS.md)
* [Software Patterns & Learning Journal](docs/LEARNING_JOURNAL.md)
* [Video Encoding Fundamentals Guide](docs/VIDEO_ENCODING_GUIDE.md)
* [Task Backlog](docs/TASKS.md)
* [Testing Contract](docs/TESTING.md)
