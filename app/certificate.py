from pathlib import Path
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfbase.pdfmetrics import stringWidth

OUTPUT_DIR = Path("certificates")
OUTPUT_DIR.mkdir(exist_ok=True)


def centered(pdf, text, page_width, y, font="Helvetica", size=16, color=black):
    pdf.setFont(font, size)
    pdf.setFillColor(color)
    text_width = stringWidth(text, font, size)
    pdf.drawString((page_width - text_width) / 2, y, text)


def centered_at(pdf, text, x, y, font, size, color):
    pdf.setFont(font, size)
    pdf.setFillColor(color)
    width = stringWidth(text, font, size)
    pdf.drawString(x - width / 2, y, text)


def create_certificate(
    recipient_name,
    achievement,
    event_name,
    event_date,
    issuer,
    recipient_id,
):
    """Generate one PDF from the predefined certificate template."""
    file_path = OUTPUT_DIR / f"certificate_{recipient_id}.pdf"
    width, height = landscape(A4)

    pdf = canvas.Canvas(str(file_path), pagesize=(width, height))

    navy = HexColor("#182848")
    gold = HexColor("#D4A72C")
    cream = HexColor("#F6F2E8")

    # Background
    pdf.setFillColor(cream)
    pdf.rect(0, 0, width, height, fill=1, stroke=0)

    # Double border
    pdf.setStrokeColor(navy)
    pdf.setLineWidth(5)
    pdf.rect(22, 22, width - 44, height - 44, fill=0, stroke=1)

    pdf.setStrokeColor(gold)
    pdf.setLineWidth(1.5)
    pdf.rect(32, 32, width - 64, height - 64, fill=0, stroke=1)

    centered(pdf, "CERTIFICATE", width, height - 105, "Helvetica-Bold", 34, navy)
    centered(pdf, "OF ACHIEVEMENT", width, height - 137, "Helvetica", 14, gold)

    centered(
        pdf,
        "This certificate is proudly presented to",
        width,
        height - 195,
        "Helvetica",
        13,
        navy,
    )

    centered(pdf, recipient_name, width, height - 245, "Helvetica-Bold", 28, navy)

    # Simple wrapping for the achievement text
    words = achievement.split()
    lines = []
    line = ""

    for word in words:
        if len(line) + len(word) + 1 <= 90:
            line = (line + " " + word).strip()
        else:
            lines.append(line)
            line = word

    if line:
        lines.append(line)

    y = height - 290
    for line in lines[:2]:
        centered(pdf, line, width, y, "Helvetica", 12, black)
        y -= 18

    centered(pdf, event_name, width, height - 350, "Helvetica-Bold", 16, navy)
    centered(pdf, f"Date: {event_date}", width, height - 380, "Helvetica", 11, black)

    # Signature
    pdf.setStrokeColor(navy)
    pdf.setLineWidth(1)
    pdf.line(width - 250, 92, width - 90, 92)
    centered_at(pdf, issuer, width - 170, 72, "Helvetica-Bold", 10, navy)

    # Small gold seal
    pdf.setFillColor(gold)
    pdf.circle(92, 92, 27, fill=1, stroke=0)
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawCentredString(92, 88, "✓")

    pdf.save()
    return str(file_path)
