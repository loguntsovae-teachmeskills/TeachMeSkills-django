from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework import status, mixins
from .models import Training, Exercise, TrainingPlan, ExerciseToPlan, Coach
from .serializers import (
    ExerciseSerializer,
    TrainingPlanSerializer,
    CoachSerializer, ExerciseOnlyTitleSerializer,
)
from rest_framework.response import Response
from rest_framework.decorators import action
from .permissions import ExercisePermission
from .tasks import fill_plan_from_parent

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

    @action(detail=True, methods=["post"], url_path="duplicate")
    def duplicate(self, request, pk=None):
        """
        POST /training-plans/{id}/duplicate/
        Создаёт копию плана вместе с упражнениями.
        """
        plan = self.get_object()

        # создаём копию плана
        new_plan = TrainingPlan.objects.create(
            # title=f"{plan.title} (копия)",
            author=request.user if request.user.is_authenticated else plan.author,
        )

        print("start")
        fill_plan_from_parent.apply_async(
            kwargs={
                "new_plan_id": new_plan.id,
                "parent_plan_id": plan.id,
            },
            countdown=5
        )
        print("finish")

        serializer = self.get_serializer(new_plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
    queryset = Exercise.objects.all().prefetch_related("plan")
    serializer_class = ExerciseSerializer
    permission_classes = [ExercisePermission]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]

        perms = [permissions.IsAuthenticated()]

        if self.action == "destroy":
            perms.append(permissions.IsAdminUser())

        return perms

    @action(detail=True, methods=["post"], url_path="duplicate")
    # exercises/<ID>/duplicate/
    def duplicate_exercise_with_prefix(self, request, pk=None):
        instance = self.get_object()
        data = {"title": instance.title + "DUPLICATE"}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="list-titles")
    # exercises/list_titles
    def list_titles(self, request):
        instances = self.get_queryset()
        serializer = ExerciseOnlyTitleSerializer(instances, many=True)
        return Response(serializer.data)
