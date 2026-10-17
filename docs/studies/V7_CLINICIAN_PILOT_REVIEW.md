# V7 Clinician Pilot Review

Status: **Intake complete and boundary review ready, 15 October 2026.**

Decision update: the first substantive review identified a systematic P1-to-P2 convention difference. The clinician's task-based boundaries are retained as the primary OAUTHC annotation. Cholec80-derived guidance remains preserved separately; see `OAUTHC_CHOLECYSTECTOMY_TRAINING_MANUAL.md` and `LOCAL_VIDEO_DIFFERENCES_DRAFT.md`.

## Purpose

Review the two returned local cholecystectomy annotations with the clinician, determine whether the draft protocol transfers to OAUTHC practice, and decide what must change before the wider 15-video annotation set.

These videos have no independent gold labels. V7 is therefore a structured clinical and usability review, not an accuracy score or a test of the clinician.

## Intake record

- Both expected canonical sidecars were returned.
- Both use session schema 1.4 and the packaged cholecystectomy ontology.
- Both identify the same clinician account as creator and last editor.
- Both pass schema, phase-ID, continuous-coverage, filename, file-size, and source compatibility checks in Phase Annotator 0.1.2.
- Both are marked `draft`; neither has persisted completion attribution. The project lead subsequently confirmed that the clinician had finished both annotations and appears not to have understood that a separate **Mark Completed** action was required.
- The received files are preserved unchanged in the ignored local workspace under `test_dataset/clinician_pilot/returned_originals/2026-10-15/`.

Do not open or edit the preservation copies in the application. Work only from review copies beside authorised video copies.

## Review sequence

### 1. Lifecycle finding — resolved administratively

The project lead confirms that both returned files represent finished annotation work. Treat them as **administratively confirmed complete** for pilot review while retaining their actual persisted status (`draft`) in all technical descriptions.

Do not change the lifecycle field manually in JSON and do not invent completion attribution. Preserve the original returns as received. If a formally completed application artifact is later required, create a review copy and have the clinician use **Mark Completed**, or document an explicitly approved researcher correction separately.

Classify this as **usability/training friction**: completion was available, but the clinician did not discover or understand the action. Before V8, make completion part of the return checklist and consider whether the application needs a more visible completion prompt.

### 2. Prepare a boundary review sheet

For each video, extract a read-only table containing:

- segment number;
- phase and phase transition;
- start and end timecodes;
- duration;
- segment note, if present;
- a space for the clinician's explanation and the researcher's review comment.

Do not infer that a short or repeated phase is wrong. Flag it for discussion and inspect the surrounding video.

### 3. Review clinically meaningful transitions

Prioritise:

- the visible start of the first classifiable phase in a partial recording;
- P1 to P2 and the beginning of focused hepatocystic-triangle dissection;
- P2 to P3 and the beginning of cystic-structure occlusion;
- P3 to P4 after division of the secured cystic structures;
- transitions among P4, P5, P6, and P7 where packaging, haemostasis, inspection, and extraction may occur in different orders;
- any Undefined interval, repeated phase, unusually short interval, or note.

For every disagreement, classify the cause before proposing a correction:

1. software defect;
2. usability or training friction;
3. ambiguous wording in the draft protocol;
4. a real local difference in instruments, recording, or operative workflow;
5. ordinary clinical judgement where more than one boundary is defensible.

### 4. Review the software experience separately

Record launch, procedure selection, opening/resuming, hotkeys, mouse controls, boundary correction, notes, completion, autosave, and return of the JSON. The computer-transfer rejection discovered at intake is a software defect fixed in 0.1.2; it is not an annotation-quality problem.

### 5. Produce controlled outputs

V7 should produce:

- preserved original returns;
- the administrative confirmation that both Draft files represent finished work;
- a boundary-review sheet for each video;
- a short software/usability findings list;
- agreed additions to `LOCAL_VIDEO_DIFFERENCES_DRAFT.md`;
- a versioned revision of the annotation protocol;
- corrected review sidecars only if corrections are jointly agreed;
- a documented go, revise, or stop decision for V8.

The training revision includes a phase-organised library with two examples for every phase. It prefers OAUTHC evidence and uses clearly labelled Cholec80 examples only where the two OAUTHC pilot annotations do not provide two suitable examples. The older nine-boundary OAUTHC extraction remains preserved as internal review evidence.

## V8 entry gate

Do not distribute the 15-video set until:

- the persisted Draft status and administrative completion confirmation are both recorded;
- major boundary ambiguities have been reviewed with the clinician;
- serious software/data-integrity defects are resolved or explicitly mitigated;
- the approved application and protocol versions are named;
- assignment, return, backup, support, and quality-review procedures are written down.
