import uuid

from django.db import models


class BaseTimeStampedMixin(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class TimeStampedMixin(BaseTimeStampedMixin, models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class UUIDMixin:
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False, auto_created=True
    )

    class Meta:
        abstract = True


class BaseModel(TimeStampedMixin, models.Model):

    class Meta:
        abstract = True


class BaseUUIDModel(UUIDMixin, BaseModel):

    class Meta:
        abstract = True
