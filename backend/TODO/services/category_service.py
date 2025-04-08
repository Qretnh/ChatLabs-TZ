from TODO.models import Category, User
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class CategoryService:

    @staticmethod
    def create_category(user_id: str, serializer) -> Category:
        if not user_id:
            logger.warning("user_id не передан")
            raise ValidationError("Не передан user_id")

        try:
            user = User.objects.get(telegram_id=user_id)
        except User.DoesNotExist:
            logger.warning(f"Пользователь с telegram_id={user_id} не найден")
            raise ValidationError("Пользователь не найден")

        category = serializer.save(user=user)
        logger.info(f"Категория создана для пользователя {user}")
        return category
