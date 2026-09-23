from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from phase_annotator.domain.ontology import PhaseOntology


class ShortcutsHelpDialog(QDialog):
    """Compact visual reference for the application's interaction model."""

    def __init__(self, ontology: PhaseOntology, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Shortcuts and controls")
        self.setModal(True)
        self.setMinimumWidth(620)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 16)
        layout.setSpacing(14)

        title = QLabel("Shortcuts and controls", self)
        title.setObjectName("helpTitle")
        subtitle = QLabel(
            "Fast navigation and safe annotation correction", self
        )
        subtitle.setObjectName("helpSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        columns = QHBoxLayout()
        columns.setSpacing(12)
        columns.addWidget(
            self._shortcut_section(
                "Playback",
                [
                    ("Space", "Play or pause"),
                    ("← / →", "Step one estimated frame"),
                    ("Buttons", "Jump ±5 seconds"),
                    ("Speed", "Play at 1× to 12×"),
                ],
            )
        )
        columns.addWidget(
            self._shortcut_section(
                "Editing",
                [
                    ("Ctrl+Z", "Undo annotation change"),
                    ("Ctrl+Shift+Z", "Redo annotation change"),
                    ("Delete", "Selected segment → Undefined"),
                    ("Right-click", "Open segment corrections"),
                    ("Drag", "Move a timeline boundary"),
                ],
            )
        )
        layout.addLayout(columns)

        phase_card = QFrame(self)
        phase_card.setObjectName("helpCard")
        phase_layout = QGridLayout(phase_card)
        phase_layout.setContentsMargins(14, 12, 14, 12)
        phase_layout.setHorizontalSpacing(10)
        phase_layout.setVerticalSpacing(7)
        heading = QLabel("Phase hotkeys", phase_card)
        heading.setObjectName("helpSectionTitle")
        phase_layout.addWidget(heading, 0, 0, 1, 4)
        for index, phase in enumerate(ontology.ordered_phases):
            row = 1 + index // 2
            column = (index % 2) * 2
            key = QLabel(phase.hotkey, phase_card)
            key.setObjectName("shortcutKey")
            key.setFixedWidth(34)
            key.setAlignment(Qt.AlignmentFlag.AlignCenter)
            key.setStyleSheet(
                f"background-color: {phase.color_hex}; color: white;"
            )
            name = QLabel(phase.name, phase_card)
            name.setWordWrap(True)
            phase_layout.addWidget(key, row, column)
            phase_layout.addWidget(name, row, column + 1)
        layout.addWidget(phase_card)

        tip = QLabel(
            "Tip: click a segment card or the timeline to select it. "
            "Use the Annotation menu for video notes and completion.",
            self,
        )
        tip.setObjectName("helpTip")
        tip.setWordWrap(True)
        layout.addWidget(tip)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _shortcut_section(self, title: str, rows: list[tuple[str, str]]) -> QFrame:
        card = QFrame(self)
        card.setObjectName("helpCard")
        grid = QGridLayout(card)
        grid.setContentsMargins(14, 12, 14, 12)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(8)
        heading = QLabel(title, card)
        heading.setObjectName("helpSectionTitle")
        grid.addWidget(heading, 0, 0, 1, 2)
        for row, (shortcut, description) in enumerate(rows, start=1):
            key = QLabel(shortcut, card)
            key.setObjectName("shortcutKey")
            description_label = QLabel(description, card)
            grid.addWidget(key, row, 0)
            grid.addWidget(description_label, row, 1)
        grid.setColumnStretch(1, 1)
        return card
