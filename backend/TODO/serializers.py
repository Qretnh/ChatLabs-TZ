from hashid_field.rest import HashidSerializerCharField
from rest_framework import serializers
from .models import Task, Category, User


class CategorySerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('user',)


class TaskSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)
    telegram_id = serializers.CharField(write_only=True, required=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    category = CategorySerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    due_time = serializers.TimeField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            'id', 'telegram_id', 'user', 'category_id', 'category', 'title',
            'description', 'created_at', 'due_date', 'due_time', 'is_completed'
        ]
        read_only_fields = ('user', 'id', 'created_at')

    def create(self, validated_data):
        telegram_id = validated_data.pop('telegram_id')
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        validated_data.pop('user_id', None)

        # Дефолтное время 18:00, если пользователь не указал
        due_time = validated_data.get('due_time')
        if not due_time:
            from datetime import time
            validated_data['due_time'] = time(hour=18, minute=0)

        task = Task.objects.create(user=user, **validated_data)
        return task


class UserSerializer(serializers.ModelSerializer):
    telegram_id = serializers.CharField()
    username = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = User
        fields = ['telegram_id', 'username']
