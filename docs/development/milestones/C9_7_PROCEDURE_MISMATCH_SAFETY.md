# C9.7 Procedure-Mismatch Safety

## Decision

Keep one canonical `<video filename>.phase-annotations.json` sidecar per video. Do not put the procedure in the filename and do not silently create a second annotation when the operator selects the wrong procedure.

The sidecar's persisted `ontology_id` and `ontology_version` remain the authority for interpreting phase IDs. A mismatch is a safe blocked state, not a recoverable warning that may be ignored.

## User-visible behavior

When the selected procedure differs from an existing sidecar:

- name the procedure used by the saved annotation;
- name the procedure selected for the current launch;
- state that nothing was changed;
- instruct the annotator to close and restart with the saved procedure;
- disable annotation for that load and preserve the canonical JSON byte-for-byte.

Unknown/custom ontology IDs fall back to displaying the stored ID rather than inventing a procedure name.

## Why filenames remain procedure-neutral

Procedure-specific filenames would allow an accidental selection to appear as a new unannotated video and create a second, clinically incorrect annotation. Because procedure type is intrinsic to the video in the current workflow, one canonical sidecar plus strict ontology validation is safer and easier to explain.

Supporting multiple ontologies for one video would be a distinct product feature requiring an explicit selection and export model; C9.7 does not imply that behavior.

## Status and validation

C9.7 is implemented. Storage returns the loaded session only for explicit ontology-mismatch explanation, while the UI translates known IDs through the packaged procedure registry. Tests verify the mismatch is blocked, both friendly names are shown, and the sidecar is unchanged.
