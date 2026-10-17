# ISBI Project A: Cross-Domain TeCNO With HMM Decoding

## Status and deadline

This is the primary, time-critical research project for a possible four-page ISBI 2027 submission. The submission deadline is **26 October 2026 at 11:59 pm US Eastern time**.

Complete this project before starting the separate expert-prompted vision-language study. The immediate purpose is to test the HMM experiment requested by the project lead's manager, not to build a large collection of methods.

## Research question

> Does an explicit Cholec80-derived phase-transition model improve the cross-domain robustness of an already temporal TeCNO surgical phase-recognition network on OAUTHC laparoscopic cholecystectomy videos?

TeCNO already models temporal context. The HMM may nevertheless add a global, explicit workflow prior. Do not assume it will help. It may:

- improve phase recognition and boundaries;
- reduce implausible switching without improving accuracy;
- have little effect because TeCNO is already temporally coherent; or
- suppress real atypical, repeated or out-of-order OAUTHC phases and make performance worse.

All four outcomes are scientifically interpretable if evaluated honestly.

## Minimum contribution

- Reproduce a pretrained Cholec80 TeCNO baseline using compatible preprocessing.
- Quantify its unmodified transfer to 15 de-identified OAUTHC cholecystectomy videos.
- Decode the exact same cached TeCNO emissions with an HMM derived without held-out OAUTHC tuning.
- Measure recognition, boundary and temporal-consistency effects.
- Analyse whether remaining errors are compatible with visual/procedural shift or with the known Preparation-to-Calot boundary difference.

Do not add prompting, multimodal large language models, model ensembles or extensive test-time augmentation to the first experiment.

## Data split

Expected local data:

- Cholec80 videos and official phase labels;
- 15 de-identified OAUTHC laparoscopic cholecystectomy videos;
- canonical OAUTHC annotations from Phase Annotator.

Freeze this split before inspecting model results:

- **2 OAUTHC pilot cases:** pipeline checking and prospective HMM decisions;
- **13 OAUTHC held-out cases:** final evaluation.

Use the selected TeCNO implementation's established Cholec80 train/validation/test protocol. Estimate HMM transitions from Cholec80 training labels, make method choices using Cholec80 validation data and the two declared OAUTHC pilot cases, and report source results on the untouched Cholec80 test set.

Do not repeatedly inspect the thirteen OAUTHC results while changing HMM parameters.

## Model and score contract

Select a reproducible TeCNO implementation and pretrained Cholec80 checkpoint. Before use, inspect and record:

- repository revision and licence;
- checkpoint provenance;
- source split;
- CNN feature extractor;
- frame preprocessing and sampling frequency;
- seven-class ordering;
- online/causal assumptions;
- reported evaluation protocol.

Do not combine a checkpoint from one implementation with preprocessing from another unless compatibility is demonstrated.

Persist timestamped pre-argmax logits or probabilities for all seven phases. Each score record must contain a pseudonymous case ID, timestamp, sampling index, class order, checkpoint identity and preprocessing identity. Expensive video inference should run once; native and HMM results must be regenerated from identical cached emissions.

## HMM contract

- Hidden states: the seven configured cholecystectomy phases.
- Emissions: documented probabilities derived from cached TeCNO outputs.
- Initial probabilities: estimated from Cholec80 training labels or fixed prospectively.
- Transition probabilities: estimated from Cholec80 training annotations.
- Decoding: Viterbi over the complete sampled timeline.
- Smoothing: all transitions receive non-zero probability.

Do not impose a hard monotonic phase order. OAUTHC recordings may omit phases, begin partway through surgery, repeat phases or follow an atypical order. A hard transition graph could erase genuine clinical workflow.

Any temperature, transition weight, self-transition scaling or duration treatment must be selected before held-out evaluation. Include an identity/no-op regression test showing that native emissions are unchanged by the evaluation pipeline.

## Experiment matrix

| ID | Emissions | Decoder | Purpose |
| --- | --- | --- | --- |
| T0 | TeCNO | Native argmax | Source and target baseline |
| T1 | Identical TeCNO scores | HMM Viterbi | Explicit transition-prior effect |

If time remains after T0/T1 are frozen, one conservative test-time augmentation experiment may be considered, but it must be a separate factor and must not obscure the HMM comparison.

## Metrics

The independent statistical unit is the **video**, not the frame.

Primary:

- macro-F1 per video;
- per-phase precision, recall and F1;
- P1-to-P2 boundary error in seconds;
- proportion of cases where P2 is predicted too early.

Secondary:

- frame accuracy;
- mean Jaccard if compatible with the baseline literature;
- phase switches per hour;
- number and duration of implausibly short segments;
- segmental edit/F1@overlap only if correctly implemented and justified.

Use paired video-level comparisons between T0 and T1 and video-level bootstrap confidence intervals. With thirteen held-out videos, emphasise uncertainty and effect sizes rather than treating correlated frames as independent samples.

## Annotation-policy caveat

The canonical OAUTHC rule is:

> Instrument appearance alone does not determine the phase. Calot triangle dissection begins when focused dissection of the hepatocystic triangle becomes the sustained operative objective.

Some reviewed Cholec80 examples appear to place the P1-to-P2 transition closer to hook use. Do not alter canonical OAUTHC annotations to improve TeCNO scores. For this first study, report the boundary issue as a prespecified interpretation and limitation. A separate proxy-boundary experiment belongs to Project B unless it becomes essential to explain Project A's result.

## Privacy, reproducibility and leakage rules

- Run clinical-video inference only in the authorised local environment.
- Never commit videos, frames, clinical sidecars, identifying filenames, absolute paths or raw predictions derived from real videos.
- Commit only pseudonymous manifests, code, configurations and approved aggregate results.
- Pin code/checkpoint revisions and record Python, PyTorch and CUDA versions.
- Preserve raw model scores and exact sampling timestamps.
- Validate phase-ID mappings and millisecond alignment at IO boundaries.
- Record every excluded or failed case and its reason.
- Do not tune against the thirteen held-out OAUTHC labels.
- Do not claim frame accuracy beyond the actual sampling/timestamp evidence.

## Instructions for Codex

Act as the senior research software engineer. Before implementation:

1. Read this README completely.
2. Inspect the entire repository and run `git status --short`.
3. Inspect the chosen TeCNO implementation, licence, checkpoint and preprocessing rather than trusting this plan alone.
4. Inventory GPU, storage, Python/CUDA versions and local data layout without committing sensitive paths.
5. Propose and persist justified plan changes before implementation.
6. Work in small vertical slices and do not introduce Project B methods.

At each milestone report the observable result, commands and tests, runtime/resource cost, methodological risks, one focused manual check and the next go/no-go decision. Do not commit or push without approval.

## Milestones

### A0 — Handover and environment

- Inventory code/data and add protective ignore rules.
- Freeze the 2/13 split in a pseudonymous manifest.
- Document phase mapping and annotation time units.
- Create `.venv` or a justified isolated environment.
- Record hardware and dependencies.

Acceptance: environment imports succeed and no restricted data are tracked.

### A1 — TeCNO reproduction

- Load the selected checkpoint with its compatible preprocessing.
- Reproduce one official or Cholec80 example.
- Confirm seven-class ordering and sampling timestamps.
- Run one OAUTHC pilot video.
- Persist cached emissions.

Acceptance: source and pilot scores are meaningful, aligned and reproducible.

### A2 — Evaluation pipeline

- Define score, prediction and metric schemas.
- Test phase mapping, timestamp conversion and interval lookup synthetically.
- Reproduce native TeCNO predictions from cached scores.
- Generate one pilot timeline for manual inspection.

Acceptance: T0 runs end to end without rerunning inference.

### A3 — HMM

- Estimate source transition/initial probabilities.
- Implement smoothed Viterbi decoding.
- Unit-test known synthetic paths and numerical edge cases.
- Compare T0/T1 on source validation data and the two pilots only.
- Freeze HMM configuration.

Acceptance: T1 uses exactly T0's emissions and cannot hard-forbid atypical transitions.

### A4 — Held-out evaluation

- Record the frozen code/configuration revision.
- Run T0/T1 on Cholec80 test and thirteen OAUTHC cases.
- Preserve failures explicitly.
- Generate video-level paired metrics and intervals.

Acceptance: one command regenerates all numerical tables from cached scores.

### A5 — Scientific decision

Classify the result:

1. HMM materially improves held-out recognition;
2. HMM improves coherence but not recognition;
3. HMM has negligible effect; or
4. HMM harms atypical workflows.

Decide whether this supports a complete short-paper contribution. If not, stop adding unrelated methods here and open Project B's README as the separate fallback study.

## Suggested repository structure

```text
isbi_tecno_hmm/
├── README.md
├── pyproject.toml
├── configs/
├── manifests/
├── src/tecno_hmm/
│   ├── data/
│   ├── inference/
│   ├── temporal/
│   ├── evaluation/
│   └── reporting/
├── tests/
├── scripts/
├── docs/
└── outputs/                 # ignored except approved aggregate results
```

## Immediate first-night target

1. Create the repository and protective ignore rules.
2. Freeze the two pilot and thirteen held-out IDs.
3. Inspect hardware and the candidate TeCNO checkpoint.
4. Create the environment.
5. Reproduce one Cholec80 example.
6. Run one OAUTHC pilot video or representative pilot clip.
7. Save timestamped seven-class scores.
8. Implement and test Viterbi decoding.
9. Compare T0/T1 on the pilot only.

Do not begin Project B tonight. The desired result is evidence that the TeCNO-versus-HMM experiment is technically feasible before the deadline.
