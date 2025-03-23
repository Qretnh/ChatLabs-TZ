from django.db import models
from hashid_field import HashidAutoField

class User(models.Model):
    telegram_id = models.CharField(max_length=20, unique=True, primary_key=True)
    username = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    id = HashidAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('user', 'name')
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Task(models.Model):
    id = HashidAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='TODO')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    due_time = models.TimeField(null=True, blank=True)
    notified = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
