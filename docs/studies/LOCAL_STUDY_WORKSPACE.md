# Ignored Local Study Workspace

The real and derived media workspace is ignored by Git. Its logical structure is:

```text
test_dataset/cholec80_protocol_study/
├── reference_cases/
│   ├── videos/              # 10 MP4s plus protected live sidecars
│   ├── source_labels/       # original Cholec80 frame TXT files
│   ├── reference_answers/   # converted sidecars and provenance manifests
│   └── transition_clips/    # generated one-minute boundary clips and manifests
├── self_practice/
│   ├── cholec80_blind_3/    # no adjacent answer sidecars
│   ├── protected_answers/   # inaccessible until each exercise is completed
│   └── scoring/             # offline comparison reports
├── local_adaptation/
│   ├── practice_videos_2/   # two representative project videos
│   └── review/              # local-differences observations and reviewed labels
└── clinician_package/
    ├── application/
    ├── user_guide/
    ├── protocol/
    ├── clip_library/
    └── exercises/
```

The earlier `cholec80_v3/` and `cholec80_v4/` staging folders were consolidated into this structure after their files were verified. No media, source labels, converted answers, clips, scoring reports, or machine-specific paths belong in Git.

The folder layout separates reference evidence, blind work, local adaptation, and distributable material. In particular, never copy `protected_answers/` beside a blind-practice video before that exercise is complete.
