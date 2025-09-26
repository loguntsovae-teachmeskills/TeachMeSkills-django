import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Кастомный User:
    - логин по email
    - UUID как PK
    - безопасное "удаление" через is_active
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField("Email", unique=True)
    first_name = models.CharField("Имя", max_length=150, blank=True)
    last_name = models.CharField("Фамилия", max_length=150, blank=True)

    # обязательные для Django флаги
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # доступ в админку
    is_superuser = models.BooleanField(default=False)

    # полезные метаданные
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # при createsuperuser будут спрашивать только email и пароль

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            # на всякий случай — case-insensitive уникальность (Postgres)
            models.UniqueConstraint(Lower("email"), name="uniq_user_email_ci")
        ]
        ordering = ("-date_joined",)

    def __str__(self):
        return self.email
