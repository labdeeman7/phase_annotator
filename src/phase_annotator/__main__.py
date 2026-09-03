import sys
from PySide6.QtWidgets import QApplication
from phase_annotator.config import load_default_ontology
from phase_annotator.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    # Procedure selection belongs here at the composition root; reusable UI
    # widgets receive a generic ontology and do not load appendectomy data.
    ontology = load_default_ontology()
    window = MainWindow(ontology=ontology)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
