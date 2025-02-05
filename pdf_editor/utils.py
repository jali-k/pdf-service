from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color

def create_watermark(email, page_size):
    """Generate multiple small watermarks and hidden encoding."""
    watermark_pdf = BytesIO()
    c = canvas.Canvas(watermark_pdf, pagesize=page_size)

    # Set watermark color, opacity, and font
    c.setFillColor(Color(0.5, 0.5, 0.5, alpha=0.2))  # Light gray with transparency
    c.setFont("Helvetica-Bold", 12)

    # Multiple small watermarks in various positions
    positions = [
        (page_size[0] * 0.15, page_size[1] * 0.85),
        (page_size[0] * 0.6, page_size[1] * 0.75),
        (page_size[0] * 0.3, page_size[1] * 0.55),
        (page_size[0] * 0.75, page_size[1] * 0.35),
        (page_size[0] * 0.2, page_size[1] * 0.15)
    ]
    for x, y in positions:
        c.drawString(x, y, email)

    # Invisible text (White-on-White)
    c.setFillColor(Color(1, 1, 1, alpha=1))  # Pure white
    c.setFont("Helvetica", 6)
    c.drawString(10, 20, email)  # White text at the bottom

    # Hidden encoding: Microtext spanning the full width of the page
    c.setFillColor(Color(0, 0, 0, alpha=1))  # Black for microtext
    c.setFont("Helvetica", 1)  # Extremely small font
    microtext = (email + " ") * ((int(page_size[0]) // (len(email) + 1)) + 1)*1000  # Repeat email to fill width
    c.drawString(0, 5, microtext[:int(page_size[0] // 1)])  # Ensure full width coverage
    
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
