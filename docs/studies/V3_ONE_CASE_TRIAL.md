# V3 One-Case Conversion Trial

Status: **Automated checks passed; visual boundary review pending.**

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

## Remaining manual acceptance

- [ ] Launch Phase Annotator with the laparoscopic cholecystectomy procedure.
- [ ] Open the staged `video04.mp4`; confirm all seven segments load without a banner error.
- [ ] Check the 291,000 ms first boundary and at least two internal boundaries against visible activity.
- [ ] Seek near 1,522,040 ms and confirm Phase 7 covers the available end without an artificial extra interval.
- [ ] Close and reopen without editing; confirm the same seven segments reload.
- [ ] Record whether the source boundary convention is visually credible or reopen V2 before batch conversion.

Do not mark V3 complete from structural checks alone. Frame semantics need this visual review.
