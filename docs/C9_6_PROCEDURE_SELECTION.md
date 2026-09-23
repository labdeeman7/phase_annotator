# C9.6 Procedure Selection and Bundled Ontologies

## Why this is required

The annotation engine and widgets already consume a generic `PhaseOntology`, but the composition root currently always calls `load_default_ontology()` and therefore always selects appendectomy. Before packaging, the startup workflow must expose the flexibility that already exists in the architecture.

## Product contract

- After confirming the annotator's first name, ask which procedure is being annotated.
- Initially offer two clinician-facing choices: **Laparoscopic appendectomy** and **Laparoscopic cholecystectomy**.
- Keep both phase definitions as validated, versioned JSON resources bundled with the application.
- Show the chosen procedure unobtrusively in the application title and use its configured phases, colors, order, hotkeys, initial phase, and Undefined phase throughout the UI.
- Keep the chosen ontology fixed for each open video. Opening a sidecar created with a different ontology must remain blocked rather than reinterpreting stored phase IDs.
- Do not require doctors to browse the filesystem or edit configuration files during ordinary use.

## Configuration decision

JSON remains the canonical format. A line-based text file cannot safely express stable numeric IDs, colors, hotkeys, optional phases, ontology versions, descriptions, and the special initial/Undefined roles without inventing another parser and schema.

`load_ontology_from_path()` already supports a future advanced **Import ontology JSON...** workflow, but arbitrary external configurations are deferred until there is a real user-management and validation experience. The first packaged release should expose only reviewed bundled ontologies.

## Packaging

This design is packaging-safe. `pyproject.toml` already includes every `*.json` file in `phase_annotator.config` as package data, and `importlib.resources` reads those files both during editable development and from an installed package. C10 must verify that both resources are present and loadable in the built executable.

## Implementation slices

- **C9.6.1 — Registry (implemented):** friendly procedure metadata maps to packaged JSON resources without putting procedure knowledge in reusable widgets.
- **C9.6.2 — Cholecystectomy ontology (implemented):** the seven user-approved phases are configured as P1-P7 plus the application's Undefined class.
- **C9.6.3 — Startup selection (implemented):** a compact procedure chooser follows identity confirmation and `__main__.py` injects the selected ontology.
- **C9.6.4 — Context and safety (implemented):** the title displays procedure context and existing ontology identity/version validation blocks cross-procedure sidecars.
- **C9.6.5 — Packaging acceptance:** prove both bundled JSON resources survive the Windows build.

## Data-integrity constraints

- Never infer procedure from the video filename.
- Never remap interval IDs from one ontology to another.
- Never silently open a sidecar under a different ontology identity/version.
- Changes to an already-used ontology require a version and compatibility/migration decision.
- Example configurations and tests must contain no patient-identifying information.

## Cholecystectomy phase contract

The project supplied and approved this expected order: Preparation; Calot triangle dissection; Clipping and cutting; Gallbladder dissection; Gallbladder packaging; Cleaning and coagulation; Gallbladder retraction. P1 Preparation is the provisional initial phase. None are marked optional. Undefined remains a separate application class with hotkey `U`.

## Current status

C9.6.1-C9.6.4 are implemented and tested. C9.6.5 belongs to the C10 Windows-build acceptance work.
