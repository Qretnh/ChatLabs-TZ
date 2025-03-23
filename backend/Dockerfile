FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR .

# Копируем зависимости и ставим их
COPY requirements.txt .

# Обновляем pip, wheel обязательна для сборки C-зависимостей
RUN pip install --upgrade pip && \
    pip install wheel && \
    pip install -r requirements.txt

# Копируем весь проект
COPY . .

# Убираем буферизацию логов (важно для docker-логов)
ENV PYTHONUNBUFFERED=1

# Команда по умолчанию для Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
