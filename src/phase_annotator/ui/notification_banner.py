from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QFrame


class NotificationBanner(QFrame):
    """Dismissible high-visibility feedback for actionable problems."""

    dismissed = Signal()

    _COLORS = {
        "error": ("#3B161B", "#F87171"),
        "warning": ("#3A2A0D", "#FBBF24"),
        "info": ("#102D3A", "#38BDF8"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)
        self.setAccessibleName("Application notification")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 8, 8)
        self._message = QLabel(self)
        self._message.setWordWrap(True)
        layout.addWidget(self._message, stretch=1)
        self._dismiss = QPushButton("Dismiss", self)
        self._dismiss.setAccessibleName("Dismiss notification")
        self._dismiss.clicked.connect(self.hide_notification)
        layout.addWidget(self._dismiss)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide_notification)

    @property
    def message(self) -> str:
        return self._message.text()

    def show_notification(
        self, message: str, *, level: str = "error", timeout_ms: int = 0
    ) -> None:
        background, accent = self._COLORS.get(level, self._COLORS["info"])
        self.setStyleSheet(
            f"NotificationBanner {{ background: {background}; "
            f"border: 1px solid {accent}; border-left: 5px solid {accent}; "
            "border-radius: 6px; }}"
        )
        self._message.setText(message)
        self.setVisible(True)
        self.raise_()
        self._timer.stop()
        if timeout_ms > 0:
            self._timer.start(timeout_ms)

    def hide_notification(self) -> None:
        self._timer.stop()
        self.setVisible(False)
        self.dismissed.emit()
