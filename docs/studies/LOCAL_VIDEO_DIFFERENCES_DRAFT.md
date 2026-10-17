# Project-Video Differences — Review Draft

Status: **Known differences to verify from the first clinician's annotations of `LOCAL-01` and `LOCAL-02`.**

This document records why the Cholec80-derived convention was adapted for the doctor-facing OAUTHC protocol. The source convention remains preserved in `CHOLEC80_DERIVED_TRAINING_MANUAL.md`; the current OAUTHC instruction is `OAUTHC_CHOLECYSTECTOMY_TRAINING_MANUAL.md`.

## Confirmed adaptation: Preparation to Calot triangle dissection

The supplied Cholec80 labels often place P1-to-P2 near hook-electrocautery appearance. This is a reasonable reproducible convention in those reference cases and is not treated as an annotation error.

In the two OAUTHC pilot cases, inflammation, adhesions, and obscuring fat required hook use for general exposure before focused hepatocystic-triangle dissection. The Nigerian clinician retained this work in P1 and began P2 only when sustained dissection aimed at exposing or identifying the cystic duct/artery became visible.

The local project adopts the clinician's task-based boundary. Instrument appearance remains supporting evidence, not the definition. This creates a known annotation-policy difference from some Cholec80 boundaries and must be reported alongside the visual domain shift when evaluating Cholec80-trained models.

## Known differences

### Partial procedures

Project recordings may begin after the operation has started or end before it is complete. Annotate only the available footage:

- begin at `0ms` with the first confidently observable phase, even if earlier expected phases are absent;
- use Undefined at the start only when the opening activity cannot be classified confidently;
- allow the final observable phase to continue to the video end when the recording stops mid-phase;
- use Undefined at the end only when the remaining footage is not assignable;
- never add a phase merely because it would normally occur before or after the visible portion.

Full timeline coverage does not mean full procedure coverage.

### Different instruments

Project surgeons may use instruments that differ from Cholec80 examples. The activity and surgical objective define the phase; a particular instrument is supporting evidence, not an absolute requirement, unless clinical review establishes otherwise.

Transition clips should therefore teach both:

- the visible instrument cues present in Cholec80; and
- the underlying action completed and action begun, so annotators can recognise equivalent work with another instrument.

### Workflow and phase order

Phases may be absent, repeated, interrupted, or occur in a different order. Follow observable activity rather than forcing the nominal phase list. The reference review already contains examples where Cleaning/coagulation and Packaging occur in different orders.

### Image quality and non-classifiable footage

Use Undefined when smoke, occlusion, loss of view, out-of-body footage, or another limitation prevents confident assignment. Undefined is not a replacement for an absent phase and should not be used merely because an operation differs from the most common sequence.

## Questions for the two local clinician-pilot cases

- Which two videos best represent the range doctors will receive?
- Do their recordings start or end mid-procedure?
- Which Cholec80 instrument cues do not transfer directly?
- Are there local techniques that change the visible start/end cue for a phase?
- What footage should be Undefined rather than a surgical phase?
- Are any additional examples needed in the clip library before clinician training?

## Questions for Dr Olugbami

- Are the phase names and descriptions clinically understandable?
- Is task-based recognition sufficient when instruments differ?
- Are the partial-video rules safe and unambiguous?
- Which inferred Cholec80 boundary rules need qualification for local practice?
- Which two local videos should be used for adaptation rehearsal?
