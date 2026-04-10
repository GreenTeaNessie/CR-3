# FastAPI — Контрольная работа №3
## Установка

```bash
pip install -r requirements.txt
```

Скопируй `.env.example` в `.env` и при необходимости измени значения:

```bash
cp .env.example .env
```

---

## Задания 6.1 / 6.2 / 6.3

Авторизация, хеширование паролей, защита документации.

```bash
uvicorn 6.main:app --reload
```

### Регистрация пользователя

```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'
```

### Вход

```bash
curl -u alice:secret123 http://127.0.0.1:8000/login
```

### Неверный пароль — 401

```bash
curl -u alice:wrongpass http://127.0.0.1:8000/login
```

### Документация (DEV режим, защищена Basic Auth)

```bash
curl -u admin:change_me http://127.0.0.1:8000/docs
```

В `PROD` режиме (`MODE=PROD` в `.env`) `/docs` недоступен совсем.

---

## Задания 6.4 / 6.5 / 7.1

JWT аутентификация, rate limit, роли.

```bash
uvicorn 6_jwt.main:app --reload
```

### Регистрация (1 запрос в минуту)

```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123", "role": "admin"}'
```

Допустимые роли: `admin`, `user`, `guest`.

### Вход — получить токен (5 запросов в минуту)

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'
```

### Защищённый ресурс

```bash
curl http://127.0.0.1:8000/protected_resource \
  -H "Authorization: Bearer <токен>"
```

### RBAC-эндпоинты

```bash
# Только admin
curl http://127.0.0.1:8000/admin -H "Authorization: Bearer <токен>"

# admin и user
curl http://127.0.0.1:8000/user -H "Authorization: Bearer <токен>"

# Все роли
curl http://127.0.0.1:8000/guest -H "Authorization: Bearer <токен>"
```

---

## Задание 8.1

Регистрация пользователей в SQLite (без SQLAlchemy).

```bash
uvicorn 8_sqlite.main:app --reload
```

### Регистрация

```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'
```

### Повторная регистрация — 409

```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "other"}'
```

---

## 8_crud — Задание 8.2

CRUD для задач (Todo) в SQLite.

```bash
uvicorn 8_crud.main:app --reload
```

### Создать задачу

```bash
curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Купить молоко", "description": "2 литра"}'
```

### Получить задачу

```bash
curl http://127.0.0.1:8000/todos/1
```

### Обновить задачу

```bash
curl -X PUT http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Удалить задачу

```bash
curl -X DELETE http://127.0.0.1:8000/todos/1
```
