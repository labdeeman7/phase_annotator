from typing import Optional, Sequence

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from phase_annotator.domain.ontology import OtherSubtype
from phase_annotator.domain.other_types import compose_note, split_tag

PLAIN_OTHER_LABEL = "Something else (describe it below)"


class OtherDetailsDialog(QDialog):
    """Choose what kind of Other a segment is; the tag is written at the note's start."""

    def __init__(
        self,
        notes: str,
        subtypes: Sequence[OtherSubtype],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("What is this Other segment?")
        self.setModal(True)
        self.resize(460, 280)
        self._subtypes = list(subtypes)

        tag, text = split_tag(notes)
        known = [subtype.tag for subtype in self._subtypes]
        if tag is not None and tag not in known:
            # An unfamiliar tag stays part of the text rather than being dropped.
            tag, text = None, notes

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Type", self))
        self._type_combo = QComboBox(self)
        for subtype in self._subtypes:
            self._type_combo.addItem(subtype.label, subtype.tag)
        self._type_combo.addItem(PLAIN_OTHER_LABEL, None)
        self._type_combo.setCurrentIndex(
            known.index(tag) if tag in known else len(self._subtypes)
        )
        layout.addWidget(self._type_combo)

        layout.addWidget(QLabel("Description", self))
        self._text_edit = QPlainTextEdit(self)
        self._text_edit.setPlainText(text)
        self._text_edit.setPlaceholderText(
            "What happens here? Required for 'Something else'; optional otherwise."
        )
        layout.addWidget(self._text_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @property
    def tag(self) -> Optional[str]:
        data = self._type_combo.currentData()
        return data if isinstance(data, str) else None

    @property
    def notes(self) -> str:
        return compose_note(self.tag, self._text_edit.toPlainText())
