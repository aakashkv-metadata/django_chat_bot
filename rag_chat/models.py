from django.db import models
import os

class UploadedDocument(models.Model):
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    def __str__(self):
        return os.path.basename(self.file.name)
