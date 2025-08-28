from django.db import models


class Schedule(models.Model):
    movie_start = models.DateTimeField()
    movie = models.ForeignKey('cinema.Movie', on_delete=models.CASCADE, related_name='schedule_movie')
    price = models.DecimalField(decimal_places=2, max_digits=10)
