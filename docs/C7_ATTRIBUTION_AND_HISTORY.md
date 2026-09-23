# C7 Annotator Attribution and Historical Snapshots

## Outcome

Each application launch has one confirmed annotator identity. The canonical JSON records who created and most recently edited the annotation, and one historical snapshot is retained when a changed video is closed or replaced. External sidecar changes cannot be silently overwritten.

Historical snapshots provide a lightweight local trail and recovery aid. They are not a regulated, tamper-proof audit log and do not enable simultaneous collaborative editing.

## Approved product contract

- Ask for the annotator's first name every time the application launches, normalize it to lowercase, and reject whitespace-separated names.
- Keep that identity fixed for the lifetime of the application and across opened videos.
- Do not remember the previous ID, provide in-application identity switching, or create user accounts.
- Show the confirmed ID unobtrusively in the window title.
- Keep the requested identity deliberately minimal: first name only. Do not request surname, email, staff number, or account details.
- Multiple annotators may work sequentially on the same canonical annotation by launching the application separately. Simultaneous editing is unsupported.

## Attribution semantics

Schema 1.3 preserves the existing `annotator_id` for backward compatibility and distinguishes:

- `created_by`: the annotator who created the annotation session;
- `last_edited_by`: the current-launch annotator responsible for the latest annotation-data mutation;
- `completed_by`: reserved for C8 and set only by explicit completion.

Watching, seeking, selection, and resume checkpoints do not change `last_edited_by`. Phase changes, notes, relabeling, boundary changes, removal/merge, undo, redo, and future completion do.

Resume position remains shared per video and is convenience only; it is not per-user progress or evidence that footage was reviewed.

## Historical snapshot contract

- Keep `<video filename>.phase-annotations.json` as the sole canonical working file.
- On clean application close or video replacement, create exactly one snapshot only if annotation data changed since that video was opened.
- Do not create a snapshot merely for opening, watching, seeking, checkpointing resume position, or closing without annotation edits.
- Save and validate the canonical sidecar before snapshotting. Never archive unresolved dirty memory as if it were saved data.
- Store snapshots under `<video filename>.phase-annotations-history/` using collision-safe UTC timestamp filenames.
- Snapshot filenames must not contain annotator names or identifiers. Attribution belongs inside the JSON.
- Initially retain all snapshots. Retention/cleanup requires a separate evidence-based decision.
- A history-write failure is distinct from canonical dirty state: report it and offer Retry, Continue without snapshot, or Cancel without falsely claiming that canonical annotations are unsaved.

## Conflict safety

The desktop application is a single-writer system. Before replacing an existing canonical sidecar, compare its current lightweight file revision evidence with what was last loaded or written. If another process changed it, stop and report a conflict rather than overwriting it.

This check prevents common overwrite accidents but is not a collaborative merge system or security boundary. C7 does not implement automatic merging, user accounts, permissions, cloud synchronization, or server storage.

## Completed slices

- **C7.1 — Schema:** schema 1.3 preserves legacy identity and adds validated creator/last-editor attribution.
- **C7.2 — Launch identity:** startup requires one confirmed ID that remains fixed for the application run.
- **C7.3 — Historical snapshots:** one validated atomic copy is created per changed video run.
- **C7.4 — External-change detection:** lightweight revision evidence blocks destructive overwrite.
- **C7.5 — Validation:** tests cover legacy defaults, identity validation, changed versus resume-only behavior, collisions, snapshot failure, and external conflicts.

## Learning-mode reading map

Focus on the distinction between application identity, persisted attribution, and file ownership. The central engineering idea is that **dirty**, **annotation changed since this video was opened**, and **resume position changed** represent different facts and must not share one Boolean flag.
