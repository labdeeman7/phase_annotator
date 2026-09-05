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

### B. Historical Factory Method (`PhaseOntology.default_appendectomy()`)
* **What it was**: The M1 implementation used a class method (`@classmethod`) to hide construction of six hard-coded `Phase` objects.
* **C1 replacement**: Phase metadata now lives in packaged/user-selected versioned JSON. Generic config adapters perform resource/path I/O and delegate pure validation/construction to `PhaseOntology.from_config()`. The composition root calls `load_default_ontology()` for today's launch policy and injects the result, keeping reusable UI independent of procedure choice.

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
    window = MainWindow(ontology=test_ontology)
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

### One command, multiple input methods

A mouse button and a keyboard hotkey are two ways to express the same user intention: assign a phase at the playhead. They should not contain separate annotation logic. `PhasePaletteWidget` emits a phase ID, while configured hotkeys resolve to a phase ID; both then call `MainWindow.record_phase_transition()`. This keeps validation, interval changes, feedback, and view refresh behavior identical.

The palette's checked button is derived from the interval under the playhead rather than treated as an independent source of truth. This prevents the palette, timeline, and session from disagreeing after a seek or edit.

### Keyboard focus is an interaction context

Qt sends ordinary key events to the widget that currently owns keyboard focus. A `QListWidget` may consume a phase key after the user selects a segment, so relying only on `MainWindow.keyPressEvent()` makes application hotkeys intermittent. Window-scoped `QShortcut` objects make configured annotation keys available across ordinary child widgets.

Global availability is not always desirable. The application disables phase shortcuts while a text field or the segment list has focus: text must remain text, and list keys are reserved for explicit segment editing. The timeline accepts click focus, so clicking it deliberately restores the normal playhead-annotation context. This treats focus as meaningful UI state rather than forcing focus back to the main window after every action.

### Selected state is not active state

The segment selected for editing and the segment beneath the video playhead answer different questions. `MainWindow` owns the transient selected interval index and sends it to both views; it separately derives the active interval from the current timestamp. This permits an annotator to select one segment and move the playhead for comparison or boundary work without silently changing the edit target.

An interval index is safe only while the interval list keeps the same structure. Splitting or coalescing can make index 2 refer to a different segment, so current structural transitions clear selection. A later editing command can deliberately reselect the resulting segment once its outcome is defined.

### Comments should explain why, not narrate what

Useful comments preserve information that the code cannot express clearly by itself: an invariant, a design tradeoff, a framework quirk, or why an apparently unnecessary guard exists. For example, the selection bounds check is not merely “checking the index”; it protects future session-replacement paths from displaying an old index as a different segment.

Comments such as `# increment count` above `count += 1` add no information. They make a file longer and can become false when code changes. Prefer clear names and small functions for explaining *what* code does, docstrings for a function's contract or role, and a short inline comment for a surprising *why*. Detailed architectural reasoning belongs in project documentation or a decision record rather than inside every call site.

### A UI draft is not committed domain data

The discarded permanent-inspector prototype demonstrated that text in an editor can differ from committed `AnnotationInterval.notes`. The final modal design narrows that temporary draft to the lifetime of one dialog: `AnnotationSession` remains the source of truth, Save commits through the editor, and Cancel simply closes the draft.

A navigation action originally used separate “select” and “seek” signals. C3.2 combines them into one selection request containing the index and timestamp, so `MainWindow` receives the complete user intention before performing its consequences. The modal note design no longer needs to cancel navigation, but the combined signal still prevents ordering ambiguity and represents the interaction more clearly.

### C3.2 Python and engineering idioms

`dataclasses.replace(interval, notes=new_notes)` constructs a new dataclass instance while copying every field not explicitly replaced. It expresses “the same interval except for its notes” more safely than repeating every constructor argument, and avoids mutating the existing object before validation succeeds.

`SegmentInspectorWidget.is_dirty` is a derived `@property`: it compares current editor text with the last committed text whenever asked. Keeping the source values and deriving the answer avoids a second Boolean flag that could become inconsistent with them.

Qt signals carry intent across ownership boundaries. `save_note_requested = Signal(str)` lets the inspector announce “the user wants to save this text” without knowing about `AnnotationSession` or `AnnotationEditor`. Likewise, the combined `(interval_index, seek_ms)` selection request allows `MainWindow` to approve or cancel the whole interaction before applying either consequence.

### Match persistent UI space to task frequency

The first C3.2 prototype placed note editing permanently in the sidebar. Review showed that notes are exceptional supporting data, while video, timeline, and segment navigation are the frequent core workflow. The accepted direction moves note editing behind a right-click context menu and a visible **...** affordance, then uses a modal Save/Cancel dialog. Persistent screen space should generally serve frequent tasks; uncommon actions can use progressive disclosure, provided there is a discoverable path.

This change also reduces state complexity. A permanent editable draft requires every navigation and structural action to negotiate Save/Discard/Cancel. A modal dialog contains the draft within one interaction, so the rest of the application does not need to coordinate partially edited note text. Good interaction design can remove state and error cases rather than merely rearranging widgets.

The editor returns `False` for a no-op rather than treating it as an error. “The command was valid but changed nothing” is different from “the command was invalid”; callers can avoid unnecessary refreshes and present accurate feedback when that distinction matters.

### Law of Demeter

The Law of Demeter is often summarized as “talk only to your immediate friends.” Code such as `main_window._player_widget._player.position()` reaches through one object into another object's private implementation and creates fragile coupling. A public property such as `player_widget.position_ms` lets callers depend on the wrapper's contract instead.

Directly assigning `session.intervals` is a conscious tradeoff in the current dataclass/domain-service design. A richer domain model could instead make the session validate and commit replacements, while another approach could have the editor return a new state without mutating the session. We should choose that boundary deliberately as undo/redo and persistence are developed.

---

## 12. Deriving UI State from the Component That Owns It

The Play/Pause button should reflect `QMediaPlayer`'s actual playback state, not merely toggle its own text when clicked. Playback can also stop because media ends, loading fails, or another command pauses it. `VideoPlayerWidget` therefore translates Qt's detailed playback-state signal into a simple `playback_state_changed(bool)` signal, and `MainWindow` derives the button text/icon from that event.

This follows a broader single-source-of-truth rule:

```text
QMediaPlayer owns playback state -> signal -> button presentation
AnnotationSession owns intervals -> refresh -> timeline and segment list
```

Views should display authoritative state rather than maintain independent guesses. This is why the segment-list regression was fixed at the annotation-state boundary instead of teaching the list widget to repair intervals itself.

---

## 13. Configuration Roles Are Not the Same as IDs

A phase ID is a stable identity stored in annotations. It should not also be expected to imply display order, keyboard input, or which phase initializes a new video. C1 separates these concepts:

```text
id                 persisted identity
order              expected clinical/display guidance
hotkey             user input mapping
initial_phase_id   provisional starting label
undefined_phase_id uncertainty/exception role
```

This avoids fragile assumptions such as “the smallest ID is always first” or “list position determines meaning.” It also lets another ontology choose Undefined as its initial phase without changing annotation algorithms.

The parser/adapter split preserves architectural boundaries: `PhaseOntology.from_config()` validates an already-decoded mapping using pure Python, while `phase_annotator.config` owns JSON and packaged-resource/path I/O. Invalid configuration is rejected before reaching widgets or sessions.

Full provisional coverage still does not imply completed review. The separately approved lifecycle model will persist draft/completed status, resume position, and contiguous review progress when session persistence is integrated.

### Composition root and dependency injection

An early C1 version had `MainWindow` call `load_default_appendectomy_ontology()`. That made a supposedly reusable window decide both which procedure it represented and how configuration was loaded.

The corrected flow is:

```text
__main__.py (composition root)
    -> select/load current ontology
    -> MainWindow(ontology)
        -> AnnotationEditor(ontology roles)
        -> TimelineWidget(ontology)
        -> SegmentListWidget(ontology)
```

The **composition root** is the outer startup location where concrete dependencies are selected and assembled. **Dependency injection** means a component receives what it needs rather than constructing a specific dependency internally. `MainWindow` now knows only the `PhaseOntology` contract, so a future cholecystectomy ontology can be supplied without changing window logic.
