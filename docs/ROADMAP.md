# Project Roadmap

## Product outcome

Deliver a dependable desktop application for annotating temporal phases in surgical videos. It should ship with a clinically reviewed appendectomy phase set, allow phase selection by mouse and keyboard, preserve annotations safely, resume interrupted work, and export deterministic research data.

The architecture should remain sufficiently flexible to load another phase set without rewriting UI or domain logic. This is flexibility through a small validated configuration contract—not a general-purpose annotation platform or plugin system.

## Definition of project completion

The first complete release is reached when an annotator can:

1. launch an installable application on a supported Windows system;
2. select an annotator identity and open a supported local video;
3. see the configured phases, colors, and hotkeys, including `U` for Undefined;
4. annotate and correct the entire video using mouse or keyboard;
5. save, close, reopen, and resume without losing or corrupting work;
6. recover a newer autosave after an interrupted session;
7. see validation problems and resolve them before final export;
8. export versioned JSON and deterministic research CSV;
9. reproduce the same results through documented tests and a CI build.

Real representative videos must be used for a manual acceptance pass. Automated widget tests alone cannot prove codec availability, seeking behavior, usability, or timing accuracy.

## Delivery principles

- Build small vertical slices with one observable outcome each.
- Specify annotation semantics before persisting or exporting them.
- Keep domain rules pure Python; keep Qt and filesystem concerns at adapters/boundaries.
- Route mouse and keyboard actions through the same application command so behavior cannot diverge.
- Treat milliseconds as the authoritative time unit until media probing and frame semantics are explicitly implemented.
- Preserve backward compatibility or provide a deliberate migration when persisted schemas change.
- Prefer clear, inspectable designs over speculative abstractions.
- Do not use real patient identifiers or commit clinical media/data.

## Inherited baseline: Antigravity M0-M3

Status: prototype complete; stabilization required.

- Repository structure, domain isolation rules, and documentation exist.
- Phase/session/interval models and a six-phase appendectomy ontology exist.
- Atomic JSON replacement exists as an unwired storage adapter.
- Qt Multimedia playback shell, timeline, segment cards, seeking, and hotkeys exist.
- The local Python 3.11 `.venv` is established; all 18 inherited tests and GUI startup smoke test pass.

These milestones are not considered production-ready. Known gaps are tracked in `CURRENT_STATE.md`.

## Codex milestone sequence

### C0 — Annotation contract and safe transition engine

Goal: make phase transitions a well-defined, testable domain/application operation before expanding the UI.

Status: **Completed on 2026-09-02.**

Accepted product rules:

- `Undefined` is a real configured label selected by `U`.
- The timeline has full coverage; gaps and overlaps are invalid.
- Phase labels may repeat and appear out of nominal surgical order.
- Delete asks whether to convert to Undefined, merge into the previous/next segment, or cancel.
- Adjacent equal labels are automatically merged.

Settled transition semantics:

- Once duration is known, an empty session begins as one interval using the ontology's explicit `initial_phase_id` over `[0, duration_ms)`; the appendectomy default is Phase 1.
- Selecting the phase already active at the playhead is a no-op.
- Selecting a different phase inside a segment splits it at the playhead and relabels only the remainder of that segment; later established segments remain intact.
- Selecting at an existing boundary relabels the segment beginning at that boundary.
- A transition at the exact video end is invalid under half-open interval semantics.
- Resulting adjacent equal labels are coalesced.

C0 implementation status:

- The pure-Python transactional `AnnotationEditor` and contiguous-coverage validation are implemented and tested.
- `MainWindow` delegates phase transitions to the editor and refreshes both annotation views from the resulting session state.
- `VideoPlayerWidget` exposes public position, duration, and playback-state APIs/signals instead of requiring access to its private Qt player.
- Positive media duration initializes one full-video interval using the ontology's configured initial phase (Phase 1 for the appendectomy default).
- Play/Pause text and icons follow actual Qt playback state, and the status bar distinguishes Loading from Loaded.
- A regression test covers backward correction and verifies that stale segment cards are not retained.

Implementation:

- Introduce a pure-Python annotation command/service instead of mutating intervals in `MainWindow`.
- Validate phase IDs, bounds, ordering, overlap, and no-partial-mutation behavior.
- Expose player position and duration through public APIs.
- Add focused unit tests for boundary, same-time, backward, repeated, and end-of-video cases.

Exit gate: **Passed.** Transition semantics are documented; invalid commands leave the session unchanged; domain and GUI integration tests cover the agreed cases.

Learning focus: invariants, transactional state changes, and why UI event handlers should not own domain rules.

### C1 — Configurable phase definitions and Undefined

Goal: make appendectomy the default data-driven phase set rather than hard-coded UI behavior.

Status: **Completed on 2026-09-02.**

Implementation:

- Define a versioned JSON configuration schema containing stable ID, display name, hotkey, color, optional flag, description, and ordering.
- Include explicit ontology identity/version, expected display order, `initial_phase_id`, and `undefined_phase_id`; never infer these roles from numeric ordering.
- Add the default appendectomy configuration as a packaged resource, including `Undefined` with hotkey `U`.
- Validate duplicate IDs/hotkeys, missing labels, malformed colors, and unsupported schema versions with useful errors.
- Keep a programmatic fallback only if it serves a deliberate recovery/testing purpose.
- Record the configuration identity/version in each session so annotations remain interpretable later.

Exit gate: **Passed.** Valid configuration constructs an ordered ontology; invalid files fail clearly; the packaged default and session ontology identity/version round trips are covered by tests.

Learning focus: configuration versus code, schema validation, and stable identifiers.

### C2 — Visible mouse-and-keyboard phase palette

Goal: make phase selection discoverable and equally usable by mouse or hotkey.

Status: **Completed on 2026-09-02.**

Implementation:

- Add a visible palette showing key, color, phase name, and optional status.
- Clicking a phase and pressing its hotkey dispatch the same transition command.
- Show current/active phase and immediate transition feedback.
- Handle focus correctly so text-entry controls do not accidentally trigger annotations.
- Add accessible labels/tooltips and keyboard navigation.

Exit gate: every configured class can be selected both ways; pytest-qt verifies both paths produce identical session state; manual inspection confirms mappings are legible.

Learning focus: Qt signals/slots and one-command/multiple-input design.

### C3 — Selection, navigation, and precise correction

Goal: enable realistic annotation, not only append-at-playhead transitions.

Status: **In progress; C3.1 selection/navigation implemented on 2026-09-03.**

Implementation:

- Keep the phase palette visible above the segment list in the right sidebar.
- Select a segment from either the timeline or segment list and seek reliably.
- Visually distinguish the selected segment from the segment under the playhead.
- Relabel a selected segment only through an explicit editing interaction, avoiding ambiguous hotkey behavior.
- Provide precise start/end controls and set-boundary-to-playhead actions.
- Add notes editing.
- Implement Delete as conversion to Undefined and explicit Merge Left/Merge Right.
- Highlight the active segment and keep palette, list, timeline, and playhead synchronized.
- Remove or consolidate the unused duplicate segment widget once behavior is covered.

Exit gate: a user can navigate, relabel, delete-to-Undefined, merge, and precisely correct a complete synthetic annotation without editing JSON; all views remain synchronized.

Learning focus: model/view synchronization, editing context, and UI state ownership.

### C4 — Draggable boundaries and undo/redo

Goal: make temporal correction fast while keeping every edit safe and reversible.

Implementation:

- Draw discoverable shared-boundary handles on the timeline.
- Dragging a boundary previews the candidate time, seeks the video, and changes both neighboring intervals without gaps/overlaps.
- Enforce minimum positive duration and video bounds.
- Treat an entire mouse drag as one command rather than one command per movement event.
- Add undo/redo for transitions, relabeling, boundary moves, delete-to-Undefined, merges, and notes.
- Add `Ctrl+Z`, `Ctrl+Shift+Z`, and `Ctrl+Y` with visible availability/state.

Exit gate: boundary dragging is precise and cannot invalidate coverage; every supported annotation mutation round-trips through undo/redo; GUI tests cover drag commit/cancel behavior where practical.

Learning focus: command pattern, transient preview state, and transactional UI gestures.

### C5 — Media metadata and playback reliability

Goal: make timing claims explicit and playback failures understandable.

Implementation:

- Capture media duration, dimensions, and available frame-rate metadata.
- Choose and document a source-video identity strategy (for example normalized metadata plus file size/hash tradeoff).
- Surface Qt media loading/codec errors in the UI.
- Define CFR/VFR behavior and label displayed frame numbers as exact or estimated accordingly.
- Test seeking and annotation against small synthetic CFR media; manually test representative project media.

Exit gate: sessions can be matched safely to their source; unsupported media produces a useful error; timing limitations are visible and documented.

Learning focus: media time bases, metadata trust, and platform decoder boundaries.

### C6 — Manual session save, load, and dirty-state safety

Goal: establish the reliable session lifecycle before adding background recovery.

Implementation:

- Wire a session/application service to `JsonSessionRepository`.
- Implement Save, Save As, Open Session, `Ctrl+S`, recent path handling, and meaningful errors.
- Prompt before replacing/closing dirty work.
- Validate loaded schema, configuration identity, source-video identity, and intervals.
- Persist draft/completed lifecycle metadata plus distinct resume and contiguous-review progress fields.
- Decide backup and stale-temporary-file behavior; test write failures and round trips.

Exit gate: save-close-reopen preserves all data; destructive navigation is guarded; simulated persistence failures do not corrupt the last valid session.

Learning focus: repository boundaries, dirty state, atomicity, and failure-path testing.

### C7 — Autosave and crash recovery

Goal: recover work predictably without confusing autosaves with user-approved saves.

Implementation:

- Periodic/debounced autosave only when state is dirty.
- Separate recovery artifact and provenance from the canonical session.
- Startup/reopen prompt comparing recovery and saved timestamps.
- Restore, discard, and stale-recovery cleanup paths.
- Logging that contains no sensitive annotation content or patient identifiers.
- Restore resume position without treating a forward seek as reviewed footage.

Exit gate: forced termination loses at most the documented autosave interval; recovery choices are tested and understandable.

Learning focus: timers, recovery state machines, and canonical versus derived data.

### C8 — Validation, completion, and research export

Goal: produce trustworthy, reproducible research artifacts.

Implementation:

- Add a validation summary for gaps, overlaps, unknown phases, invalid bounds, and incomplete coverage according to the annotation contract.
- Distinguish draft save from completed/finalized session.
- Require an explicit completion action, validate review progress, and summarize Undefined duration/segments for informed confirmation.
- Confirm that editing a completed session reopens it as draft.
- Define a deterministic CSV schema with video identity, annotator, phase identity/name, timestamps, and configuration/schema versions.
- Ensure locale-independent ordering and formatting.
- Add golden-file and JSON-to-CSV integration tests.

Exit gate: invalid finalization is blocked with actionable messages; the same session always produces byte-equivalent CSV where intended; schema documentation includes an example.

Learning focus: validation boundaries, stable exports, and reproducible datasets.

### C9 — Usability and annotation efficiency pass

Goal: make sustained annotation practical after correctness is established.

Candidate work, validated with actual use rather than assumed upfront:

- Configurable seek/step controls and playback-speed options.
- Keyboard shortcut reference and onboarding hints.
- Better timeline zoom/navigation for long procedures.
- Status bar for save/autosave/media state.
- Layout persistence and high-DPI/accessibility review.
- Performance checks with long videos and many intervals.

Exit gate: a documented end-to-end usability session completes without data loss or high-severity friction; shortcuts and behavior match documentation.

Learning focus: profiling and evidence-led UX refinement.

### C10 — Engineering quality, CI, and release

Goal: make the project reproducible for contributors and distributable to users.

Implementation:

- Add a minimal formatter/linter/type-check policy after choosing tools deliberately.
- Add GitHub Actions for supported Python versions, domain/storage tests, and headless Qt tests.
- Add test coverage for critical workflows rather than pursuing a vanity percentage.
- Package a Windows build and document Qt Multimedia/runtime considerations.
- Perform clean-machine install, launch, annotate, recover, and export acceptance tests.
- Reconcile package/window versioning and write release notes/user guide.

Exit gate: CI is green from a clean checkout; a versioned artifact passes the release checklist on a clean supported machine.

Learning focus: CI, packaging boundaries, semantic versioning, and release discipline.

## Milestone workflow

Each milestone follows the same collaboration loop:

1. **Scope together:** confirm the user-visible outcome and any domain choice that changes data meaning.
2. **Inspect:** Codex reads the existing implementation and identifies the smallest coherent slice.
3. **Tests first where practical:** demonstrate the missing behavior or failure before implementation.
4. **Implement:** Codex owns the core engineering work and keeps the diff focused.
5. **Verify:** run narrow tests, the complete suite, compilation/static checks, and an appropriate GUI/manual smoke test.
6. **Explain:** summarize the architecture, important tradeoffs, and files worth inspecting.
7. **Small user exercise:** offer one bounded task—typically reviewing domain wording, adjusting a configuration entry, adding one analogous test, or manually exercising a workflow. It must reinforce the milestone, not transfer core delivery responsibility.
8. **Review and document:** update `CURRENT_STATE.md`, `TASKS.md`, decisions/schema/user docs, and the learning journal where useful.
9. **Commit checkpoint:** after user review, prepare a small milestone commit rather than mixing unrelated changes.

## Quality gates applied throughout

- No domain package imports from Qt or storage frameworks.
- No session/export write without validation and failure-path coverage appropriate to its risk.
- No UI-only implementation of a rule that determines annotation meaning.
- No claim of passing tests or working playback without executing the relevant check.
- No real clinical identifiers or media in fixtures, examples, logs, or commits.
- No silent schema/configuration incompatibility or data loss.
- No milestone is “done” solely because its happy-path widget exists.

## Immediate next step

Begin C3 by adding an explicit selected-segment editing context and synchronized timeline/list navigation. C3 and C4 deliver the core correction workflow before persistence work begins.
