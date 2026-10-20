from typing import Optional

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from phase_annotator.domain.completion import CompletionSummary
from phase_annotator.domain.time_utils import format_timecode

PRIVACY_CHECKBOX_TEXT = (
    "I checked this video for out-of-body footage and for faces, names or dates "
    "on screen, and marked any I found as De-identify"
)


class CompletionDialog(QDialog):
    """Review facts plus the required privacy declaration before marking complete."""

    def __init__(
        self,
        summary: CompletionSummary,
        other_name: str,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Mark annotation complete?")
        self.setModal(True)

        lines = [
            f"Duration: {format_timecode(summary.duration_ms)}",
            f"Segments: {summary.segment_count}",
            f"{other_name}: {summary.undefined_segment_count} segment(s), "
            f"{format_timecode(summary.undefined_duration_ms)}",
            f"Video note: {'present' if summary.has_session_note else 'none'}",
        ]
        warnings = []
        if summary.undescribed_other_count:
            warnings.append(
                f"{summary.undescribed_other_count} {other_name} segment(s) have no "
                "type and no description."
            )
        if summary.short_other_count:
            warnings.append(
                f"{summary.short_other_count} {other_name} segment(s) are shorter than "
                "30 seconds (only De-identify may be shorter)."
            )

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("\n".join(lines), self))
        if warnings:
            warning_label = QLabel("Please check:\n- " + "\n- ".join(warnings), self)
            warning_label.setWordWrap(True)
            layout.addWidget(warning_label)
        self._privacy_checkbox = QCheckBox(PRIVACY_CHECKBOX_TEXT, self)
        self._privacy_checkbox.setChecked(False)
        layout.addWidget(self._privacy_checkbox)
        layout.addWidget(
            QLabel("This declares that you have reviewed the annotation.", self)
        )

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No,
            parent=self,
        )
        self._yes_button = self._buttons.button(QDialogButtonBox.StandardButton.Yes)
        self._yes_button.setText("Mark complete")
        self._yes_button.setEnabled(False)
        self._privacy_checkbox.toggled.connect(self._yes_button.setEnabled)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)
        layout.addWidget(self._buttons)

    @property
    def privacy_checked(self) -> bool:
        return self._privacy_checkbox.isChecked()
