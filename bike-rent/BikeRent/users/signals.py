# users/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models.profile import Profile
from .models.user import User


@receiver(post_save, sender=User)
def create_profile_on_user_create(sender, instance: User, created: bool, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(pre_save, sender=User)
def normalize_email(sender, instance: User, **kwargs):
    if instance.email:
        instance.email = instance.email.lower().strip()
