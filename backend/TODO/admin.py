from django.contrib import admin
from .models import User, Category, Task


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username')
    search_fields = ('telegram_id', 'username')
    ordering = ('telegram_id',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user')
    list_filter = ('user',)
    search_fields = ('name', 'user__telegram_id')
    ordering = ('user', 'name')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'category', 'due_date', 'is_completed')
    list_filter = ('is_completed', 'category', 'due_date')
    search_fields = ('title', 'user__telegram_id', 'category__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
