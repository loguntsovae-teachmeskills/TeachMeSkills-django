from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Coach, Exercise, TrainingPlan, ExerciseToPlan

User = get_user_model()


class UserNestedSerializer(serializers.ModelSerializer):
    is_coach = serializers.SerializerMethodField()

    def get_is_coach(self, user) -> bool:
        return hasattr(user, "coach")

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_coach"]


class CoachSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)

    class Meta:
        model = Coach
        fields = ["id", "user"]


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ["id", "title"]



class ExercisePlanNestedSerializer(serializers.ModelSerializer):
    exercise = serializers.SerializerMethodField()

    def get_exercise(self, exercise):
        return exercise.exercise.title

    class Meta:
        model = ExerciseToPlan
        fields = ["id", "exercise", "amount"]


class TrainingPlanSerializer(serializers.ModelSerializer):
    author = UserNestedSerializer(read_only=True)
    exercise = ExercisePlanNestedSerializer(read_only=True, many=True)

    class Meta:
        model = TrainingPlan
        fields = ["id", "author", "exercise"]
