from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
import pikepdf


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
        (page_size[0] * 0.2, page_size[1] * 0.15),
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
    microtext = (
        (email + " ") * ((int(page_size[0]) // (len(email) + 1)) + 1) * 1000
    )  # Repeat email to fill width
    c.drawString(
        0, 5, microtext[: int(page_size[0] // 1)]
    )  # Ensure full width coverage

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


def embed_metadata_in_pdf(pdf_file, email):
    """Embed encrypted XMP metadata inside the PDF."""
    # Valid XMP metadata format
    xmp_metadata = b"""<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?>
    <x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 5.6-c147 79.164387, 2020/06/02-14:39:35">
       <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
          <rdf:Description rdf:about=""
                xmlns:pdf="http://ns.adobe.com/pdf/1.3/"
                pdf:Producer="pikepdf">
             <pdf:CustomMetadata>{}</pdf:CustomMetadata>
          </rdf:Description>
       </rdf:RDF>
    </x:xmpmeta>
    <?xpacket end="w"?>""".format(
        email
    ).encode(
        "utf-8"
    )

    # Open the PDF
    pdf = pikepdf.Pdf.open(pdf_file)

    # Create a metadata stream
    metadata_stream = pikepdf.Stream(pdf, xmp_metadata)

    # Make it an indirect object (harder to remove)
    metadata_obj = pdf.make_indirect(metadata_stream)

    # Assign encrypted metadata to the PDF
    pdf.Root.Metadata = metadata_obj

    # Save the PDF with **metadata encryption only**
    pdf.save(
        "final_pdf_with_metadata_encryption.pdf",
        encryption=pikepdf.Encryption(
            owner="THeHellOF**@@675ejtdy",  # Password required to modify metadata
            user="",  # Empty user password → anyone can open the file
            R=6,  # AES-256 encryption
            allow=pikepdf.Permissions(
                extract=False,
                modify_assembly=False,
            ),  # Disable metadata editing
        ),
    )

    pdf.close()
    print("PDF with encrypted metadata created successfully!")


# Main Function: Add watermark, embed metadata, and save final PDF
def process_pdf(input_pdf, email):
    # Step 1: Add watermark with email
    output_pdf_with_watermark = add_email_to_pdf(input_pdf, email)

    # Step 2: Embed encrypted metadata into the PDF
    embed_metadata_in_pdf(output_pdf_with_watermark, email)
