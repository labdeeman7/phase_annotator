# Laparoscopic Cholecystectomy Annotation Protocol — Working Draft

Status: **Early working generalisations derived from `video04`; not clinically approved.**

This document records candidate transition rules while the reference cohort is reviewed. The phase descriptions below are the reviewer's first **working generalisations after watching `video04`**, not merely a transcription of that case's labels. They should be retained and tested against later videos rather than discarded because they began with one case.

The supplied Cholec80 labels and the reviewer's visual interpretation are two separate forms of evidence. It must not yet be presented to students as the final protocol. Later cases and clinical-owner review will determine which working generalisations become approved rules.

## How knowledge is recorded

Keep three levels distinct:

1. **Working generalisation:** the current proposed rule that may apply across videos. The phase definitions and candidate cues below currently occupy this level.
2. **Case observation:** what is visibly happening in one named video near a supplied boundary.
3. **Clinical decision:** the reviewed rule accepted after comparing multiple cases and resolving disagreements.

When a boundary is uncertain or appears inconsistent, record both sides explicitly:

> **Source label:** In `video04`, Cholec80 changes from P1 to P2 at `00:04:51.000`.
>
> **Reviewer observation:** The hook is visible here, but purposeful Calot dissection appears to begin earlier/later at `[time]` because `[observable reason]`.
>
> **Proposed generalisation:** Start P2 at `[instrument entry / positioning / first purposeful tissue interaction]`.
>
> **Decision:** Pending comparison with `[case IDs]` and clinical review.

This format preserves disagreement instead of silently moving a boundary or treating the supplied label as unquestionable truth.

## Core annotation rules

1. Label only observable activity in the available recording.
2. Cover every available millisecond, but do not invent an absent phase.
3. Use **Undefined** when visible activity cannot be assigned confidently.
4. A recording may begin in a later phase or end before the operation is complete.
5. Expected order is guidance only: phases may be absent, repeated, or out of order.
6. Place a transition at the first defensible visual evidence of the new phase. Record uncertainty instead of silently guessing.

## Provisional cross-video phase definitions

Unless stated otherwise, these are the reviewer's current generalisations from `video04`. Each definition should accumulate supporting examples, counterexamples, and revisions as more cases are watched.

### P1 — Preparation

**Working definition:** Entry and initial setup of the laparoscopic view before focused Calot triangle dissection begins.

**Candidate start cue:** First classifiable preparation activity in the available recording.

**Candidate end cue:** First defensible evidence that focused Calot triangle dissection has begun.

**Questions to resolve:** Which access, camera-adjustment, exposure, or traction actions remain Preparation rather than becoming Calot triangle dissection?

### P2 — Calot triangle dissection

**Working definition:** Dissection to expose and identify structures in the Calot triangle.

**Working generalisation from `video04`:** The appearance of the hook immediately before dissection/cutting activity may be a useful transition cue.

**Alternative to test:** Instrument appearance alone may be too early if the instrument is visible before purposeful dissection begins.

**Questions to resolve:** Should the boundary be the instrument's entry, its positioning, or its first purposeful tissue interaction?

### P3 — Clipping and cutting

**Working definition:** Ligation of the cystic duct and artery using clips or ties, followed by division of the secured structures.

**Candidate start cue:** First purposeful introduction or use of the clipping/ligation instrument for this task.

**Candidate end cue:** Completion of the final relevant cut, before gallbladder dissection from the liver bed begins.

**Questions to resolve:** How should preparation for clipping, instrument exchanges, and delays between clipping and cutting be labelled?

### P4 — Gallbladder dissection

**Working definition:** Separation of the gallbladder from the liver bed after division of the duct and artery.

**Candidate start cue:** First purposeful dissection separating the gallbladder from the liver bed.

**Candidate end cue:** The gallbladder is visibly fully detached and the next task begins.

**Questions to resolve:** If packaging equipment appears before the last attachment is divided, does dissection continue until full detachment?

### P5 — Gallbladder packaging

**Working definition:** Placement and securing of the detached gallbladder in a retrieval bag.

**Candidate start cue:** First purposeful action to introduce, open, or position the retrieval bag for the gallbladder.

**Candidate end cue:** The gallbladder is contained and the bag is closed or otherwise secured, followed by another task.

**Questions to resolve:** Does bag introduction count immediately, or only once placement of the specimen begins?

### P6 — Cleaning and coagulation

**Working definition:** Irrigation, suction, inspection, cleaning, or haemostatic coagulation after or between the principal dissection tasks.

**Working generalisation from `video04`:** Cleaning begins after the gallbladder has been secured in the bag and cleaning/coagulation activity starts.

**Ordering hypothesis to test:** P6 need not always follow packaging. A case may clean before packaging, before retraction, after retraction attempts, or in repeated episodes; label the visible task rather than forcing the `video04` order.

**Questions to resolve:** How should brief haemostasis during another dominant phase be handled, and when is an activity long or distinct enough to become P6?

### P7 — Gallbladder retraction

**Working definition:** Withdrawal/removal of the packaged gallbladder from the operative field.

**Candidate start cue:** First purposeful action directed at extracting the packaged gallbladder after the preceding task ends.

**Candidate end cue:** End of visible extraction activity or end of the available recording.

**Questions to resolve:** The term “retraction” may be confused with ordinary tissue traction. Confirm whether “gallbladder retrieval/extraction” would be clinically clearer while retaining compatibility with the configured/source label.

## Evidence log

Use one row per candidate boundary. The supplied boundary is recorded first; the reviewer may then add a different proposed time and explain the visible reason. Times are source-video times, not descriptions such as “around the middle.” Keep media outside Git and refer to clips by a non-identifying local study ID.

| Case | From → To | Source boundary | Reviewer's proposed boundary | Observable cue or disagreement | Confidence | Clip/image ID | Clinical decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| `video04` | P1 → P2 | 00:04:51.000 | To review | Is hook appearance or purposeful dissection the stronger cue? | Pending | `V04-B01` | Pending |
| `video04` | P2 → P3 | 00:14:58.000 | To review | To review | Pending | `V04-B02` | Pending |
| `video04` | P3 → P4 | 00:16:04.000 | To review | To review | Pending | `V04-B03` | Pending |
| `video04` | P4 → P5 | 00:20:40.000 | To review | To review | Pending | `V04-B04` | Pending |
| `video04` | P5 → P6 | 00:21:18.000 | To review | Test the proposed secured-bag-to-cleaning cue | Pending | `V04-B05` | Pending |
| `video04` | P6 → P7 | 00:22:53.000 | To review | To review | Pending | `V04-B06` | Pending |

## Clip and image placeholders

Short clips are preferred for transition teaching because they show activity on both sides of a boundary. A still image may supplement a clip when one frame contains an especially useful visual cue.

For each accepted example, prepare outside the repository:

- a short pre-boundary segment;
- the boundary moment;
- a short post-boundary segment;
- a caption explaining the observable cue and why nearby alternatives were rejected;
- licence/attribution information required for the dataset-derived asset.

Suggested working convention: `V04-B01` identifies video 04, boundary example 01. Do not embed absolute local paths or identifiable reviewer details in this document.

## Review record

| Protocol version | Cases reviewed | Clinical owner | Status | Main unresolved issue |
| --- | ---: | --- | --- | --- |
| Working draft 0.1 | 1 started | To assign | Observational | Operational transition cues require visual and clinical review |

