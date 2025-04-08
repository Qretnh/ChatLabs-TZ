from rest_framework import viewsets, generics, serializers
from .models import Task, Category, User
from .serializers import TaskSerializer, CategorySerializer, UserSerializer

from .services.category_service import CategoryService
from .services.task_service import TaskService
from .services.user_service import UserService

import logging

logger = logging.getLogger(__name__)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        telegram_id = self.request.query_params.get('user_id')
        if telegram_id:
            return TaskService.get_tasks_by_user(telegram_id)
        return super().get_queryset()

    def perform_create(self, serializer):
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except serializers.ValidationError as e:
            logger.error(f"Validation Error: {e.detail}")
            raise

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        return Category.objects.filter(user__telegram_id=user_id)

    def perform_create(self, serializer):
        user_id = self.request.data.get('user_id')
        CategoryService.create_category(user_id=user_id, serializer=serializer)



class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        telegram_id = serializer.validated_data['telegram_id']
        username = serializer.validated_data.get('username', '')
        return UserService.create_or_get_user(telegram_id, username)