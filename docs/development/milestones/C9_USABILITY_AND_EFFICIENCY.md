# C9 Usability and Annotation Efficiency

## Outcome

Sustained annotation should be fast, discoverable, and calm. C9 improves navigation and feedback without changing phase semantics, interval integrity, completion rules, or persisted JSON.

## Interaction contract

- Routine success/loading/playback information remains in the status bar.
- Errors and warnings that require attention appear in a dismissible banner above the workspace.
- Playback speed is selectable from a small fixed set and applies only to media playback.
- Five-second backward/forward jumps complement approximate frame stepping.
- A polished Help dialog visually groups playback, editing, phase, and completion controls without occupying permanent workspace.
- Delete resolves the currently selected segment to Undefined through the same validated, undoable command used by its menu action.
- The timeline remains one full-width overview. A trial zoom/scroller was removed after use because its multiplier controls were easily confused with playback speed.
- Controls remain usable at common laptop and high-DPI desktop sizes.

## Sub-slices

- **C9.1 — Notification hierarchy (implemented):** reusable error/warning banner and routing of important failures.
- **C9.2 — Playback efficiency (implemented):** speed selector and ±5-second navigation.
- **C9.3 — Discoverability (implemented):** concise shortcuts/workflow reference dialog.
- **C9.4 — Long-video navigation (evaluated, then removed):** the zoom prototype added more confusion than value; retain the full-width timeline.
- **C9.5 — Acceptance (automated complete; manual pending):** regression checks plus a short representative manual workflow.

## Constraints

- Do not claim decoder-accurate frame stepping.
- Do not make playback rate annotation data.
- Do not replace modal confirmation where an irreversible or lifecycle decision requires an explicit answer.
- Do not add configurable complexity until actual use demonstrates a need; the speed and jump choices are intentionally small.

## Reading map

Start with `ui/main_window.py` for orchestration, `ui/notification_banner.py` for feedback presentation, and `ui/player_widget.py` for the narrow media-control adapter.

## Current status

C9 is implemented pending manual acceptance. Important media, persistence, and blocked-sidecar failures use the banner; routine feedback remains in the status bar. Playback offers 1×, 2×, 4×, 8×, and 12× rates, ±5-second jumps, and existing frame steps. The Help menu opens a structured visual reference. Delete converts the selected segment to Undefined without creating a gap. The timeline remains an uncluttered full-width overview.
