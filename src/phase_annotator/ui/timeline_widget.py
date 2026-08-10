from typing import List
from PySide6.QtCore import Signal, Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QWidget

from phase_annotator.domain.models import AnnotationInterval
from phase_annotator.domain.ontology import PhaseOntology


class TimelineWidget(QWidget):
    """Custom Qt canvas widget rendering surgical phase intervals & interactive playhead needle."""

    seek_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setMinimumWidth(300)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._duration_ms: int = 0
        self._current_position_ms: int = 0
        self._intervals: List[AnnotationInterval] = []
        self._ontology = PhaseOntology.default_appendectomy()

    def set_duration(self, duration_ms: int) -> None:
        self._duration_ms = max(0, duration_ms)
        self.update()

    def set_position(self, position_ms: int) -> None:
        self._current_position_ms = max(0, position_ms)
        self.update()

    def set_intervals(self, intervals: List[AnnotationInterval]) -> None:
        self._intervals = intervals
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Background track
        painter.fillRect(0, 0, width, height, QColor("#222222"))

        # Draw Phase Interval Blocks
        if self._duration_ms > 0:
            for interval in self._intervals:
                try:
                    phase = self._ontology.get_phase_by_id(interval.phase_id)
                    color_hex = phase.color_hex
                except KeyError:
                    color_hex = "#888888"

                start_x = int((interval.start_ms / self._duration_ms) * width)
                end_x = int((interval.end_ms / self._duration_ms) * width)
                block_width = max(2, end_x - start_x)

                painter.fillRect(start_x, 4, block_width, height - 8, QColor(color_hex))

            # Draw Playhead Needle (Red Vertical Line)
            needle_x = int((self._current_position_ms / self._duration_ms) * width)
            pen = QPen(QColor("#FF0000"), 3)
            painter.setPen(pen)
            painter.drawLine(needle_x, 0, needle_x, height)

        # Draw Border
        painter.setPen(QPen(QColor("#444444"), 1))
        painter.drawRect(0, 0, width - 1, height - 1)

    def mousePressEvent(self, event) -> None:
        if self._duration_ms > 0 and event.button() == Qt.MouseButton.LeftButton:
            click_x = event.position().x()
            ratio = max(0.0, min(1.0, click_x / self.width()))
            target_ms = int(ratio * self._duration_ms)
            self.seek_requested.emit(target_ms)
