# Laparoscopic Cholecystectomy Phase Annotation Protocol

Version: **Clinical-review draft 0.2, 4 October 2026**

Basis: rules inferred by Tosin from the supplied phase annotations for ten Cholec80 reference videos. This document is intended to make those conventions reproducible on OAUTHC project videos. It has not yet received formal clinical approval. We would therefore appreciate clinicians noting any ambiguous or clinically inappropriate rule so it can be reviewed with Tosin.

## Using the video examples

This protocol is supplied with an offline **Example Clip Library** containing 18 one-minute clips extracted from the reviewed Cholec80 videos. Each clip is centred on a transition and normally shows 30 seconds before and 30 seconds after the supplied boundary. Open the `03_Example_Clips` folder, double-click `OPEN_CLIP_LIBRARY.html`, and select examples using the clip IDs cited below, such as `V04-B01`.

While watching, pay attention to the surgical activity before and after the transition and to the coloured phase name in the **top-right corner**. The name and colour change at the supplied Cholec80 boundary. A clip shows only the transition context, not the complete phase. Use the written operational rule when OAUTHC instruments or workflow differ from an example.

## Annotation objective

Assign one phase to every moment of the available recording according to the **dominant visible surgical task**. The seven phases describe tasks, not a compulsory sequence. A phase may be absent, repeated, interrupted, or occur in an unusual order.

### General boundary rule

Place a boundary at the first defensible visual evidence that the **surgical objective has changed** and the new task has begun.

- Identify what the surgeon is trying to accomplish before using an instrument as a boundary cue.
- Introduction of a phase-specific instrument—such as hook electrocautery, a clip applier, a specimen-retrieval bag, or suction/irrigation—supports a transition only when its purpose in the new task is visually clear.
- If an instrument appears transiently, remains idle, leaves the field, or is used for a different purpose, do not change phase solely because it was seen.
- Do not move a boundary backwards merely because the next task could be anticipated.
- Do not prolong a completed phase through clear activity belonging to the next phase.
- Brief repositioning or inspection belongs to the surrounding task unless it becomes a distinct cleaning, haemostasis, packaging, or extraction episode.

Cholec80's supplied boundaries vary by several seconds in visually similar situations. The rules below choose consistent, observable cues instead of attempting to reproduce that annotation noise.

## Rules for partial or unclear recordings

- Cover the entire available timeline, even when the recording contains only part of the operation.
- Begin with the first phase that is confidently visible. Do not invent earlier phases; for example, a recording may begin directly with P2.
- Let the final visible phase continue to the end when the recording stops during that task. Do not invent a later phase.
- A short camera movement, smoke episode, or occlusion does not automatically become Undefined when the surrounding task remains clear.
- Recognise the surgical task even when local surgeons use instruments that differ from the reference clips.

## Phase definitions and boundaries

### P1 — Preparation

**Definition:** Initial laparoscopic survey, exposure and retraction of the gallbladder, and operative setup before focused dissection of the hepatocystic (Calot) triangle.

**Start:** The beginning of the recording when preparation is the first classifiable activity.

**End / transition to P2:** Focused dissection of the hepatocystic triangle begins. Hook electrocautery or another dissecting/energy device may provide the clearest cue when it is purposefully positioned at the cystic structures and dissection begins. A transient appearance without sustained dissection does not end P1.

**Important:** P1 may be absent when the available recording begins after preparation. Start with the first phase that is confidently visible rather than inventing earlier activity.

**Useful examples:** `V04-B01`, `V14-B01`, and `V50-B01` show the transition from preparation to focused hepatocystic-triangle dissection. `V79-B01` shows why a transient early appearance of an energy device should not automatically trigger the transition.

### P2 — Calot triangle dissection

**Definition:** Dissection within the hepatocystic (Calot) triangle to expose and identify the cystic duct and cystic artery before their occlusion and division.

**Start:** The P1-to-P2 rule above, or the beginning of the recording when focused Calot triangle dissection is already underway.

**End / transition to P3:** Dissection gives way to occlusion of the cystic duct or cystic artery. Normally place the boundary when a clip applier, ligature, or equivalent occlusion device is purposefully introduced and positioned to secure a cystic structure.

**Important:** Use the intended action rather than requiring a particular clipper design. Do not switch merely because dissection pauses or the structures are being held exposed.

**Useful examples:** `V01-B02`, `V50-B02`, `V64-B02`, and `V68-B02` show the change from hepatocystic-triangle dissection to cystic-structure occlusion. Some supplied labels precede visible clip-applier entry by a few seconds; do not anticipate an action that is not yet visually supported when annotating new videos.

### P3 — Clipping and cutting

**Definition:** Occlusion of the cystic duct and artery with clips, ties, or an equivalent method, followed by division of the secured structures.

**Start:** Purposeful introduction of the clipping or ligation instrument, as described above. A recording may also begin in P3 when this task is already visible.

**End / transition to P4:** The secured cystic duct and artery have been divided and any brief confirmation of complete division has ended. Place the boundary before purposeful separation of the gallbladder from the liver bed begins. Hook electrocautery or another energy device may support the transition when it is repositioned and used for liver-bed dissection.

**Important:** Do not use the scissors merely leaving the view as an inflexible cue: the surgeon may still inspect or perform another cut. Conversely, do not wait through clear gallbladder dissection simply because there was no long pause.

**Useful examples:** `V64-B03`, `V68-B03`, and `V37-B03` show final division followed by a short confirmation interval before P4. The supplied Cholec80 timing varies between final cutting and the next instrument's arrival; task completion is the consistent rule.

### P4 — Gallbladder dissection

**Definition:** Separation of the gallbladder from the liver bed after the cystic duct and artery have been divided.

**Start:** Completion of P3 as defined above, followed by purposeful separation of the gallbladder from the liver bed.

**End:** Continue P4 until the gallbladder is detached and there is positive evidence of the next dominant task. The next phase is determined by what actually begins:

- transition to **P5 Packaging** when a retrieval bag is introduced, opened, or purposefully positioned for the gallbladder;
- transition to **P6 Cleaning and coagulation** when irrigation, suction, inspection, or haemostasis becomes the dominant task;
- do not infer the next phase solely because the camera temporarily leaves the abdomen.

**Important:** Detachment alone may be followed by a pause, inspection, cleaning, or packaging. Keep P4 during a short ambiguous pause and change at the first defensible evidence of the next task. If haemostasis is only a brief part of continuing liver-bed dissection, remain in P4.

**Useful examples:** `V44-B04` demonstrates movement towards packaging; `V37-B04` demonstrates movement towards cleaning/coagulation. These examples show why the observable next task is more reliable than assuming a fixed phase order.

### P5 — Gallbladder packaging

**Definition:** Introducing, opening, and using a specimen-retrieval bag (endobag) to contain and secure the detached gallbladder.

**Start:** First purposeful introduction, opening, or positioning of the retrieval bag for the specimen. If the bag is already present when the view returns, begin P5 at the earliest visible moment when its use is clear; do not guess what occurred off camera.

**End:** The gallbladder has been placed and secured in the bag and another task purposefully begins:

- transition to **P6** when attention turns to irrigation, suction, liver-bed inspection, or haemostasis;
- transition to **P7** when the bag or its extraction handle is engaged and sustained withdrawal begins.

**Important:** Merely touching the bag does not end P5 if packaging continues. Conversely, complete closure is not required when the surgeon clearly stops packaging and begins extraction.

**Useful examples:** `V01-B05` demonstrates packaging followed by cleaning; `V14-B05` and `V50-B05` demonstrate packaging followed by extraction; `V37-B05` and `V64-B05` demonstrate cleaning/coagulation followed by packaging.

### P6 — Cleaning and coagulation

**Definition:** A distinct episode in which liver-bed inspection, irrigation, suction, clearance of blood or fluid, or haemostasis becomes the principal activity after or between the main operative tasks.

**Start:** The first purposeful cleaning or haemostatic action when that activity becomes the dominant task. Supporting cues include introduction of an irrigator or suction device, deliberate inspection of the liver bed, or use of a coagulating instrument specifically for haemostasis.

**End:** Continue P6 until another dominant task purposefully begins. For a transition to P7, this means the retrieval bag or extraction handle is engaged and sustained withdrawal begins. If the surgeon briefly touches or repositions the bag and returns to cleaning, remain in P6.

**Ordering:** P6 is not tied to one fixed point in the operation. It may occur before or after P5, before or after an attempted P7, may repeat, or may be absent. Follow the visible dominant task rather than forcing P6 into one expected position.

**Dominant-task rule:** Brief coagulation used as part of ongoing P2 or P4 dissection remains in that dissection phase. Create a separate P6 interval only when cleaning, inspection, or haemostasis becomes a distinct episode rather than a momentary supporting action.

### P7 — Gallbladder retraction (specimen extraction)

**Definition:** Retrieval or extraction of the packaged gallbladder from the operative field. The source ontology calls this phase “Gallbladder retraction”; here, **retraction means specimen extraction**, not ordinary traction on tissue during dissection.

**Start:** The extraction handle, bag neck, or packaged specimen is purposefully grasped and sustained withdrawal begins. Use the beginning of the pulling/extraction movement, not a brief touch or an idle grasp.

**End:** The packaged gallbladder has been removed, the recording ends during extraction, or another dominant task begins. If the surgeon abandons extraction and returns to a distinct cleaning or haemostasis episode, transition back to P6 at the first purposeful action of that task.

**Important:** Ordinary gallbladder traction during P2 or P4 is not P7. Camera withdrawal alone is not sufficient unless the visible context shows that it is part of specimen extraction.

**Useful examples:** `V14-B05` and `V50-B05` show the transition from packaging to extraction. P7 need not be the final phase if another distinct task follows.

## Quick transition guide

| Transition | Preferred boundary cue |
| --- | --- |
| P1 → P2 | Focused dissection of the hepatocystic triangle begins |
| P2 → P3 | Clip applier, ligature, or equivalent device is introduced to occlude a cystic structure |
| P3 → P4 | Division of the secured cystic structures is complete; separation from the liver bed begins |
| P4 → P5 | Specimen-retrieval bag is purposefully introduced, opened, or positioned |
| P4 → P6 | Liver-bed cleaning, inspection, or haemostasis becomes the dominant task |
| P5 → P6 | Packaging complete enough that cleaning/inspection/haemostasis becomes dominant |
| P5 → P7 | Sustained extraction of the packaged specimen begins |
| P6 → P7 | Cleaning ends and sustained extraction begins |
| P7 → P6 | Extraction pauses/ends and a distinct cleaning or haemostasis episode begins |

Other transitions are allowed when supported by the visible task. Never insert a phase simply to preserve the nominal order.

## Handling uncertainty

1. Review several seconds before and after the candidate boundary.
2. Identify the task that has ended and the first purposeful evidence of the task that follows.
3. Apply the preferred cue above rather than anticipating an off-screen action.
4. If the activity remains genuinely unclassifiable, add a segment note and include the uncertainty in your feedback to Tosin.
5. Do not place patient-identifying information in notes.

## Reference material

The full transition evidence library contains one clip for each of the 58 internal boundaries in the ten reviewed reference cases. The clinician package supplies 18 selected examples cited in this protocol. Each clip includes 30 seconds before and after the supplied boundary, subject to video-edge clamping, and displays the active source phase in its configured colour on every frame.

The supplied examples include transitions into dissection, clipping/cutting, packaging, cleaning/coagulation, and extraction, including examples where cleaning/coagulation and packaging occur in different orders. Use the clip IDs cited under each phase rather than looking for complete source videos.

## Clinical review points

The following points should be confirmed during the first clinical review without delaying initial use of this draft:

- whether “Gallbladder extraction” should replace “Gallbladder retraction” in a future ontology version;
- whether introduction of the retrieval bag is the preferred P5 start cue across local techniques;
- when brief haemostasis during dissection is substantial enough to become a distinct P6 episode;
- whether local instruments require additional task-based examples.

Until those decisions are approved, use the operational rules in this document consistently and record difficult cases in segment notes.

## Cholec80 reference

Twinanda AP, Shehata S, Mutter D, Marescaux J, de Mathelin M, Padoy N. *EndoNet: A Deep Architecture for Recognition Tasks on Laparoscopic Videos.* IEEE Transactions on Medical Imaging. 2017;36(1):86–97. DOI: `10.1109/TMI.2016.2593957`.
