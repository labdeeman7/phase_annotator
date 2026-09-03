from typing import List, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from phase_annotator.domain.models import AnnotationInterval
from phase_annotator.domain.ontology import Phase, PhaseOntology
from phase_annotator.domain.time_utils import format_timecode, ms_to_frame


class SegmentCardWidget(QFrame):
    """Card showing one annotated interval and its navigation state."""

    def __init__(
        self,
        interval: AnnotationInterval,
        phase: Optional[Phase],
        fps: float = 30.0,
        parent=None,
    ):
        super().__init__(parent)
        self._color_hex = phase.color_hex if phase else "#3B82F6"
        self._is_selected = False
        self._is_active = False
        phase_name = phase.name if phase else f"Phase {interval.phase_id}"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        badge_label = QLabel(f" {interval.phase_id} ", self)
        badge_label.setStyleSheet(
            f"background-color: {self._color_hex}; color: #FFFFFF; "
            "font-weight: bold; border-radius: 10px; padding: 2px 6px;"
        )
        title_label = QLabel(phase_name, self)
        title_label.setStyleSheet(
            "color: #FFFFFF; font-weight: bold; font-size: 13px;"
        )
        header_layout.addWidget(badge_label)
        header_layout.addWidget(title_label, stretch=1)
        layout.addLayout(header_layout)

        start_code = format_timecode(interval.start_ms)
        end_code = format_timecode(interval.end_ms)
        timecode_label = QLabel(f"{start_code}  →  {end_code}", self)
        timecode_label.setStyleSheet(
            "color: #00D1FF; font-family: monospace; font-size: 12px; "
            "font-weight: 500;"
        )
        layout.addWidget(timecode_label)

        duration_sec = interval.duration_ms / 1000.0
        start_frame = ms_to_frame(interval.start_ms, fps)
        end_frame = ms_to_frame(interval.end_ms, fps)
        total_frames = max(0, end_frame - start_frame)
        subtext_label = QLabel(
            f"Duration: {duration_sec:.3f}s  |  {interval.duration_ms} ms, "
            f"{total_frames} frames",
            self,
        )
        subtext_label.setStyleSheet("color: #AAAAAA; font-size: 11px;")
        layout.addWidget(subtext_label)

        if interval.notes:
            notes_label = QLabel(f"Note: {interval.notes}", self)
            notes_label.setStyleSheet(
                "color: #F59E0B; font-size: 11px; font-style: italic;"
            )
            layout.addWidget(notes_label)

        self._update_style()

    def set_selection_state(self, *, selected: bool, active: bool) -> None:
        self._is_selected = selected
        self._is_active = active
        self._update_style()

    def _update_style(self) -> None:
        # Selection wins visually when the selected and active segment coincide.
        if self._is_selected:
            border_color, border_width, background = "#00D1FF", 3, "#263845"
        elif self._is_active:
            border_color, border_width, background = "#FFFFFF", 2, "#303030"
        else:
            border_color, border_width, background = "#383838", 1, "#262626"

        self.setStyleSheet(
            f"""
            SegmentCardWidget {{
                background-color: {background};
                border: {border_width}px solid {border_color};
                border-left: 5px solid {self._color_hex};
                border-radius: 6px;
            }}
            SegmentCardWidget:hover {{
                background-color: #333333;
                border-color: #00D1FF;
            }}
            """
        )


class SegmentListWidget(QWidget):
    """Segment cards with synchronized selected and playhead-active states."""

    seek_requested = Signal(int)
    segment_selected = Signal(int)

    def __init__(self, parent=None, *, ontology: PhaseOntology):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("Annotated Segments", self)
        title_label.setStyleSheet(
            "color: #EEEEEE; font-weight: bold; font-size: 14px; padding: 4px;"
        )
        layout.addWidget(title_label)
        legend_label = QLabel("Cyan: selected  •  White: under playhead", self)
        legend_label.setStyleSheet("color: #AAAAAA; font-size: 11px; padding: 0 4px 4px;")
        layout.addWidget(legend_label)

        self._list_widget = QListWidget(self)
        self._list_widget.setStyleSheet(
            """
            QListWidget {
                background-color: #1A1A1A;
                border: 1px solid #333333;
                border-radius: 4px;
                outline: none;
            }
            QListWidget::item { margin: 4px 6px; border-radius: 6px; }
            """
        )
        self._list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._list_widget)

        self._ontology = ontology
        self._intervals: List[AnnotationInterval] = []
        self._cards: List[SegmentCardWidget] = []
        self._selected_index: Optional[int] = None
        self._active_index: Optional[int] = None
        self._fps: float = 30.0

    @property
    def selected_index(self) -> Optional[int]:
        return self._selected_index

    @property
    def active_index(self) -> Optional[int]:
        return self._active_index

    def set_ontology(self, ontology: PhaseOntology) -> None:
        self._ontology = ontology

    def set_fps(self, fps: float) -> None:
        self._fps = fps

    def set_intervals(self, intervals: List[AnnotationInterval]) -> None:
        """Rebuild cards from normalized session intervals."""
        self._intervals = intervals
        self._list_widget.clear()
        self._cards = []
        for interval in intervals:
            try:
                phase = self._ontology.get_phase_by_id(interval.phase_id)
            except KeyError:
                phase = None
            card = SegmentCardWidget(interval, phase, fps=self._fps, parent=self)
            item = QListWidgetItem(self._list_widget)
            item.setSizeHint(card.sizeHint())
            self._list_widget.addItem(item)
            self._list_widget.setItemWidget(item, card)
            self._cards.append(card)
        self.set_selected_index(self._selected_index)
        self.set_active_index(self._active_index)

    def set_selected_index(self, index: Optional[int]) -> None:
        """Mirror the application-owned selection and reveal its card."""
        if index is not None and not 0 <= index < len(self._intervals):
            index = None
        self._selected_index = index
        self._list_widget.setCurrentRow(index if index is not None else -1)
        if index is not None:
            self._list_widget.scrollToItem(self._list_widget.item(index))
        self._update_card_states()

    def set_active_index(self, index: Optional[int]) -> None:
        """Mark the interval under the playhead without changing selection."""
        if index is not None and not 0 <= index < len(self._intervals):
            index = None
        self._active_index = index
        self._update_card_states()

    def _update_card_states(self) -> None:
        for index, card in enumerate(self._cards):
            card.set_selection_state(
                selected=index == self._selected_index,
                active=index == self._active_index,
            )

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """Publish user intent; MainWindow owns the resulting selection."""
        row = self._list_widget.row(item)
        if 0 <= row < len(self._intervals):
            self.segment_selected.emit(row)
            self.seek_requested.emit(self._intervals[row].start_ms)
