from typing import Optional

from PySide6.QtWidgets import QInputDialog, QWidget

from phase_annotator.config import PACKAGED_PROCEDURES


def prompt_for_procedure(parent: Optional[QWidget] = None) -> Optional[str]:
    """Return the selected packaged procedure key; Cancel returns None."""
    labels = [procedure.display_name for procedure in PACKAGED_PROCEDURES]
    selected, accepted = QInputDialog.getItem(
        parent,
        "Select procedure",
        "Surgical procedure:",
        labels,
        0,
        False,
    )
    if not accepted:
        return None
    return next(
        procedure.key
        for procedure in PACKAGED_PROCEDURES
        if procedure.display_name == selected
    )
