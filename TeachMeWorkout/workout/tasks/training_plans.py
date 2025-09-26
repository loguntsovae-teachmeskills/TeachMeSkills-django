from celery import shared_task
from django.db import transaction
from ..models import TrainingPlan, ExerciseToPlan


@shared_task(bind=True, retry_backoff=True, retry_kwargs={"max_retries": 5})
def fill_plan_from_parent(self, new_plan_id: int, parent_plan_id: int) -> int:
    """
    Копирует упражнения из родительского плана в новый.
    Возвращает количество скопированных упражнений.
    При ошибке — до 5 повторных попыток с увеличивающейся задержкой.
    """

    try:
        new_plan = TrainingPlan.objects.get(pk=new_plan_id)
        parent_plan = TrainingPlan.objects.get(pk=parent_plan_id)
    except TrainingPlan.DoesNotExist as e:
        # если планов нет — не ретраим, а просто падаем
        raise e

    created_count = 0

    try:
        with transaction.atomic():
            for etp in parent_plan.exercise.all():
                ExerciseToPlan.objects.create(
                    exercise=etp.exercise,
                    plan=new_plan,
                    amount=etp.amount,
                )
                created_count += 1

        return created_count

    except Exception as exc:
        # кастомная логика задержки: 5, 10, 20, 40, 80 секунд
        delay = 5 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=delay, max_retries=5)