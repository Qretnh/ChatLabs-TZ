from TODO.models import User
import logging

logger = logging.getLogger(__name__)


class UserService:

    @staticmethod
    def create_or_get_user(telegram_id: str, username: str = '') -> User:
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={'username': username}
        )
        if created:
            logger.info(f"Создан новый пользователь {user}")
        else:
            logger.info(f"Пользователь найден {user}")
        return user
