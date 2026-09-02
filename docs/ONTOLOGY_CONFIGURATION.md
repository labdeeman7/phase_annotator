# Ontology Configuration

Phase definitions are loaded from versioned JSON rather than hard-coded UI logic. The packaged default is `src/phase_annotator/config/default_appendectomy.json`.

## Top-level contract

```json
{
  "schema_version": "1.0",
  "ontology_id": "laparoscopic_appendectomy.default",
  "ontology_version": "1.0",
  "name": "Laparoscopic Appendectomy Ontology",
  "initial_phase_id": 1,
  "undefined_phase_id": 0,
  "phases": []
}
```

- `schema_version` identifies the configuration-file structure. Only `1.0` is currently supported.
- `ontology_id` is a stable identity recorded in annotation sessions.
- `ontology_version` changes when the meaning/mapping of that ontology changes.
- `initial_phase_id` is the provisional class assigned to `[0, duration_ms)` when media duration becomes known. It is explicit rather than inferred from list position or the smallest ID.
- `undefined_phase_id` identifies the uncertainty/exception class used by later correction operations.

## Phase contract

Each phase requires:

```json
{
  "id": 1,
  "name": "Identification of the appendix",
  "hotkey": "1",
  "color_hex": "#3B82F6",
  "order": 1,
  "is_optional": false,
  "description": "Identification and initial assessment of the appendix."
}
```

- `id` is the stable integer stored in every annotation interval.
- `order` is expected clinical/display order only; it does not prohibit repetition or out-of-order transitions.
- `hotkey` is one printable character and is compared case-insensitively.
- `color_hex` must use `#RRGGBB` notation.
- `is_optional` and `description` provide UI/research context without changing transition validity.

IDs, hotkeys, and order values must each be unique. Both role IDs must reference configured phases. The parser rejects malformed or unsupported configuration before an ontology reaches the UI.

## Layering

`PhaseOntology.from_config()` performs pure validation/construction from an already decoded mapping. `phase_annotator.config` owns packaged-resource/path and JSON I/O through generic loaders. `__main__.py` is the composition root: it selects `load_default_ontology()` for the current application launch and injects the resulting ontology into `MainWindow`. The window and its child widgets do not know whether that object came from appendectomy, cholecystectomy, or a user-selected file.

Generic entry points:

- `load_ontology_from_path(path)`: future user-selected/custom JSON.
- `load_packaged_ontology(filename)`: any ontology shipped with the application.
- `load_default_ontology()`: current startup policy; today this selects appendectomy.

The default configuration displays surgical phases 1-6 in expected order and Undefined (`U`) last. C2 will render this metadata as the visible clickable phase palette and route configured hotkeys through the existing transition command.
