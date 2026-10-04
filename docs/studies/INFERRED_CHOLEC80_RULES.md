# Inferred Cholec80 Annotation Rules — Evidence Draft

Status: **Reverse-engineering Cholec80's demonstrated boundary convention; not the doctor-facing protocol.**

This document records candidate rules inferred from Cholec80's supplied phase boundaries. The goal is to reproduce the annotation convention demonstrated by Cholec80 as closely as possible, then teach that convention for use on project videos. The phase descriptions below are the reviewer's first **working generalisations after watching `video04`**. They should be tested and refined against later reference cases.

The supplied Cholec80 boundary is the reference decision. The reviewer watches the activity around it to infer why that point was chosen; the task is not to replace it with a personally preferred boundary. Surprising cases are retained as exceptions or interpretive questions. This evidence draft must not yet be presented to doctors as the final protocol.

## How knowledge is recorded

Keep three levels distinct:

1. **Inferred Cholec80 rule:** the current explanation of the convention that may apply across videos.
2. **Case evidence:** what is visibly happening immediately before and after one supplied boundary.
3. **Reviewed teaching rule:** the explanation retained after comparing multiple Cholec80 cases and discussing local applicability with the clinical owner.

When a boundary is uncertain or appears inconsistent, record both sides explicitly:

> **Source label:** In `video04`, Cholec80 changes from P1 to P2 at `00:04:51.000`.
>
> **Reviewer observation:** Immediately before the boundary `[activity]` is occurring; immediately after it `[new activity]` is occurring.
>
> **Inferred Cholec80 rule:** Start P2 at `[instrument entry / positioning / first purposeful tissue interaction]`.
>
> **Support status:** Pending comparison with `[case IDs]` and later clinical review.

This format explains and tests the supplied convention without silently moving its reference boundary.

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

Use one row per supplied boundary. Record the visible activity on both sides and the rule it appears to demonstrate. Times are source-video times, not descriptions such as “around the middle.” Keep media outside Git and refer to clips by a non-identifying local study ID.

| Case | From → To | Source boundary | Activity before/after boundary | Inferred rule | Support | Clip ID |
| --- | --- | ---: | --- | --- | --- | --- |
| `video04` | P1 → P2 | 00:04:51.000 | Review hook/dissection activity | Is hook appearance or purposeful dissection the operative cue? | One case | `V04-B01` |
| `video04` | P2 → P3 | 00:14:58.000 | To document | To infer | One case | `V04-B02` |
| `video04` | P3 → P4 | 00:16:04.000 | To document | To infer | One case | `V04-B03` |
| `video04` | P4 → P5 | 00:20:40.000 | To document | To infer | One case | `V04-B04` |
| `video04` | P5 → P6 | 00:21:18.000 | Review secured-bag-to-cleaning activity | Cleaning starts when cleaning/coagulation becomes the active task | One case | `V04-B05` |
| `video04` | P6 → P7 | 00:22:53.000 | To document | To infer | One case | `V04-B06` |

## Transition clip library

Short videos are the primary teaching evidence because phase segmentation depends on activity before and after a transition. Every default clip contains 30 seconds before and 30 seconds after the exact supplied Cholec80 boundary, subject only to video-edge clamping.

For each accepted example, prepare outside the repository:

- a caption explaining the before/after activity and the Cholec80 rule the clip appears to demonstrate;
- licence/attribution information required for the dataset-derived asset.

Suggested working convention: `V04-B01` identifies video 04, boundary example 01. Do not embed absolute local paths or identifiable reviewer details in this document.

## Review record

| Protocol version | Cases reviewed | Clinical owner | Status | Main unresolved issue |
| --- | ---: | --- | --- | --- |
| Working draft 0.1 | 1 completed | To assign | All `video04` source boundaries accepted | Test the working generalisations against more cases |

