# Speaker Notes

## 1. Teaching AI what is happening during surgery

Welcome everyone. This is an introductory discussion, not a test. The aim is to agree what the labels mean before asking people or AI to reproduce them.

## 2. Part 1 — Introduction

Signal that the first section explains the purpose in clinical language. No prior AI knowledge is assumed.

## 3. What we need to achieve today

Explain the four outcomes: understand the purpose, agree difficult boundaries, practise annotation and correction, and connect all 26 videos to the research.

## 4. An operation is also a timeline

A phase describes the dominant surgical objective over a period. It is not determined by a single instrument.

## 5. Why recognise surgical workflow?

Use concrete examples: retrieving teaching material, navigating long recordings, measuring workflow and giving future AI systems context. The present application does not make clinical decisions.

## 6. A practical clinical scenario

Imagine searching many long recordings for difficult Calot dissections. Phase labels make the relevant periods retrievable. The idea extends beyond cholecystectomy to any procedure with a clinically meaningful workflow.

## 7. What is Cholec80?

Cholec80 contains 80 laparoscopic cholecystectomy videos recorded in Strasbourg and labelled using seven phases. It enabled comparable research; it is a reference dataset, not a universal clinical authority.

## 8. Why every annotation must be finished

“Complete” means the full available timeline was deliberately considered and reviewed. It does not mean an annotation cannot later be corrected.

## 9. Public benchmarks are cleaner than real practice

Cholec80 was enormously valuable. The figure demonstrates why one curated benchmark cannot represent every workflow. Do not frame this as France versus Nigeria or one group being wrong.

## 10. The same phases can have different durations

Point to the published 54-minute versus 34-minute medians. Different durations and ordering change the temporal patterns learned by a model.

## 11. Greater case complexity can reduce AI performance

Published model accuracy fell from about 92% to 81% as complexity increased, while surgeon agreement remained near 90%.

## 12. Domain shift

Separate patient/anatomy, practice, imaging and label-policy differences. A boundary-convention difference can look like model failure unless documented.

## 13. Part 2 — Decisions for annotation

Move from motivation to decisions that need clinical agreement.

## 14. What the first two OAUTHC annotations revealed

Thank Dr Olugbami. Adhesiolysis may be required before access to Calot’s area, prolonging Preparation. Two videos suggest a question; the wider collection establishes whether it recurs.

## 15. Compare the boundary in two real examples

Play `V04-B01_P1-preparation_to_P2-calot-triangle-dissection.mp4` and `LOCAL-01-B01_P1-preparation_to_P2-calot-triangle-dissection.mp4`. Pause at the overlaid transition and ask what changed clinically.

## 16. Draft P1-to-P2 rule

Instrument appearance alone does not determine P2. Ask whether focused hepatocystic-triangle dissection becoming the sustained operative objective is an acceptable rule.

## 17. Long inactive periods

Preserve existing footage because deletion changes timestamps and conceals a real deployment condition. If context is clear, continue the phase; if genuinely unclassifiable or out of body, use Undefined; note important prolonged inactivity. A separate idle analysis remains possible.

## 18. Part 3 — The annotation work

Explain that annotation includes initial labelling, review and correction.

## 19. The Phase Annotator

Tell Dr Olugbami that the application has been improved since his pilot and will be resent with updated teaching material and the user guide. Point out the video/timeline, phase choices, segments and correction controls.

## 20. How Phase Annotator supports the work

Demonstrate selecting Cholecystectomy, opening a video, assigning a phase, moving a boundary, adding a note, undoing, reviewing and marking it Completed.

## 21. Annotation is a team workflow

Dr Olugbami both annotates and clinically corrects/reviews work. Students annotate complete timelines and record uncertainty. Tosin supports the software, checks batches, measures agreement and runs the AI analysis.

## 22. How the 26 videos will be annotated

Both annotators first label the same five videos. Inter-rater variability measures where two informed annotators agree or differ and reveals unclear rules. Review those five before dividing later work. Then issue videos in batches of 10, 10 and 6, checking returned files between batches. The goal is all 26, although the first experiment may use 15 or 20 for simplicity.

## 23. Part 4 — From annotation to an AI study

Transition from the clinical data-making process to the proposed experiment.

## 24. The first AI experiment

A model learns from Cholec80 and is tested unchanged on OAUTHC. Ask whether it predicts Calot dissection too early during prolonged adhesiolysis or exposure.

## 25. TeCNO already reasons across time

Do not explain convolution unless asked. TeCNO examines visual information over time and refines predictions in stages.

## 26. What does the HMM add?

An HMM adds probabilities about likely phase sequences. It must not prohibit unusual OAUTHC workflows. It may help, do nothing or cause harm; all outcomes are informative.

## 27. The controlled comparison

The same TeCNO outputs feed both branches. One selects its most likely phase at each time; the other uses the HMM to select a plausible sequence.

## 28. Decisions and next actions

Confirm the boundary rule, inactivity policy, use of Undefined, shared-five exercise and staged return batches. Record unresolved questions and responsibilities.

## 29. Key references

Leave this slide available for questions rather than reading it aloud.
