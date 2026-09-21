# C9 Usability and Annotation Efficiency

## Outcome

Sustained annotation should be fast, discoverable, and calm. C9 improves navigation and feedback without changing phase semantics, interval integrity, completion rules, or persisted JSON.

## Interaction contract

- Routine success/loading/playback information remains in the status bar.
- Errors and warnings that require attention appear in a dismissible banner above the workspace.
- Playback speed is selectable from a small fixed set and applies only to media playback.
- Five-second backward/forward jumps complement approximate frame stepping.
- A Help menu documents the active keyboard and mouse controls without occupying permanent workspace.
- Timeline zoom enlarges the existing authoritative interval view inside a horizontal scroller. Zooming changes only presentation, never timestamps.
- Controls remain usable at common laptop and high-DPI desktop sizes.

## Sub-slices

- **C9.1 — Notification hierarchy (implemented):** reusable error/warning banner and routing of important failures.
- **C9.2 — Playback efficiency (implemented):** speed selector and ±5-second navigation.
- **C9.3 — Discoverability (implemented):** concise shortcuts/workflow reference dialog.
- **C9.4 — Long-video navigation (implemented):** timeline zoom/reset and horizontal scrolling.
- **C9.5 — Acceptance (automated complete; manual pending):** regression checks plus a short representative manual workflow.

## Constraints

- Do not claim decoder-accurate frame stepping.
- Do not make zoom, playback rate, or scroll position annotation data.
- Do not replace modal confirmation where an irreversible or lifecycle decision requires an explicit answer.
- Do not add configurable complexity until actual use demonstrates a need; the speed and jump choices are intentionally small.

## Reading map

Start with `ui/main_window.py` for orchestration, `ui/notification_banner.py` for feedback presentation, and `ui/player_widget.py` for the narrow media-control adapter. Timeline zoom should remain a view concern: the domain never knows how many pixels represent a millisecond.

## Current status

C9 is implemented pending manual acceptance. Important media, persistence, and blocked-sidecar failures use the banner; routine feedback remains in the status bar. Playback offers 0.5×, 1×, 1.5×, and 2× rates, ±5-second jumps, and existing frame steps. The Help menu lists mouse and keyboard controls. Timeline zoom supports 1×, 2×, 4×, and 8× with horizontal scrolling and does not mutate annotation data.
