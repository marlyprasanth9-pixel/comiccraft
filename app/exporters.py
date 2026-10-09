from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from .config import settings


def _to_pdf_path(image_path: str) -> str:
    path = Path(image_path)

    if path.is_absolute():
        return str(path)

    return str(
        settings.BASE_DIR / path
    )


def save_pdf(layout) -> str:

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"comiccraft_{timestamp}.pdf"
    )

    output_path = (
        settings.EXPORT_DIR / filename
    )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for panel in layout:

        pdf.add_page()

        # Panel heading
        pdf.set_font(
            "Helvetica",
            "B",
            20,
        )

        pdf.cell(
            0,
            12,
            f"Panel {panel['panel_number']}: "
            f"{panel['title']}",
            ln=True,
        )

        # Image
        image_path = _to_pdf_path(
            panel["image_path"]
        )

        if Path(image_path).exists():
            pdf.image(
                image_path,
                x=15,
                y=30,
                w=180,
            )

        # Text begins below image
        pdf.set_y(145)

        pdf.set_font(
            "Helvetica",
            "I",
            11,
        )

        pdf.multi_cell(
            0,
            7,
            panel["scene_description"],
        )

        pdf.ln(3)

        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.multi_cell(
            0,
            7,
            "Caption: "
            + panel["caption"],
        )

        pdf.ln(2)

        pdf.set_font(
            "Helvetica",
            "",
            11,
        )

        pdf.multi_cell(
            0,
            7,
            "Narration: "
            + panel["narration"],
        )

        pdf.ln(2)

        pdf.multi_cell(
            0,
            7,
            "Dialogue: "
            + panel["dialogue"],
        )

    pdf.output(
        str(output_path)
    )

    return str(output_path)