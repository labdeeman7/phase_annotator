from typing import List, Optional
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget

from phase_annotator.domain.models import AnnotationInterval
from phase_annotator.domain.ontology import PhaseOntology


class TimelineWidget(QWidget):
    """Custom Qt canvas widget rendering surgical phase intervals & interactive playhead needle."""

    seek_requested = Signal(int)
    segment_selected = Signal(int)

    def __init__(
        self,
        parent=None,
        *,
        ontology: PhaseOntology,
    ):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setMinimumWidth(300)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self._duration_ms: int = 0
        self._current_position_ms: int = 0
        self._intervals: List[AnnotationInterval] = []
        self._selected_index: Optional[int] = None
        self._active_index: Optional[int] = None
        self._ontology = ontology

    @property
    def selected_index(self) -> Optional[int]:
        return self._selected_index

    @property
    def active_index(self) -> Optional[int]:
        return self._active_index

    def set_duration(self, duration_ms: int) -> None:
        self._duration_ms = max(0, duration_ms)
        self.update()

    def set_position(self, position_ms: int) -> None:
        self._current_position_ms = max(0, position_ms)
        self.update()

    def set_intervals(self, intervals: List[AnnotationInterval]) -> None:
        self._intervals = intervals
        self.update()

    def set_selected_index(self, index: Optional[int]) -> None:
        """Display the application-owned edit/navigation selection."""
        self._selected_index = self._valid_index_or_none(index)
        self.update()

    def set_active_index(self, index: Optional[int]) -> None:
        """Display the interval currently underneath the playhead."""
        self._active_index = self._valid_index_or_none(index)
        self.update()

    def _valid_index_or_none(self, index: Optional[int]) -> Optional[int]:
        if index is not None and 0 <= index < len(self._intervals):
            return index
        return None

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Background track
        painter.fillRect(0, 0, width, height, QColor("#222222"))

        # Draw Phase Interval Blocks
        if self._duration_ms > 0:
            for index, interval in enumerate(self._intervals):
                try:
                    phase = self._ontology.get_phase_by_id(interval.phase_id)
                    color_hex = phase.color_hex
                except KeyError:
                    color_hex = "#888888"

                start_x = int((interval.start_ms / self._duration_ms) * width)
                end_x = int((interval.end_ms / self._duration_ms) * width)
                block_width = max(2, end_x - start_x)

                painter.fillRect(start_x, 4, block_width, height - 8, QColor(color_hex))

                # Active and selected are independent; draw both when they
                # coincide so the timeline does not hide either state.
                if index == self._active_index:
                    painter.setPen(QPen(QColor("#FFFFFF"), 2))
                    painter.drawRect(start_x + 1, 5, max(0, block_width - 2), height - 11)
                if index == self._selected_index:
                    painter.setPen(QPen(QColor("#00D1FF"), 3))
                    painter.drawRect(start_x + 2, 6, max(0, block_width - 4), height - 13)

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
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            click_x = event.position().x()
            ratio = max(0.0, min(1.0, click_x / self.width()))
            target_ms = int(ratio * self._duration_ms)
            # Half-open intervals exclude duration_ms. Use the last real
            # millisecond only to identify a segment at the far-right edge;
            # the actual seek request may still target the video end.
            selection_ms = min(target_ms, self._duration_ms - 1)
            for index, interval in enumerate(self._intervals):
                if interval.start_ms <= selection_ms < interval.end_ms:
                    self.segment_selected.emit(index)
                    break
            self.seek_requested.emit(target_ms)
