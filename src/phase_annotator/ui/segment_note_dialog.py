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

    def __init__(
        self,
        notes: str,
        parent: QWidget | None = None,
        *,
        title: str = "Edit segment note",
        label: str = "Note",
        placeholder: str = "Optional: record an unusual event or observation",
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(420, 240)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(label, self))
        self._notes_edit = QPlainTextEdit(self)
        self._notes_edit.setPlainText(notes)
        self._notes_edit.setPlaceholderText(placeholder)
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
