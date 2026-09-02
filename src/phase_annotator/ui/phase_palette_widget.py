from typing import Dict, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from phase_annotator.domain.ontology import PhaseOntology


class PhasePaletteWidget(QWidget):
    """Visible, configured phase selector shared by mouse and keyboard input."""

    phase_selected = Signal(int)

    def __init__(self, parent=None, *, ontology: PhaseOntology):
        super().__init__(parent)
        self._ontology = ontology
        self._buttons: Dict[int, QPushButton] = {}
        self._active_phase_id: Optional[int] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(5)

        title = QLabel("Phases", self)
        title.setStyleSheet(
            "color: #EEEEEE; font-weight: bold; font-size: 14px; padding: 4px;"
        )
        layout.addWidget(title)

        for phase in ontology.ordered_phases:
            optional = " (optional)" if phase.is_optional else ""
            button = QPushButton(f"{phase.hotkey}  {phase.name}{optional}", self)
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setEnabled(False)
            button.setToolTip(
                f"Assign {phase.name} at the playhead (hotkey: {phase.hotkey})"
            )
            button.setAccessibleName(
                f"{phase.name}, hotkey {phase.hotkey}"
                + (", optional phase" if phase.is_optional else "")
            )
            button.setStyleSheet(self._button_style(phase.color_hex))
            button.clicked.connect(
                lambda checked=False, phase_id=phase.id: self.phase_selected.emit(
                    phase_id
                )
            )
            layout.addWidget(button)
            self._buttons[phase.id] = button

    @property
    def phase_buttons(self):
        return [self._buttons[phase.id] for phase in self._ontology.ordered_phases]

    @property
    def active_phase_id(self) -> Optional[int]:
        return self._active_phase_id

    @property
    def is_annotation_enabled(self) -> bool:
        return bool(self._buttons) and all(
            button.isEnabled() for button in self._buttons.values()
        )

    def button_for_phase(self, phase_id: int) -> QPushButton:
        return self._buttons[phase_id]

    def set_annotation_enabled(self, enabled: bool) -> None:
        for button in self._buttons.values():
            button.setEnabled(enabled)

    def set_active_phase(self, phase_id: Optional[int]) -> None:
        self._active_phase_id = phase_id
        for candidate_id, button in self._buttons.items():
            button.setChecked(candidate_id == phase_id)

    @staticmethod
    def _button_style(color_hex: str) -> str:
        return f"""
            QPushButton {{
                background-color: #252525;
                color: #EEEEEE;
                border: 1px solid #444444;
                border-left: 8px solid {color_hex};
                border-radius: 4px;
                padding: 7px 9px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: #333333;
                border-color: {color_hex};
            }}
            QPushButton:checked {{
                background-color: {color_hex};
                color: #FFFFFF;
                font-weight: bold;
                border-color: #FFFFFF;
            }}
            QPushButton:disabled {{
                color: #888888;
                background-color: #202020;
            }}
        """
