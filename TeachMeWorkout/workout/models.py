from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower

User = get_user_model()


class Training(models.Model):
    workday = models.DateField()
    plan = models.ForeignKey("TrainingPlan", on_delete=models.SET_NULL, null=True, blank=True, related_name="trainings")

    def __str__(self):
        return f"Training on {self.workday}"


class Exercise(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower("title"),
                name="unique_exercise_title_ci",
            )
        ]

    def __str__(self):
        return self.title


class TrainingPlan(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plans")


class ExerciseToPlan(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="plan")
    plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE, related_name="exercise")
    amount = models.PositiveSmallIntegerField()


class Coach(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="coach")
