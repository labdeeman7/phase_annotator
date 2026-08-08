# Architecture Overview

## System Layers

```
[ PySide6 Desktop UI ]
         │
         ▼
[ Presenter / Controller ]
         │
         ├───▶ [ Domain Models & Validation ] (Pure Python)
         │
         ▼
[ Storage & Export Adapters ] (Atomic JSON / CSV Export)
```

## Key Components

### 1. Domain (`src/phase_annotator/domain/`)
* **`models.py`**: Defines core entities (`Phase`, `AnnotationInterval`, `AnnotationSession`, `VideoInfo`).
* **`ontology.py`**: Configurable phase definitions (6-phase appendectomy ontology).
* **`validation.py`**: Enforces interval boundaries, overlap checks, and gap detection rules.

### 2. Storage (`src/phase_annotator/storage/`)
* **`json_repo.py`**: Manages loading and saving sessions using atomic write mechanisms (`os.replace`).
* **`export_csv.py`**: Translates internal session model to research CSV format.

### 3. UI (`src/phase_annotator/ui/`)
* **`main_window.py`**: Main PySide6 application window.
* **`player_widget.py`**: Wraps Qt `QMediaPlayer` / `QVideoWidget`.
* **`timeline_widget.py`**: Visual interactive bar showing phase intervals.
