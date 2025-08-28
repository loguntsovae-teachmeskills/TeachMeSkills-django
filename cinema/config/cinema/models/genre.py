from django.db import models


class Genre(models.Model):
    class GenreNameChoices(models.TextChoices):
        FANTASY = 'fantasy', 'Fantasy'
        COMEDY = 'comedy', 'Comedy'
        HORROR = 'horror', 'Horror'

    name = models.CharField(
        max_length=255,
        choices=GenreNameChoices.choices,
    )

    def __str__(self):
        return self.name
