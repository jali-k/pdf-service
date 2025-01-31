from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser  # Use MultiPartParser
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import FileResponse
from .utils import add_email_to_pdf
from .models import DownloadLog


class EditPdfView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # Change parser_classes

    def post(self, request):
        email = request.data.get("email")
        pdf_file = request.FILES.get("pdf")

        if not email or not pdf_file:
            return Response({"error": "Email and PDF file are required."}, status=400)

        # Add email to PDF
        edited_pdf = add_email_to_pdf(pdf_file, email)

        # Save download log
        DownloadLog.objects.create(email=email, pdf_name=pdf_file.name)

        # Return edited PDF as response
        response = FileResponse(edited_pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="edited_{pdf_file.name}"'
        )
        return response
