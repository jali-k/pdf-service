from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color


def create_watermark(email, page_size):
    """Generate a watermark PDF with the email text."""
    watermark_pdf = BytesIO()
    c = canvas.Canvas(watermark_pdf, pagesize=page_size)

    # Set watermark color, opacity, and font
    c.setFillColor(Color(0.5, 0.5, 0.5, alpha=0.3))  # Light gray with transparency
    c.setFont("Helvetica-Bold", 30)

    # Rotate and add email as a watermark
    c.saveState()
    c.translate(page_size[0] / 2, page_size[1] / 2)  # Center of the page
    c.rotate(30)  # Rotate text diagonally
    c.drawString(-100, 0, email)
    c.restoreState()

    c.save()
    watermark_pdf.seek(0)
    return watermark_pdf


def add_email_to_pdf(pdf_file, email):
    """Add a watermark with the email to each page of the PDF."""
    reader = PdfReader(pdf_file)
    writer = PdfWriter()

    for page in reader.pages:
        # Create a watermark for the current page size
        page_size = (float(page.mediabox.width), float(page.mediabox.height))
        watermark = create_watermark(email, page_size)

        # Merge watermark with page
        watermark_reader = PdfReader(watermark)
        page.merge_page(watermark_reader.pages[0])

        writer.add_page(page)

    # Save to memory
    output_pdf = BytesIO()
    writer.write(output_pdf)
    output_pdf.seek(0)

    return output_pdf  # Return file-like object
