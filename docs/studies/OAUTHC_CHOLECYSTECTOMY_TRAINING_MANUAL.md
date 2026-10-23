# OAUTHC Cholecystectomy Phase-Annotation Training Manual

Version: **Clinical adaptation draft 0.4, 15 October 2026**

Basis: the Cholec80-derived reference convention, followed by review of two OAUTHC laparoscopic cholecystectomy videos annotated from scratch by a clinician. This draft records the OAUTHC clinical interpretation demonstrated in those annotations. It requires wider clinical review before it can be described as a final consensus protocol.

## Starting the annotation application

Use the supplied Phase Annotator folder and keep `PhaseAnnotator.exe` beside its `_internal` folder. When the procedure-selection screen appears, choose **Laparoscopic Cholecystectomy**.

The research build is not commercially code-signed, so Windows may initially show the following **Windows protected your PC** message:

![Windows SmartScreen warning showing the More info link](../user/images/windows_smartscreen_protected_pc.jpg)

If the application came from the approved OAUTHC study package, select **More info**, followed by **Run anyway**. Do not disable Windows SmartScreen. If Windows reports a named malware threat or the application came from an unexpected source, stop and contact Tosin.

For complete installation, playback, correction, completion, and file-return instructions, read the supplied Phase Annotator User Guide.

## Why this adaptation exists

Cholec80 and the OAUTHC recordings differ in case mix and visible operative difficulty. In the reviewed OAUTHC cases, inflammation, adhesions, and obscuring fat required substantial exposure work before focused dissection of the hepatocystic (Calot) triangle began.

The supplied Cholec80 annotations often place the P1-to-P2 transition close to the appearance of hook electrocautery. That is a reasonable, reproducible visual convention for those cases. In the OAUTHC annotations, however, the hook may first be used for adhesiolysis, exposure, or clearance around an inflamed gallbladder. The clinician therefore kept that work in P1 and changed to P2 only when the surgical objective became sustained dissection of the hepatocystic triangle.

Neither convention is presented as clinically wrong. They operationalise a difficult transition differently in different data. For this project, the OAUTHC task-based interpretation is primary. The Cholec80-derived manual remains preserved for transparency, model comparison, and analysis of domain and annotation-policy shift.

## Using the example library

The training library is organised by **phase**, with two examples for each of P1-P7. OAUTHC examples are used wherever the two pilot annotations provide suitable evidence. Clearly labelled Cholec80 examples fill the remaining gaps:

| Phase | Example sources |
| --- | --- |
| P1 Preparation | 2 OAUTHC |
| P2 Calot triangle dissection | 2 OAUTHC |
| P3 Clipping and cutting | 2 OAUTHC |
| P4 Gallbladder dissection | 2 OAUTHC |
| P5 Gallbladder packaging | 1 OAUTHC, 1 Cholec80 fallback |
| P6 Cleaning and coagulation | 2 OAUTHC |
| P7 Gallbladder retraction | 2 Cholec80 fallbacks |

P1 examples are 30-second in-phase excerpts because these partial OAUTHC recordings begin during Preparation and do not contain its entry boundary. P2-P7 examples normally contain **15 seconds before and 15 seconds after** the relevant entry boundary. The active phase name and colour appear in the top-right corner and change at the annotated transition. Watch the surgical activity on both sides of the label change; the overlay reports the annotation but does not replace clinical judgement.

The returned OAUTHC sidecars were technically saved as Draft because the separate completion action was missed. The project lead confirms that the clinician had finished both annotations. The originals remain unchanged, and the generated manifest records that Draft input was explicitly accepted for this administratively confirmed use.

## Core annotation principle

Assign the phase according to the **dominant visible surgical objective**, not the mere presence of an instrument.

- An instrument is supporting evidence because the same instrument can serve different tasks.
- Change phase when the objective of the visible work changes and the new task is sustained.
- Do not anticipate an off-screen task.
- Do not force the nominal phase order when the visible workflow differs.
- Record genuine phase recurrence. Complex cases may return to an earlier task, including `P1 → P2 → P1 → P2`, and may contain repeated P4 or P6 episodes. Do not merge separate occurrences merely to make the timeline appear linear.
- Cover the entire available recording, including partial procedures.
- Use Undefined when the visible activity cannot be assigned confidently, plus the explicitly documented interim gallbladder-drainage exception below.

## P1 — Preparation

P1 includes initial survey, gallbladder exposure and retraction, adhesiolysis, and removal or division of tissue whose immediate purpose is to expose the gallbladder or establish access to the operative target.

An inflamed or tense gallbladder may be intentionally punctured to release pus, bile, or other contents. Kirtac et al. identified purposeful gallbladder drainage as an additional real-world phase absent from Cholec80. For the present OAUTHC study, label the complete purposeful drainage episode **Undefined** and add the exact note `Gallbladder drainage — candidate phase`. Resume the appropriate seven-class phase when drainage ends.

This interim rule preserves the event for later measurement without prematurely changing the seven-class ontology. It does not mean that the clinical action is unknown. Do not use it for incidental puncture or leakage, and do not create a new phase until the team has reviewed its frequency, duration, boundary reliability, and intended model use.

The presence of hook electrocautery does **not** by itself end P1. Remain in P1 when the hook or another energy device is being used primarily to release adhesions, clear fat or inflammatory tissue for general exposure, mobilise tissue outside the hepatocystic triangle, or expose the gallbladder before focused identification of the cystic structures.

## P2 — Calot triangle dissection

P2 begins at the first sustained dissection within the hepatocystic triangle whose operative purpose is to expose or identify the cystic duct and/or cystic artery. Use anatomy, direction of dissection, tissue target, and sustained surgical intent together. Hook entry is a useful cue only when it coincides with this change in objective.

Ask: **Is the surgeon still obtaining general exposure of a difficult or inflamed gallbladder, or are they now purposefully dissecting the hepatocystic triangle to identify the cystic structures?** Remain in P1 for the first; begin P2 when the second becomes clearly true.

## P3 — Clipping and cutting

Begin P3 when dissection gives way to purposeful occlusion of the cystic duct or cystic artery with a clip applier, ligature, or equivalent method. Continue through division of the secured structures and any brief confirmation that division is complete.

## P4 — Gallbladder dissection

Begin P4 after clipping and cutting has finished and purposeful separation of the gallbladder from the liver bed begins. Continue until detachment and positive evidence of a different dominant task.

Brief haemostasis supporting continuing liver-bed dissection remains P4. Change to P6 only when inspection, cleaning, or haemostasis becomes a distinct dominant episode.

## P5 — Gallbladder packaging

Begin P5 when a specimen-retrieval bag is purposefully introduced, opened, or positioned to contain the detached gallbladder. Continue while the specimen is being placed and secured. Packaging need not follow P4 directly; an interval of cleaning or haemostasis may occur first.

Only one suitable OAUTHC packaging entry is present in the pilot annotations, so the second example is labelled as a Cholec80 fallback.

## P6 — Cleaning and coagulation

Begin P6 when liver-bed inspection, irrigation, suction, clearance of blood or fluid, or haemostasis becomes the principal visible activity rather than a brief supporting action within dissection.

P6 may precede or follow packaging, may repeat, or may be absent. Follow the visible task rather than forcing a fixed order.

## P7 — Gallbladder retraction (specimen extraction)

Begin P7 when the contained specimen is purposefully engaged and sustained withdrawal from the operative field begins. Ordinary traction on the gallbladder during P1, P2, or P4 is not P7.

P7 was not present as a separate interval in the two returned OAUTHC pilot annotations. Both examples are therefore clearly labelled Cholec80 fallbacks. Flag difficult extraction boundaries for clinical review rather than inventing an OAUTHC rule from absent evidence.

## Undefined

Use Undefined when smoke, occlusion, an out-of-body view, corrupted footage, or loss of task context prevents confident assignment. Also use it for purposeful gallbladder drainage under the explicit interim rule above, always with the standard note. Do not use Undefined merely because a phase is difficult, unusually long, repeated, or performed with unfamiliar instruments.

## Relevant real-world evidence

Kirtac K, Aydin N, Lavanchy JL, et al. *Surgical Phase Recognition: From Public Datasets to Real-World Data*. Applied Sciences. 2022;12(17):8746. https://doi.org/10.3390/app12178746. In 384 real-world cholecystectomy videos, the authors found longer procedures, more complex transitions, and activities absent from Cholec80. They annotated gallbladder drainage as an additional phase, providing direct precedent for reviewing it prospectively in OAUTHC data.

## Domain-shift and model-evaluation note

Models trained on Cholec80 may associate hook appearance with P2 because it was a useful cue in that dataset. Inflamed or adhesed OAUTHC cases can violate that association. Poor agreement around P1-to-P2 may therefore combine:

1. **visual domain shift** — different anatomy, inflammation, adhesions, and operative difficulty; and
2. **annotation-policy shift** — instrument appearance versus change in surgical objective.

Do not overwrite OAUTHC clinical annotations merely to improve apparent agreement with a Cholec80-trained model. If scientific comparison requires separation of these effects, create a small, explicitly named convention-bridge analysis containing both the OAUTHC clinical boundary and a Cholec80-style proxy boundary. Keep that analysis separate from the canonical clinical sidecar.

## Review status

This is a two-case adaptation draft, not a final universal protocol. Before wider rollout:

- review the P1-to-P2 wording with the clinical leads;
- confirm whether the same rule is usable across additional OAUTHC cases;
- replace fallback examples when reviewed OAUTHC evidence becomes available;
- record genuine disagreements rather than silently normalising them;
- version every material change to the rules and training clips.

## Cholec80 reference

Twinanda AP, Shehata S, Mutter D, Marescaux J, de Mathelin M, Padoy N. *EndoNet: A Deep Architecture for Recognition Tasks on Laparoscopic Videos.* IEEE Transactions on Medical Imaging. 2017;36(1):86–97. DOI: `10.1109/TMI.2016.2593957`.
