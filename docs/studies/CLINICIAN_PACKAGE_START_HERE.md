# START HERE — Cholecystectomy Annotation Pilot

Version: **Pilot package 0.1, 4 October 2026**

Dear Doctor,

Thank you very much for supporting this work. We would be grateful if you could annotate two laparoscopic cholecystectomy videos as part of a pilot of the software and draft annotation protocol.

## What we are trying to achieve

We want to label surgical videos from the Obafemi Awolowo University Teaching Hospitals Complex (OAUTHC) using a convention as close as reasonably possible to Cholec80. Cholec80 is a research dataset of 80 laparoscopic cholecystectomy videos with surgical-phase annotations. Following a comparable convention will help us evaluate algorithms developed or trained with Cholec80 when they are applied to OAUTHC data.

Tosin reviewed ten Cholec80 cases and synthesised the observed convention into the supplied draft protocol. Cholec80's boundaries are not perfectly frame-consistent, so the draft expresses the observed convention as practical visual rules. We would appreciate your help in applying those rules to the two OAUTHC videos and identifying anything that is unclear or does not fit local practice.

**Cholec80 reference:** Twinanda AP, Shehata S, Mutter D, Marescaux J, de Mathelin M, Padoy N. *EndoNet: A Deep Architecture for Recognition Tasks on Laparoscopic Videos.* IEEE Transactions on Medical Imaging. 2017;36(1):86–97. DOI: `10.1109/TMI.2016.2593957`.

## What is in the package

- `01_Application`: the Windows Phase Annotator application.
- `02_Guides_and_Protocol`: the User Guide and draft Cholecystectomy Annotation Protocol.
- `03_Example_Clips`: selected Cholec80 transition examples and the clip-library page.
- `04_Local_Study/Videos_to_annotate`: the two OAUTHC videos for this pilot.
- `04_Local_Study/Return_annotations_here`: where to place the completed annotation files before returning them.

The protocol and these instructions are drafts and may change after your feedback.

## How to use the Example Clip Library

The library contains 18 one-minute clips extracted from the reviewed Cholec80 videos. Each clip is centred on a phase transition, normally showing 30 seconds before and 30 seconds after the supplied boundary.

Open `03_Example_Clips`, then double-click `OPEN_CLIP_LIBRARY.html`. Select clips using the IDs cited in the protocol, for example `V04-B01`.

While watching each example, please pay attention to both:

- what the surgeon and instruments are doing before and after the transition; and
- the coloured phase name in the **top-right corner**, which changes at the supplied Cholec80 boundary.

The clip shows only the transition context, not the complete phase. Please use the written rule when OAUTHC instruments or workflow differ from an example.

## Before annotating

1. Extract the complete pilot ZIP to a normal writable folder. Please do not run it from inside the ZIP.
2. Open `01_Application` and double-click `PhaseAnnotator.exe`. Keep the executable and `_internal` folder together.
3. Enter your first name and choose **Cholecystectomy**. Please do not choose Appendectomy for these videos.
4. Read the User Guide and draft protocol in `02_Guides_and_Protocol`.
5. Keep each video in its supplied writable folder so the application can save its annotation automatically beside it.

## Annotate the two videos

1. Open `20260505_221257.mp4` and confirm that exact filename appears in the application.
2. Annotate the complete available recording using the draft protocol.
3. Add a segment note when a difficult decision will be useful during review. Please do not include patient identifiers.
4. Review the timeline, then use **Annotation → Mark complete** when satisfied.
5. Close the application normally and keep the generated JSON beside the video.
6. Repeat the same process for `20260519_215628.mp4`.

The application saves automatically; there is no normal Save button. Please do not rename or manually edit the generated JSON files.

## Feedback we would appreciate

Please let Tosin know:

- any phase definition that was unclear or clinically unsuitable;
- any boundary for which the protocol did not provide a usable cue;
- where local instruments or techniques differed from the examples;
- any phase that was absent, repeated, interrupted, or appeared in an unexpected order;
- any software error, confusing control, or uncertainty about whether work had saved;
- approximately how long each video took to annotate; and
- whether you think another clinician could apply the same draft consistently.

Where possible, please distinguish a clinical/protocol uncertainty from a software problem. Both are important, but they require different responses.

## Files to return

When both annotations are complete, copy these files into `04_Local_Study/Return_annotations_here`:

```text
20260505_221257.mp4.phase-annotations.json
20260519_215628.mp4.phase-annotations.json
```

Please return those two JSON files together with your feedback. Tosin will review the annotations and feedback with you before the protocol is revised or the larger study begins. These pilot annotations are not automatically treated as final ground truth.

## If something goes wrong

Please stop and message Tosin if:

- the application reports the wrong procedure or an invalid annotation file;
- `[UNSAVED]` remains in the title;
- a video does not open or play normally;
- an instruction is unclear; or
- you are unsure whether continuing might overwrite work.

Please do not delete, rename, or manually edit an annotation JSON to bypass an error.
