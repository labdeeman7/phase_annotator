from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)


class SegmentNoteDialog(QDialog):
    """Modal editor for one segment's optional note."""

    def __init__(self, notes: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Edit segment note")
        self.setModal(True)
        self.resize(420, 240)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Note", self))
        self._notes_edit = QPlainTextEdit(self)
        self._notes_edit.setPlainText(notes)
        self._notes_edit.setPlaceholderText(
            "Optional: record an unusual event or observation"
        )
        layout.addWidget(self._notes_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @property
    def notes(self) -> str:
        return self._notes_edit.toPlainText()
