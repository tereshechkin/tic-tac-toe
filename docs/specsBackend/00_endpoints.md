# API Endpoints для Backend приложения

## Ограничения
На первом этапе OAuth 2.0 авторизация через VK и Google не реализуется. Соответствующие Endpoint отсутствуют.

## Базовый URL
`/api/v1`

## Аутентификация и авторизация

### Регистрация
- **POST** `/auth/register`
  - **Описание:** Регистрация нового пользователя
  - **Тело запроса:** `{ "email": "string", "username": "string" }`
  - **Ответ:** `{ "message": "Код отправлен на email", "email": "string" }`

### Подтверждение регистрации
- **POST** `/auth/verify-registration`
  - **Описание:** Подтверждение email кодом и завершение регистрации
  - **Тело запроса:** `{ "email": "string", "code": "string" }`
  - **Ответ:** `{ "access_token": "string", "refresh_token": "string", "user": { "id": "uuid", "email": "string", "username": "string" } }`

### Вход
- **POST** `/auth/login`
  - **Описание:** Отправка кода подтверждения на email
  - **Тело запроса:** `{ "email": "string" }`
  - **Ответ:** `{ "message": "Код отправлен на email", "email": "string" }`

### Подтверждение входа
- **POST** `/auth/verify-login`
  - **Описание:** Подтверждение email кодом и получение токенов
  - **Тело запроса:** `{ "email": "string", "code": "string" }`
  - **Ответ:** `{ "access_token": "string", "refresh_token": "string", "user": { "id": "uuid", "email": "string", "username": "string" } }`

### Обновление токена
- **POST** `/auth/refresh`
  - **Описание:** Получение нового access_token по refresh_token
  - **Заголовки:** `Authorization: Bearer <refresh_token>`
  - **Ответ:** `{ "access_token": "string" }`

### Выход
- **POST** `/auth/logout`
  - **Описание:** Выход из системы
  - **Заголовки:** `Authorization: Bearer <access_token>`
  - **Ответ:** `{ "message": "Успешный выход" }`

### Отправка нового кода
- **POST** `/auth/resend-code`
  - **Описание:** Повторная отправка кода на email
  - **Тело запроса:** `{ "email": "string" }`
  - **Ответ:** `{ "message": "Код отправлен повторно" }`

### Проверка токена
- **GET** `/auth/verify`
  - **Описание:** Проверка валидности access_token
  - **Заголовки:** `Authorization: Bearer <access_token>`
  - **Ответ:** `{ "valid": true, "user": { "id": "uuid", "email": "string", "username": "string" } }`

## Пользователи

### Получение профиля
- **GET** `/users/profile`
  - **Описание:** Получение профиля текущего пользователя
  - **Заголовки:** `Authorization: Bearer <access_token>`
  - **Ответ:** `{ "id": "uuid", "email": "string", "username": "string", "created_at": "datetime", "theme_preference": "light|dark" }`

### Обновление профиля
- **PATCH** `/users/profile`
  - **Описание:** Обновление профиля пользователя
  - **Заголовки:** `Authorization: Bearer <access_token>`
  - **Тело запроса:** `{ "username": "string", "theme_preference": "light|dark" }`
  - **Ответ:** `{ "id": "uuid", "email": "string", "username": "string", "theme_preference": "light|dark" }`

## Игровые сессии

### Создание новой игры
- **POST** `/games`
  - **Описание:** Создание новой игровой сессии
  - **Заголовки:** `Authorization: Bearer <access_token>` (опционально для неавторизованных)
  - **Тело запроса:** `{ "board_size": 3|5|10|30, "win_sequence": 3|4|5, "game_mode": "computer|friend", "model_id": "string", "difficulty": "easy|medium|hard", "player_x_name": "string", "player_o_name": "string" }`
  - **Ответ:** `{ "session_id": "uuid" }`

### Получение информации об игре
- **GET** `/games/{session_id}`
  - **Описание:** Получение текущего состояния игры
  - **Заголовки:** `Authorization: Bearer <access_token>` (опционально)
  - **Параметры:** `session_id` — UUID сессии
  - **Ответ:** `{ "board_size": 3|5|10|30, "win_sequence": 3|4|5, "game_mode": "computer|friend", "status": "in_progress|finished", "created_at": "datetime", "board": [["X"|"O"|null]], "current_turn": "X|O", "player_x_name": "string", "player_o_name": "string", "model_id": "string", "difficulty": "string", "winner": "X|O|draw|null", "winning_cells": [[row, col]], "move_count": number, "finished_at": "datetime|null" }`

### Список игр пользователя
- **GET** `/games`
  - **Описание:** Получение списка игр текущего пользователя
  - **Заголовки:** `Authorization: Bearer <access_token>`
  - **Параметры:** `limit` (default: 20), `offset` (default: 0), `status` (in_progress|finished), `model_id`, `date_from`, `date_to`
  - **Ответ:** `{ "items": [ { "session_id": "uuid", "board_size": number, "game_mode": "computer|friend", "status": "in_progress|finished", "created_at": "datetime", "winner": "X|O|draw|null", "model_id": "string" } ], "total": number, "limit": number, "offset": number }`

### Повтор игры
- **POST** `/games/{session_id}/restart`
  - **Описание:** Перезапуск игры с теми же параметрами
  - **Заголовки:** `Authorization: Bearer <access_token>` (опционально)
  - **Параметры:** `session_id` — UUID сессии
  - **Ответ:** `{ "session_id": "uuid", "board": [[null]], "status": "in_progress", "current_turn": "X" }`

### Выход из игры
- **POST** `/games/{session_id}/exit`
  - **Описание:** Выход из игры с сохранением состояния как незавершенной
  - **Заголовки:** `Authorization: Bearer <access_token>` (опционально)
  - **Параметры:** `session_id` — UUID сессии
  - **Ответ:** `{ "message": "Игра сохранена как незавершенная", "status": "in_progress" }`

## Модели LLM

### Получение списка моделей
- **GET** `/models`
  - **Описание:** Получение списка доступных LLM-моделей
  - **Ответ:** `{ "models": [ { "id": "string", "name": "string", "description": "string", "type": "reasoning|non-reasoning", "enabled": boolean, "manufacturer": "string", "release_date": "date" } ] }`

## Административная панель

### Список пользователей
- **GET** `/admin/users`
  - **Описание:** Получение списка всех пользователей
  - **Заголовки:** `Authorization: Bearer <access_token>` (только админ)
  - **Параметры:** `limit`, `offset`, `search`
  - **Ответ:** `{ "items": [ { "id": "uuid", "email": "string", "username": "string", "created_at": "datetime", "is_active": boolean } ], "total": number }`

### Список игровых сессий
- **GET** `/admin/games`
  - **Описание:** Получение списка всех игровых сессий
  - **Заголовки:** `Authorization: Bearer <access_token>` (только админ)
  - **Параметры:** `limit`, `offset`, `status`, `date_from`, `date_to`
  - **Ответ:** `{ "items": [ { "session_id": "uuid", "user_id": "uuid|null", "board_size": number, "status": "waiting|in_progress|finished", "created_at": "datetime", "winner": "X|O|draw|null" } ], "total": number }`

## WebSocket

### Подключение к игровой сессии
- **WebSocket** `/ws/games/{session_id}`
  - **Описание:** Подключение к игровой сессии для получения обновлений в реальном времени
  - **Заголовки:** `Authorization: Bearer <access_token>` (опционально)
  - **События от сервера:**
    - `game_state` — обновление состояния игры
    - `move_made` — совершен ход
    - `game_over` — игра завершена
    - `computer_thinking` — компьютер обдумывает ход
  - **События от клиента:**
    - `make_move` — выполнить ход
    - `request_computer_move` — запросить ход компьютера

## Общие схемы данных

### GameState
```json
{
  "session_id": "uuid",
  "board": [["X"|"O"|null]],
  "board_size": 3|5|10|30,
  "win_sequence": 3|4|5,
  "game_mode": "computer|friend",
  "status": "waiting|in_progress|finished",
  "current_turn": "X|O",
  "player_x_name": "string",
  "player_o_name": "string",
  "model_id": "string|null",
  "difficulty": "easy|medium|hard|null",
  "winner": "X|O|draw|null",
  "winning_cells": [[row, col]],
  "move_count": 0,
  "created_at": "datetime",
  "started_at": "datetime|null",
  "finished_at": "datetime|null",
  "move_history": [ { "player": "X|O", "row": number, "col": number, "timestamp": "datetime" } ]
}
```

### User
```json
{
  "id": "uuid",
  "email": "string",
  "username": "string",
  "created_at": "datetime",
  "theme_preference": "light|dark",
  "is_active": true,
  "is_admin": false
}
```

## Коды ошибок

| Код | Описание |
|-----|----------|
| 400 | Некорректный запрос |
| 401 | Не авторизован |
| 403 | Доступ запрещен |
| 404 | Ресурс не найден |
| 409 | Конфликт (например, неверный код) |
| 422 | Ошибка валидации |
| 429 | Слишком много запросов |
| 500 | Внутренняя ошибка сервера |
| 503 | Сервис недоступен (LLM) |
