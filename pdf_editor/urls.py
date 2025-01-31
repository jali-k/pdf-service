from django.urls import path
from .views import EditPdfView

urlpatterns = [
    path("edit-pdf/", EditPdfView.as_view(), name="edit_pdf"),
]
