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

---

## 5. GUI & Video Architecture: PySide6 (Qt 6)

### What is PySide6?
Python's standard library only has `tkinter`, which lacks modern video rendering capabilities. **PySide6** is the official Python binding for **Qt 6** (a industry-standard C++ framework used by Adobe, Autodesk, and Tesla for desktop UIs).

### PySide6 Multimedia Architecture (`QtMultimedia`)
PySide6 splits video playback into 3 specialized components:

```
[ QMediaPlayer ]  ──────▶ Decodes video & tracks state (Play/Pause, Position ms)
       │
       ├───▶ [ QVideoWidget ]  ────▶ Paints video frames to the screen canvas
       │
       └───▶ [ QAudioOutput ]  ────▶ Routes audio streams to system speakers
```

1. **`QMediaPlayer`**: The engine/decoder state machine. Manages timeline position in milliseconds, playback state (`PlayingState`, `PausedState`), and seeking.
2. **`QVideoWidget`**: The visual screen/canvas component.
3. **`QAudioOutput`**: Audio handler.

---

## 6. Milestone 2 UI Design Highlights & Clever Tricks

### A. Custom Qt Signals (Observer Pattern)
In `VideoPlayerWidget`, we define custom signals:
```python
position_changed = Signal(int)
```
Instead of `MainWindow` digging into internal private attributes of `VideoPlayerWidget`, `VideoPlayerWidget` emits a signal whenever time changes. `MainWindow` listens to this signal. This is the **Observer Pattern**, keeping UI components decoupled.

### B. Prevention of UI Slider Jitter
In `MainWindow._on_position_changed()`:
```python
if not self._slider.isSliderDown():
    self._slider.setValue(position_ms)
```
When a user is actively dragging a video scrubber with their mouse (`isSliderDown() == True`), the video playback position update is prevented from fighting the user's mouse drag. This prevents UI jitter!

### C. Native System Icons (`QStyle.StandardPixmap`)
In `MainWindow`:
```python
self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
```
Instead of bundling custom `.png` image assets, Qt provides access to the operating system's native play, pause, and open icons.

### D. Headless GUI Testing with `pytest-qt` (`qtbot`)
In `tests/unit/test_gui.py`:
```python
def test_main_window_instantiation(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
```
`qtbot` is a special pytest fixture that creates Qt widgets in memory and cleans them up automatically without popping up visible windows during automated testing.

---

## 7. Deep Dive: Qt Signals & Slots (Publisher / Subscriber)

Qt event handling is built on two core concepts: **Signals** and **Slots**.

```
  [ Publisher / Broadcaster ]                       [ Subscriber / Receiver ]
           SIGNAL                                             SLOT
  (e.g., position_changed) ─────── .connect() ──────▶ (e.g., _on_position_changed)
             │                                                  │
             ▼                                                  ▼
     Fires: .emit(5000)                               Executes: _on_position_changed(5000)
```

1. **Signal (Publisher)**:
   * Has no body/implementation code.
   * Shouts: *"Hey, an event just occurred!"* by calling `.emit(data)`.
2. **Slot (Subscriber / Receiver)**:
   * A standard Python function or method (e.g., `def _on_position_changed(self, position_ms: int):`).
   * Receives the emitted data and executes the actual work.
3. **Signal Forwarding**:
   In `VideoPlayerWidget`:
   ```python
   self._player.positionChanged.connect(self.position_changed.emit)
   ```
   This catches internal C++ `QMediaPlayer` events and re-emits them on our custom `position_changed` signal. This hides internal player implementation details from `MainWindow`.

---

## 8. Milestone 3 Architecture: LosslessCut-Style Segment Cards

### A. Custom Canvas Painting (`TimelineWidget.paintEvent`)
Instead of relying on standard buttons or sliders, `TimelineWidget` subclasses `QWidget` and overrides `paintEvent()`. Using Qt's `QPainter` API, it converts timestamp ratios ($\frac{\text{start\_ms}}{\text{duration\_ms}} \times \text{width}$) to draw color-coded rectangles representing each surgical phase in real-time.

### B. Segment Card List (`SegmentCardWidget` & `IntervalTableWidget`)
Inspired by **LosslessCut**, `IntervalTableWidget` uses `QListWidget` rendering custom `SegmentCardWidget` cards displaying:
* Colored Phase Number Badge (`①`, `②`) matching `phase.color_hex`.
* Bold Surgical Phase Name.
* Monospace Timecode Range (`00:00:00.000  ➔  00:00:15.000`).
* Duration (seconds), Milliseconds, and Frame Count.

Clicking or double-clicking any segment card emits `seek_requested = Signal(int)`, instantly jumping video playback to that exact timestamp!

### C. Resizable Splitter Layout (`QSplitter`)
Using `QSplitter(Qt.Orientation.Horizontal)` allows annotators to dynamically drag and resize the boundary between the video player panel and the segment list panel to suit their monitor resolution.

---

## 9. Qt Key Enum Math Trick (`key - Qt.Key.Key_0`)

In `MainWindow.keyPressEvent()`:
```python
if Qt.Key.Key_1 <= key <= Qt.Key.Key_6:
    phase_id = key - Qt.Key.Key_0
    self.record_phase_transition(phase_id)
```

### How Enum Subtraction Works:
In C++ and Python Qt, key enum constants are sequential integers under the hood:
* `Qt.Key.Key_0` = `48`
* `Qt.Key.Key_1` = `49`
* `Qt.Key.Key_2` = `50`
* ...
* `Qt.Key.Key_6` = `54`

By subtracting `Qt.Key.Key_0` (48), we extract the exact integer `phase_id` mathematically:
* `49 - 48 = 1` (Phase 1)
* `51 - 48 = 3` (Phase 3)
* `54 - 48 = 6` (Phase 6)

This avoids writing 6 repetitive `if key == Qt.Key.Key_1: phase_id = 1` statements!

---

## 10. C0: Transactional Annotation Editing

An annotation edit can involve several related intervals. Mutating the existing interval first and validating later risks leaving the session half-changed if a later operation fails.

`AnnotationEditor` instead follows a transactional pattern:

1. Validate the current timeline and requested phase/timestamp.
2. Build a candidate interval list without changing the session.
3. Coalesce adjacent equal phase labels.
4. Validate complete `[0, duration_ms)` coverage.
5. Commit the candidate list and update the session timestamp only after every check succeeds.

This is the same core idea used by database transactions: either the complete change succeeds, or the original state remains intact. Keeping this service in the pure-Python domain layer also lets boundary behavior be tested without starting Qt.

---

## 11. Encapsulation, Coupling, and Domain Services

### Encapsulation and information hiding

Encapsulation means an object protects its internal state and exposes intentional operations that preserve its rules. Merely replacing a public assignment with a trivial getter or setter does not add meaningful protection; a useful method should express behavior or enforce an invariant.

For example, `session.replace_intervals(candidate)` would improve encapsulation only if it validated and committed the replacement safely, not if it simply assigned `self.intervals = candidate`.

### Coupling is not automatically bad

Objects must know about some other objects to collaborate. The goal is **loose, appropriate coupling**, not zero coupling. `AnnotationEditor` knowing about `AnnotationSession` and `AnnotationInterval` is appropriate because safely editing them is its domain responsibility. It should not know about Qt buttons, media-player internals, JSON paths, or timeline painting.

### Domain service versus presenter

`AnnotationEditor` is a domain service: it contains pure annotation rules such as splitting, coalescing, and validating intervals. A presenter/controller coordinates application components: it receives a mouse or hotkey action, asks the player for its position, calls the editor, handles errors, and refreshes the timeline and segment list.

```text
Qt input -> Presenter/controller -> AnnotationEditor -> AnnotationSession
                |
                +----------------------> refresh UI views
```

`MainWindow` currently performs presenter work as well as view construction. The planned architecture gradually removes domain mutation from it.

### Law of Demeter

The Law of Demeter is often summarized as “talk only to your immediate friends.” Code such as `main_window._player_widget._player.position()` reaches through one object into another object's private implementation and creates fragile coupling. A public method such as `player_widget.position_ms()` lets callers depend on the wrapper's contract instead.

Directly assigning `session.intervals` is a conscious tradeoff in the current dataclass/domain-service design. A richer domain model could instead make the session validate and commit replacements, while another approach could have the editor return a new state without mutating the session. We should choose that boundary deliberately as undo/redo and persistence are developed.
