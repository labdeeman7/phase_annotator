"""Application-wide visual theme for the annotation workstation."""

APPLICATION_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #111820;
    color: #E6EDF3;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 12px;
}

QMenuBar {
    background-color: #18222D;
    color: #E6EDF3;
    border-bottom: 1px solid #2B3B4B;
    padding: 4px 8px;
    font-weight: 600;
}
QMenuBar::item {
    background: transparent;
    border-radius: 5px;
    padding: 7px 12px;
}
QMenuBar::item:selected, QMenuBar::item:pressed {
    background-color: #263746;
    color: #FFFFFF;
}
QMenu {
    background-color: #1B2632;
    color: #E6EDF3;
    border: 1px solid #3A4D5F;
    border-radius: 6px;
    padding: 6px;
}
QMenu::item { padding: 8px 30px 8px 12px; border-radius: 4px; }
QMenu::item:selected { background-color: #087EA4; color: #FFFFFF; }
QMenu::item:disabled { color: #667788; }
QMenu::separator { height: 1px; background: #344554; margin: 5px 8px; }

QPushButton, QToolButton {
    background-color: #243240;
    color: #E6EDF3;
    border: 1px solid #405164;
    border-radius: 6px;
    padding: 7px 12px;
    min-height: 18px;
}
QPushButton:hover, QToolButton:hover {
    background-color: #304354;
    border-color: #38BDF8;
}
QPushButton:pressed, QToolButton:pressed { background-color: #17232E; }
QPushButton:disabled, QToolButton:disabled {
    background-color: #18222B;
    color: #5F7080;
    border-color: #263543;
}
QPushButton#openVideoButton {
    background-color: #087EA4;
    border-color: #22B8E6;
    color: #FFFFFF;
    font-weight: 600;
}
QPushButton#playButton { font-weight: 600; }

QSlider::groove:horizontal {
    height: 5px;
    background: #314150;
    border-radius: 2px;
}
QSlider::sub-page:horizontal { background: #22B8E6; border-radius: 2px; }
QSlider::handle:horizontal {
    background: #F8FAFC;
    border: 2px solid #22B8E6;
    width: 14px;
    margin: -6px 0;
    border-radius: 8px;
}

QStatusBar {
    background-color: #18222D;
    color: #AFC1D1;
    border-top: 1px solid #2B3B4B;
}
QStatusBar::item { border: none; }
QSplitter::handle { background-color: #2A3947; width: 2px; }

QDialog { background-color: #16212B; }
QPlainTextEdit, QLineEdit, QTextEdit, QComboBox, QAbstractSpinBox {
    background-color: #0E151C;
    color: #E6EDF3;
    border: 1px solid #405164;
    border-radius: 6px;
    padding: 7px;
    selection-background-color: #087EA4;
}
QPlainTextEdit:focus, QLineEdit:focus, QTextEdit:focus {
    border-color: #22B8E6;
}
QMessageBox { background-color: #16212B; }
QToolTip {
    background-color: #253544;
    color: #FFFFFF;
    border: 1px solid #52687C;
    padding: 5px;
}

QScrollBar:vertical { background: #141D26; width: 11px; margin: 0; }
QScrollBar::handle:vertical {
    background: #415467;
    min-height: 30px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover { background: #587086; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""
