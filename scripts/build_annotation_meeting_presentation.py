"""Build the OAUTHC clinician/student annotation meeting presentation."""

from __future__ import annotations

import argparse
from pathlib import Path

import pymupdf
from PIL import Image, ImageChops
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Inches, Pt

NAVY = RGBColor(12, 27, 42)
PANEL = RGBColor(23, 44, 62)
PANEL_LIGHT = RGBColor(235, 243, 247)
WHITE = RGBColor(250, 252, 253)
TEXT = RGBColor(26, 42, 54)
MUTED = RGBColor(87, 111, 126)
CYAN = RGBColor(20, 184, 220)
BLUE = RGBColor(59, 130, 246)
GREEN = RGBColor(16, 185, 129)
AMBER = RGBColor(245, 158, 11)
RED = RGBColor(239, 68, 68)
PURPLE = RGBColor(139, 92, 246)
PINK = RGBColor(236, 72, 153)
GREY = RGBColor(100, 116, 139)

PHASES = (
    ("P1", "Preparation", BLUE),
    ("P2", "Calot triangle dissection", GREEN),
    ("P3", "Clipping and cutting", AMBER),
    ("P4", "Gallbladder dissection", RED),
    ("P5", "Gallbladder packaging", PURPLE),
    ("P6", "Cleaning and coagulation", PINK),
    ("P7", "Specimen extraction", GREY),
)


def add_text(
    slide,
    text: str,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    size: int = 24,
    color: RGBColor = TEXT,
    bold: bool = False,
    align=PP_ALIGN.LEFT,
    font: str = "Aptos",
    margin: float = 0.06,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.margin_left = Inches(margin)
    frame.margin_right = Inches(margin)
    frame.margin_top = Inches(margin)
    frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    frame.word_wrap = True
    frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def add_box(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fill: RGBColor = PANEL_LIGHT,
    line: RGBColor | None = None,
    radius: bool = True,
):
    kind = (
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE
        if radius
        else MSO_AUTO_SHAPE_TYPE.RECTANGLE
    )
    shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line or fill
    return shape


def set_background(slide, color: RGBColor = WHITE) -> None:
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def add_title(slide, title: str, kicker: str | None = None) -> None:
    if kicker:
        add_text(
            slide, kicker.upper(), 0.65, 0.25, 11.8, 0.3, size=10, color=CYAN, bold=True
        )
    add_text(
        slide,
        title,
        0.65,
        0.58 if kicker else 0.35,
        12.0,
        0.65,
        size=28,
        color=NAVY,
        bold=True,
    )
    line = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(0.65),
        Inches(1.24),
        Inches(1.0),
        Inches(0.055),
    )
    line.fill.solid()
    line.fill.fore_color.rgb = CYAN
    line.line.color.rgb = CYAN


def add_footer(slide, number: int, citation: str | None = None) -> None:
    if citation:
        add_text(slide, citation, 0.7, 7.12, 11.7, 0.2, size=8, color=MUTED)
    add_text(
        slide,
        str(number),
        12.35,
        7.1,
        0.35,
        0.2,
        size=9,
        color=MUTED,
        align=PP_ALIGN.RIGHT,
    )


def add_section_divider(slide, number: str, title: str, subtitle: str) -> None:
    """Create a quiet visual break between the meeting's major conversations."""
    add_text(slide, number, 0.85, 0.75, 1.2, 0.55, size=18, color=CYAN, bold=True)
    add_text(slide, title, 0.85, 2.05, 11.5, 1.0, size=38, color=WHITE, bold=True)
    add_text(
        slide,
        subtitle,
        0.9,
        3.35,
        10.8,
        1.0,
        size=23,
        color=RGBColor(180, 207, 222),
    )
    add_box(slide, 0.9, 5.2, 2.0, 0.09, fill=CYAN, radius=False)


def add_bullets(
    slide,
    bullets: list[str],
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    size: int = 22,
    color: RGBColor = TEXT,
) -> None:
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    for index, item in enumerate(bullets):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = item
        paragraph.level = 0
        paragraph.font.name = "Aptos"
        paragraph.font.size = Pt(size)
        paragraph.font.color.rgb = color
        paragraph.space_after = Pt(12)
        paragraph.text = f"•  {item}"


def add_arrow(
    slide, x: float, y: float, w: float = 0.55, h: float = 0.32, color: RGBColor = CYAN
) -> None:
    arrow = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = color
    arrow.line.color.rgb = color


def crop_pdf(
    pdf_path: Path,
    page_number: int,
    clip: tuple[float, float, float, float],
    output: Path,
    *,
    scale: float = 3.0,
) -> None:
    document = pymupdf.open(pdf_path)
    page = document[page_number]
    pixmap = page.get_pixmap(
        matrix=pymupdf.Matrix(scale, scale),
        clip=pymupdf.Rect(*clip),
        alpha=False,
    )
    pixmap.save(output)


def trim_whitespace(path: Path, padding: int = 10) -> None:
    image = Image.open(path).convert("RGB")
    background = Image.new("RGB", image.size, "white")
    difference = ImageChops.difference(image, background)
    bbox = difference.getbbox()
    if bbox:
        left, top, right, bottom = bbox
        image.crop(
            (
                max(0, left - padding),
                max(0, top - padding),
                min(image.width, right + padding),
                min(image.height, bottom + padding),
            )
        ).save(path)


def add_picture_contain(
    slide, path: Path, x: float, y: float, w: float, h: float
) -> None:
    image = Image.open(path)
    ratio = image.width / image.height
    box_ratio = w / h
    if ratio > box_ratio:
        actual_w = w
        actual_h = w / ratio
        actual_x = x
        actual_y = y + (h - actual_h) / 2
    else:
        actual_h = h
        actual_w = h * ratio
        actual_x = x + (w - actual_w) / 2
        actual_y = y
    slide.shapes.add_picture(
        str(path),
        Inches(actual_x),
        Inches(actual_y),
        Inches(actual_w),
        Inches(actual_h),
    )


def prepare_assets(source_dir: Path, asset_dir: Path) -> dict[str, Path]:
    asset_dir.mkdir(parents=True, exist_ok=True)
    assets = {
        "real_world_ribbons": asset_dir / "real_world_phase_ribbons.png",
        "real_world_durations": asset_dir / "real_world_phase_durations.png",
        "tecno": asset_dir / "tecno_architecture.png",
        "phase_annotator": asset_dir / "phase_annotator_main_window.png",
    }
    crop_pdf(
        source_dir / "real_world.pdf",
        1,
        (145, 520, 470, 710),
        assets["real_world_ribbons"],
    )
    crop_pdf(
        source_dir / "real_world.pdf",
        6,
        (105, 45, 515, 285),
        assets["real_world_durations"],
    )
    crop_pdf(source_dir / "tecno.pdf", 2, (90, 55, 535, 260), assets["tecno"])
    for path in (
        assets["real_world_ribbons"],
        assets["real_world_durations"],
        assets["tecno"],
    ):
        trim_whitespace(path)
    return assets


def build_presentation(assets: dict[str, Path], output: Path) -> None:
    presentation = Presentation()
    presentation.slide_width = Inches(13.333)
    presentation.slide_height = Inches(7.5)
    blank = presentation.slide_layouts[6]
    slide_number = 0

    def new_slide(
        title: str | None = None, kicker: str | None = None, *, dark: bool = False
    ):
        nonlocal slide_number
        slide_number += 1
        slide = presentation.slides.add_slide(blank)
        set_background(slide, NAVY if dark else WHITE)
        if title:
            add_title(slide, title, kicker)
        return slide

    # 1
    slide = new_slide(dark=True)
    add_text(
        slide,
        "SURGICAL WORKFLOW • OAUTHC",
        0.8,
        0.65,
        8.0,
        0.35,
        size=12,
        color=CYAN,
        bold=True,
    )
    add_text(
        slide,
        "Teaching AI what is\nhappening during surgery",
        0.8,
        1.25,
        7.7,
        1.55,
        size=36,
        color=WHITE,
        bold=True,
    )
    add_text(
        slide,
        "Cholecystectomy phase annotation, domain shift and the TeCNO + HMM study",
        0.85,
        3.05,
        7.3,
        0.8,
        size=20,
        color=RGBColor(190, 211, 224),
    )
    add_box(slide, 8.65, 0.8, 3.85, 5.6, fill=PANEL, line=RGBColor(44, 73, 94))
    y = 1.25
    for phase_id, name, color in PHASES:
        add_box(slide, 9.0, y, 0.5, 0.42, fill=color, radius=True)
        add_text(
            slide,
            phase_id,
            9.02,
            y + 0.02,
            0.45,
            0.35,
            size=12,
            color=WHITE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_text(slide, name, 9.7, y, 2.45, 0.42, size=15, color=WHITE)
        y += 0.69
    add_text(
        slide,
        "OAUTHC annotation discussion • 17 October 2026",
        0.85,
        6.75,
        8.0,
        0.3,
        size=11,
        color=RGBColor(153, 181, 198),
    )

    slide = new_slide(dark=True)
    add_section_divider(
        slide,
        "PART 1",
        "Introduction",
        "What phase recognition is, why it can be useful, and where Cholec80 fits.",
    )

    # 2
    slide = new_slide("What we need to achieve today", "Purpose")
    items = [
        ("UNDERSTAND", "Why surgical workflow labels matter", BLUE),
        ("AGREE", "How we define difficult boundaries", GREEN),
        ("PRACTISE", "How to annotate, review and correct", AMBER),
        ("CONNECT", "How 26 OAUTHC videos support an AI experiment", PURPLE),
    ]
    for i, (head, body, color) in enumerate(items):
        x = 0.85 + (i % 2) * 6.1
        y = 1.65 + (i // 2) * 2.35
        add_box(slide, x, y, 5.55, 1.85, fill=PANEL_LIGHT, line=RGBColor(204, 220, 229))
        add_box(slide, x + 0.25, y + 0.32, 1.25, 0.42, fill=color)
        add_text(
            slide,
            head,
            x + 0.27,
            y + 0.34,
            1.2,
            0.34,
            size=10,
            color=WHITE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_text(
            slide, body, x + 0.25, y + 0.86, 4.95, 0.65, size=21, color=NAVY, bold=True
        )
    add_footer(slide, slide_number)

    # 3
    slide = new_slide("An operation is also a timeline", "The basic idea")
    add_text(slide, "Video", 0.8, 1.65, 1.0, 0.4, size=17, color=MUTED, bold=True)
    x = 1.75
    widths = [1.8, 2.15, 1.55, 2.1, 1.2, 1.45, 1.15]
    for (phase_id, _, color), width in zip(PHASES, widths, strict=True):
        add_box(slide, x, 1.55, width, 0.62, fill=color, radius=False)
        add_text(
            slide,
            phase_id,
            x,
            1.63,
            width,
            0.4,
            size=14,
            color=WHITE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        x += width
    add_text(slide, "0 min", 1.75, 2.25, 1.0, 0.3, size=11, color=MUTED)
    add_text(
        slide, "End", 11.75, 2.25, 0.7, 0.3, size=11, color=MUTED, align=PP_ALIGN.RIGHT
    )
    add_text(
        slide, "A phase answers:", 0.9, 3.15, 3.0, 0.45, size=20, color=NAVY, bold=True
    )
    add_box(slide, 0.9, 3.75, 5.15, 1.35, fill=NAVY)
    add_text(
        slide,
        "“What is the dominant surgical objective at this time?”",
        1.2,
        3.97,
        4.55,
        0.8,
        size=24,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_text(slide, "Not simply:", 6.6, 3.15, 2.5, 0.45, size=20, color=NAVY, bold=True)
    add_box(
        slide,
        6.6,
        3.75,
        5.15,
        1.35,
        fill=RGBColor(249, 235, 235),
        line=RGBColor(244, 183, 183),
    )
    add_text(
        slide,
        "“Which instrument can I see?”",
        7.05,
        3.97,
        4.25,
        0.8,
        size=24,
        color=RED,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "The timeline turns a long video into clinically meaningful sections.",
        1.2,
        5.75,
        10.9,
        0.55,
        size=24,
        color=CYAN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    # 4
    slide = new_slide("Why recognise surgical workflow?", "Clinical motivation")
    motivations = [
        ("FIND", "Navigate directly to a phase in a long video", BLUE),
        ("TEACH", "Retrieve comparable examples for training and review", GREEN),
        ("MEASURE", "Study phase duration, workflow and delays", AMBER),
        ("SUPPORT", "Give future AI systems the current surgical context", PURPLE),
    ]
    for i, (head, body, color) in enumerate(motivations):
        x = 0.8 + i * 3.08
        add_box(
            slide, x, 1.65, 2.72, 3.65, fill=PANEL_LIGHT, line=RGBColor(205, 220, 229)
        )
        add_box(slide, x + 0.85, 2.0, 1.0, 1.0, fill=color)
        add_text(
            slide,
            head,
            x + 0.15,
            3.25,
            2.42,
            0.42,
            size=16,
            color=color,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_text(
            slide,
            body,
            x + 0.25,
            3.85,
            2.22,
            1.05,
            size=17,
            color=NAVY,
            align=PP_ALIGN.CENTER,
        )
    add_box(slide, 1.35, 5.65, 10.65, 0.75, fill=NAVY)
    add_text(
        slide,
        "Phase recognition is foundational context—not yet a clinical decision-maker.",
        1.55,
        5.79,
        10.25,
        0.45,
        size=21,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(
        slide,
        slide_number,
        "Clinical applications: Hashimoto et al., Ann Surg 2022; Mascagni et al., npj Digit Med 2022.",
    )

    slide = new_slide("A practical clinical scenario", "Beyond one operation")
    add_box(slide, 0.8, 1.55, 3.55, 4.55, fill=NAVY)
    add_text(
        slide,
        "A trainee wants to review how difficult Calot dissections were approached across many long operations.",
        1.15,
        2.05,
        2.85,
        2.1,
        size=23,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_arrow(slide, 4.65, 3.25, 0.8, 0.45)
    uses = [
        ("Without phases", "Open every video and search manually", RED),
        ("With phases", "Retrieve relevant sections for teaching or review", GREEN),
        ("Later", "Give safety and decision-support research workflow context", PURPLE),
    ]
    for i, (head, body, color) in enumerate(uses):
        y = 1.45 + i * 1.65
        add_box(slide, 5.75, y, 6.25, 1.25, fill=PANEL_LIGHT, line=color)
        add_text(
            slide, head, 6.05, y + 0.18, 1.55, 0.4, size=17, color=color, bold=True
        )
        add_text(slide, body, 7.7, y + 0.14, 3.95, 0.72, size=17, color=NAVY)
    add_text(
        slide,
        "The same principle applies to appendectomy, colorectal surgery and other procedures once their phases are defined.",
        1.1,
        6.45,
        11.1,
        0.42,
        size=19,
        color=CYAN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    slide = new_slide("What is Cholec80?", "The benchmark we are comparing with")
    add_box(slide, 0.85, 1.55, 4.0, 4.75, fill=NAVY)
    add_text(
        slide,
        "80",
        1.35,
        1.95,
        3.0,
        1.0,
        size=48,
        color=CYAN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "laparoscopic cholecystectomy videos",
        1.25,
        3.0,
        3.2,
        1.0,
        size=23,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "Recorded in Strasbourg, France\nand labelled with seven operative phases",
        1.25,
        4.35,
        3.2,
        1.0,
        size=18,
        color=RGBColor(190, 211, 224),
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide, "Why it matters", 5.45, 1.65, 5.8, 0.5, size=25, color=NAVY, bold=True
    )
    add_bullets(
        slide,
        [
            "it made surgical phase-recognition studies comparable",
            "many influential models were trained or evaluated on it",
            "its seven-phase convention gives us a useful reference",
            "it does not represent every hospital, patient or difficult workflow",
        ],
        5.45,
        2.4,
        6.2,
        2.8,
        size=20,
    )
    add_box(slide, 5.4, 5.5, 6.4, 0.8, fill=RGBColor(255, 246, 220), line=AMBER)
    add_text(
        slide,
        "Our aim is comparison and transfer—not to treat Cholec80 as the only clinically valid interpretation.",
        5.65,
        5.66,
        5.9,
        0.45,
        size=17,
        color=RGBColor(126, 83, 0),
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(
        slide,
        slide_number,
        "Twinanda et al., IEEE TMI 2017. Cholec80 was collected at University Hospital of Strasbourg.",
    )

    # 5
    slide = new_slide("Why every annotation must be finished", "Ground truth")
    add_box(
        slide,
        0.85,
        1.55,
        5.4,
        4.7,
        fill=RGBColor(233, 248, 244),
        line=RGBColor(172, 223, 207),
    )
    add_text(
        slide,
        "A completed timeline tells us",
        1.2,
        1.9,
        4.7,
        0.5,
        size=23,
        color=GREEN,
        bold=True,
    )
    add_bullets(
        slide,
        [
            "every available moment was considered",
            "absent phases are truly absent",
            "uncertainty was labelled or noted",
            "the annotator deliberately reviewed the result",
        ],
        1.15,
        2.55,
        4.65,
        2.9,
        size=19,
    )
    add_box(
        slide,
        7.05,
        1.55,
        5.4,
        4.7,
        fill=RGBColor(253, 239, 239),
        line=RGBColor(245, 190, 190),
    )
    add_text(
        slide,
        "An unfinished timeline can mean",
        7.4,
        1.9,
        4.7,
        0.5,
        size=23,
        color=RED,
        bold=True,
    )
    add_bullets(
        slide,
        [
            "the phase was absent—or merely not labelled",
            "duration and transition statistics are wrong",
            "model evaluation is invalid",
            "the HMM learns the wrong workflow",
        ],
        7.35,
        2.55,
        4.65,
        2.9,
        size=19,
    )
    add_text(
        slide,
        "Complete does not mean perfect. It means ready for review.",
        1.2,
        6.55,
        10.9,
        0.42,
        size=24,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    # 6
    slide = new_slide(
        "Public benchmarks are cleaner than real practice", "Why local data matter"
    )
    add_picture_contain(slide, assets["real_world_ribbons"], 0.75, 1.4, 7.25, 5.25)
    add_box(slide, 8.3, 1.55, 4.2, 4.8, fill=PANEL_LIGHT, line=RGBColor(201, 219, 229))
    add_text(
        slide,
        "What this figure shows",
        8.65,
        1.9,
        3.5,
        0.45,
        size=22,
        color=NAVY,
        bold=True,
    )
    add_bullets(
        slide,
        [
            "phase lengths vary substantially",
            "phases may repeat or occur out of order",
            "additional real-world activities appear",
            "one linear workflow cannot represent every case",
        ],
        8.55,
        2.55,
        3.55,
        2.8,
        size=18,
    )
    add_text(
        slide,
        "Cholec80 is an influential benchmark—not a universal clinical standard.",
        8.6,
        5.55,
        3.5,
        0.55,
        size=16,
        color=CYAN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(
        slide,
        slide_number,
        "Figure 1: Ramesh et al., Surgical Phase Recognition: From Public Datasets to Real-World Data, Appl Sci 2022 (CC BY 4.0).",
    )

    # 7
    slide = new_slide("The same phases can have different durations", "Domain shift")
    add_picture_contain(slide, assets["real_world_durations"], 0.75, 1.45, 7.55, 4.95)
    add_box(slide, 8.55, 1.6, 3.95, 4.55, fill=NAVY)
    add_text(
        slide,
        "Real-world dataset",
        8.9,
        2.0,
        3.2,
        0.45,
        size=22,
        color=CYAN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "Median operation",
        8.95,
        2.8,
        3.1,
        0.35,
        size=16,
        color=RGBColor(184, 207, 221),
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "54 min",
        8.95,
        3.15,
        3.1,
        0.75,
        size=36,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "Cholec80 median: 34 min",
        8.95,
        4.1,
        3.1,
        0.45,
        size=18,
        color=WHITE,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "Different duration distributions change the temporal patterns a model sees.",
        8.95,
        4.85,
        3.1,
        0.85,
        size=16,
        color=RGBColor(184, 207, 221),
        align=PP_ALIGN.CENTER,
    )
    add_footer(
        slide,
        slide_number,
        "Figure 3 and reported medians: Ramesh et al., Appl Sci 2022 (CC BY 4.0).",
    )

    # 8
    slide = new_slide(
        "Greater case complexity can reduce AI performance", "Published evidence"
    )
    chart_x, chart_y, chart_w, chart_h = 0.85, 1.65, 7.4, 4.55
    add_box(
        slide,
        chart_x,
        chart_y,
        chart_w,
        chart_h,
        fill=RGBColor(247, 250, 252),
        line=RGBColor(205, 220, 229),
    )
    levels = [1, 2, 3, 4, 5]
    ai = [92, 90, 88, 81, 81]
    agreement = [92, 91, 89, 90, 90]
    for i, level in enumerate(levels):
        x = chart_x + 0.8 + i * 1.25
        baseline = chart_y + 3.75
        for offset, value, color in ((0.0, agreement[i], BLUE), (0.38, ai[i], AMBER)):
            height = (value - 70) / 25 * 3.0
            add_box(
                slide,
                x + offset,
                baseline - height,
                0.3,
                height,
                fill=color,
                radius=False,
            )
            add_text(
                slide,
                str(value),
                x + offset - 0.05,
                baseline - height - 0.35,
                0.4,
                0.3,
                size=10,
                color=color,
                bold=True,
                align=PP_ALIGN.CENTER,
            )
        add_text(
            slide,
            str(level),
            x,
            baseline + 0.08,
            0.7,
            0.3,
            size=12,
            color=MUTED,
            align=PP_ALIGN.CENTER,
        )
    add_text(
        slide,
        "Complexity level",
        3.2,
        5.82,
        2.8,
        0.3,
        size=13,
        color=MUTED,
        align=PP_ALIGN.CENTER,
    )
    add_box(slide, 1.15, 1.9, 0.28, 0.28, fill=BLUE)
    add_text(slide, "Surgeon agreement", 1.5, 1.86, 1.6, 0.32, size=11, color=MUTED)
    add_box(slide, 3.2, 1.9, 0.28, 0.28, fill=AMBER)
    add_text(slide, "AI accuracy", 3.55, 1.86, 1.2, 0.32, size=11, color=MUTED)
    add_box(slide, 8.65, 1.65, 3.8, 4.55, fill=NAVY)
    add_text(
        slide,
        "92% → 81%",
        8.95,
        2.05,
        3.2,
        0.7,
        size=34,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "AI accuracy fell as operative complexity increased.",
        9.1,
        2.95,
        2.9,
        0.9,
        size=19,
        color=WHITE,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "At the highest complexity, surgeon agreement remained about 90%.",
        9.1,
        4.15,
        2.9,
        1.0,
        size=17,
        color=RGBColor(190, 211, 224),
        align=PP_ALIGN.CENTER,
    )
    add_footer(
        slide,
        slide_number,
        "Redrawn from Figure 3A: Golany et al., Surg Endosc 2022, DOI 10.1007/s00464-022-09405-5 (CC BY 4.0).",
    )

    # 9
    slide = new_slide(
        "Domain shift: the deployment data are not the training data",
        "The research problem",
    )
    cards = [
        ("PATIENTS", "Inflammation, adhesions, anatomy and disease severity", BLUE),
        ("PRACTICE", "Technique, instruments, workflow and interruptions", GREEN),
        ("IMAGING", "Camera, resolution, smoke, lighting and recording", AMBER),
        ("LABELS", "The same phase name may use a different boundary rule", PURPLE),
    ]
    for i, (head, body, color) in enumerate(cards):
        x = 0.8 + (i % 2) * 6.15
        y = 1.55 + (i // 2) * 2.25
        add_box(slide, x, y, 5.55, 1.75, fill=PANEL_LIGHT, line=RGBColor(205, 220, 229))
        add_box(slide, x + 0.25, y + 0.25, 1.25, 0.42, fill=color)
        add_text(
            slide,
            head,
            x + 0.27,
            y + 0.27,
            1.2,
            0.32,
            size=10,
            color=WHITE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_text(
            slide, body, x + 1.75, y + 0.28, 3.45, 1.0, size=18, color=NAVY, bold=True
        )
    add_box(slide, 1.45, 6.05, 10.4, 0.62, fill=NAVY)
    add_text(
        slide,
        "A model can fail because the video looks different—or because “correct” is defined differently.",
        1.65,
        6.14,
        10.0,
        0.4,
        size=19,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    # 10
    slide = new_slide(dark=True)
    add_section_divider(
        slide,
        "PART 2",
        "Decisions for annotation",
        "Agree what the phases mean before asking people—or AI—to reproduce them.",
    )

    slide = new_slide(
        "What the first two OAUTHC annotations revealed", "Clinical observation"
    )
    add_box(
        slide,
        0.8,
        1.5,
        5.5,
        4.8,
        fill=RGBColor(236, 244, 254),
        line=RGBColor(180, 207, 244),
    )
    add_text(
        slide,
        "Cholec80-style visual cue",
        1.15,
        1.85,
        4.8,
        0.5,
        size=22,
        color=BLUE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "Hook appearance/use is often close to the P1 → P2 transition.",
        1.3,
        2.7,
        4.5,
        1.0,
        size=23,
        color=NAVY,
        align=PP_ALIGN.CENTER,
    )
    add_arrow(slide, 3.25, 4.05, 0.7, 0.4, BLUE)
    add_text(
        slide,
        "P2 may begin earlier",
        1.5,
        4.65,
        4.1,
        0.45,
        size=18,
        color=BLUE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_box(
        slide,
        7.0,
        1.5,
        5.5,
        4.8,
        fill=RGBColor(232, 248, 243),
        line=RGBColor(169, 221, 202),
    )
    add_text(
        slide,
        "OAUTHC task-based rule",
        7.35,
        1.85,
        4.8,
        0.5,
        size=22,
        color=GREEN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "Hook use for adhesiolysis and exposure remains Preparation until focused Calot dissection begins.",
        7.45,
        2.55,
        4.6,
        1.45,
        size=21,
        color=NAVY,
        align=PP_ALIGN.CENTER,
    )
    add_arrow(slide, 9.35, 4.05, 0.7, 0.4, GREEN)
    add_text(
        slide,
        "Longer P1 in difficult cases",
        7.55,
        4.65,
        4.3,
        0.45,
        size=18,
        color=GREEN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "Dr Olugbami: extensive pericholecystic adhesions require adhesiolysis before access to Calot’s area.",
        1.2,
        6.52,
        10.9,
        0.38,
        size=16,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    slide = new_slide("Compare the boundary in two real examples", "Video discussion")
    examples = [
        (
            "CHOLEC80-STYLE VISUAL CUE",
            "V04-B01: Preparation → Calot triangle dissection",
            "Watch when the hook appears and begins to be used.",
            BLUE,
            "../../../test_dataset/reference_cases/transition_clips/video04/"
            "V04-B01_P1-preparation_to_P2-calot-triangle-dissection.mp4",
        ),
        (
            "OAUTHC TASK-BASED RULE",
            "LOCAL-01-B01: Preparation → Calot triangle dissection",
            "Watch for the sustained change in operative objective.",
            GREEN,
            "../../../test_dataset/clinician_pilot/"
            "Local_Clinical_Training_Material_0.3/clips/"
            "LOCAL-01-B01_P1-preparation_to_P2-calot-triangle-dissection.mp4",
        ),
    ]
    for i, (head, filename, prompt, color, video_path) in enumerate(examples):
        x = 0.75 + i * 6.25
        add_box(slide, x, 1.55, 5.8, 4.65, fill=NAVY, line=color)
        add_text(
            slide,
            head,
            x + 0.35,
            1.9,
            5.1,
            0.45,
            size=18,
            color=color,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        play = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.ISOSCELES_TRIANGLE,
            Inches(x + 2.35),
            Inches(2.65),
            Inches(1.1),
            Inches(1.1),
        )
        play.rotation = 90
        play.fill.solid()
        play.fill.fore_color.rgb = color
        play.line.color.rgb = color
        play.click_action.hyperlink.address = video_path
        add_text(
            slide,
            filename,
            x + 0.4,
            4.1,
            5.0,
            0.7,
            size=17,
            color=WHITE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_text(
            slide,
            prompt,
            x + 0.45,
            5.0,
            4.9,
            0.65,
            size=16,
            color=RGBColor(190, 211, 224),
            align=PP_ALIGN.CENTER,
        )
    add_text(
        slide,
        "Play the two supplied one-minute clips. Pause at the displayed phase change and ask: what changed clinically?",
        1.0,
        6.45,
        11.3,
        0.42,
        size=19,
        color=CYAN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    # 11
    slide = new_slide(
        "Draft rule: Preparation → Calot triangle dissection", "Decision for annotation"
    )
    add_box(slide, 0.85, 1.45, 11.65, 1.12, fill=NAVY)
    add_text(
        slide,
        "Instrument appearance alone does not determine the phase. P2 begins when focused dissection of the hepatocystic triangle becomes the sustained operative objective.",
        1.15,
        1.65,
        11.05,
        0.72,
        size=21,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_box(
        slide,
        0.85,
        3.0,
        5.55,
        2.85,
        fill=RGBColor(237, 244, 254),
        line=RGBColor(180, 207, 244),
    )
    add_text(
        slide,
        "REMAIN IN P1",
        1.2,
        3.3,
        4.85,
        0.42,
        size=18,
        color=BLUE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_bullets(
        slide,
        [
            "adhesiolysis",
            "general exposure",
            "clearing fat/inflammatory tissue",
            "hook use outside focused Calot dissection",
        ],
        1.15,
        3.85,
        4.75,
        1.65,
        size=16,
    )
    add_box(
        slide,
        6.95,
        3.0,
        5.55,
        2.85,
        fill=RGBColor(232, 248, 243),
        line=RGBColor(169, 221, 202),
    )
    add_text(
        slide,
        "BEGIN P2",
        7.3,
        3.3,
        4.85,
        0.42,
        size=18,
        color=GREEN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_bullets(
        slide,
        [
            "sustained work in the hepatocystic triangle",
            "purposeful exposure of cystic structures",
            "clear change from general exposure to Calot-specific work",
        ],
        7.25,
        3.85,
        4.75,
        1.65,
        size=16,
    )
    add_text(
        slide,
        "Two videos suggest the pattern. The wider 26-video collection will show whether it recurs.",
        1.25,
        6.4,
        10.85,
        0.45,
        size=20,
        color=CYAN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    # 12
    slide = new_slide(
        "Long inactive periods: preserve first, analyse separately",
        "Dr Olugbami's concern",
    )
    add_text(
        slide,
        "The concern is valid",
        0.85,
        1.55,
        3.4,
        0.45,
        size=22,
        color=GREEN,
        bold=True,
    )
    add_text(
        slide,
        "Searching for clips or resolving an issue outside the field is different from a brief pause.",
        0.85,
        2.1,
        3.9,
        1.15,
        size=20,
        color=NAVY,
    )
    add_text(
        slide,
        "Why not delete it now?",
        4.95,
        1.55,
        3.4,
        0.45,
        size=22,
        color=RED,
        bold=True,
    )
    add_bullets(
        slide,
        [
            "changes timestamps and durations",
            "hides a real deployment condition",
            "may inflate model performance",
            "removes information about workflow delay",
        ],
        4.9,
        2.05,
        3.55,
        2.6,
        size=16,
    )
    add_text(
        slide,
        "Draft seven-phase rule",
        8.75,
        1.55,
        3.4,
        0.45,
        size=22,
        color=BLUE,
        bold=True,
    )
    add_bullets(
        slide,
        [
            "context clear → continue current phase",
            "unclassifiable/out of body → Undefined",
            "do not guess an invisible cause",
            "flag important long delay in a note",
        ],
        8.7,
        2.05,
        3.65,
        2.6,
        size=16,
    )
    add_box(slide, 1.0, 5.45, 11.3, 0.9, fill=NAVY)
    add_text(
        slide,
        "We can add an auxiliary idle analysis later without changing the seven primary phases.",
        1.35,
        5.66,
        10.6,
        0.48,
        size=21,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "Published complex-LC work has used separate idle and out-of-body states; this is a valid but different annotation task.",
        1.25,
        6.55,
        10.85,
        0.32,
        size=12,
        color=MUTED,
        align=PP_ALIGN.CENTER,
    )
    add_footer(
        slide,
        slide_number,
        "Idle/out-of-body precedent: Golany et al., Surg Endosc 2022, DOI 10.1007/s00464-022-09405-5.",
    )

    slide = new_slide(dark=True)
    add_section_divider(
        slide,
        "PART 3",
        "The annotation work",
        "Use the improved Phase Annotator to label, review and correct each complete timeline.",
    )

    slide = new_slide("The Phase Annotator", "Improved since the pilot")
    add_picture_contain(slide, assets["phase_annotator"], 0.7, 1.4, 11.9, 4.7)
    callouts = [
        ("Video + timeline", 1.0, BLUE),
        ("Phase choices", 9.25, GREEN),
        ("Segments to review", 9.15, PURPLE),
        ("Playback + corrections", 3.6, AMBER),
    ]
    for label, x, color in callouts:
        add_box(slide, x, 6.05, 2.55, 0.48, fill=color)
        add_text(
            slide,
            label,
            x + 0.05,
            6.1,
            2.45,
            0.32,
            size=13,
            color=WHITE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
    add_text(
        slide,
        "The updated application and training materials will be resent after this meeting. The full user guide remains the reference.",
        0.95,
        6.65,
        11.4,
        0.35,
        size=15,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    # Tool demonstration
    slide = new_slide("How Phase Annotator supports the work", "Live demonstration")
    steps = [
        ("1", "Select Cholecystectomy", BLUE),
        ("2", "Open the de-identified video", GREEN),
        ("3", "Label with hotkeys or phase buttons", AMBER),
        ("4", "Correct boundaries and notes", RED),
        ("5", "Review the complete timeline", PURPLE),
        ("6", "Mark Completed and return JSON", PINK),
    ]
    for i, (number, label, color) in enumerate(steps):
        row, col = divmod(i, 3)
        x = 0.75 + col * 4.18
        y = 1.55 + row * 2.25
        add_box(slide, x, y, 3.75, 1.65, fill=PANEL_LIGHT, line=RGBColor(205, 220, 229))
        add_box(slide, x + 0.25, y + 0.35, 0.65, 0.65, fill=color)
        add_text(
            slide,
            number,
            x + 0.27,
            y + 0.37,
            0.6,
            0.55,
            size=20,
            color=WHITE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_text(
            slide, label, x + 1.1, y + 0.25, 2.3, 0.95, size=17, color=NAVY, bold=True
        )
    add_text(
        slide,
        "LIVE: create one boundary → move it → add a note → undo → reopen the saved annotation",
        1.05,
        6.25,
        11.2,
        0.52,
        size=20,
        color=CYAN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    # 14
    slide = new_slide("Annotation is a team workflow", "Roles")
    roles = [
        (
            "STUDENTS",
            [
                "first annotate the same five cases",
                "then split assigned full timelines",
                "follow the draft rules",
                "note uncertainty",
            ],
            BLUE,
        ),
        (
            "DR OLUGBAMI",
            [
                "annotate and correct cases",
                "review the shared five cases",
                "teach difficult transitions",
                "review disagreements",
            ],
            GREEN,
        ),
        (
            "TOSIN",
            [
                "prepare de-identified videos",
                "support the software",
                "check each returned batch",
                "measure agreement and run the AI study",
            ],
            PURPLE,
        ),
    ]
    for i, (head, bullets, color) in enumerate(roles):
        x = 0.7 + i * 4.2
        add_box(
            slide, x, 1.55, 3.75, 4.75, fill=PANEL_LIGHT, line=RGBColor(202, 219, 229)
        )
        add_box(slide, x + 0.75, 1.9, 2.25, 0.48, fill=color)
        add_text(
            slide,
            head,
            x + 0.78,
            1.94,
            2.19,
            0.35,
            size=12,
            color=WHITE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_bullets(slide, bullets, x + 0.35, 2.75, 3.05, 2.75, size=16)
    add_text(
        slide,
        "Clinical review is part of annotation—not an afterthought.",
        1.15,
        6.55,
        11.0,
        0.4,
        size=22,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    # 15
    slide = new_slide("How the 26 videos will be annotated", "Staged rollout")
    rollout = [
        (
            "FIRST: 5 SHARED",
            "Both annotators label the same five videos",
            "We measure inter-rater variability: where two informed people agree or differ.",
            BLUE,
        ),
        (
            "NEXT: 10",
            "After reviewing the shared five, divide the next ten",
            "Return this batch promptly so Tosin can check the files while annotation continues.",
            GREEN,
        ),
        (
            "THEN: 10 + 6",
            "Send the remaining videos in two manageable batches",
            "The two annotators split the work rather than each repeating all 26.",
            PURPLE,
        ),
    ]
    for i, (head, body, why, color) in enumerate(rollout):
        x = 0.65 + i * 4.22
        add_box(slide, x, 1.5, 3.8, 4.8, fill=PANEL_LIGHT, line=color)
        add_box(slide, x + 0.55, 1.85, 2.7, 0.5, fill=color)
        add_text(
            slide,
            head,
            x + 0.6,
            1.91,
            2.6,
            0.34,
            size=14,
            color=WHITE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_text(
            slide,
            body,
            x + 0.38,
            2.65,
            3.05,
            1.05,
            size=20,
            color=NAVY,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_text(
            slide,
            why,
            x + 0.42,
            4.15,
            2.98,
            1.25,
            size=16,
            color=MUTED,
            align=PP_ALIGN.CENTER,
        )
    add_text(
        slide,
        "Goal: annotate all 26 available cholecystectomy videos. The first experiment may use 15 or 20 to keep the initial analysis simple.",
        0.95,
        6.55,
        11.4,
        0.4,
        size=18,
        color=CYAN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    slide = new_slide(dark=True)
    add_section_divider(
        slide,
        "PART 4",
        "From annotation to an AI study",
        "Test whether a model learned elsewhere understands OAUTHC operations—and whether explicit workflow knowledge helps.",
    )

    slide = new_slide("The first AI experiment", "From labels to evidence")
    stages = [
        ("Cholec80", "Public training benchmark", BLUE),
        ("TeCNO", "Learns visual + temporal patterns", GREEN),
        ("OAUTHC", "Clinically annotated local videos", AMBER),
        ("Compare", "Where and why does it fail?", PURPLE),
    ]
    x = 0.7
    for i, (head, body, color) in enumerate(stages):
        add_box(
            slide, x, 2.05, 2.55, 2.1, fill=PANEL_LIGHT, line=RGBColor(203, 219, 228)
        )
        add_box(slide, x + 0.65, 2.35, 1.25, 0.48, fill=color)
        add_text(
            slide,
            head,
            x + 0.68,
            2.39,
            1.19,
            0.35,
            size=12,
            color=WHITE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_text(
            slide,
            body,
            x + 0.25,
            3.05,
            2.05,
            0.75,
            size=17,
            color=NAVY,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        if i < len(stages) - 1:
            add_arrow(slide, x + 2.72, 2.88, 0.55, 0.38)
        x += 3.15
    add_box(slide, 1.35, 5.25, 10.65, 0.85, fill=NAVY)
    add_text(
        slide,
        "The question is transfer: does a model trained elsewhere understand our operations?",
        1.65,
        5.45,
        10.05,
        0.45,
        size=22,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    # 16
    slide = new_slide("TeCNO already reasons across time", "Model overview")
    add_picture_contain(slide, assets["tecno"], 0.65, 1.45, 8.4, 4.9)
    add_box(slide, 9.25, 1.6, 3.25, 4.55, fill=NAVY)
    add_text(
        slide,
        "In plain language",
        9.6,
        1.95,
        2.55,
        0.42,
        size=21,
        color=CYAN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_bullets(
        slide,
        [
            "extract visual information from frames",
            "look across preceding frames",
            "refine phase predictions in stages",
            "produce a phase for each sampled time",
        ],
        9.55,
        2.65,
        2.55,
        2.65,
        size=16,
        color=WHITE,
    )
    add_text(
        slide,
        "This is why the HMM may—or may not—add value.",
        9.55,
        5.4,
        2.55,
        0.5,
        size=16,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(
        slide,
        slide_number,
        "Figure 1: Czempiel et al., TeCNO, MICCAI 2020, arXiv:2003.10751.",
    )

    # 17
    slide = new_slide("What does the HMM add?", "Explicit workflow probabilities")
    y = 2.05
    positions = [0.7, 2.45, 4.2, 5.95, 7.7, 9.45, 11.2]
    for i, ((phase_id, _, color), x) in enumerate(zip(PHASES, positions, strict=True)):
        add_box(slide, x, y, 1.15, 0.85, fill=color)
        add_text(
            slide,
            phase_id,
            x,
            y + 0.16,
            1.15,
            0.45,
            size=18,
            color=WHITE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        if i < 6:
            add_arrow(slide, x + 1.22, y + 0.25, 0.45, 0.3, RGBColor(125, 151, 167))
    add_text(
        slide, "Common path", 0.75, 1.5, 2.0, 0.35, size=15, color=MUTED, bold=True
    )
    add_box(
        slide, 3.0, 3.55, 7.35, 1.35, fill=PANEL_LIGHT, line=RGBColor(199, 217, 227)
    )
    add_text(
        slide,
        "Same TeCNO probabilities",
        3.25,
        3.82,
        2.75,
        0.5,
        size=19,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_arrow(slide, 6.1, 3.93, 0.8, 0.35)
    add_text(
        slide,
        "HMM chooses the most plausible sequence",
        7.0,
        3.7,
        3.0,
        0.72,
        size=19,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_box(
        slide,
        0.95,
        5.55,
        11.45,
        0.82,
        fill=RGBColor(255, 246, 220),
        line=RGBColor(239, 203, 108),
    )
    add_text(
        slide,
        "Important: transitions are probabilities, not rules. Unusual OAUTHC workflows must remain possible.",
        1.2,
        5.76,
        10.95,
        0.42,
        size=20,
        color=RGBColor(126, 83, 0),
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    # 18
    slide = new_slide("The controlled comparison", "TeCNO versus TeCNO + HMM")
    add_box(slide, 0.85, 1.65, 3.1, 3.8, fill=NAVY)
    add_text(
        slide,
        "One set of TeCNO\nclass probabilities",
        1.25,
        2.5,
        2.3,
        1.1,
        size=25,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_arrow(slide, 4.3, 2.25, 0.75, 0.4, BLUE)
    add_arrow(slide, 4.3, 4.25, 0.75, 0.4, GREEN)
    add_box(
        slide,
        5.35,
        1.55,
        3.1,
        1.75,
        fill=RGBColor(235, 244, 254),
        line=RGBColor(178, 207, 244),
    )
    add_text(
        slide,
        "TeCNO's most likely\nphase at each time",
        5.75,
        1.9,
        2.3,
        0.75,
        size=24,
        color=BLUE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_box(
        slide,
        5.35,
        3.75,
        3.1,
        1.75,
        fill=RGBColor(232, 248, 243),
        line=RGBColor(167, 221, 201),
    )
    add_text(
        slide,
        "HMM Viterbi\ndecoding",
        5.75,
        4.1,
        2.3,
        0.75,
        size=24,
        color=GREEN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_box(
        slide, 9.05, 1.75, 3.45, 3.55, fill=PANEL_LIGHT, line=RGBColor(203, 219, 228)
    )
    add_text(
        slide,
        "We measure",
        9.5,
        2.05,
        2.55,
        0.4,
        size=21,
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_bullets(
        slide,
        [
            "accuracy and macro-F1",
            "each phase",
            "boundary timing",
            "fragmentation",
            "harm to unusual workflows",
        ],
        9.4,
        2.65,
        2.45,
        2.25,
        size=15,
    )
    add_text(
        slide,
        "The HMM is useful only if the evidence says so.",
        1.15,
        6.3,
        11.0,
        0.42,
        size=22,
        color=CYAN,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    # 20
    slide = new_slide("Decisions and next actions", "Discussion")
    questions = [
        "Confirm the P1 → P2 task-based rule",
        "Agree how to label long inactive periods",
        "Agree when Undefined should be used",
        "Confirm the shared-five agreement exercise",
        "Confirm the 10, 10 and 6 return batches",
    ]
    for i, question in enumerate(questions, start=1):
        y = 1.45 + (i - 1) * 0.92
        add_box(
            slide, 0.95, y, 0.58, 0.58, fill=[BLUE, GREEN, AMBER, PURPLE, PINK][i - 1]
        )
        add_text(
            slide,
            str(i),
            0.98,
            y + 0.05,
            0.52,
            0.42,
            size=17,
            color=WHITE,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_text(slide, question, 1.8, y, 10.3, 0.58, size=21, color=NAVY, bold=True)
    add_box(slide, 1.05, 6.25, 11.2, 0.62, fill=NAVY)
    add_text(
        slide,
        "The quality of the AI study begins with the quality and clarity of the clinical annotation.",
        1.3,
        6.36,
        10.7,
        0.38,
        size=20,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    # 21
    slide = new_slide("Key references", "Sources")
    references = [
        "Czempiel T et al. TeCNO: Surgical Phase Recognition with Multi-Stage Temporal Convolutional Networks. MICCAI 2020. arXiv:2003.10751.",
        "Ramesh S et al. Surgical Phase Recognition: From Public Datasets to Real-World Data. Applied Sciences. 2022;12:8746. DOI: 10.3390/app12178746.",
        "Golany T et al. Artificial intelligence for phase recognition in complex laparoscopic cholecystectomy. Surgical Endoscopy. 2022;36:9215–9223. DOI: 10.1007/s00464-022-09405-5.",
        "Twinanda AP et al. EndoNet: A Deep Architecture for Recognition Tasks on Laparoscopic Videos. IEEE TMI. 2017;36:86–97.",
        "Hashimoto DA et al. Machine Learning for Surgical Phase Recognition. Annals of Surgery. 2022;275:846–855.",
        "Mascagni P et al. Computer vision in surgery: from potential to clinical value. npj Digital Medicine. 2022;5:163.",
    ]
    for i, reference in enumerate(references, start=1):
        y = 1.35 + (i - 1) * 0.88
        add_text(slide, f"{i}.", 0.85, y, 0.4, 0.55, size=14, color=CYAN, bold=True)
        add_text(slide, reference, 1.25, y, 11.0, 0.65, size=14, color=TEXT)
    add_text(
        slide,
        "Borrowed figures are cited on their slides. The complexity chart was redrawn from published values for legibility.",
        1.0,
        6.75,
        11.2,
        0.3,
        size=11,
        color=MUTED,
        align=PP_ALIGN.CENTER,
    )
    add_footer(slide, slide_number)

    output.parent.mkdir(parents=True, exist_ok=True)
    presentation.save(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--asset-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assets = prepare_assets(args.source_dir, args.asset_dir)
    build_presentation(assets, args.output)
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
