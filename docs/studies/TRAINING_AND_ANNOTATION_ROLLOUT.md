# Training and Annotation Rollout

## Goal

Preserve the convention inferred from Cholec80, adapt it transparently using clinician annotation of two local laparoscopic cholecystectomy cases, and use the resulting task-based local manual before beginning the larger annotation set.

## Current decisions

- The researcher will not perform the previously planned three blind Cholec80 annotations.
- The researcher will not pre-annotate the two local pilot videos.
- The first clinician reviewer will annotate both local videos from scratch.
- The pilot tests protocol transfer and application usability; it is not a Cholec80 scoring exercise.
- The clinician's P1-to-P2 boundaries are retained: local P2 begins with sustained hepatocystic-triangle dissection, not hook appearance alone.
- The Cholec80-derived manual remains available for source-convention and model-comparison work; this adaptation does not imply that CAMMA annotated its dataset incorrectly.
- The phase-organised OAUTHC representative-example library is retained as internal evidence but withdrawn from current annotator distribution: representative in-phase excerpts were not an adequate substitute for transition-centred examples. The shared-five package therefore restores the original Cholec80-derived protocol and transition clip library used in the first clinician review.
- The earlier nine-boundary OAUTHC extraction is retained as internal review evidence, not as the current doctor-facing library.
- Markdown is the maintained source format. Clinician-facing protocol, instructions, and user guide should be distributed as versioned PDFs.
- HTML remains optional for a future searchable/indexed clip library. PowerPoint is not the source of truth.

## Workstreams

### V4 — Infer Cholec80 rules and create clips

Status: **Complete for the initial draft.**

Ten converted reference cases were reviewed. The study produced 58 labelled transition clips, archived case-level reasoning, and an operational clinician-review protocol. The protocol deliberately uses reproducible visible cues where the supplied Cholec80 timing was inconsistent.

### V5 — Assemble the two-video clinician pilot package

Status: **Complete.**

Package:

- Phase Annotator 0.1.1 or an explicitly approved successor;
- the Phase Annotator User Guide;
- the draft Laparoscopic Cholecystectomy Phase Annotation Protocol;
- the consolidated `START HERE` pilot instructions;
- `LOCAL-01` / `20260505_221257.mp4`;
- `LOCAL-02` / `20260519_215628.mp4`;
- optional selected labelled Cholec80 transition clips if the clinician needs examples;
- application/version and document-version identifiers.

Before transfer, export the three Markdown documents to PDF and check every PDF visually. Keep the editable Markdown in the repository. Do not embed videos in the PDFs.

### V6 — Clinician annotation of two local videos

The first clinician reviewer:

1. launches the application and selects **Cholecystectomy**;
2. opens each video without an adjacent sidecar;
3. annotates the complete available timeline using the draft protocol;
4. uses notes for meaningful ambiguity without adding patient identifiers;
5. reviews and marks each annotation complete;
6. returns both canonical JSON sidecars and structured feedback.

These videos have no Cholec80 gold labels. Do not report an accuracy score against Cholec80, and do not describe the first returned labels as final ground truth before review.

### V7 — Joint review and protocol revision

Status: **Active.** The returned annotations passed automated intake. The completion action was missed but the project lead confirms both annotations were finished. The first review decision adopts the clinician's task-based P1-to-P2 boundary and separates the preserved Cholec80-derived manual from the new OAUTHC clinical manual.

Review the returned annotations and feedback with the clinician. Separate:

- software defects;
- usability friction;
- protocol ambiguity;
- genuine clinical disagreement;
- local differences in instruments, recording coverage, and workflow.

Resolve serious application problems, revise and version the protocol, document local adaptations, and decide whether the two annotations need correction. If corrections are made, preserve the original pilot returns as evidence rather than overwriting the only copy.

### V8 — Wider clinical annotation set

Status: **Shared-five calibration package in preparation.** The wider local collection now contains 26 cholecystectomy videos.

The rollout begins with five common cases annotated independently by both annotators. These cases measure inter-rater variability and expose remaining protocol ambiguity before later work is divided. After review of the shared five, distribute the remaining cases in manageable batches and check returned annotations between batches rather than waiting for the entire collection.

The shared-study package replaces the earlier pilot wording for current distribution. The two-video pilot and its returned files remain preserved as development and protocol-revision evidence.

Before wider distribution:

- approve an application build and protocol version;
- define video assignments, annotator identity, support, completion, return, backup, and quality-review procedures;
- decide whether any additional calibration case or inter-annotator review is needed;
- distribute the approved workflow for the 15-video clinical set.

## Minimal pilot package layout

```text
cholecystectomy_pilot/
├── application/
│   ├── PhaseAnnotator.exe
│   └── _internal/
├── documents/
│   ├── 01_phase_annotator_user_guide.pdf
│   └── 02_draft_annotation_protocol.pdf
├── videos/
│   ├── 20260505_221257.mp4
│   └── 20260519_215628.mp4
└── return_annotations_here/
```

Send the folder as an archive or through the project's approved secure transfer route. Do not use public source control or an unapproved public file-sharing link for clinical videos.

## Pilot acceptance criteria

The pilot is complete when:

- both videos have returned completed, loadable canonical JSON sidecars;
- each sidecar names the Cholecystectomy ontology and matches its video;
- the clinician's feedback has been recorded;
- data-integrity and software problems have been triaged;
- clinical ambiguities have been reviewed rather than silently normalised;
- the next protocol version and wider-rollout decision are documented.
