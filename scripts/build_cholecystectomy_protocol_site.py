"""Build the offline, multi-page cholecystectomy annotation protocol."""

from __future__ import annotations

import argparse
import html
import shutil
from pathlib import Path

NAVIGATION = (
    ("OPEN_PROTOCOL.htm", "Start"),
    ("01_core_rules.htm", "Core rules"),
    ("02_preparation_and_calot.htm", "P1–P2"),
    ("03_clipping_and_dissection.htm", "P3–P4"),
    ("04_packaging_cleaning_extraction.htm", "P5–P7"),
    ("05_uncertainty_and_idle_time.htm", "Uncertainty"),
    ("06_transition_examples.htm", "Video examples"),
    ("07_completion_and_return.htm", "Finish and return"),
)


CSS = """
:root { --navy:#102538; --cyan:#19b6dc; --blue:#3b82f6; --green:#10b981;
  --amber:#f59e0b; --red:#ef4444; --purple:#8b5cf6; --pink:#ec4899;
  --grey:#64748b; --paper:#f4f7f9; --ink:#1a2a36; --muted:#5d7381; }
* { box-sizing:border-box; }
body { margin:0; font-family:"Segoe UI",Arial,sans-serif; background:var(--paper); color:var(--ink); line-height:1.55; }
header { background:var(--navy); color:white; padding:26px max(22px,5vw) 18px; }
header h1 { margin:0; font-size:clamp(1.55rem,3vw,2.35rem); }
header p { max-width:920px; color:#c9d8e2; margin:8px 0 0; }
nav { display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }
nav a { color:white; text-decoration:none; border:1px solid #496478; border-radius:7px; padding:7px 11px; font-size:.92rem; }
nav a.active, nav a:hover { background:var(--cyan); border-color:var(--cyan); color:#062131; }
main { max-width:1050px; margin:24px auto 48px; padding:0 20px; }
.banner,.card,.phase,.video-card { background:white; border:1px solid #cddae1; border-radius:11px; padding:18px 20px; margin:16px 0; box-shadow:0 2px 8px #0c1b2a0b; }
.banner { border-left:6px solid var(--cyan); }
.warning { background:#fff7df; border-left-color:var(--amber); }
.decision { background:#eaf8f3; border-left-color:var(--green); }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:14px; }
h2 { color:#174b6b; margin-top:28px; } h3 { color:#245f7d; }
.phase { border-left:7px solid var(--phase); }
.phase strong,.badge { color:var(--phase); }
.badge { font-weight:700; text-transform:uppercase; letter-spacing:.04em; font-size:.78rem; }
table { width:100%; border-collapse:collapse; background:white; }
th,td { border:1px solid #bdcbd3; padding:9px; text-align:left; vertical-align:top; } th { background:#deedf4; }
video { display:block; width:100%; max-height:520px; background:black; margin:12px 0 5px; }
.video-card h3 { margin-bottom:4px; }
.clip-link { font-weight:600; color:#075f87; }
.rule { font-size:1.12rem; font-weight:650; color:var(--navy); }
footer { max-width:1050px; margin:0 auto 30px; padding:0 20px; color:var(--muted); font-size:.86rem; }
code { background:#e7edf1; padding:2px 4px; border-radius:3px; }
@media print { nav,video,.clip-link { display:none; } body { background:white; } .card,.phase,.banner { box-shadow:none; break-inside:avoid; } }
"""


PAGES = {
    "OPEN_PROTOCOL.htm": (
        "Draft Cholecystectomy Phase-Annotation Protocol",
        """
<section class="banner decision">
  <div class="badge">Draft for shared annotation</div>
  <p class="rule">This protocol uses the seven Cholec80 phases as its reference convention, with a small number of explicit OAUTHC adaptations where the pilot annotations exposed a reproducibility problem.</p>
</section>
<h2>Purpose</h2>
<p>Use this protocol to label the dominant visible operative activity throughout each available laparoscopic cholecystectomy recording. The resulting timelines will support inter-rater analysis and evaluation of models trained on Cholec80.</p>
<div class="grid">
  <section class="card"><h3>Reference</h3><p>Retain the Cholec80 seven-phase vocabulary so results remain comparable with established research.</p></section>
  <section class="card"><h3>Clinical adaptation</h3><p>Do not let instrument appearance alone override the visible surgical objective, especially at the P1-to-P2 boundary.</p></section>
  <section class="card"><h3>Evidence</h3><p>Use transition-centred clips to learn where labels change. Video evidence is more useful than isolated representative frames for temporal boundaries.</p></section>
</div>
<h2>Seven phases</h2>
<table><tr><th>ID</th><th>Phase</th><th>Primary question</th></tr>
<tr><td>P1</td><td>Preparation</td><td>Is the surgeon obtaining access and exposure?</td></tr>
<tr><td>P2</td><td>Calot triangle dissection</td><td>Is focused hepatocystic-triangle dissection the sustained objective?</td></tr>
<tr><td>P3</td><td>Clipping and cutting</td><td>Are cystic structures being occluded and divided?</td></tr>
<tr><td>P4</td><td>Gallbladder dissection</td><td>Is the gallbladder being separated from the liver bed?</td></tr>
<tr><td>P5</td><td>Gallbladder packaging</td><td>Is the specimen being placed into a retrieval bag?</td></tr>
<tr><td>P6</td><td>Cleaning and coagulation</td><td>Is inspection, irrigation, suction or haemostasis now dominant?</td></tr>
<tr><td>P7</td><td>Gallbladder retraction</td><td>Is sustained specimen withdrawal/extraction occurring?</td></tr></table>
<section class="banner warning"><strong>Status:</strong> this is a working protocol. The shared five cases are intended to reveal where two informed annotators still interpret it differently.</section>
""",
    ),
    "01_core_rules.htm": (
        "Core Annotation Rules",
        """
<section class="banner"><p class="rule">Annotate the dominant visible surgical objective over time—not a single instrument, isolated motion, or presumed off-screen intention.</p></section>
<h2>Rules that apply throughout</h2>
<ol>
 <li>Cover the complete available recording. A partial recording does not need to begin at P1 or end at P7.</li>
 <li>Place a boundary when the new operative objective becomes clear and sustained.</li>
 <li>Do not force the nominal phase order. Phases may repeat, be absent, or occur in an unusual order.</li>
 <li>Record a genuine return to an earlier task. Sequences such as <code>P1 → P2 → P1 → P2</code> and repeated P4 or P6 episodes are valid in complex cases.</li>
 <li>Brief supporting actions remain in the surrounding phase. Change only when that action becomes the dominant task.</li>
 <li>Do not infer an invisible action or future task.</li>
 <li>Use notes for meaningful ambiguity, unusual workflow, or prolonged inactivity.</li>
 <li>Use Undefined when the visible activity genuinely cannot be classified, plus the documented interim gallbladder-drainage exception.</li>
</ol>
<section class="banner decision"><h3>Complex operations may be non-linear</h3><p>Do not smooth a complex operation into one pass through P1–P7. If focused Calot dissection stops and renewed adhesiolysis or general exposure becomes dominant, return to P1; change back to P2 if focused Calot dissection later resumes. Retain every genuine recurrence.</p></section>
<h2>Boundary test</h2>
<div class="grid">
 <section class="card"><h3>Before</h3><p>What is the surgeon mainly trying to achieve immediately before this moment?</p></section>
 <section class="card"><h3>After</h3><p>What has become the sustained objective immediately after this moment?</p></section>
 <section class="card"><h3>Evidence</h3><p>Which anatomy, action sequence and instrument use demonstrate that change?</p></section>
</div>
""",
    ),
    "02_preparation_and_calot.htm": (
        "P1 Preparation and P2 Calot Triangle Dissection",
        """
<section class="phase" style="--phase:var(--blue)"><div class="badge">P1</div><h2>Preparation</h2>
<p>Includes survey, exposure and retraction, adhesiolysis, and removal or division of tissue whose immediate purpose is to expose the gallbladder or obtain access to the operative target.</p>
<p><strong>Remain in P1</strong> during general exposure, clearing fat or inflammatory tissue, and hook use outside focused hepatocystic-triangle dissection.</p></section>
<section class="banner decision"><h3>Interim gallbladder-drainage rule</h3><p>An inflamed or tense gallbladder may be purposefully punctured to release pus, bile, or other contents. Label the complete purposeful drainage episode <strong>Undefined</strong> and add the exact note <code>Gallbladder drainage — candidate phase</code>. Return to the appropriate seven-class phase when drainage ends.</p><p>This preserves a candidate real-world phase for later review; it does not mean the clinical action is unknown. Do not apply the rule to incidental puncture or leakage.</p></section>
<section class="phase" style="--phase:var(--green)"><div class="badge">P2</div><h2>Calot triangle dissection</h2>
<p>Begins when focused dissection within the hepatocystic triangle, intended to expose or identify the cystic duct and/or artery, becomes the sustained operative objective.</p></section>
<section class="banner decision"><h3>OAUTHC adaptation</h3><p class="rule">Hook appearance alone does not determine the P1-to-P2 boundary.</p><p>Inflamed and adhesed cases may require prolonged hook adhesiolysis or exposure before true Calot dissection. Use anatomy, tissue target, direction of dissection and sustained intent together.</p></section>
<section class="video-card"><h3>Reference transition: V04-B01</h3><p>Watch activity on both sides of the overlaid Cholec80 boundary.</p><video controls preload="metadata" src="clips/V04-B01_P1-preparation_to_P2-calot-triangle-dissection.mp4"></video><a class="clip-link" href="clips/V04-B01_P1-preparation_to_P2-calot-triangle-dissection.mp4">Open clip separately</a></section>
<section class="video-card"><h3>Reference transition: V79-B01</h3><p>An early transient device appearance is not used as the boundary; the label changes when sustained dissection begins.</p><video controls preload="metadata" src="clips/V79-B01_P1-preparation_to_P2-calot-triangle-dissection.mp4"></video><a class="clip-link" href="clips/V79-B01_P1-preparation_to_P2-calot-triangle-dissection.mp4">Open clip separately</a></section>
""",
    ),
    "03_clipping_and_dissection.htm": (
        "P3 Clipping/Cutting and P4 Gallbladder Dissection",
        """
<section class="phase" style="--phase:var(--amber)"><div class="badge">P3</div><h2>Clipping and cutting</h2><p>Begins when dissection gives way to purposeful occlusion of the cystic duct or artery with a clip applier, ligature or equivalent method. Continue through division and brief confirmation that division is complete.</p></section>
<section class="video-card"><h3>P2 → P3: V50-B02</h3><video controls preload="metadata" src="clips/V50-B02_P2-calot-triangle-dissection_to_P3-clipping-and-cutting.mp4"></video><a class="clip-link" href="clips/V50-B02_P2-calot-triangle-dissection_to_P3-clipping-and-cutting.mp4">Open clip separately</a></section>
<section class="phase" style="--phase:var(--red)"><div class="badge">P4</div><h2>Gallbladder dissection</h2><p>Begins after clipping/cutting has finished and purposeful separation of the gallbladder from the liver bed begins. Brief haemostasis supporting continuing separation remains P4.</p></section>
<section class="video-card"><h3>P3 → P4: V64-B03</h3><video controls preload="metadata" src="clips/V64-B03_P3-clipping-and-cutting_to_P4-gallbladder-dissection.mp4"></video><a class="clip-link" href="clips/V64-B03_P3-clipping-and-cutting_to_P4-gallbladder-dissection.mp4">Open clip separately</a></section>
""",
    ),
    "04_packaging_cleaning_extraction.htm": (
        "P5 Packaging, P6 Cleaning and P7 Extraction",
        """
<section class="phase" style="--phase:var(--purple)"><div class="badge">P5</div><h2>Gallbladder packaging</h2><p>Begins when a retrieval bag is purposefully introduced, opened or positioned to contain the detached gallbladder.</p></section>
<section class="video-card"><h3>P4 → P5: V44-B04</h3><video controls preload="metadata" src="clips/V44-B04_P4-gallbladder-dissection_to_P5-gallbladder-packaging.mp4"></video><a class="clip-link" href="clips/V44-B04_P4-gallbladder-dissection_to_P5-gallbladder-packaging.mp4">Open clip separately</a></section>
<section class="phase" style="--phase:var(--pink)"><div class="badge">P6</div><h2>Cleaning and coagulation</h2><p>Begins when inspection, irrigation, suction, clearance of blood/fluid, or haemostasis becomes the principal activity rather than brief support for dissection.</p></section>
<section class="video-card"><h3>P4 → P6: V37-B04</h3><video controls preload="metadata" src="clips/V37-B04_P4-gallbladder-dissection_to_P6-cleaning-and-coagulation.mp4"></video><a class="clip-link" href="clips/V37-B04_P4-gallbladder-dissection_to_P6-cleaning-and-coagulation.mp4">Open clip separately</a></section>
<section class="phase" style="--phase:var(--grey)"><div class="badge">P7</div><h2>Gallbladder retraction (specimen extraction)</h2><p>Begins when the contained specimen is purposefully engaged and sustained withdrawal from the operative field begins. Ordinary traction during P1, P2 or P4 is not P7.</p></section>
<section class="video-card"><h3>P5 → P7: V50-B05</h3><video controls preload="metadata" src="clips/V50-B05_P5-gallbladder-packaging_to_P7-gallbladder-retraction.mp4"></video><a class="clip-link" href="clips/V50-B05_P5-gallbladder-packaging_to_P7-gallbladder-retraction.mp4">Open clip separately</a></section>
""",
    ),
    "05_uncertainty_and_idle_time.htm": (
        "Uncertainty, Partial Recordings and Inactive Time",
        """
<h2>Partial recordings</h2><p>Annotate only what is visible. Begin with whichever phase is already occurring and end when the supplied recording ends. Do not invent missing beginning or ending phases.</p>
<h2>Inactive periods</h2>
<section class="banner decision"><p class="rule">Preserve the original timeline; do not cut inactive periods out before annotation.</p></section>
<ul><li>If operative context remains clear, continue the current phase.</li><li>If a prolonged pause is important, add a short neutral note.</li><li>Do not guess whether an invisible delay relates to equipment, staffing or another cause.</li><li>A separate future idle-time analysis can be created without changing the seven primary phases.</li></ul>
<h2>Undefined</h2><p>Use Undefined for smoke, occlusion, corrupted footage, an out-of-body view, or loss of task context that prevents confident assignment. Also use it for purposeful gallbladder drainage under the documented interim rule, always with the standard note. Do not use it merely because a phase is difficult, long, repeated or uses unfamiliar instruments.</p>
<section class="card"><h3>Why drainage is being retained separately</h3><p>Kirtac et al., <em>Surgical Phase Recognition: From Public Datasets to Real-World Data</em> (Applied Sciences, 2022;12(17):8746), treated gallbladder drainage as an additional phase absent from Cholec80. OAUTHC will review its frequency, duration and boundary reliability before changing the current ontology.</p><p><a href="https://doi.org/10.3390/app12178746">Open the paper (internet required)</a></p></section>
<section class="banner warning"><strong>Notes must never contain patient-identifying information.</strong></section>
""",
    ),
    "06_transition_examples.htm": (
        "Transition Video Library",
        """
<section class="banner"><p class="rule">Watch before and after the label change. The boundary is a change over time, so a still image cannot teach it reliably.</p></section>
<p>The linked library contains 18 one-minute Cholec80 transition clips with the current phase overlaid. Use it alongside the written rules. These reference clips do not imply that every OAUTHC case will look identical.</p>
<p><a class="clip-link" href="OPEN_CLIP_LIBRARY.html">Open the complete transition clip library</a></p>
<div class="grid">
 <section class="card"><h3>P1 → P2</h3><p>Compare device appearance with sustained focused dissection.</p></section>
 <section class="card"><h3>P2 → P3</h3><p>Look for purposeful introduction of clipping or occlusion.</p></section>
 <section class="card"><h3>P3 → P4</h3><p>Look for completed division followed by liver-bed separation.</p></section>
 <section class="card"><h3>P4/P6 → P5</h3><p>Look for purposeful retrieval-bag introduction and positioning.</p></section>
 <section class="card"><h3>P5 → P7</h3><p>Separate packaging from sustained specimen withdrawal.</p></section>
</div>
""",
    ),
    "07_completion_and_return.htm": (
        "Complete, Check and Return Each Annotation",
        """
<h2>Before marking Completed</h2><ol><li>Review the entire available timeline.</li><li>Confirm there are no accidental rapid fragments or misplaced boundaries.</li><li>Check uncertain intervals and add a neutral note where useful.</li><li>Confirm the correct video name and Cholecystectomy ontology.</li><li>Select <strong>Annotation → Mark complete</strong>.</li></ol>
<h2>Return files</h2><p>The application saves <code>&lt;video filename&gt;.phase-annotations.json</code> beside the video. Copy each completed JSON into <code>05_Return_Annotations_Here</code>. Do not rename the video or JSON and do not edit JSON manually.</p>
<section class="banner warning"><strong>Shared-five rule:</strong> annotate independently. Do not copy another annotator's boundaries or resolve disagreements together until both sets have been returned.</section>
<h2>What happens next</h2><p>Tosin will verify that files load, measure phase and boundary agreement, and organise clinical review of meaningful differences. Disagreement is evidence about the protocol; it is not automatically an annotator error.</p>
""",
    ),
}


def render_page(filename: str, title: str, body: str) -> str:
    links = "".join(
        f'<a class="{"active" if target == filename else ""}" href="{target}">{html.escape(label)}</a>'
        for target, label in NAVIGATION
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><link rel="stylesheet" href="protocol.css"></head>
<body><header><h1>{html.escape(title)}</h1><p>OAUTHC draft protocol • Cholec80 reference convention with documented local adaptations</p><nav>{links}</nav></header>
<main>{body}</main><footer>Draft protocol • 17 October 2026 • For internal OAUTHC research annotation</footer></body></html>"""


def build_site(output_dir: Path, clip_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "protocol.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    for filename, (title, body) in PAGES.items():
        (output_dir / filename).write_text(
            render_page(filename, title, body), encoding="utf-8"
        )

    referenced = {
        item.split('src="clips/', 1)[1].split('"', 1)[0]
        for _, body in PAGES.values()
        for item in body.split("<video")
        if 'src="clips/' in item
    }
    missing = sorted(name for name in referenced if not (clip_dir / name).is_file())
    if missing:
        raise FileNotFoundError(f"Missing protocol video clips: {missing}")

    target_clips = output_dir / "clips"
    if target_clips.resolve() != clip_dir.resolve():
        if target_clips.exists():
            shutil.rmtree(target_clips)
        shutil.copytree(clip_dir, target_clips)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--clip-dir", type=Path, required=True)
    args = parser.parse_args()
    build_site(args.output_dir.resolve(), args.clip_dir.resolve())
    print(args.output_dir.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
