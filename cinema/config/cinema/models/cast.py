from django.db import models


class CastPerson(models.Model):
    name = models.CharField(max_length=255)
    dob = models.DateField()
    avatar = models.ImageField(upload_to="avatars/")

    class Meta:
        abstract = True


class Actor(CastPerson):
    rewards = models.TextField()

    def __str__(self):
        return self.name

class Director(CastPerson):
    pass

    def __str__(self):
        return self.name
