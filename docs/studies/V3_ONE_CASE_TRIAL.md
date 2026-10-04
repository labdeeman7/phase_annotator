# V3 One-Case Conversion Trial

Status: **Complete and visually accepted on 2026-10-03.**

## Case and evidence

- Selected reference case: `video04` (the first seeded reference case).
- Staging location: ignored local study workspace; no clinical media or source labels are committed.
- Source labels: 38,051 contiguous frame rows.
- Qt media result: 1,522,040 ms, 25 FPS, 854 × 480.
- Label-derived duration: 38,051 × 40 ms = 1,522,040 ms.
- Final endpoint adjustment: 0 ms.
- Converted phase runs: 7.
- Persistence inspection: `loaded`, with no validation or source mismatch message.
- Reference lifecycle: `completed`, protected by the normal reopen confirmation.

## Boundaries for visual review

| Phase ID | Start | End |
| ---: | ---: | ---: |
| 1 | 0 ms | 291,000 ms |
| 2 | 291,000 ms | 898,000 ms |
| 3 | 898,000 ms | 964,000 ms |
| 4 | 964,000 ms | 1,240,000 ms |
| 5 | 1,240,000 ms | 1,278,000 ms |
| 6 | 1,278,000 ms | 1,373,000 ms |
| 7 | 1,373,000 ms | 1,522,040 ms |

## Manual acceptance

- [x] Launch Phase Annotator with the laparoscopic cholecystectomy procedure.
- [x] Open the staged `video04.mp4`; confirm all seven segments load without a banner error.
- [x] Review all six supplied transitions against visible activity.
- [x] Confirm Phase 7 covers the available end without an artificial extra interval.
- [x] Confirm the 25 FPS source-frame to half-open millisecond convention is visually credible.

The reviewer confirmed that all supplied `video04` boundaries were correct and used those observations to begin the working protocol. This accepts the conversion timing contract for batch processing. It does not make the phase definitions clinically final; those generalisations still require comparison across the remaining reference cases and clinical review.
