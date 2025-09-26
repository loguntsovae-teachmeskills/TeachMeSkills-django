from datetime import timedelta
from celery import Celery
import os
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TeachMeWorkout.settings")
app = Celery("TeachMeWorkout")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # каждые 2 секунды (как у тебя)
    "say-hello": {
        "task": "workout.tasks.main.test_task",
        "schedule": timedelta(seconds=10),
    },
    # каждый день в 7 утра
    "morning-task": {
        "task": "workout.tasks.main.test_task",
        "schedule": crontab(hour=7, minute=0),
    },
    # каждые 5 минут
    "every-5-minutes": {
        "task": "workout.tasks.main.test_task",
        "schedule": crontab(minute="*/5"),
    },
    # каждое воскресенье в 23:30
    "weekly-task": {
        "task": "workout.tasks.main.test_task",
        "schedule": crontab(hour=23, minute=30, day_of_week=0),
    },
}