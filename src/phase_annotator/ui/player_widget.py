from pathlib import Path
from typing import Optional
from PySide6.QtCore import Signal, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QWidget, QVBoxLayout


class VideoPlayerWidget(QWidget):
    """Wrapper around Qt QMediaPlayer & QVideoWidget with surgical video playback signals."""

    # Custom signals
    position_changed = Signal(int)  # Emits current position in ms
    duration_changed = Signal(int)  # Emits video duration in ms
    playback_state_changed = Signal(bool)  # True while actively playing

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)

        self._video_widget = QVideoWidget(self)
        self._player.setVideoOutput(self._video_widget)

        self._fps: float = 30.0  # Default FPS assumption until loaded

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._video_widget)

        # Connect signals
        self._player.positionChanged.connect(self.position_changed.emit)
        self._player.durationChanged.connect(self.duration_changed.emit)
        self._player.playbackStateChanged.connect(self._forward_playback_state)

    @property
    def fps(self) -> float:
        return self._fps

    @fps.setter
    def fps(self, value: float) -> None:
        if value > 0:
            self._fps = value

    @property
    def position_ms(self) -> int:
        """Current playback position without exposing the internal Qt player."""
        return self._player.position()

    @property
    def duration_ms(self) -> int:
        """Loaded media duration without exposing the internal Qt player."""
        return self._player.duration()

    @property
    def is_playing(self) -> bool:
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def load_video(self, video_path: Path) -> None:
        """Loads a video file into the media player."""
        url = QUrl.fromLocalFile(str(video_path))
        self._player.setSource(url)

    def play(self) -> None:
        self._player.play()

    def pause(self) -> None:
        self._player.pause()

    def toggle_play(self) -> None:
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def seek_ms(self, position_ms: int) -> None:
        """Seeks to a specific timestamp in milliseconds."""
        self._player.setPosition(position_ms)

    def step_frames(self, frame_count: int) -> None:
        """Steps forward or backward by N frames based on current FPS setting."""
        ms_per_frame = 1000.0 / self._fps
        target_ms = int(self.position_ms + (frame_count * ms_per_frame))
        target_ms = max(0, min(self.duration_ms, target_ms))
        self.seek_ms(target_ms)

    def _forward_playback_state(
        self, state: QMediaPlayer.PlaybackState
    ) -> None:
        self.playback_state_changed.emit(
            state == QMediaPlayer.PlaybackState.PlayingState
        )
