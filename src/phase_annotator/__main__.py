import sys
from PySide6.QtWidgets import QApplication
from phase_annotator.config import load_default_ontology
from phase_annotator.ui.main_window import MainWindow
from phase_annotator.ui.annotator_identity import prompt_for_annotator_id


def main():
    app = QApplication(sys.argv)
    annotator_id = prompt_for_annotator_id()
    if annotator_id is None:
        return 0
    # Procedure selection belongs here at the composition root; reusable UI
    # widgets receive a generic ontology and do not load appendectomy data.
    ontology = load_default_ontology()
    window = MainWindow(ontology=ontology, annotator_id=annotator_id)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
