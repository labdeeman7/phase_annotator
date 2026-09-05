# C3 Segment Selection and Correction Workflow

## Outcome

C3 turns the existing phase-transition prototype into a usable correction tool. An annotator must be able to choose an existing segment, inspect it, relabel it, adjust its shared boundaries, edit notes, and deliberately remove/merge it without creating a gap, overlap, or ambiguous edit target.

This milestone is intentionally split into reviewable vertical slices. C4 adds timeline dragging and undo/redo only after the underlying correction commands are safe.

## Interaction concepts

- **Playhead-active segment:** the interval containing the current video timestamp. It is derived from session intervals and shown with a white outline.
- **Selected segment:** the interval explicitly chosen for navigation or editing. `MainWindow` owns this transient selection and projects it into the timeline and segment list; it is shown with a cyan outline.
- **Phase transition:** a palette click or configured hotkey applies a phase from the playhead to the end of the containing segment.
- **Selected-segment edit:** an explicit action from the selected segment's context menu changes that existing segment. Merely selecting a segment never mutates annotation data.

Selection and active state may refer to different segments. Moving the ordinary playback slider changes the active segment while preserving the selected edit target.

## C3.1 — Selection and navigation

Status: **Completed and manually accepted on 2026-09-03.**

- Single-clicking a segment card selects it and seeks to its start.
- Clicking inside a timeline interval selects it and seeks to the clicked timestamp.
- Timeline and segment-list selection stay synchronized; the selected card scrolls into view.
- Cyan identifies selection and white identifies the playhead-active interval.
- The playback slider moves the playhead without changing selection.
- A structural phase transition clears selection because splitting/coalescing can make an old interval index refer to different data.
- Segment-list focus reserves phase hotkeys for future editing; clicking the timeline restores the annotation shortcut context.

## C3.2 — Compact segment actions and notes

Status: **Revised interaction implemented on 2026-09-05; awaiting manual acceptance.** The earlier permanent inspector prototype was replaced before acceptance.

Notes are occasional supporting information, so they must not permanently consume right-sidebar space needed by the segment list. Keep phase, start/end, and duration visible on each segment card. A card with a non-empty note displays a compact note indicator and may expose the note in a tooltip.

Right-clicking a segment card, or clicking its visible **...** action button, opens the same context menu. The first action is **Edit note...**. This visible button makes the otherwise hidden right-click interaction discoverable. The menu becomes the shared home for later selected-segment actions such as relabeling, boundary correction, conversion to Undefined, and merging.

**Edit note...** opens a small modal dialog with a multiline editor and explicit Save/Cancel actions. Save invokes the tested `AnnotationEditor.update_notes()` operation, updates `session.updated_at`, refreshes the segment card, and preserves selection because interval structure did not change. Cancel closes the dialog without modifying the session. Empty notes are valid. Because the draft is modal, ordinary seeking and selection do not need global unsaved-inspector handling.

Interaction vocabulary:

- Single-click a segment: select it and navigate to it.
- Right-click or click **...**: show actions that modify that segment.
- Palette click or phase hotkey: record a phase transition at the playhead.
- Double-click remains unassigned until a frequent primary action justifies it.

## C3.3 — Whole-segment relabeling

Add **Change phase...** to the shared segment context menu. It opens an explicit configured phase-selection interaction before applying the whole-segment change.

- Palette/hotkey input continues to mean **transition at playhead**.
- Context-menu phase input means **relabel the complete selected segment**.
- Relabeling to the existing phase is a no-op.
- Adjacent equal phases coalesce automatically.
- Notes are preserved when relabeling and combined rather than discarded if coalescing occurs.
- Selection should move to the resulting coalesced segment when it can be identified unambiguously; otherwise clear it rather than selecting the wrong data.

## C3.4 — Precise shared-boundary correction

Add **Set start to playhead** and **Set end to playhead** actions. These move a shared boundary; they must never create gaps or overlaps.

- Setting a selected segment's start also changes the previous segment's end.
- Setting its end also changes the next segment's start.
- The first segment always starts at `0`; therefore it has no movable start boundary.
- The last segment always ends at `video.duration_ms`; therefore it has no movable end boundary.
- The proposed boundary must leave both neighboring intervals with positive duration and remain inside video bounds.
- Build and validate a candidate interval list before committing it. Invalid requests leave the session unchanged and produce useful feedback.
- Button-based precision comes before draggable handles; dragging is C4.

## C3.5 — Remove, Undefined, and merge

An explicit removal action asks the annotator to choose:

- **Convert to Undefined:** relabel the selected interval with the configured `undefined_phase_id`, then coalesce equal neighbors.
- **Merge left:** absorb the selected interval into the previous segment by adopting the previous phase, preserving/combining notes, then coalescing.
- **Merge right:** equivalent using the following segment.
- **Cancel:** make no change.

Unavailable directions must be disabled: the first segment cannot merge left, the last cannot merge right, and a single full-video segment has neither merge direction. Conversion to Undefined remains available, including for the only segment.

## Data-integrity rules

Every C3 mutation belongs in the pure-Python editor, not a Qt event handler. It must:

1. validate the current session and requested target;
2. construct a candidate interval sequence;
3. preserve notes unless the user explicitly changes them;
4. coalesce adjacent equal labels where applicable;
5. validate known phase IDs and exact contiguous `[0, duration_ms)` coverage;
6. commit once, updating `session.updated_at`, only after validation succeeds.

UI selection is transient and is not persisted as annotation data.

## Testing and acceptance

- Unit tests cover successful operations, no-ops, first/last interval restrictions, invalid playhead positions, note preservation, coalescing, and no partial mutation after failure.
- Qt tests cover context-menu invocation by right-click and the visible action button, note-dialog Save/Cancel behavior, note indication, selection preservation or deliberate clearing, and synchronization of timeline/list.
- Manual acceptance uses a synthetic or non-sensitive representative video to correct several segments using both navigation views and the playback slider.

## Learning-mode reading map

For each slice, focus on:

1. the new public method on `AnnotationEditor` and its tests;
2. the context-menu/dialog action that calls it;
3. the small `MainWindow` method that coordinates selection and refresh.

Widget layout/style declarations and repetitive pytest setup can be skimmed unless visual behavior is under review.

The handoff should also identify a few intermediate/advanced Python or engineering idioms actually used by the slice. These are complements to the reading map, not extra exercises or a requirement to explain every language feature.
