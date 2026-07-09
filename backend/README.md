# Tic-Tac-Toe Backend

Backend-часть веб-сайта для игры в крестики-нолики против LLM-моделей.

## Установка и запуск

### 1. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Скопируйте файл `.env.example` в `.env` и заполните его:

```bash
cp .env.example .env
```

Обязательные переменные:
- `DATABASE_URL` — строка подключения к PostgreSQL (например, `postgresql://user:pass@localhost:5432/tictactoe`)
- `REDIS_URL` — для кэширования и сессий
- `SMTP_*` — для отправки email
- API-ключи для LLM-провайдеров

### 4. Создание базы данных

Если база данных ещё не создана, создайте её через `psql` или другой клиент:

```sql
-- Создание пользователя с паролем
CREATE USER tictactoe_user WITH 
    LOGIN
    NOSUPERUSER
    INHERIT
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION
    PASSWORD '****';

-- Создание базы данных
CREATE DATABASE tictactoe_db
    WITH 
    OWNER = tictactoe_user
    ENCODING = 'UTF8'
    LC_COLLATE = 'Russian_Russia.1251'
    LC_CTYPE = 'Russian_Russia.1251'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Предоставление привилегий на базу данных
GRANT CONNECT ON DATABASE tictactoe_db TO tictactoe_user;

-- Подключение к созданной базе данных
\c tictactoe_db

-- Предоставление привилегий на схему public
GRANT USAGE ON SCHEMA public TO tictactoe_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tictactoe_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tictactoe_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO tictactoe_user;
```

### 5. Применение миграций базы данных

Для управления схемой БД используется Alembic.

**Применить все миграции (создать таблицы):**

```bash
alembic upgrade head
```

**Создать новую миграцию после изменения моделей:**

```bash
alembic revision --autogenerate -m "описание изменений"
```

**Откатить последнюю миграцию:**

```bash
alembic downgrade -1
```

**Посмотреть текущую версию:**

```bash
alembic current
```

**Посмотреть историю миграций:**

```bash
alembic history
```

> **Примечание:** Миграции выполняются синхронно, несмотря на то, что приложение использует асинхронный SQLAlchemy. В файле `app/db/migrations/env.py` настроен синхронный движок для корректной работы Alembic.

### 6. Запуск сервера

```bash
uvicorn app.main:app --reload
```

Сервер будет доступен по адресу: http://localhost:8000

Документация API (Swagger): http://localhost:8000/docs

### 7. Запуск тестов

```bash
pytest
```

Для проверки покрытия:

```bash
pytest --cov=app
```

## Структура проекта

```
restapi/
├── app/
│   ├── api/                # Маршруты API (v1, websocket)
│   ├── core/               # Ядро: безопасность, кэш, rate limiter
│   ├── db/                 # Подключение к БД и миграции
│   ├── middleware/         # Промежуточное ПО
│   ├── modules/            # Функциональные модули
│   │   ├── idm/            # Управление идентификацией
│   │   ├── game_engine/    # Игровая логика
│   │   ├── game_repository/# Хранение данных игр
│   │   ├── email_manager/  # Email-уведомления
│   │   ├── llm_manager/    # Взаимодействие с LLM
│   │   └── admin/          # Администрирование
│   └── utils/              # Утилиты
├── restapi_tests/          # Тесты (unit/integration)
├── alembic.ini             # Конфигурация Alembic
├── .env.example            # Пример переменных окружения
├── requirements.txt        # Зависимости
└── README.md               # Этот файл
```

## Дополнительные команды

**Форматирование кода:**

```bash
black .
isort .
```

**Проверка линтерами:**

```bash
flake8 .
```

**Сборка Docker-образа:**

```bash
docker build -t tictactoe-backend .
```

**Запуск в Docker Compose (локальная разработка):**

```bash
docker-compose up -d
```

## Лицензия

MIT
