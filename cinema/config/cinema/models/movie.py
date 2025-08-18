from django.db import models


class Movie(models.Model):
    name = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()

    genres = models.ManyToManyField("cinema.Genre")
    actors = models.ManyToManyField("cinema.Actor")
    directors = models.ManyToManyField("cinema.Director")
