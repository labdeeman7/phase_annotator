"""Build the offline two-video cholecystectomy clinician pilot package."""

from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QFont, QTextDocument
from PySide6.QtWidgets import QApplication


@dataclass(frozen=True)
class ClipExample:
    clip_id: str
    section: str
    description: str


CLIP_EXAMPLES = (
    ClipExample(
        "V04-B01",
        "P1 Preparation → P2 Calot triangle dissection",
        "Transition from Preparation to Calot triangle dissection: hook "
        "electrocautery enters the operative field and focused dissection begins.",
    ),
    ClipExample(
        "V14-B01",
        "P1 Preparation → P2 Calot triangle dissection",
        "Transition from Preparation to Calot triangle dissection: an energy device "
        "is positioned at the hepatocystic triangle and purposeful dissection begins.",
    ),
    ClipExample(
        "V50-B01",
        "P1 Preparation → P2 Calot triangle dissection",
        "Transition from Preparation to Calot triangle dissection: the phase changes "
        "as focused dissection of the hepatocystic triangle begins.",
    ),
    ClipExample(
        "V79-B01",
        "P1 Preparation → P2 Calot triangle dissection",
        "Transition from Preparation to Calot triangle dissection: an early, transient "
        "appearance of the energy device is not used as the boundary; the phase changes "
        "when the device returns for sustained dissection.",
    ),
    ClipExample(
        "V01-B02",
        "P2 Calot triangle dissection → P3 Clipping and cutting",
        "Transition from Calot triangle dissection to Clipping and cutting: the clip "
        "applier is introduced to occlude the cystic structures.",
    ),
    ClipExample(
        "V50-B02",
        "P2 Calot triangle dissection → P3 Clipping and cutting",
        "Transition from Calot triangle dissection to Clipping and cutting: dissection "
        "ends and the clip applier is brought into the operative field.",
    ),
    ClipExample(
        "V64-B02",
        "P2 Calot triangle dissection → P3 Clipping and cutting",
        "Transition from Calot triangle dissection to Clipping and cutting: purposeful "
        "introduction of the clip applier marks the start of cystic-structure occlusion.",
    ),
    ClipExample(
        "V68-B02",
        "P2 Calot triangle dissection → P3 Clipping and cutting",
        "Transition from Calot triangle dissection to Clipping and cutting: the phase "
        "changes when the clip applier enters for cystic-structure occlusion.",
    ),
    ClipExample(
        "V64-B03",
        "P3 Clipping and cutting → P4 Gallbladder dissection",
        "Transition from Clipping and cutting to Gallbladder dissection: division of "
        "the secured cystic structures is completed, followed by a brief visual check "
        "before separation from the liver bed begins.",
    ),
    ClipExample(
        "V68-B03",
        "P3 Clipping and cutting → P4 Gallbladder dissection",
        "Transition from Clipping and cutting to Gallbladder dissection: after the final "
        "division, a short inspection precedes dissection of the gallbladder from the "
        "liver bed.",
    ),
    ClipExample(
        "V37-B03",
        "P3 Clipping and cutting → P4 Gallbladder dissection",
        "Transition from Clipping and cutting to Gallbladder dissection: the boundary "
        "falls after final division and before the energy device is used to separate "
        "the gallbladder from the liver bed.",
    ),
    ClipExample(
        "V44-B04",
        "P4 Gallbladder dissection → P5 Gallbladder packaging",
        "Transition from Gallbladder dissection to Gallbladder packaging: separation "
        "from the liver bed is complete and attention turns to placing the specimen in "
        "a retrieval bag.",
    ),
    ClipExample(
        "V37-B04",
        "P4 Gallbladder dissection → P6 Cleaning and coagulation",
        "Transition from Gallbladder dissection to Cleaning and coagulation: separation "
        "from the liver bed ends and liver-bed inspection or haemostasis becomes the "
        "dominant task.",
    ),
    ClipExample(
        "V01-B05",
        "P5 Gallbladder packaging → P6 Cleaning and coagulation",
        "Transition from Gallbladder packaging to Cleaning and coagulation: after the "
        "specimen is contained, attention returns to liver-bed inspection and "
        "haemostasis.",
    ),
    ClipExample(
        "V14-B05",
        "P5 Gallbladder packaging → P7 Gallbladder retraction",
        "Transition from Gallbladder packaging to Gallbladder retraction (specimen "
        "extraction): the contained specimen begins sustained withdrawal from the "
        "operative field.",
    ),
    ClipExample(
        "V37-B05",
        "P6 Cleaning and coagulation → P5 Gallbladder packaging",
        "Transition from Cleaning and coagulation to Gallbladder packaging: liver-bed "
        "inspection or haemostasis ends and the retrieval bag is introduced for the "
        "specimen.",
    ),
    ClipExample(
        "V50-B05",
        "P5 Gallbladder packaging → P7 Gallbladder retraction",
        "Transition from Gallbladder packaging to Gallbladder retraction (specimen "
        "extraction): packaging is complete and sustained withdrawal of the bagged "
        "specimen begins.",
    ),
    ClipExample(
        "V64-B05",
        "P6 Cleaning and coagulation → P5 Gallbladder packaging",
        "Transition from Cleaning and coagulation to Gallbladder packaging: cleaning "
        "and haemostasis conclude, and the retrieval bag is positioned to receive the "
        "specimen.",
    ),
)


def render_markdown_pdf(
    source: Path, destination: Path, *, browser_path: Path, html_dir: Path
) -> None:
    """Convert Markdown through Qt and print browser-quality PDF with Chromium."""
    document = QTextDocument()
    document.setBaseUrl(QUrl.fromLocalFile(f"{source.parent.resolve()}/"))
    document.setDefaultFont(QFont("Arial", 10))
    document.setMarkdown(source.read_text(encoding="utf-8"))
    base_url = source.parent.resolve().as_uri() + "/"
    styles = """
    <style>
      @page { size: A4; margin: 16mm; }
      body { font-family: Arial, sans-serif; color: #18242c; font-size: 10.5pt;
             line-height: 1.42; max-width: 180mm; margin: 0 auto; }
      h1 { color: #12324a; font-size: 20pt; line-height: 1.2; margin-bottom: 8px; }
      h2 { color: #174b6b; font-size: 17pt; margin-top: 22px; page-break-after: avoid; }
      h3 { color: #245f7d; font-size: 13pt; margin-top: 18px; page-break-after: avoid; }
      blockquote { background: #eef6fa; border-left: 5px solid #1aa7d6;
                   margin: 14px 0; padding: 8px 14px; }
      table { width: 100%; border-collapse: collapse; font-size: 9.5pt; }
      th, td { border: 1px solid #aebdc5; padding: 6px; vertical-align: top; }
      th { background: #dcecf4; color: #12324a; }
      code { background: #edf1f3; padding: 1px 3px; }
      pre { background: #edf1f3; padding: 10px; white-space: pre-wrap; }
      img { max-width: 100%; height: auto; }
      a { color: #075f87; }
      li { display: list-item !important; margin-bottom: 6px; }
      li p { display: block !important; margin: 0 0 4px 0; }
    </style>
    """
    html_text = document.toHtml()
    html_text = html_text.replace(
        "</head>", f'<base href="{html.escape(base_url)}">{styles}</head>'
    )
    html_path = html_dir / f"{destination.stem}.html"
    html_path.write_text(html_text, encoding="utf-8")

    profile_dir = html_dir / f"browser-profile-{destination.stem}"
    command = [
        str(browser_path),
        "--headless=new",
        "--disable-gpu",
        "--disable-extensions",
        "--disable-background-mode",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-default-apps",
        "--disable-sync",
        "--no-first-run",
        "--no-pdf-header-footer",
        f"--user-data-dir={profile_dir}",
        f"--print-to-pdf={destination.resolve()}",
        html_path.resolve().as_uri(),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
    if not destination.is_file() or destination.stat().st_size == 0:
        raise RuntimeError(f"Browser did not create PDF: {destination}")


def find_clip(clip_root: Path, clip_id: str) -> Path:
    matches = list(clip_root.rglob(f"{clip_id}_*.mp4"))
    if len(matches) != 1:
        raise ValueError(f"Expected one clip for {clip_id}; found {len(matches)}.")
    return matches[0]


def write_clip_index(
    examples: list[tuple[ClipExample, Path]], destination: Path
) -> None:
    cards = []
    for example, clip in examples:
        filename = html.escape(clip.name)
        cards.append(
            f"""
            <article id="{html.escape(example.clip_id)}">
              <div class="heading">
                <span class="badge">{html.escape(example.clip_id)}</span>
                <strong>{html.escape(example.section)}</strong>
              </div>
              <p>{html.escape(example.description)}</p>
              <video controls preload="none" src="clips/{filename}"></video>
              <p class="fallback"><a href="clips/{filename}">Open this clip in your video player</a></p>
            </article>
            """
        )
    destination.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cholecystectomy Example Clip Library</title>
  <style>
    body {{ margin: 0; font-family: "Segoe UI", Arial, sans-serif; background: #f2f5f7; color: #18242c; }}
    header {{ background: #12324a; color: white; padding: 28px max(24px, 6vw); }}
    header h1 {{ margin: 0 0 8px; }}
    header p {{ max-width: 900px; line-height: 1.5; }}
    main {{ max-width: 1050px; margin: 24px auto; padding: 0 18px 40px; }}
    .notice {{ background: #e8f5fb; border-left: 5px solid #1aa7d6; padding: 14px 18px; margin-bottom: 22px; }}
    article {{ background: white; border: 1px solid #ccd7dd; border-radius: 10px; padding: 18px; margin: 18px 0; box-shadow: 0 2px 8px #00000012; }}
    .heading {{ display: flex; align-items: center; gap: 12px; font-size: 1.15rem; }}
    .badge {{ background: #176c91; color: white; border-radius: 6px; padding: 5px 9px; font-weight: 700; }}
    video {{ width: min(100%, 800px); max-height: 520px; background: black; display: block; margin-top: 12px; }}
    .fallback a {{ color: #075f87; font-weight: 600; }}
  </style>
</head>
<body>
  <header>
    <h1>Cholecystectomy Example Clip Library</h1>
    <p>These are one-minute clips centred on selected Cholec80 transitions. Watch the surgical activity and the coloured phase name in the top-right corner; the label changes at the supplied boundary. Apply the written task-based rule when local instruments differ.</p>
  </header>
  <main>
    <div class="notice"><strong>How to use:</strong> press Play on one example at a time. If playback inside this page does not work, select “Open this clip in your video player”. For internal research pilot use only; do not redistribute the videos.</div>
    {"".join(cards)}
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_return_note(destination: Path) -> None:
    destination.write_text(
        "Copy the two completed annotation JSON files into this folder before "
        "returning the pilot package.\n\nExpected files:\n"
        "20260505_221257.mp4.phase-annotations.json\n"
        "20260519_215628.mp4.phase-annotations.json\n",
        encoding="utf-8",
    )


def create_zip(package_dir: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", allowZip64=True) as archive:
        for path in sorted(package_dir.rglob("*")):
            if not path.is_file():
                continue
            relative = Path(package_dir.name) / path.relative_to(package_dir)
            compression = (
                zipfile.ZIP_STORED
                if path.suffix.casefold() in {".mp4", ".zip"}
                else zipfile.ZIP_DEFLATED
            )
            archive.write(path, relative.as_posix(), compress_type=compression)


def build_package(
    repository: Path, output_dir: Path, zip_path: Path, *, browser_path: Path
) -> None:
    if not browser_path.is_file():
        raise FileNotFoundError(browser_path)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    html_dir = output_dir.parent / ".clinician-package-pdf-build"
    if html_dir.exists():
        shutil.rmtree(html_dir)
    html_dir.mkdir()

    app_dir = output_dir / "01_Application"
    documents_dir = output_dir / "02_Guides_and_Protocol"
    clips_dir = output_dir / "03_Example_Clips"
    clip_media_dir = clips_dir / "clips"
    local_dir = output_dir / "04_Local_Study"
    videos_dir = local_dir / "Videos_to_annotate"
    returns_dir = local_dir / "Return_annotations_here"
    for directory in (documents_dir, clip_media_dir, videos_dir, returns_dir):
        directory.mkdir(parents=True, exist_ok=True)

    shutil.copytree(repository / "dist" / "PhaseAnnotator", app_dir, dirs_exist_ok=True)

    source_documents = (
        (
            repository / "docs" / "studies" / "CLINICIAN_PACKAGE_START_HERE.md",
            output_dir / "00_START_HERE.pdf",
        ),
        (
            repository / "docs" / "user" / "USER_GUIDE.md",
            documents_dir / "01_Phase_Annotator_User_Guide.pdf",
        ),
        (
            repository / "docs" / "studies" / "INFERRED_CHOLEC80_RULES.md",
            documents_dir / "02_Draft_Annotation_Protocol.pdf",
        ),
    )
    try:
        for source, destination in source_documents:
            render_markdown_pdf(
                source,
                destination,
                browser_path=browser_path,
                html_dir=html_dir,
            )
    finally:
        shutil.rmtree(html_dir, ignore_errors=True)

    clip_root = repository / "test_dataset" / "reference_cases" / "transition_clips"
    copied_examples = []
    for example in CLIP_EXAMPLES:
        source = find_clip(clip_root, example.clip_id)
        destination = clip_media_dir / source.name
        shutil.copy2(source, destination)
        copied_examples.append((example, destination))
    write_clip_index(copied_examples, clips_dir / "OPEN_CLIP_LIBRARY.html")

    source_video_dir = (
        repository
        / "test_dataset"
        / "clinician_pilot"
        / "Phase_Annotator_Cholecystectomy_0.1_Pilot"
        / "04_Local_Study"
        / "Videos_to_annotate"
    )
    for filename in ("20260505_221257.mp4", "20260519_215628.mp4"):
        source = source_video_dir / filename
        if not source.is_file():
            raise FileNotFoundError(source)
        shutil.copy2(source, videos_dir / filename)
    write_return_note(returns_dir / "COPY_COMPLETED_JSON_FILES_HERE.txt")

    create_zip(output_dir, zip_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--zip-path", type=Path, required=True)
    parser.add_argument("--browser-path", type=Path, required=True)
    args = parser.parse_args()

    repository = args.repository.resolve()
    output_dir = args.output_dir.resolve()
    zip_path = args.zip_path.resolve()
    browser_path = args.browser_path.resolve()
    if output_dir == repository or repository not in output_dir.parents:
        parser.error("output-dir must be a dedicated directory inside the repository")
    if zip_path == repository or repository not in zip_path.parents:
        parser.error("zip-path must be a file inside the repository")
    if zip_path == output_dir or output_dir in zip_path.parents:
        parser.error("zip-path must be outside output-dir")

    QApplication.instance() or QApplication([])
    build_package(repository, output_dir, zip_path, browser_path=browser_path)
    print(output_dir)
    print(zip_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
