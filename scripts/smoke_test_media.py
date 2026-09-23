"""Manual Qt media smoke test; never reads or hashes video content directly."""

import argparse
import json
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from phase_annotator.config import load_default_ontology
from phase_annotator.ui.main_window import MainWindow


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Load one local video through the application's Qt pipeline."
    )
    parser.add_argument("video", type=Path)
    parser.add_argument("--timeout-ms", type=int, default=15_000)
    args = parser.parse_args()
    if args.timeout_ms <= 0:
        parser.error("--timeout-ms must be positive")

    app = QApplication.instance() or QApplication(sys.argv[:1])
    window = MainWindow(ontology=load_default_ontology())
    result = {"exit_code": 2}

    def finish_success(duration_ms: int) -> None:
        # Allow late track metadata to arrive after the duration signal.
        def report() -> None:
            video_info = window._session.video_info
            print(
                json.dumps(
                    {
                        "video": args.video.name,
                        "duration_ms": duration_ms,
                        "width": video_info.width,
                        "height": video_info.height,
                        "fps": video_info.fps,
                        "fps_source": video_info.fps_source,
                        "frame_rate_mode": video_info.frame_rate_mode,
                        "frame_numbers_are_estimated": (
                            video_info.frame_numbers_are_estimated
                        ),
                        "interval_count": len(window._session.intervals),
                    },
                    sort_keys=True,
                )
            )
            result["exit_code"] = 0
            app.quit()

        if duration_ms > 0:
            QTimer.singleShot(500, report)

    def finish_error(message: str) -> None:
        # Avoid printing absolute local paths that a backend may include.
        safe_message = message.replace(str(args.video.resolve()), "<video>")
        print(
            f"Media load failed for {args.video.name}: {safe_message}", file=sys.stderr
        )
        result["exit_code"] = 1
        app.quit()

    def finish_timeout() -> None:
        print(f"Media load timed out for {args.video.name}", file=sys.stderr)
        app.quit()

    window._player_widget.duration_changed.connect(finish_success)
    window._player_widget.media_error.connect(finish_error)
    QTimer.singleShot(args.timeout_ms, finish_timeout)
    window._load_video(args.video)
    if window._media_load_failed:
        QTimer.singleShot(
            0,
            lambda: finish_error("The file is missing or unreadable."),
        )
    app.exec()
    window.close()
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
