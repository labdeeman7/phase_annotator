# V1 Cholec80 Intake and Cohort Selection

Status: **Complete on 2026-10-03.**

## Purpose

V1 establishes which local dataset copy was inspected, what the source labels actually contain, which cases are eligible, and how the 15-case cohort was selected. It does not yet define the JSON conversion boundary contract or copy clinical video into this repository.

## Source and terms

- Source inspected: the existing authorised Cholec80 research copy on the project DGX.
- Committed documentation deliberately omits machine-specific absolute paths.
- The extracted local root contained videos, phase annotations, 1 FPS derived frames, archives, and a results CSV, but no README or licence file was found within three directory levels.
- The official [CAMMA dataset page](https://camma.unistra.fr/datasets/) states that Cholec80 contains 80 videos captured at 25 FPS, phase labels at 25 FPS, and tool-presence annotations at 1 FPS. It identifies the dataset licence as CC BY-NC-SA 4.0 and requests citation of the originating EndoNet work.
- Because the local copy lacks bundled terms, any redistributed derivative/training package must retain the official attribution and licence information explicitly rather than assuming recipients know it.

## Read-only inventory result

| Item | Result |
| --- | --- |
| MP4 videos | 80, named `video01.mp4` through `video80.mp4` |
| Phase TXT files | 80, named `video01-phase.txt` through `video80-phase.txt` |
| Video/label pairs | 80 complete pairs |
| TXT header | `Frame<TAB>Phase` |
| Frame indices | Every file begins at 0 and is contiguous through its final labelled frame |
| Label frequency | One phase label per source frame |
| Allowed vocabulary | Exactly the seven configured Cholec80 phase names |
| Invalid rows or unknown labels | None detected |
| Derived frame files | 184,578 JPEG frames plus one manifest; filenames advance by 25 source frames, consistent with 1 FPS extraction |

The seven source tokens are:

- `Preparation`
- `CalotTriangleDissection`
- `ClippingCutting`
- `GallbladderDissection`
- `GallbladderPackaging`
- `CleaningCoagulation`
- `GallbladderRetraction`

The source files use compact tokens while the application uses clinician-facing names. V2 must map tokens explicitly by name; it must not infer phase identity from list position.

## Eligibility definition

A case was eligible when:

1. both the expected MP4 and phase TXT existed;
2. the TXT header was valid;
3. every data row contained an integer frame and one phase token;
4. frame indices were exactly contiguous from zero;
5. every phase token was in the approved seven-token vocabulary.

All 80 cases were eligible. No exclusions were made.

## Reproducible selection

- Eligible IDs were sorted as `video01` through `video80`.
- Python's `random.Random(20261003).sample(eligible_ids, 15)` selected 15 unique cases.
- The first 10 sampled IDs were assigned to reference walkthrough; the final 5 were assigned to blind practice.
- Machine-readable selection and case metadata are in `cohorts/cholec80_15_seed_20261003.json`.

### Reference walkthrough — 10 cases

1. `video04`
2. `video79`
3. `video01`
4. `video44`
5. `video19`
6. `video64`
7. `video37`
8. `video68`
9. `video14`
10. `video50`

### Blind practice — 5 cases

1. `video67`
2. `video39`
3. `video07`
4. `video03`
5. `video61`

## Useful characteristics discovered after random selection

- `video19` begins with `CalotTriangleDissection`; no Preparation interval is present.
- `video50` contains six source phases and no `CleaningCoagulation` interval.
- `video79`, `video64`, and `video37` place Cleaning/coagulation before Packaging.
- `video14` places Retraction before Cleaning/coagulation and ends in Cleaning/coagulation.
- Every source phase that is present occupies one contiguous run in these annotations. The source therefore does not demonstrate repeated returns to a phase even though the application and local protocol permit them when observable.
- All five blind-practice cases contain all seven source phases. This is a random outcome, not an eligibility requirement.

These observations support the agreed rule: full timeline coverage does not imply complete or nominally ordered procedure coverage.

## V1 decisions and remaining boundary

V1 confirms that the cohort can be selected without copying video. It also confirms a likely frame-to-time basis of 25 FPS through official documentation. V2 must still define and test:

- whether source frame `n` begins at exactly `n / 25` seconds;
- inclusive source-frame runs versus half-open application intervals;
- how the final labelled frame relates to Qt-reported video duration;
- rounding to integer milliseconds;
- truthful converter attribution/provenance in schema 1.4;
- overwrite protection and separation of reference answers from blind sidecars.

No JSON conversion should be treated as accepted until V3 visually checks one case against its source boundaries.
