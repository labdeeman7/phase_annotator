import sys

from PySide6.QtWidgets import QApplication

from phase_annotator.config import PACKAGED_PROCEDURES, load_procedure_ontology
from phase_annotator.ui.annotator_identity import prompt_for_annotator_id
from phase_annotator.ui.main_window import MainWindow
from phase_annotator.ui.procedure_selection import prompt_for_procedure
from phase_annotator.ui.theme import APPLICATION_STYLESHEET

ARTIFACT_SMOKE_ARGUMENT = "--artifact-smoke-test"


def artifact_smoke_check() -> None:
    """Load every packaged ontology and construct its real application window."""
    for procedure in PACKAGED_PROCEDURES:
        ontology = load_procedure_ontology(procedure.key)
        if ontology.ontology_id != procedure.ontology_id:
            raise RuntimeError(
                f"Packaged procedure '{procedure.key}' loaded unexpected ontology "
                f"'{ontology.ontology_id}'."
            )
        window = MainWindow(ontology=ontology, annotator_id="artifact-smoke-test")
        if procedure.display_name.casefold() not in window.windowTitle().casefold():
            raise RuntimeError(
                f"Window title does not identify packaged procedure '{procedure.key}'."
            )
        window.close()


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv if argv is None else argv)
    app = QApplication.instance() or QApplication(arguments)
    app.setStyleSheet(APPLICATION_STYLESHEET)
    if ARTIFACT_SMOKE_ARGUMENT in arguments[1:]:
        artifact_smoke_check()
        return 0
    annotator_id = prompt_for_annotator_id()
    if annotator_id is None:
        return 0
    procedure_key = prompt_for_procedure()
    if procedure_key is None:
        return 0
    # Procedure selection belongs here at the composition root; reusable UI
    # widgets receive a generic ontology and do not load appendectomy data.
    ontology = load_procedure_ontology(procedure_key)
    window = MainWindow(ontology=ontology, annotator_id=annotator_id)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
