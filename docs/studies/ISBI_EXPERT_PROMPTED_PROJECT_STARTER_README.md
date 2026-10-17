# ISBI Project B: Expert-Prompted Zero-Shot Phase Recognition

## When to use this plan

This is a separate fallback research project. Do not begin it until Project A (`ISBI_TECNO_HMM_PROJECT_STARTER_README.md`) reaches its scientific decision gate.

Activate this project only if TeCNO plus HMM is technically successful but scientifically weak, or if its errors show that temporal decoding cannot address the central target-domain problem.

## Research question

> Can clinically informed phase descriptions improve zero-shot transfer of a frozen surgical vision-language model to complex OAUTHC laparoscopic cholecystectomy videos without target-domain parameter training?

A secondary question is:

> How sensitive is apparent cross-domain model failure to a clinically defensible difference in the Preparation-to-Calot-triangle-dissection annotation convention?

Distinguish:

1. **visual/procedural domain shift** — inflammation, adhesions, difficulty, anatomy, technique, equipment and recording appearance; and
2. **annotation-policy shift** — especially whether P2 begins near hook use or when focused hepatocystic-triangle dissection becomes the sustained objective.

Do not claim that these effects can be separated perfectly.

## Terminology and claim

Call the method **expert-prompted zero-shot inference** or **protocol-guided zero-shot adaptation without parameter updates**.

No OAUTHC data update model parameters, but two target-domain pilot annotations informed the clinical protocol and prompt wording. Therefore claim:

> No target-domain examples were used for model training or parameter optimisation.

Do not claim:

> No target-domain information was used.

## Model strategy

### Primary: SurgVLP/PeskaVLP

Use the official CAMMA implementation and authors' recommended PeskaVLP checkpoint where licensing and environment permit. It is preferred because it was designed for surgical vision-language representation learning, includes official zero-shot Cholec80 evaluation code, and provides image/text similarity scores suitable for reproducible seven-class evaluation.

### Optional comparator: Qwen3-VL

Use an official small Qwen3-VL Instruct checkpoint only after PeskaVLP works. It asks whether broad multimodal reasoning benefits from the protocol, but it may be slow and may not expose comparable seven-class probabilities.

Retain Qwen3-VL only if one short clip can be classified deterministically into `P1`–`P7` and reproducible forced-choice class scores can be extracted. Otherwise use it qualitatively or omit it. The study must not depend on Qwen3-VL.

Do not ensemble model families unless the core study is complete and the hypothesis was defined before viewing held-out results.

## Data split and leakage control

- **2 OAUTHC pilot cases:** protocol and prompt development.
- **13 OAUTHC cases:** untouched held-out evaluation.
- Cholec80: use an established source train/validation/test protocol.

Freeze exact prompt text before evaluating the thirteen cases. Do not select prompts, augmentation or decoder settings by repeatedly inspecting held-out performance.

## Prompt conditions

### B0 — Phase names

Use only the seven phase names as the ordinary zero-shot baseline.

### B1 — Cholec80-derived descriptions

Use concise descriptions derived from the reviewed source convention. Phrase them cautiously; do not claim that every Cholec80 transition is determined by hook appearance.

### B2 — OAUTHC task-aware descriptions

Use clinically confirmed descriptions based on dominant operative objective. For P1/P2:

> Preparation includes exposure, adhesiolysis and clearance of fat or inflammatory tissue, even when a hook is used. Calot triangle dissection begins with sustained, purposeful dissection within the hepatocystic triangle to identify cystic structures.

Store every exact prompt and template in versioned configuration.

## Canonical and proxy boundaries

The OAUTHC task-based annotation remains canonical and must never be overwritten for model convenience.

For analysis, store a separate Cholec80-style proxy P1-to-P2 timestamp where defensible. This is not a second full annotation. Store it in a research table containing pseudonymous case ID, canonical boundary, proxy boundary, applicability, confirmation status and non-identifying rationale.

For a fixed method define:

```text
M_source          = Cholec80 test performance
M_target_proxy    = OAUTHC performance with only the proxy P1/P2 boundary substituted in memory
M_target_clinical = OAUTHC performance against canonical clinical annotations

G_domain = M_source - M_target_proxy
G_policy = M_target_proxy - M_target_clinical
```

Describe `G_domain` as a target-domain generalisation gap under a more harmonised boundary convention—not pure causal visual domain shift. Describe `G_policy` as evaluation sensitivity to annotation policy.

## Optional temporal decoding and TTA

If a temporal decoder is used, its emissions must be the frozen vision-language scores and its transitions must be defined without held-out OAUTHC tuning. Permit all transitions with non-zero probability; do not hard-code monotonic phase order.

TTA is optional and secondary. Use only mild, clinically non-destructive deterministic transforms selected on source validation/pilot data. Avoid flips, large rotations and aggressive colour changes unless justified.

## Minimum experiment matrix

| ID | Prompt | Temporal decoder | Purpose |
| --- | --- | --- | --- |
| E0 | Phase names | None | Zero-shot baseline |
| E1 | OAUTHC task-aware | None | Expert-prompt effect |
| E2 | Phase names | Optional HMM | Temporal effect |
| E3 | OAUTHC task-aware | Optional HMM | Complementarity |

Add source-style prompts, TTA or Qwen3-VL only after E0/E1 work end to end.

## Metrics

Use video as the independent unit:

- per-video macro-F1;
- per-phase precision, recall and F1;
- frame accuracy as a secondary metric;
- P1-to-P2 boundary error;
- frequency of early P2 prediction;
- video-level bootstrap confidence intervals;
- temporal fragmentation measures where relevant.

## Privacy and reproducibility

- Run clinical videos locally in the authorised environment.
- Never commit videos, frames, real sidecars, raw predictions, identifying names or absolute paths.
- Pin repositories and checkpoint revisions and inspect licences.
- Preserve timestamped raw scores before post-processing.
- Validate class mapping and annotation alignment.
- Record every failure/exclusion.
- Use deterministic inference and generation.
- Do not tune on the thirteen held-out labels.

## Instructions for Codex

Act as the senior research software engineer. Read this file completely, inspect repository state, official model implementations, licences, checkpoints, hardware and data contracts, then propose justified changes before implementation.

Work in small vertical slices. Report observable results, validation, runtime, leakage/method risks, one manual check and the next go/no-go decision. Do not commit or push without approval. Do not reopen Project A or combine its codebase unless the project owner explicitly chooses a shared framework.

## Milestones

### B0 — Handover and split

- Protect all real data with ignore rules.
- Freeze the two-development/thirteen-test manifest.
- Document phase mapping, timestamps and hardware.
- Create an isolated environment.

### B1 — PeskaVLP feasibility

- Reproduce the smallest official zero-shot example.
- Run one Cholec80 and one OAUTHC pilot clip.
- Preserve timestamped seven-class similarities.

Acceptance: meaningful scores are produced within acceptable runtime.

### B2 — Evaluation pipeline

- Define reusable score/prediction/metric schemas.
- Test mapping and time alignment synthetically.
- Run the phase-name baseline on pilots.

### B3 — Expert prompts

- Encode exact prompt variants.
- Confirm clinical wording.
- Compare and freeze prompts using source validation and the two pilots only.

### B4 — Proxy-boundary analysis

- Create the separate comparison table.
- Substitute proxy boundaries only in memory during evaluation.
- Prove canonical JSON remains unchanged.

### B5 — Frozen evaluation

- Freeze code/configuration.
- Run E0/E1 on the thirteen cases.
- Add E2/E3 only if already justified.
- Generate video-level results and confidence intervals.

### B6 — Optional Qwen3-VL gate

- Run one short clip with a small official Instruct checkpoint.
- Require deterministic valid output and usable class scores.
- Retain only if it can be evaluated fairly without delaying the paper.

## Suggested repository structure

```text
isbi_expert_prompted_phase/
├── README.md
├── pyproject.toml
├── configs/
│   ├── prompts.yaml
│   └── experiments.yaml
├── manifests/
├── src/expert_prompted_phase/
│   ├── data/
│   ├── models/
│   ├── inference/
│   ├── evaluation/
│   └── reporting/
├── tests/
├── scripts/
├── docs/
└── outputs/                 # ignored except approved aggregates
```

## Activation checklist

Before starting Project B, write down:

- Project A's actual result;
- why TeCNO+HMM is insufficient for the intended paper;
- the remaining time before submission;
- whether all thirteen canonical annotations will be ready;
- whether PeskaVLP can realistically be installed and evaluated in that time.

If those conditions are not satisfied, do not activate this larger study merely because it sounds more novel.
