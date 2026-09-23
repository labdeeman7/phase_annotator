from typing import Optional

from PySide6.QtWidgets import QInputDialog, QMessageBox, QWidget


def normalize_annotator_id(value: str) -> str:
    annotator_id = value.strip().lower()
    if not annotator_id:
        raise ValueError("First name cannot be empty.")
    if any(character.isspace() for character in annotator_id):
        raise ValueError("Please enter only your first name.")
    if len(annotator_id) > 50:
        raise ValueError("First name must be 50 characters or fewer.")
    return annotator_id


def prompt_for_annotator_id(
    parent: Optional[QWidget] = None,
    *,
    initial: str = "",
    title: str = "Who is annotating?",
) -> Optional[str]:
    """Request the annotator's first name; Cancel returns None."""
    current = initial
    while True:
        value, accepted = QInputDialog.getText(
            parent,
            title,
            "First name:",
            text=current,
        )
        if not accepted:
            return None
        try:
            return normalize_annotator_id(value)
        except ValueError as error:
            QMessageBox.warning(parent, "Invalid first name", str(error))
            current = value
