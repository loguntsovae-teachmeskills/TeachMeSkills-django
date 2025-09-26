# workout/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Training, Exercise, TrainingPlan, ExerciseToPlan, Coach

User = get_user_model()


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ("id", "workday")
    list_display_links = ("id", "workday")
    date_hierarchy = "workday"
    ordering = ("-workday",)
    search_fields = ("workday",)
    list_filter = ("workday",)


class ExerciseToPlanInlineForPlan(admin.TabularInline):
    """
    Инлайн для редактирования упражнений внутри плана.
    Поле plan скрываем — оно берётся из родителя.
    """
    model = ExerciseToPlan
    fk_name = "plan"
    extra = 1
    autocomplete_fields = ("exercise",)
    fields = ("exercise", "amount")


class ExerciseToPlanInlineForExercise(admin.TabularInline):
    """
    Инлайн для просмотра/редактирования включения упражнения в планы.
    Поле exercise скрываем — оно берётся из родителя.
    """
    model = ExerciseToPlan
    fk_name = "exercise"
    extra = 0
    autocomplete_fields = ("plan",)
    fields = ("plan", "amount")
    readonly_fields = ()  # можно оставить всё редактируемым


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "plans_count")
    list_display_links = ("id", "title")
    search_fields = ("title",)
    ordering = ("title",)
    inlines = (ExerciseToPlanInlineForExercise,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Подсчитываем, в скольких планах используется упражнение
        return qs.annotate(_plans_count=admin.models.Count("plan"))

    @admin.display(description="В планах", ordering="_plans_count")
    def plans_count(self, obj):
        return getattr(obj, "_plans_count", 0)


@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "exercises_total")
    list_display_links = ("id", "author")
    autocomplete_fields = ("author",)
    search_fields = (
        "author__username",
        "author__email",
        "author__first_name",
        "author__last_name",
    )
    inlines = (ExerciseToPlanInlineForPlan,)
    ordering = ("-id",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    @admin.display(description="Всего повторений", ordering="_ex_total")
    def exercises_total(self, obj):
        return getattr(obj, "_ex_total", 0) or 0


@admin.register(ExerciseToPlan)
class ExerciseToPlanAdmin(admin.ModelAdmin):
    """
    Отдельная админка для быстрого массового редактирования связей.
    """
    list_display = ("id", "plan", "exercise", "amount")
    list_select_related = ("plan", "exercise")
    autocomplete_fields = ("plan", "exercise")
    search_fields = ("plan__author__username", "exercise__title")
    list_filter = ("plan",)
    ordering = ("plan", "exercise__title")


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    list_display_links = ("id", "user")
    autocomplete_fields = ("user",)
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    ordering = ("user__username",)
