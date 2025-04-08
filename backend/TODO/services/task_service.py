from TODO.models import Task


class TaskService:

    @staticmethod
    def get_tasks_by_user(telegram_id: str):
        return Task.objects.filter(user__telegram_id=telegram_id).order_by('-created_at')
