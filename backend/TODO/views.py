from rest_framework import viewsets, generics, serializers
from .models import Task, Category, User
from .serializers import TaskSerializer, CategorySerializer, UserSerializer
import logging

logger = logging.getLogger(__name__)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except serializers.ValidationError as e:
            print("Validation Error:", e.detail)
            logger.error(f"Validation Error: {e.detail}")
            raise

    def get_queryset(self):
        telegram_id = self.request.query_params.get('user_id')
        if telegram_id:
            return Task.objects.filter(user__telegram_id=telegram_id).order_by('-created_at')
        return super().get_queryset()

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        return Category.objects.filter(user__telegram_id=user_id)

    def perform_create(self, serializer):
        user_id = self.request.data.get('user_id')
        logger.debug(f"Получен user_id: {user_id}")

        if not user_id:
            logger.warning("user_id не передан в запросе")
            raise serializers.ValidationError("Не передан user_id")

        try:
            user = User.objects.get(telegram_id=user_id)
            logger.debug(f"Найден пользователь: {user}")
        except User.DoesNotExist:
            logger.warning(f"Пользователь с telegram_id={user_id} не найден")
            raise serializers.ValidationError("Пользователь с таким telegram_id не найден")

        serializer.save(user=user)
        logger.info(f"Категория успешно создана для пользователя {user}")


class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        telegram_id = serializer.validated_data['telegram_id']
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={'username': serializer.validated_data.get('username', '')}
        )
        return user