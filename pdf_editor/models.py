from django.db import models


class DownloadLog(models.Model):
    email = models.EmailField()
    pdf_name = models.CharField(max_length=255)
    download_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} downloaded {self.pdf_name} at {self.download_time}"
