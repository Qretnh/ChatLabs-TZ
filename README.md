# 🛠 Стек технологий

- **Backend:** Django, DRF
- **Бот:** aiogram, aiogram_dialog
- **Инфраструктура:** Redis, PostgreSQL, Celery, Celery-Beat, Docker, httpx

---

# 🚀 Запуск проекта

### ✅ Подготовка
- Все основные переменные уже есть в `.env.example`.
- Нужно указать **только токен бота**, остальное готово.

### ✅ Запуск

0. создать в корневой директории файл .env (можно взять всё из файла .env.example добавив в него только свой токен бота)

1. Удалить файл .keep из pg_data (он не нужен, папка должна быть пустой при запуске чтобы маунт БД был корректный)

2. В корневой директории ввести:
```bash
docker-compose up
```

3. Готово!

---

# 🧐 Архитектура проекта

## 📡 Backend ( папка `backend` )
- Django + DRF
- Своя структура:
  - `backend/backend` — базовое приложение
  - `backend/TODO` — приложение ToDo: модели, сериализаторы, views
  - `backend/TODO/services` — сервисы для Celery
- Работа с PostgreSQL:
  - Модели с `HashidAutoField` вместо стандартных PK
- Админка доступна по логину/паролю:
  ```
  Логин: admin
  Пароль: admin
  ```
- Celery + Celery Beat:
  - Отправка уведомлений о дедлайнах задач
- Взаимодействие с ботом — через REST API (httpx)
- Таймзона: `America/Adak`
- Dockerfile внутри директории

## 🤖 Бот ( папка `bot` )
- aiogram + aiogram_dialog
- Структура:
  - `handlers` — базовые хендлеры (start)
  - `dialogs` — основные диалоги, разбитые по модулям (окна, геттеры, функции)
  - `services/api` — работа с DRF через httpx, разнесено по моделям (tasks, categories, users)
- Функционал:
  - Создание, изменение, удаление, просмотр и архивирование задач
  - Отображение времени создания задач
  - Работа с категориями (создание и просмотр)

- Dockerfile внутри директории

---

# 🏗 Структура Docker-сервисов

Проект состоит из 6 контейнеров:

| № | Сервис       | Назначение                                      |
|---|------------- |-----------------------------------------------|
| 1 | **postgres** | База данных для Django                        |
| 2 | **django**   | Backend + DRF                                  |
| 3 | **bot**      | Телеграм-бот на aiogram + aiogram_dialog      |
| 4 | **redis**    | Хранилище для Celery                           |
| 5 | **celery**   | Отправка уведомлений по дедлайнам              |
| 6 | **celery-beat** | Регулярные задачи для проверки дедлайнов  |

✅ Все данные PostgreSQL сохраняются в `pg_data`, чтобы избежать потерь при перезапуске.

✅ В `docker-compose.yml` настроен `restart: always` для автоподнятия сервисов.

---

# ⚠ Проблемы и решения

### 1. Работа с первичными ключами (PK)
- Столкнулся с ограничениями стандартных PK.
- Решение: использовал `HashidAutoField` для безопасности и удобства.

### 2. Архитектура заметок и UX
- Требовалась продуманная структура To-Do и удобный интерфейс бота.
- Решение: Проектирование "от требований", постепенное добавление фич.

Консультировался с DeepSeek и ChatGPT по улучшению UX/UI.

### 3. Чистота архитектуры проекта
- Много сервисов — возникли сложности в построении структуры.
- Решение: Изучал репозитории на GitHub, рефакторил по ходу.

Так же писал свои идеи по архитектуре GPT и спрашивал какие есть подводные камни и что ещё можно улучшить

Для обратной связи: 

Telegram; @Aaaar05
