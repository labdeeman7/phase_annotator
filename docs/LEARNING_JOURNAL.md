# Software Engineering Concepts & Design Patterns Journal

This document records the architectural patterns, design decisions, and testing concepts used in **Phase Annotator**. Appendectomy is the currently bundled default ontology, not a restriction of the annotation engine.

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

### Relabel by command, relocate selection by domain identity

C3.3 relabels and coalesces transactionally, so the selected interval's numeric list index may disappear or change. The UI records a timestamp inside the original interval and, after a successful commit, selects whichever normalized interval contains that timestamp. This avoids pretending that a mutable list position is a durable segment identity. A future persisted segment identifier could replace this temporal anchor if annotation operations require stronger identity semantics.

### Model one shared boundary, not two independent endpoints

C3.4 represents the boundary between adjacent intervals by the index of the interval on its right. Moving it replaces the left interval's end and the right interval's start together, then validates and commits once. This models the real invariant directly: adjacent segments share one boundary. Exposing unrelated setters for both timestamps would make gaps and overlaps representable during an edit.

The editor returns `False` for a no-op rather than treating it as an error. “The command was valid but changed nothing” is different from “the command was invalid”; callers can avoid unnecessary refreshes and present accurate feedback when that distinction matters.

### Delete is a domain decision, not merely list removal

C3.5 does not remove an interval from the list and leave a temporal hole. It asks how the interval's time should be represented: Undefined, absorbed left, or absorbed right. The UI disables impossible directions, while the domain independently rejects them so correctness does not depend on button state. Destructive-looking UI commands should be translated into explicit domain operations that preserve the aggregate's invariants.

## C4.1 — Undo/redo as a state machine

Undo/redo uses two stacks. A successful new command stores its before/after snapshots on the Undo stack and clears Redo. Undo restores the newest before-state, moves that entry to Redo, and Redo restores its after-state and moves it back to Undo. This is not a loop in the Python-control-flow sense; it is a small state machine driven by commands from the user.

Snapshot history was chosen over custom inverse commands. Inverses are attractive when operations are simple, but this editor splits and coalesces intervals and combines notes. Reconstructing the exact prior state from an inverse would be harder to reason about than retaining a copied valid state. The tradeoff is memory, so history is bounded to 100 commands.

Copies are essential because `AnnotationInterval` is mutable. Storing references to `session.intervals` would not preserve history: later note or boundary changes could modify objects supposedly representing the past. `_snapshot()` creates replacement interval objects both when recording and restoring.

`AnnotationHistory.execute()` accepts the mutation as a callable. It captures Before, invokes the transactional editor operation, and captures After only when that operation returns `True`. A no-op or exception therefore creates no entry. It also detects a broken command that reports a change without changing intervals, or reports no change after mutating them.

Undo checks that the current annotation equals the entry's expected After snapshot; Redo checks for Before. This optimistic consistency check prevents a stale history stack from silently overwriting intervals changed outside the command pipeline. Restoration then goes through `AnnotationEditor.restore_intervals()` instead of assigning the list directly.

The temporal anchor is separate from the snapshot. Interval indexes are unstable after splitting and coalescing, so the UI selects the restored interval containing the command's anchor rather than reusing an old index. Text-entry focus disables application history shortcuts so `Ctrl+Z` remains available to the active text editor.

### C4.2 — Hit testing before mutation

The timeline converts every internal boundary timestamp into an x-coordinate, then uses a generator expression to find the `(distance, boundary_index)` pair with the smallest distance. Python tuple ordering also makes an exact tie deterministic by choosing the smaller index. The boundary is interactive only when that distance is within eight pixels.

Separating hit testing and hover feedback from dragging makes the interaction easier to verify: C4.2 can prove which boundary the user targeted without changing annotation data. C4.3 can then build a drag state machine on top of that stable geometric decision.

### C4.3 — Preview is not committed state

An active drag stores boundary index, original timestamp, preview timestamp, and preview validity inside `TimelineWidget`. Mouse movement changes only those fields and requests a video seek. Mouse release emits one commit intent only when valid and changed; `MainWindow` then uses the same `AnnotationEditor.move_boundary()` and history gateway as button-based correction.

This distinction prevents dozens of mouse-move events from becoming dozens of domain mutations or Undo entries. It is a general interaction pattern: keep rapidly changing gesture state local and temporary, then translate the completed gesture into one application command.

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

---

## C5.1 — Store a value together with what we know about it

A numeric value alone can overstate certainty. The player currently uses `30.0` FPS, but that number is an application assumption rather than a fact measured from the video. `VideoInfo` therefore stores `fps`, `fps_source`, and `frame_rate_mode` separately. This lets later code display an estimated frame number without pretending that the media is confirmed constant-frame-rate.

This is a reusable modeling technique: when provenance or confidence changes the meaning of a value, represent it explicitly instead of hiding it in comments or relying on callers to remember. The derived `frame_numbers_are_estimated` property centralizes the rule so UI code does not repeatedly reconstruct it.

A file path is similarly a **locator**, not an identity. Size and modification time are cheap comparison evidence, but two files can share them and a single file can move. Naming the group a source descriptor makes that limitation visible in the design. Schema 1.1 adds these fields as optional defaults, which is a simple additive-evolution strategy that keeps older 1.0 JSON readable.

## C5.2 — Adapters isolate uncertain external metadata

Qt metadata arrives asynchronously and differs by operating-system backend. `MediaMetadata` is therefore a small neutral result, while `read_qt_media_metadata()` is an adapter that translates Qt-specific objects at the application boundary. The annotation domain never imports Qt and missing metadata remains `None` rather than becoming a fabricated default.

Asynchronous results can become stale: a slow signal for video A might arrive after video B is opened. `MainWindow` compares the result's resolved source path with the current source before applying it. This is a reusable UI rule—an asynchronous result should carry enough context for its receiver to prove that it still belongs to the current request.

## C5.3 — Conservative comparisons should explain their evidence

A source comparison is not naturally just `True` or `False`. Missing old-session metadata means “we do not know,” which differs from “a known field conflicts.” `SourceMatchStatus` therefore models three states, while `SourceEvidence` preserves how every field contributed. This is useful whenever uncertainty must not be silently converted into success or failure.

The absolute path is deliberately excluded from the overall conflict decision: paths answer “where was it?” rather than “what is it?” A moved file can still match its filename and other descriptor evidence. Conversely, filename agreement alone remains unknown because it is too weak to accept a source confidently.

## C5.4 — The UI must preserve uncertainty from the model

The first implementation repeated `Estimated`, FPS provenance, milliseconds, and approximation symbols across the main label, buttons, and every segment card. Manual use showed that this was technically explicit but harmed the primary clinical workflow. The revised UI keeps compact `Frame N`/`N frames` labels and puts the caveat in one tooltip, while the model retains full provenance and uncertainty.

This illustrates progressive disclosure: preserve important detail, but present it only where it helps the current decision. Internal correctness does not require every implementation detail to occupy permanent screen space. Millisecond timestamps remain authoritative in storage even though segment cards show the friendlier duration in seconds.

## C5.5 — Translate infrastructure failures at the boundary

`QMediaPlayer` reports framework-specific error enums and backend strings. `VideoPlayerWidget` translates those into application-level messages before emitting them, so `MainWindow` only decides what failed media means for the workflow: pause, disable unsafe controls, and show the explanation.

This separates mechanism from policy. The wrapper understands Qt's failure vocabulary; the window understands whether annotation is allowed. The same distinction makes both sides easier to test.

## C6.1 — Continuous persistence changes what “dirty” means

In a traditional document editor, an edit usually makes the document dirty until the user presses Save. Phase Annotator will instead write its canonical sidecar after every successful annotation command. Here, dirty means only that memory differs from the **last successful write**, usually because persistence failed. That definition makes close prompts exceptional rather than routine.

The JSON repository knows how to serialize and atomically replace one file. The persistence coordinator adds application policy: derive the sidecar path, decide when saving is allowed, validate before loading, track dirty state, and interpret failures. Keeping those responsibilities separate prevents file-format code from becoming coupled to Qt workflow.

C7 originally deferred additional autosave/recovery under the YAGNI principle (“you aren't gonna need it”). Supervisor feedback later supplied a concrete need for a lightweight historical trail, so C7 was narrowed to one snapshot per changed video run rather than periodic duplicate autosaves. CSV remains deferred until a downstream consumer demonstrates a need.

### Identity, attribution, and resume are different state

The person currently operating the application is not automatically the creator, last editor, or completer of every opened annotation. Likewise, the shared resume position is navigation state rather than evidence of an individual's review. Modeling these concepts separately prevents convenient UI state from becoming misleading research provenance.

Canonical dirty state and “annotation changed since this video was opened” answer different questions. Dirty means memory is ahead of the last successful disk write; changed-since-open decides whether close/replacement merits a historical snapshot. One Boolean cannot safely represent both facts.

The first C7 design modeled explicit work sessions and in-application identity switching. Manual use showed that the additional controls and records made the annotator feel administrative. Removing a technically coherent abstraction after usability feedback is good engineering: the simplest model that preserves the required attribution and history is preferable.

## C8.1 — Paired fields can encode a state-machine invariant

`status`, `completed_at`, and `completed_by` are not three independent values. Together they describe one lifecycle state: a draft has neither completion field, while a completed annotation has both. Enforcing that relationship in `AnnotationSession.__post_init__()` makes invalid combinations impossible at every construction boundary, including JSON loading and tests, instead of relying on each future UI action to remember the rule.

This is a small example of modeling a state machine with validated data. The UI will later perform the transition, but the domain model remains the final authority on which states are legal.

## C8 — Protect transitions, not just fields

Marking an annotation complete is a human declaration, while reopening it is a state transition with side effects. The application therefore routes every annotation mutation through one editability guard. Reopening verifies the canonical file, archives the completed version, and only then changes the working state to Draft. Centralizing that rule prevents individual hotkeys, menus, drag handlers, undo, or redo from accidentally bypassing it.

The completion summary is a pure function: identical session data always produces identical review facts. Keeping calculation separate from the confirmation dialog makes it easy to test and avoids placing data rules inside widget code.

## C8.7 — A design system fixes hierarchy, not only color

The original interface mixed dark custom annotation widgets with Qt's default light window, menus, controls, and dialogs. Each individual part worked, but the visual system looked accidental and important navigation blended into empty chrome. A small centralized stylesheet now defines shared surfaces, borders, hover/focus states, disabled states, and primary-action emphasis.

Centralizing these tokens is more maintainable than adding unrelated style strings to every widget. Phase-specific color remains local because it represents annotation data; general application chrome belongs to the shared theme.

## C9 — Usability features still need evidence

The first C9 pass added timeline zoom beside playback speed. Although zoom was presentation-only and technically correct, two nearby multiplier controls made the interface harder to understand. Manual use supplied stronger evidence than the original feature hypothesis, so timeline zoom was removed and playback speed was made more capable. Deleting a confusing feature is often a better usability improvement than refining it.

Playback rate remains transient player state rather than annotation data. Keeping convenience settings out of `AnnotationSession` prevents them from contaminating research data or creating unnecessary saves.

Feedback also has hierarchy. A status bar is suitable for routine, short-lived state, but write failures and blocked source associations can be missed there. A reusable banner gives actionable problems a stable visual location while lifecycle decisions continue to use explicit modal confirmation.

Keyboard shortcuts should be alternate entrances to existing commands, not separate implementations. Delete calls the same Convert to Undefined resolution used by the segment menu, so validation, undo history, persistence, completed-state protection, note preservation, and view refresh remain consistent.

## C9.7 — A visible filename is not the data authority

Adding the procedure to sidecar filenames initially sounds clearer, but it would let an accidental procedure choice miss the existing file and create a second incorrect annotation. The safer rule is one canonical sidecar whose persisted ontology identity controls interpretation. The filename locates the annotation; validated content determines what its phase IDs mean.

## C10.2 — Tool output is evidence, not a command

A linter can report hundreds of findings when broad rule families are enabled, but the count is not a defect count. Many findings are mechanical modernization or stylistic preferences. A useful baseline selects rules whose purpose the team understands, reviews behavior-sensitive findings manually, and expands deliberately rather than rewriting the repository to satisfy a tool.

Formatting, linting, type checking, and tests answer different questions. Ruff formatting makes layout deterministic; Ruff linting detects selected suspicious source patterns; Mypy checks declared type relationships; pytest exercises observable behavior. Passing one layer does not substitute for the others.

Static typing can be adopted by architectural boundary. The pure domain and persistence layers have predictable values and are a strong initial target. Qt APIs expose dynamic objects and GUI state changes over time, so the UI needs deliberate narrowing rather than blanket `ignore` comments. At a genuinely dynamic adapter boundary, `cast(Any, value)` documents where static knowledge ends while runtime validation and exception handling remain authoritative.

### TOML, `pyproject.toml`, and build systems

TOML is a general configuration-data format, like JSON or YAML; a `.toml` file is not inherently a build script. `pyproject.toml` is the standardized Python project configuration file. Its `[build-system]` table chooses a build backend such as setuptools, while other tables describe package metadata, dependencies, tests, formatting, linting, and type checking.

This overlaps with what `CMakeLists.txt` does for a C/C++ project, but they are not direct equivalents. CMake is a build-system generator with its own command language. `pyproject.toml` is declarative configuration read by multiple independent Python tools; the selected backend performs the package build, and tools such as pytest, Ruff, and Mypy read only their own tables.

### A successful build is not necessarily a releasable build

PyInstaller successfully produced and launched the first one-folder application, but its build log also reported unresolved DLLs inherited from the Miniconda base interpreter. The artifact is useful evidence that entry-point, Qt-hook, and resource discovery work, but it is not an approved release candidate. Build provenance and warnings are part of correctness: release automation should distinguish an exploratory artifact from one created in the supported clean environment.

PyInstaller's `build/` and `dist/` directories have different roles. `build/` contains intermediate analysis, archives, warnings, and a partially assembled executable used by the build pipeline. That intermediate executable is not expected to run alone because its collected Python/Qt runtime is absent. `dist/` contains the deliverable layout; for one-folder mode, the runnable executable and its `_internal` directory must remain together.

### Project metadata, packaging recipe, and build orchestration are separate layers

`pyproject.toml` declares the Python project: metadata, runtime/development/release dependencies, the setuptools backend, package data for Python distributions, and settings for pytest/Ruff/Mypy. Pip reads it when creating or installing the development/release environment. PyInstaller does not normally use it as the executable recipe.

`PhaseAnnotator.spec` is the executable-freezing recipe. PyInstaller executes this Python file to analyze imports, create the Python module archive and bootloader executable, include explicit data/native dependencies, and collect the one-folder artifact. `scripts/build_windows.ps1` is the outer orchestration and safety layer: it selects and validates the interpreter, invokes PyInstaller with the `.spec`, checks exit status, and verifies release-critical output files.

### Test the artifact through its public boundary

Source tests can prove that resource loaders and windows work in a virtual environment, while a filesystem check can prove that JSON files exist under `dist/`; neither proves the frozen executable can actually load those resources. A narrow noninteractive executable argument lets release automation exercise the application from outside the bundle, using the same packaged resource APIs and real window construction, and judge success by process exit code. This complements rather than replaces manual codec and workflow acceptance.

### CI is a clean-room execution of repository knowledge

Continuous integration is not merely “run the tests somewhere else.” A hosted runner begins without the project's virtual environment or local shell history, so every dependency, Python version, environment variable, command, and build input must be declared in the repository. A green CI run is evidence that the project can be reconstructed from versioned knowledge rather than undocumented machine state.

Validation and artifact production have different costs and triggers. Fast source checks should run on every push and pull request. A large Windows application artifact can be built intentionally through manual dispatch after validation succeeds, avoiding unnecessary build time and storage while keeping the release recipe automated.
