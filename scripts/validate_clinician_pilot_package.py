"""Validate and preview the generated clinician pilot package."""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtPdf import QPdfDocument


def validate_package(package_dir: Path, zip_path: Path, preview_dir: Path) -> None:
    expected_pdfs = (
        package_dir / "00_START_HERE.pdf",
        package_dir / "02_Guides_and_Protocol" / "01_Phase_Annotator_User_Guide.pdf",
        package_dir / "02_Guides_and_Protocol" / "02_Draft_Annotation_Protocol.pdf",
    )
    preview_dir.mkdir(parents=True, exist_ok=True)
    for pdf_path in expected_pdfs:
        document = QPdfDocument()
        error = document.load(str(pdf_path))
        if error != QPdfDocument.Error.None_ or document.pageCount() < 1:
            raise ValueError(f"Invalid PDF: {pdf_path} ({error})")
        source = document.render(0, QSize(1240, 1754))
        canvas = QImage(1240, 1754, QImage.Format.Format_RGB32)
        canvas.fill(Qt.GlobalColor.white)
        painter = QPainter(canvas)
        painter.drawImage(0, 0, source)
        painter.end()
        canvas.save(str(preview_dir / f"{pdf_path.stem}.png"))
        print(f"pdf={pdf_path.name} pages={document.pageCount()}")

    clip_root = package_dir / "03_Example_Clips"
    index = (clip_root / "OPEN_CLIP_LIBRARY.html").read_text(encoding="utf-8")
    media_links = set(re.findall(r'(?:src|href)="(clips/[^"]+\.mp4)"', index))
    missing = [
        relative for relative in media_links if not (clip_root / relative).is_file()
    ]
    if len(media_links) != 18 or missing:
        raise ValueError(
            f"Clip index validation failed: links={len(media_links)}, missing={missing}"
        )

    videos = list((package_dir / "04_Local_Study" / "Videos_to_annotate").glob("*.mp4"))
    sidecars = list(
        (package_dir / "04_Local_Study" / "Videos_to_annotate").glob(
            "*.phase-annotations.json"
        )
    )
    if len(videos) != 2 or sidecars:
        raise ValueError(
            f"Local-study validation failed: videos={len(videos)}, sidecars={len(sidecars)}"
        )

    with zipfile.ZipFile(zip_path) as archive:
        bad_member = archive.testzip()
        names = archive.namelist()
    if bad_member is not None:
        raise ValueError(f"ZIP integrity failure: {bad_member}")
    if not any(name.endswith("/01_Application/PhaseAnnotator.exe") for name in names):
        raise ValueError("ZIP does not contain PhaseAnnotator.exe")
    print(f"clips={len(media_links)} videos={len(videos)} zip_entries={len(names)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("preview_dir", type=Path)
    args = parser.parse_args()
    validate_package(args.package_dir, args.zip_path, args.preview_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
