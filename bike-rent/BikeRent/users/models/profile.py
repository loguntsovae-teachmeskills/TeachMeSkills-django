# users/models/profile.py
import uuid

from django.conf import settings
from django.db import models


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )

    # avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True)
    locale = models.CharField(max_length=10, blank=True)
    tz = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f"Profile({self.user.email})"
