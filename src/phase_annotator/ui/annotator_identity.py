from typing import Optional

from PySide6.QtWidgets import QInputDialog, QMessageBox, QWidget


def normalize_annotator_id(value: str) -> str:
    annotator_id = value.strip()
    if not annotator_id:
        raise ValueError("Annotator ID cannot be empty.")
    if len(annotator_id) > 100:
        raise ValueError("Annotator ID must be 100 characters or fewer.")
    return annotator_id


def prompt_for_annotator_id(
    parent: Optional[QWidget] = None,
    *,
    initial: str = "",
    title: str = "Annotator identity",
) -> Optional[str]:
    """Request a confirmed study/user identifier; Cancel returns None."""
    current = initial
    while True:
        value, accepted = QInputDialog.getText(
            parent,
            title,
            "Annotator ID (for example study ID, username, or initials):",
            text=current,
        )
        if not accepted:
            return None
        try:
            return normalize_annotator_id(value)
        except ValueError as error:
            QMessageBox.warning(parent, "Invalid annotator ID", str(error))
            current = value
