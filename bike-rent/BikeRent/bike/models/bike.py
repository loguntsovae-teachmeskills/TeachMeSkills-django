from django.contrib.auth import get_user_model
from django.db import models
from common.models import TimeStampedMixin

User = get_user_model()


class Bike(TimeStampedMixin, models.Model):
    class Category(models.TextChoices):
        ROAD = "road", "Шоссейный"
        MTB = "mtb", "Горный"
        CITY = "city", "Городской"
        ELECTRIC = "electric", "Электровелосипед"

    class Colour(models.TextChoices):
        RED = "red", "Красный"
        BLUE = "blue", "Синий"
        BLACK = "black", "Чёрный"
        WHITE = "white", "Белый"
        GREEN = "green", "Зелёный"

    class Brand(models.TextChoices):
        TREK = "trek", "Trek"
        GIANT = "giant", "Giant"
        SPECIALIZED = "specialized", "Specialized"
        CUBE = "cube", "Cube"
        AUTHOR = "author", "Author"

    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="bikes", null=True, blank=True
    )

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        blank=True,
        null=True,
        verbose_name="Category",
    )
    name = models.CharField(max_length=1024, blank=True, null=True)
    brand = models.CharField(
        max_length=50, choices=Brand.choices, verbose_name="Bike Brand"
    )
    electricity = models.BooleanField(default=False, help_text="Есть ли у него педали")
    colour = models.CharField(
        max_length=20,
        choices=Colour.choices,
        verbose_name="Colour",
    )
    available = models.BooleanField(default=True)

    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name="Bike History",
        help_text="Тут мы храним всю историю о велосипеде и его обслуживании",
    )
    preview = models.FileField(upload_to="bike/preview", blank=True, null=True)

    station = models.ForeignKey(
        "bike.Station", on_delete=models.PROTECT, related_name="bikes"
    )

    class Meta:
        verbose_name = "Bicycle"
        verbose_name_plural = "Bicycles"

    def __str__(self):
        return f"Bike name {self.name or 'No name'}"
