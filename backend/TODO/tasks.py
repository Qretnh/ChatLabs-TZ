from celery import shared_task
from django.utils.timezone import now
from .models import Task
from .services.send_notification import send_notification


@shared_task
def check_and_notify_tasks():
    tasks_due = Task.objects.filter(due_date__lte=now(), notified=False)
    for task in tasks_due:
        send_notification(task)
        task.notified = True
        task.save()
