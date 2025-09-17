from django.contrib.auth import get_user_model
from django.db.models.aggregates import Count
from rest_framework import generics, permissions
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework import status, mixins
from .models import Training, Exercise, TrainingPlan, ExerciseToPlan, Coach
from .serializers import (
    ExerciseSerializer,
    TrainingPlanSerializer,
    CoachSerializer,
)

User = get_user_model()


class CoachViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Coach.objects.all().select_related("user")
    serializer_class = CoachSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class TrainingPlanViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = TrainingPlanSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            q1 = Q(author=user)
        else:
            q1 = Q()

        q2 = Q(author__coach__isnull=False)
        return TrainingPlan.objects.filter(q1 | q2).select_related("author").prefetch_related("exercise", "exercise__exercise")


class ExerciseViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]

        perms = [permissions.IsAuthenticated()]

        if self.action == "destroy":
            perms.append(permissions.IsAdminUser())

        return perms
