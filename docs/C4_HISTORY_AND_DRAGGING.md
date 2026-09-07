# C4 Undo/Redo and Draggable Boundaries

## Outcome

C4 makes corrections fast and reversible without weakening the timeline invariants established in C0-C3. Every committed annotation mutation can be undone and redone, and a complete mouse drag becomes exactly one validated boundary command.

History is in memory and belongs to the currently loaded video. It is not persisted in session JSON. Playback, seeking, and UI selection are navigation state and do not enter annotation history.

## C4.1 — Undo/redo foundation

Status: **Completed and manually accepted on 2026-09-07.**

Use validated before/after interval snapshots rather than bespoke inverse logic. Snapshot storage is appropriate because interval sequences are small, while deriving inverses for splitting, coalescing, merging, and note combination would be complex and error-prone.

- Record successful phase transitions, note changes, relabels, boundary moves, Convert to Undefined, and Merge left/right.
- Do not record failed commands or valid no-ops.
- Undo restores the exact before-snapshot; Redo restores the exact after-snapshot.
- A new committed edit after Undo clears the redo stack.
- Loading a video clears both stacks.
- Restoring a snapshot goes through `AnnotationEditor` validation and updates `session.updated_at`.
- History snapshots must be copied so later mutation cannot alter past entries.
- Keep a bounded history of 100 commands to prevent indefinite memory growth during long annotation sessions.
- Add visible Undo/Redo buttons and `Ctrl+Z`, `Ctrl+Shift+Z`, and `Ctrl+Y` shortcuts.
- Disable unavailable controls and reserve text-editor undo/redo while a text-entry widget has focus.
- After restoration, select the interval containing the command's temporal anchor when possible; never trust a stale list index.

## C4.2 — Boundary handles and hit testing

Status: **Completed and manually accepted on 2026-09-07.**

- Draw subtle lines only for internal shared boundaries and emphasize the hovered handle in cyan.
- Use an 8-pixel nearest-boundary hit area and a horizontal-resize cursor near a handle.
- Preserve normal click-to-select/seek behavior away from handles.
- Test boundary choice independently from mutation.

## C4.3 — Drag preview and single commit

Status: **Planned.**

- Mouse press on a handle begins transient preview state.
- Mouse movement updates the preview and seeks the video without mutating the session.
- Valid mouse release calls `AnnotationEditor.move_boundary()` exactly once and creates one history entry.
- Invalid release displays a red preview/error and leaves the session unchanged rather than silently clamping.
- Escape cancels a drag; releasing at the original position is a no-op.

## C4.4 — Integration and refinement

Status: **Planned.**

- Verify one drag undoes/redoes as one action.
- Keep timeline, segment list, palette, playhead, selection, and history controls synchronized.
- Cover commit, no-op, invalid release, cancellation, redo invalidation, and repeated corrections.
- Perform a representative manual workflow before completing C4.

## Data-integrity contract

History never bypasses annotation validation. A history stack is not an alternative source of truth: `AnnotationSession.intervals` remains the current committed annotation, while entries contain isolated copies of earlier and later valid states. UI selection is not annotation data and is restored only by a safe temporal anchor.

## Deep-review reading map

For C4.1, read the complete history component and its focused tests, then inspect the small `MainWindow` command wrapper and undo/redo handlers. Pay particular attention to copy boundaries, stack transitions, exception behavior, and redo invalidation. Button styling and repetitive GUI fixtures can be skimmed.
