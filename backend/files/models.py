from django.db import models
from django.conf import settings

import secrets

class File(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255, null=True)
    size = models.PositiveIntegerField(null=True)
    mime = models.CharField(max_length=50, null=True)

class SharedFile(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_files')
    share_hash = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)