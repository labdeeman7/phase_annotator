# Local Cholecystectomy Pilot Cohort

Status: **Two-video clinician pilot cohort selected and media-checked on 4 October 2026.**

## Purpose

These two local project videos will be annotated from scratch by the first clinician reviewer. They replace the previously planned three-case internal Cholec80 blind rehearsal and the researcher's own two-video annotation exercise.

The pilot tests three things together:

1. whether the draft Cholec80-derived protocol can be applied to local operations;
2. whether Phase Annotator is understandable and reliable during real annotation work; and
3. which clinical, instrument, recording, or workflow differences must be added before wider distribution.

These videos do not have Cholec80 reference labels. The resulting annotations must therefore not be described as scored against Cholec80 or as ground truth before clinical review.

## Video record

| Pilot ID | Normalised filename | Original received filename | Size (bytes) | Qt duration | Video properties | Role |
| --- | --- | --- | ---: | ---: | --- | --- |
| `LOCAL-01` | `20260505_221257.mp4` | `20260505_221257-cut-merged-1785102793199.mp4` | 779,564,110 | 00:59:24.891 | H.264, 720×576, approximately 25 fps | First clinician annotation |
| `LOCAL-02` | `20260519_215628.mp4` | `20260519_215628-cut-merged-1786446692993.mp4` | 784,379,592 | 00:59:48.333 | H.264, 720×576, approximately 25 fps | First clinician annotation |

The normalised names retain the date/time identifier supplied at the start of each original filename and remove only the generated `-cut-merged-<number>` suffix. No video hashes are created under the project's source-identification policy.

Both videos loaded successfully through the application's Qt media pipeline after renaming. Frame numbers remain timestamp-derived estimates; annotation timestamps in milliseconds are authoritative.

## Handling rules

- Keep both videos outside Git in the ignored local study workspace.
- Do not rename them again after annotation begins: the canonical sidecar name includes the complete video filename.
- Supply no adjacent annotation JSON when the clinician starts; each must open as a new annotation.
- Keep each returned `<video filename>.phase-annotations.json` beside its corresponding video during review.
- Do not include patient-identifying information in filenames, video notes, segment notes, screenshots, or feedback documents.
- Record any authorised transfer location separately; never put absolute machine or network paths in committed documentation.

## Expected return

For each pilot video, collect:

- the completed canonical `.phase-annotations.json` sidecar;
- confirmation that the filename shown in the application matched the assigned video;
- approximate annotation time and whether work was resumed across sessions;
- clinical ambiguities and any boundary where the protocol was insufficient;
- software errors or usability problems, recorded separately from clinical uncertainty.
