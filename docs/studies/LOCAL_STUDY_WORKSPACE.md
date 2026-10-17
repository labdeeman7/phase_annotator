# Ignored Local Media Workspace

The real and derived media workspace is ignored by Git. It is organised by purpose rather than by temporary study stage:

```text
test_dataset/
├── application_smoke_test/
│   ├── 20250922_121504.mp4
│   └── 20250922_121504.mp4.phase-annotations.json
├── clinician_pilot/
│   ├── Phase_Annotator_Cholecystectomy_0.1_Pilot/
│   ├── Phase_Annotator_Cholecystectomy_0.1_Pilot.zip
│   ├── returned_originals/              # immutable returned clinician sidecars
│   ├── Local_Clinical_Training_Material_0.3/ # preserved internal evidence
│   └── OAUTHC_Cholecystectomy_Training_Material_0.4/
└── reference_cases/
    ├── videos/              # 10 Cholec80 MP4s plus protected live sidecars
    ├── source_labels/       # original Cholec80 frame-label TXT files
    ├── reference_answers/   # converted sidecars and provenance manifests
    └── transition_clips/    # generated labelled boundary clips and manifests
```

## Directory roles

- `application_smoke_test/` is disposable application-development media. It is not clinician study material.
- `clinician_pilot/` contains exactly what was prepared for the Nigerian clinician pilot. Keep the unpacked package and its transfer ZIP together. Returned annotation sidecars may remain adjacent to their corresponding videos inside the unpacked package.
- `clinician_pilot/Local_Clinical_Training_Material_0.3/` preserves the first nine-boundary extraction as internal review evidence; do not delete or distribute it as the current manual.
- `clinician_pilot/OAUTHC_Cholecystectomy_Training_Material_0.4/` is the current phase-organised material: two examples per phase, preferring OAUTHC evidence and clearly labelling Cholec80 fallbacks.
- `reference_cases/` contains the ten selected Cholec80 cases and all evidence derived from them. It is research/protocol-development material, not part of the clinician handout except for the selected clips copied into the package.

The obsolete staging, self-practice, preview-render, and duplicate local-video directories were removed on 15 October 2026 after the final pilot package and reference corpus were verified.

No media, source labels, converted answers, clips, returned annotations, feedback, or machine-specific paths belong in Git.

## Clinician-pilot handling

- The local study videos are `20260505_221257.mp4` and `20260519_215628.mp4`.
- Preserve each returned sidecar before making any reviewed correction.
- Keep each sidecar beside the video with the exact name `<video filename>.phase-annotations.json`.
- Phase Annotator 0.1.2 or later is required when opening annotations copied from another computer.
- Keep transfer locations and absolute paths outside committed documentation.
