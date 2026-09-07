from typing import List, Optional
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget

from phase_annotator.domain.models import AnnotationInterval
from phase_annotator.domain.ontology import PhaseOntology


class TimelineWidget(QWidget):
    """Custom Qt canvas widget rendering surgical phase intervals & interactive playhead needle."""

    BOUNDARY_HIT_RADIUS_PX = 8
    segment_selection_requested = Signal(int, int)  # interval index, seek time
    boundary_preview_requested = Signal(int)  # preview timestamp
    boundary_move_requested = Signal(int, int)  # boundary index, timestamp
    boundary_drag_cancelled = Signal(str, int)  # reason, original timestamp

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
        self.setMouseTracking(True)

        self._duration_ms: int = 0
        self._current_position_ms: int = 0
        self._intervals: List[AnnotationInterval] = []
        self._selected_index: Optional[int] = None
        self._active_index: Optional[int] = None
        self._hovered_boundary_index: Optional[int] = None
        self._drag_boundary_index: Optional[int] = None
        self._drag_original_ms: Optional[int] = None
        self._drag_preview_ms: Optional[int] = None
        self._drag_preview_valid = False
        self._ontology = ontology

    @property
    def selected_index(self) -> Optional[int]:
        return self._selected_index

    @property
    def active_index(self) -> Optional[int]:
        return self._active_index

    @property
    def hovered_boundary_index(self) -> Optional[int]:
        return self._hovered_boundary_index

    @property
    def drag_boundary_index(self) -> Optional[int]:
        return self._drag_boundary_index

    @property
    def drag_preview_ms(self) -> Optional[int]:
        return self._drag_preview_ms

    @property
    def is_drag_preview_valid(self) -> bool:
        return self._drag_preview_valid

    def set_duration(self, duration_ms: int) -> None:
        self._duration_ms = max(0, duration_ms)
        self._reset_drag_state()
        self._set_hovered_boundary(None)
        self.update()

    def set_position(self, position_ms: int) -> None:
        self._current_position_ms = max(0, position_ms)
        self.update()

    def set_intervals(self, intervals: List[AnnotationInterval]) -> None:
        self._intervals = intervals
        self._reset_drag_state()
        self._set_hovered_boundary(None)
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

            # Internal boundaries are shared by two intervals. Keep their
            # resting treatment subtle, then make the active handle obvious.
            for boundary_index in range(1, len(self._intervals)):
                boundary_x = self._boundary_x(boundary_index)
                hovered = boundary_index == self._hovered_boundary_index
                color = QColor("#00D1FF" if hovered else "#D0D0D0")
                painter.setPen(QPen(color, 4 if hovered else 1))
                painter.drawLine(boundary_x, 3, boundary_x, height - 4)
                if hovered:
                    painter.fillRect(boundary_x - 4, 2, 9, 6, color)
                    painter.fillRect(boundary_x - 4, height - 8, 9, 6, color)

            # Draw Playhead Needle (Red Vertical Line)
            needle_x = int((self._current_position_ms / self._duration_ms) * width)
            pen = QPen(QColor("#FF0000"), 3)
            painter.setPen(pen)
            painter.drawLine(needle_x, 0, needle_x, height)

            # Draw transient preview last so the playhead cannot hide whether
            # the proposed release is valid (cyan) or invalid (red).
            if self._drag_preview_ms is not None:
                preview_x = round(
                    (self._drag_preview_ms / self._duration_ms) * width
                )
                preview_color = QColor(
                    "#00D1FF" if self._drag_preview_valid else "#FF3B30"
                )
                painter.setPen(QPen(preview_color, 4))
                painter.drawLine(preview_x, 0, preview_x, height)

        # Draw Border
        painter.setPen(QPen(QColor("#444444"), 1))
        painter.drawRect(0, 0, width - 1, height - 1)

    def mousePressEvent(self, event) -> None:
        if self._duration_ms > 0 and event.button() == Qt.MouseButton.LeftButton:
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            click_x = event.position().x()
            boundary_index = self.boundary_index_at_x(click_x)
            if boundary_index is not None:
                original_ms = self._intervals[boundary_index].start_ms
                self._drag_boundary_index = boundary_index
                self._drag_original_ms = original_ms
                self._drag_preview_ms = original_ms
                self._drag_preview_valid = True
                self.setCursor(Qt.CursorShape.SplitHCursor)
                self.update()
                event.accept()
                return
            ratio = max(0.0, min(1.0, click_x / self.width()))
            target_ms = int(ratio * self._duration_ms)
            # Half-open intervals exclude duration_ms. Use the last real
            # millisecond only to identify a segment at the far-right edge;
            # the actual seek request may still target the video end.
            selection_ms = min(target_ms, self._duration_ms - 1)
            for index, interval in enumerate(self._intervals):
                if interval.start_ms <= selection_ms < interval.end_ms:
                    self.segment_selection_requested.emit(index, target_ms)
                    break
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self._drag_boundary_index is not None
        ):
            self._update_drag_preview(event.position().x())
            boundary_index = self._drag_boundary_index
            original_ms = self._drag_original_ms
            preview_ms = self._drag_preview_ms
            preview_valid = self._drag_preview_valid
            self._reset_drag_state()
            self._set_hovered_boundary(
                self.boundary_index_at_x(event.position().x())
            )
            if preview_ms == original_ms:
                self.boundary_drag_cancelled.emit("unchanged", original_ms)
            elif preview_valid:
                self.boundary_move_requested.emit(boundary_index, preview_ms)
            else:
                self.boundary_drag_cancelled.emit("invalid", original_ms)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_boundary_index is not None:
            self._update_drag_preview(event.position().x())
            event.accept()
            return
        self._set_hovered_boundary(self.boundary_index_at_x(event.position().x()))
        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:
        if self._drag_boundary_index is None:
            self._set_hovered_boundary(None)
        super().leaveEvent(event)

    def keyPressEvent(self, event) -> None:
        if (
            event.key() == Qt.Key.Key_Escape
            and self._drag_boundary_index is not None
        ):
            original_ms = self._drag_original_ms
            self._reset_drag_state()
            self._set_hovered_boundary(None)
            self.boundary_drag_cancelled.emit("cancelled", original_ms)
            event.accept()
            return
        super().keyPressEvent(event)

    def boundary_index_at_x(self, x_position: float) -> Optional[int]:
        """Return the nearest internal boundary within the pixel hit radius."""
        if self._duration_ms <= 0 or self.width() <= 0 or len(self._intervals) < 2:
            return None
        candidates = (
            (abs(x_position - self._boundary_x(index)), index)
            for index in range(1, len(self._intervals))
        )
        distance, boundary_index = min(candidates)
        if distance <= self.BOUNDARY_HIT_RADIUS_PX:
            return boundary_index
        return None

    def _boundary_x(self, boundary_index: int) -> int:
        boundary_ms = self._intervals[boundary_index].start_ms
        return round((boundary_ms / self._duration_ms) * self.width())

    def _set_hovered_boundary(self, boundary_index: Optional[int]) -> None:
        if boundary_index == self._hovered_boundary_index:
            return
        self._hovered_boundary_index = boundary_index
        cursor = (
            Qt.CursorShape.SplitHCursor
            if boundary_index is not None
            else Qt.CursorShape.PointingHandCursor
        )
        self.setCursor(cursor)
        self.update()

    def _update_drag_preview(self, x_position: float) -> None:
        if self._drag_boundary_index is None:
            return
        ratio = max(0.0, min(1.0, x_position / self.width()))
        preview_ms = round(ratio * self._duration_ms)
        left = self._intervals[self._drag_boundary_index - 1]
        right = self._intervals[self._drag_boundary_index]
        self._drag_preview_ms = preview_ms
        self._drag_preview_valid = left.start_ms < preview_ms < right.end_ms
        self.setCursor(Qt.CursorShape.SplitHCursor)
        self.update()
        self.boundary_preview_requested.emit(preview_ms)

    def _reset_drag_state(self) -> None:
        self._drag_boundary_index = None
        self._drag_original_ms = None
        self._drag_preview_ms = None
        self._drag_preview_valid = False
