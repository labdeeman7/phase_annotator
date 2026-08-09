# Software Engineering Concepts & Design Patterns Journal

This document records the architectural patterns, design decisions, and testing concepts used in the **Appendectomy Phase Annotation Tool**.

---

## 1. Design Patterns Used in Milestone 1

### A. The Repository Pattern (`JsonSessionRepository`)
* **What it is**: A design pattern that abstracts data persistence behind a simple interface.
* **Why `JsonSessionRepository` has no `__init__` state**:
  `JsonSessionRepository` is a **stateless service class**. Its only job is translation: converting in-memory domain objects (`AnnotationSession`) to disk formats (`.json`) and back. 
* **Benefits**:
  * **Single Source of Truth**: The `AnnotationSession` object in memory and the `.json` file on disk are the state. The repository itself doesn't need to hold data in `self.xxx`.
  * **Swappability**: If we later want to save sessions to an SQLite database or cloud API instead of JSON files, we can create `SqliteSessionRepository` with the exact same `.save()` and `.load()` methods. The rest of the app won't need to change a single line of code!

### B. The Factory Method Pattern (`PhaseOntology.default_appendectomy()`)
* **What it is**: A class method (`@classmethod`) that handles complex object instantiation.
* **Why we use it**: Instead of forcing callers to manually construct 6 `Phase` objects, `PhaseOntology.default_appendectomy()` encapsulates the standard 6-phase surgical definition in one clean line.

### C. Data Transfer Objects / Dataclasses (`@dataclass`)
* **What it is**: Pure data containers with built-in `__repr__`, `__eq__`, and validation hooks (`__post_init__`).
* **Why we use it**: Keeps domain entities (`AnnotationInterval`, `VideoInfo`) concise and readable without writing boilerplate getter/setter code.

---

## 2. Data Integrity & Atomic File Operations

### The Problem: Partial File Corruption
If an app writes directly to `session_01.json` and power drops or the app crashes halfway through:
`session_01.json` is left half-written and corrupt.

### The Solution: Atomic Write via `.tmp` and `os.replace()`
1. Write complete JSON content to a hidden temporary file: `.session_01.json.tmp`.
2. Call `os.replace(".session_01.json.tmp", "session_01.json")`.

### Why `os.replace()` instead of `os.rename()`?
* On **Linux/POSIX**, `os.rename()` replaces existing files atomically.
* On **Windows (NTFS)**, `os.rename()` throws a `FileExistsError` if the target file already exists!
* `os.replace()` is cross-platform: it guarantees atomic replacement on both Windows and Linux without throwing errors if the destination file exists.

---

## 3. How Pytest Auto-Injects `tmp_path` (Fixtures)

Pytest has a powerful feature called **Dependency Injection via Fixtures**.

When pytest runs:
1. It discovers any function starting with `test_` (e.g. `def test_save_session_atomic(tmp_path: Path):`).
2. It inspects the function arguments.
3. If it sees `tmp_path`, pytest automatically creates a fresh, isolated temporary directory on disk for that test run and passes it into `tmp_path` as a `pathlib.Path` object.
4. After the test finishes, pytest automatically cleans up the temporary directory.

This allows unit tests to test real file IO safely without polluting your actual project folders or leaving garbage files behind!

---

## 4. The Testing Pyramid (Types of Testing)

Software engineering classifies tests into a hierarchy known as the **Testing Pyramid**:

```
      ▲
     / \     E2E / System Tests (GUI & Full Application)
    /   \    
   /-----\   Integration Tests (Domain + Persistence interaction)
  /       \  
 /---------\ Unit Tests (Isolated functions & models)
```

1. **Unit Tests** (`tests/unit/`):
   * Tests a single function or class in total isolation (e.g. `test_annotation_interval_duration`).
   * Extremely fast (runs hundreds of tests in milliseconds).
2. **Integration Tests** (`tests/integration/`):
   * Tests how multiple components work together (e.g. `test_full_session_lifecycle` combining ontology, session models, validation, and JSON storage).
3. **End-to-End (E2E) / System Tests**:
   * Tests the full user workflow through the GUI (e.g. clicking "Play", selecting Phase 2, clicking "Save").
4. **Property-Based / Fuzz Testing**:
   * Generates thousands of random inputs to find edge-case crashes.
