# 📨 Lumin Message Service

Микросервис для управления сообщениями в системе Lumin. Обеспечивает создание, редактирование, удаление и получение сообщений, а также пометку сообщений как прочитанных.

## 🚀 Возможности

- ✅ **Создание сообщений** с поддержкой асинхронной обработки через Taskiq
- ✅ **Получение сообщений** по ID
- ✅ **Редактирование текста** сообщений
- ✅ **Пометка сообщений** как прочитанных
- ✅ **Удаление сообщений**
- ✅ **Асинхронная обработка** через NATS JetStream
- ✅ **RESTful API** с документацией OpenAPI
- ✅ **Поддержка UUID** для всех идентификаторов
- ✅ **Валидация данных** через Pydantic модели

## 🏗️ Архитектура

```
┌─────────────────┐     HTTP     ┌──────────────────┐     NATS     ┌─────────────────────┐
│   Клиент        │─────────────▶│   API Gateway    │─────────────▶│   Message Service   │
│   (Web/Mobile)  │◀─────────────│   (Litestar)     │◀─────────────│   (Taskiq Worker)   │
└─────────────────┘              └──────────────────┘              └─────────────────────┘
                                        │                                    │
                                        ▼                                    ▼
                                ┌──────────────────┐                 ┌──────────────────┐
                                │   Контроллеры    │                 │   Обработчики    │
                                │   (REST API)     │                 │   (Commands)     │
                                └──────────────────┘                 └──────────────────┘
```

## 📦 Технологии

- **Python 3.12+** - основной язык
- **Litestar** - веб-фреймворк для API
- **Taskiq** - асинхронная обработка задач
- **NATS JetStream** - брокер сообщений
- **PostgreSQL** - основная база данных
- **Pydantic** - валидация данных
- **Docker** - контейнеризация
- **Uvicorn** - ASGI сервер

## 🔧 Установка и запуск

### 1. Предварительные требования

```bash
# Установите Docker и Docker Compose
# Установите Python 3.12+
# Установите Poetry для управления зависимостями
```

### 2. Клонирование и настройка

```bash
git clone <repository-url>
cd LuminMessageService

# Создайте виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows

# Установите зависимости
poetry install
# или
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env`:

```env
# База данных
DATABASE_URL=postgresql://user:password@localhost:5432/message_service
DATABASE_ECHO=false

# NATS
NATS_URL=nats://localhost:4222
NATS_QUEUE=message_service

# Сервер
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### 4. Запуск с Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Или только определенных сервисов
docker-compose up -d nats postgres
```

### 5. Запуск вручную

**Терминал 1 - NATS:**
```bash
docker run -d --name nats-server -p 4222:4222 -p 8222:8222 nats:latest -js
```

**Терминал 2 - База данных:**
```bash
docker run -d --name postgres -p 5432:5432 \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=message_service \
  postgres:15
```

**Терминал 3 - Taskiq Worker:**
```bash
python -m taskiq worker \
  LuminMessageService.app.application.taskiq.message_commands:broker \
  --workers 4
```

**Терминал 4 - Сервер API:**
```bash
uvicorn LuminMessageService.app.presentation.api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
```

## 📡 API Endpoints

### Сообщения

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/messages/{message_id}` | Получить сообщение по ID |
| `POST` | `/api/messages/` | Создать новое сообщение |
| `PATCH` | `/api/messages/{message_id}/edit_text` | Редактировать текст сообщения |
| `PATCH` | `/api/messages/{message_id}/mark_as_read` | Пометить сообщение как прочитанное |
| `PATCH` | `/api/messages/{message_id}/delete` | Удалить сообщение |

### Примеры запросов

**Создание сообщения:**
```bash
curl -X POST "http://localhost:8000/api/messages/" \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "123e4567-e89b-12d3-a456-426614174000",
    "sender_id": "11111111-1111-1111-1111-111111111111",
    "recipient_id": "22222222-2222-2222-2222-222222222222",
    "chat_id": "33333333-3333-3333-3333-333333333333",
    "text": "Привет! Как дела?",
    "sent_at": "2024-01-07T22:10:00Z",
    "read_at": null,
    "edited_at": null
  }'
```

**Получение сообщения:**
```bash
curl "http://localhost:8000/api/messages/123e4567-e89b-12d3-a456-426614174000"
```

## 📊 Модели данных

### Сообщение (Message)

```python
{
    "id": "uuid",
    "sender_id": "uuid",
    "recipient_id": "uuid",
    "chat_id": "uuid",
    "text": "string",
    "sent_at": "datetime",
    "read_at": "datetime | null",
    "edited_at": "datetime | null",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### Запрос на создание сообщения

```python
{
    "message_id": "uuid",
    "sender_id": "uuid",
    "recipient_id": "uuid",
    "chat_id": "uuid",
    "text": "string (1-5000 символов)",
    "sent_at": "ISO datetime string",
    "read_at": "ISO datetime string | null",
    "edited_at": "ISO datetime string | null"
}
```

## 🔄 Асинхронная обработка

Сервис использует Taskiq для асинхронной обработки операций:

- **Создание сообщений** - через очередь `create_message_task`
- **Редактирование** - через очередь `edit_message_text_task`
- **Пометка прочитанным** - через очередь `mark_as_read_task`
- **Удаление** - через очередь `delete_message_task`
- **Получение по ID** - через очередь `get_message_by_id_task`

## 🐳 Docker Compose

Полная конфигурация для запуска:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: message_service
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  nats:
    image: nats:latest
    ports:
      - "4222:4222"
      - "8222:8222"
    command: "-js --max_pending=10000000 --write_deadline=30s"
    volumes:
      - nats_data:/data
    healthcheck:
      test: ["CMD", "nats", "server", "check", "--healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/message_service
      NATS_URL: nats://nats:4222
    depends_on:
      postgres:
        condition: service_healthy
      nats:
        condition: service_healthy
    restart: unless-stopped

  worker:
    build: .
    command: python -m taskiq worker message_commands:broker --workers 4
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/message_service
      NATS_URL: nats://nats:4222
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  nats_data:
```

## 🧪 Тестирование

```bash
# Запуск тестов
pytest tests/ -v

# Запуск с покрытием кода
pytest tests/ --cov=LuminMessageService --cov-report=html

# Линтинг
flake8 LuminMessageService/
black LuminMessageService/ --check
mypy LuminMessageService/
```

## 📈 Мониторинг

- **API Документация**: `http://localhost:8000/schema` (Swagger/OpenAPI)
- **NATS Мониторинг**: `http://localhost:8222` (JetStream UI)
- **Метрики здоровья**: `http://localhost:8000/health`

## 🔒 Безопасность

- Валидация всех входных данных через Pydantic
- Поддержка CORS
- Подготовка для JWT аутентификации
- SQL-инъекции предотвращаются ORM
- Логирование всех операций

## 📁 Структура проекта

```
LuminMessageService/
├── app/
│   ├── application/          # Бизнес-логика
│   │   ├── commands/         # Команды CQRS
│   │   ├── queries/          # Запросы CQRS
│   │   └── taskiq/           # Taskiq задачи
│   ├── domain/               # Доменная модель
│   │   ├── models/           # Модели домена
│   │   └── common/           # Общие доменные объекты
│   ├── infrastructure/       # Инфраструктура
│   │   ├── persistance/      # Хранение данных
│   │   └── tasks/            # Taskiq конфигурация
│   └── presentation/         # Представление
│       └── api/              # REST API
│           ├── controllers/  # Контроллеры
│           └── main.py       # Точка входа
├── tests/                    # Тесты
├── docker-compose.yml        # Docker конфигурация
├── Dockerfile               # Docker образ
├── pyproject.toml           # Зависимости
└── README.md               # Документация
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для фичи (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - смотрите файл [LICENSE](LICENSE) для деталей.

## 👥 Команда

- **Разработка и поддержка**: Команда Lumin
- **Контакты**: [team@lumin.example.com](mailto:team@lumin.example.com)

## 🙏 Благодарности

- [Litestar](https://litestar.dev/) - отличный ASGI фреймворк
- [Taskiq](https://taskiq-python.github.io/) - простой распределенный планировщик задач
- [NATS](https://nats.io/) - высокопроизводительный брокер сообщений
- Всем контрибьюторам проекта

---

**⭐ Если этот проект был полезен, поставьте звезду на GitHub!**
