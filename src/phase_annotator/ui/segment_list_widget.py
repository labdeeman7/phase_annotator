from typing import List, Optional
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QFrame
)

from phase_annotator.domain.models import AnnotationInterval
from phase_annotator.domain.ontology import PhaseOntology, Phase
from phase_annotator.domain.time_utils import format_timecode, ms_to_frame


class SegmentCardWidget(QFrame):
    """Custom styled card widget representing a single surgical segment (LosslessCut style)."""

    def __init__(self, interval: AnnotationInterval, phase: Optional[Phase], fps: float = 30.0, parent=None):
        super().__init__(parent)
        
        color_hex = phase.color_hex if phase else "#3B82F6"
        phase_name = phase.name if phase else f"Phase {interval.phase_id}"

        # Card Frame Styling
        self.setStyleSheet(f"""
            SegmentCardWidget {{
                background-color: #262626;
                border: 1px solid #383838;
                border-left: 5px solid {color_hex};
                border-radius: 6px;
            }}
            SegmentCardWidget:hover {{
                background-color: #333333;
                border-color: {color_hex};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        # Header Row: Badge + Phase Name
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        badge_label = QLabel(f" {interval.phase_id} ", self)
        badge_label.setStyleSheet(f"""
            background-color: {color_hex};
            color: #FFFFFF;
            font-weight: bold;
            border-radius: 10px;
            padding: 2px 6px;
        """)

        title_label = QLabel(phase_name, self)
        title_label.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 13px;")

        header_layout.addWidget(badge_label)
        header_layout.addWidget(title_label, stretch=1)
        layout.addLayout(header_layout)

        # Timecode Span Row
        start_code = format_timecode(interval.start_ms)
        end_code = format_timecode(interval.end_ms)
        timecode_label = QLabel(f"{start_code}  ➔  {end_code}", self)
        timecode_label.setStyleSheet("color: #00D1FF; font-family: monospace; font-size: 12px; font-weight: 500;")
        layout.addWidget(timecode_label)

        # Subtext Row: Duration & Frames
        duration_sec = interval.duration_ms / 1000.0
        start_frame = ms_to_frame(interval.start_ms, fps)
        end_frame = ms_to_frame(interval.end_ms, fps)
        total_frames = max(0, end_frame - start_frame)
        subtext_label = QLabel(f"Duration: {duration_sec:.3f}s  |  {interval.duration_ms} ms, {total_frames} frames", self)
        subtext_label.setStyleSheet("color: #AAAAAA; font-size: 11px;")
        layout.addWidget(subtext_label)

        if interval.notes:
            notes_label = QLabel(f"Note: {interval.notes}", self)
            notes_label.setStyleSheet("color: #F59E0B; font-size: 11px; font-style: italic;")
            layout.addWidget(notes_label)


class SegmentListWidget(QWidget):
    """Segment card list view displaying surgical phase annotations."""

    # Emitted when annotator clicks a segment card (carries start_ms)
    seek_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header Title
        title_label = QLabel("Annotated Segments", self)
        title_label.setStyleSheet("color: #EEEEEE; font-weight: bold; font-size: 14px; padding: 4px;")
        layout.addWidget(title_label)

        # List Widget
        self._list_widget = QListWidget(self)
        self._list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1A1A1A;
                border: 1px solid #333333;
                border-radius: 4px;
                outline: none;
            }
            QListWidget::item {
                margin: 4px 6px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #2D3748;
            }
        """)
        self._list_widget.itemClicked.connect(self._on_item_clicked)
        self._list_widget.itemDoubleClicked.connect(self._on_item_clicked)
        layout.addWidget(self._list_widget)

        self._ontology = PhaseOntology.default_appendectomy()
        self._intervals: List[AnnotationInterval] = []
        self._fps: float = 30.0

    def set_ontology(self, ontology: PhaseOntology) -> None:
        self._ontology = ontology

    def set_fps(self, fps: float) -> None:
        self._fps = fps

    def set_intervals(self, intervals: List[AnnotationInterval]) -> None:
        """Populates segment cards for each AnnotationInterval domain model."""
        self._intervals = intervals
        self._list_widget.clear()

        for interval in intervals:
            try:
                phase = self._ontology.get_phase_by_id(interval.phase_id)
            except KeyError:
                phase = None

            card_widget = SegmentCardWidget(interval, phase, fps=self._fps, parent=self)
            
            list_item = QListWidgetItem(self._list_widget)
            list_item.setSizeHint(card_widget.sizeHint())
            
            self._list_widget.addItem(list_item)
            self._list_widget.setItemWidget(list_item, card_widget)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        row = self._list_widget.row(item)
        if 0 <= row < len(self._intervals):
            start_ms = self._intervals[row].start_ms
            self.seek_requested.emit(start_ms)
