from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CoachViewSet, TrainingPlanViewSet, ExerciseViewSet

router = DefaultRouter()
router.register(r"coaches", CoachViewSet, basename="coach")
router.register(r"plans", TrainingPlanViewSet, basename="trainingplan")
router.register(r"exercises", ExerciseViewSet, basename="exercise")

urlpatterns = [
    path("", include(router.urls)),
]
