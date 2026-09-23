import sys
from PySide6.QtWidgets import QApplication
from phase_annotator.config import load_procedure_ontology
from phase_annotator.ui.main_window import MainWindow
from phase_annotator.ui.annotator_identity import prompt_for_annotator_id
from phase_annotator.ui.procedure_selection import prompt_for_procedure
from phase_annotator.ui.theme import APPLICATION_STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APPLICATION_STYLESHEET)
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
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
