# 📨 Lumin Message Service

**Микросервис управления сообщениями** с архитектурой DDD/CQRS/Event Sourcing, построенный на современном стеке Python. Обеспечивает полный жизненный цикл сообщений с поддержкой асинхронной обработки.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Litestar](https://img.shields.io/badge/Litestar-2.0-purple.svg)](https://litestar.dev)
[![Taskiq](https://img.shields.io/badge/Taskiq-Async_Queue-green.svg)](https://taskiq-python.github.io/)
[![NATS](https://img.shields.io/badge/NATS-JetStream-orange.svg)](https://nats.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🎯 Особенности

- **🧠 DDD & CQRS** - Чистая архитектура с разделением команд и запросов
- **📝 Event Sourcing** - Все изменения хранятся как серия доменных событий
- **⚡ Асинхронная обработка** - Распределенная очередь задач через Taskiq + NATS
- **🔍 Полнотекстовый поиск** - Оптимизированный поиск по сообщениям
- **📱 Мультиплатформенность** - Поддержка чатов, групп и каналов
- **🔒 Безопасность** - Валидация, авторизация и аудит операций
- **🚀 Масштабируемость** - Горизонтальное масштабирование через NATS JetStream
- **🧪 Полное тестирование** - Unit, интеграционные и нагрузочные тесты

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Presentation Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │   REST API      │  │   WebSocket     │  │   GraphQL       │     │
│  │   (Litestar)    │  │   (NATS WS)     │  │   (Strawberry)  │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────────────────────────────────────┐
│                          Application Layer                           │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │                     Taskiq Task Dispatcher                  │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐     │     │
│  │  │   Create    │  │    Edit     │  │      Read       │     │     │
│  │  │   Message   │  │   Message   │  │   Operations    │     │     │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘     │     │
│  └─────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────────────────────────────────────┐
│                           Domain Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │   Aggregates    │  │     Events      │  │  Value Objects  │     │
│  │    (Message)    │  │ (MessageSent,   │  │ (MessageText,   │     │
│  │                 │  │   Edited, Read) │  │    ChatType)    │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│  ┌─────────────────┐  ┌─────────────────┐                          │
│  │   Domain        │  │   Repositories  │                          │
│  │   Services      │  │   (Interfaces)  │                          │
│  └─────────────────┘  └─────────────────┘                          │
└─────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────────────────────────────────────┐
│                        Infrastructure Layer                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │PostgreSQL│ │  Redis  │ │  NATS   │ │Taskiq   │ │Elastic-│       │
│  │(Primary) │ │ (Cache) │ │(Queue)  │ │Worker   │ │ Search │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

## 🚀 Быстрый старт

### Предварительные требования

- **Python 3.12+**
- **Docker & Docker Compose**
- **PostgreSQL 15+** (основная база)
- **NATS Server 2.10+** (с поддержкой JetStream)

### Установка и запуск

```bash
# Клонирование репозитория
git clone https://github.com/lumin-team/lumin-message-service.git
cd lumin-message-service

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -e ".[dev]"

# Настройка окружения
cp .env.example .env
# Отредактируйте .env файл под ваши нужды

# Запуск инфраструктуры
docker-compose up -d postgres nats

# Применение миграций
alembic upgrade head
```

### Разработка

```bash
# Запуск API сервера с hot-reload
uvicorn LuminMessageService.app.presentation.api.main:app --reload --port 8000

# В отдельном терминале: запуск Taskiq worker
python -m taskiq worker \
  LuminMessageService.app.application.taskiq.message_commands:broker \
  --workers 4

# Откройте документацию API
open http://localhost:8000/schema
```

### Docker Compose (полный стек)

```bash
# Запуск всех сервисов
docker-compose up --build

# Или только инфраструктура
docker-compose up -d postgres nats redis

# Просмотр логов
docker-compose logs -f api
```

## 📡 API Документация

### Основные эндпоинты

#### Сообщения
```
GET    /api/messages/{message_id}           # Получить сообщение по ID
POST   /api/messages/                       # Создать новое сообщение (асинхронно)
PATCH  /api/messages/{message_id}/edit_text # Редактировать текст сообщения
PATCH  /api/messages/{message_id}/mark_as_read # Пометить как прочитанное
PATCH  /api/messages/{message_id}/delete    # Удалить сообщение
```

#### Чат-комнаты (в разработке)
```
GET    /api/chats/{chat_id}/messages        # Получить историю сообщений
GET    /api/chats/{chat_id}/unread_count    # Количество непрочитанных
POST   /api/chats/{chat_id}/mark_all_read   # Пометить все как прочитанные
```

### Примеры использования

```bash
# Создание сообщения (асинхронно)
curl -X POST "http://localhost:8000/api/messages/" \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "550e8400-e29b-41d4-a716-446655440000",
    "sender_id": "11111111-1111-1111-1111-111111111111",
    "recipient_id": "22222222-2222-2222-2222-222222222222",
    "chat_id": "33333333-3333-3333-3333-333333333333",
    "text": "Привет! Как твои дела? 🚀",
    "sent_at": "2024-01-07T22:10:00Z",
    "read_at": null,
    "edited_at": null
  }'

# Получение сообщения
curl "http://localhost:8000/api/messages/550e8400-e29b-41d4-a716-446655440000"

# Редактирование текста (асинхронно)
curl -X PATCH \
  "http://localhost:8000/api/messages/550e8400-e29b-41d4-a716-446655440000/edit_text" \
  -H "Content-Type: application/json" \
  -d '{"new_text": "Обновленный текст сообщения ✨"}'

# Пометка как прочитанного
curl -X PATCH \
  "http://localhost:8000/api/messages/550e8400-e29b-41d4-a716-446655440000/mark_as_read"
```

## 🏗️ Структура проекта

```
LuminMessageService/
├── app/
│   ├── application/              # Слой приложения
│   │   ├── commands/             # Команды CQRS
│   │   │   ├── create.py         # CreateMessageCommand
│   │   │   ├── edit_text.py      # EditMessageTextCommand
│   │   │   ├── mark_as_read.py   # MarkMessageAsReadCommand
│   │   │   └── delete.py         # DeleteMessageCommand
│   │   ├── queries/              # Запросы CQRS
│   │   │   └── get_by_id.py      # GetMessageByIDQuery
│   │   ├── services/             # Доменные сервисы
│   │   │   └── message_service.py # Сервис сообщений
│   │   └── taskiq/               # Taskiq задачи
│   │       └── message_commands.py # Задачи для брокера
│   ├── domain/                   # Доменный слой
│   │   ├── models/               # Доменные модели
│   │   │   ├── aggregates/       # Агрегаты
│   │   │   │   ├── aggregate_root.py
│   │   │   │   └── message.py    # Message aggregate
│   │   │   ├── entities/         # Сущности
│   │   │   └── common/           # Общие объекты
│   │   │       └── value_objects.py # MessageText, ChatId и др.
│   │   ├── events/               # Доменные события
│   │   │   ├── message_created.py
│   │   │   ├── message_edited.py
│   │   │   └── message_read.py
│   │   └── repositories/         # Интерфейсы репозиториев
│   │       └── message_repository.py
│   ├── infrastructure/           # Инфраструктурный слой
│   │   ├── persistance/          # Персистентность
│   │   │   ├── database.py       # Настройка БД
│   │   │   ├── repositories/     # Репозитории
│   │   │   ├── mappers/          # Data mappers
│   │   │   └── models/           # Модели БД
│   │   ├── tasks/                # Асинхронные задачи
│   │   │   ├── taskiq_broker.py  # NATS брокер
│   │   │   ├── taskiq_service.py # Сервис задач
│   │   │   └── taskiq_tasks.py   # Регистрация задач
│   │   └── dependency_container.py # DI контейнер
│   └── presentation/             # Слой представления
│       └── api/                  # REST API
│           ├── controllers.py    # Контроллеры
│           ├── dependencies.py   # Зависимости
│           └── main.py           # Точка входа
├── tests/                        # Тесты
│   ├── unit/                     # Юнит-тесты
│   ├── integration/              # Интеграционные тесты
│   ├── e2e/                      # End-to-end тесты
│   └── fixtures/                 # Фикстуры
├── migrations/                   # Миграции Alembic
├── scripts/                      # Вспомогательные скрипты
├── docker-compose.yml           # Docker компоновка
├── Dockerfile                   # Docker образ
├── pyproject.toml               # Зависимости и конфигурация
├── alembic.ini                  # Конфигурация миграций
├── .env.example                 # Пример переменных окружения
└── README.md                    # Документация
```

## 🛠️ Технологический стек

### Основные
- **Python 3.12+** - Основной язык разработки
- **Litestar 2.0** - Высокопроизводительный async web framework
- **Taskiq** - Распределенная очередь задач
- **NATS JetStream** - Брокер сообщений с persistence
- **PostgreSQL 15+** - Основная реляционная база
- **Asyncpg** - Асинхронный драйвер PostgreSQL

### Поддерживающие
- **Pydantic v2** - Валидация и сериализация данных
- **SQLAlchemy 2.0** - Современный async ORM
- **Alembic** - Управление миграциями базы
- **Redis** - Кэширование и сессии
- **Docker & Docker Compose** - Контейнеризация
- **Poetry** - Управление зависимостями

### Инструменты разработки
- **Pytest** - Фреймворк для тестирования
- **Black & Ruff** - Форматирование и линтинг
- **MyPy** - Статическая типизация
- **Pre-commit** - Git хуки
- **GitHub Actions** - CI/CD

## 📊 Модели данных

### Message (Агрегат)
```python
{
    "id": "uuid",
    "sender_id": "uuid",
    "recipient_id": "uuid",
    "chat_id": "uuid",
    "text": "MessageText(value: str, min=1, max=5000)",
    "sent_at": "datetime",
    "read_at": "datetime | null",
    "edited_at": "datetime | null",
    "status": "sent | delivered | read | deleted",
    "metadata": {
        "attachments": "list[uuid]",
        "reply_to": "uuid | null",
        "forward_from": "uuid | null"
    },
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### События (Event Sourcing)
```python
# MessageCreated
# MessageTextEdited
# MessageRead
# MessageDeleted
# MessageDelivered
```

## 🔄 Асинхронная обработка

Сервис использует Taskiq + NATS JetStream для надежной асинхронной обработки:

### Очереди задач
```python
# message_commands.py
@broker.task
async def create_message_task(message_data: dict) -> dict:
    """Создание сообщения через очередь"""
    pass

@broker.task  
async def edit_message_text_task(message_id: str, new_text: MessageText) -> dict:
    """Редактирование текста"""
    pass

@broker.task
async def mark_as_read_task(message_id: str) -> dict:
    """Пометка как прочитанного"""
    pass

@broker.task
async def delete_message_task(message_id: str) -> dict:
    """Удаление сообщения"""
    pass

@broker.task
async def get_message_by_id_task(message_id: str) -> dict:
    """Получение сообщения по ID"""
    pass
```

### Конфигурация NATS
```bash
# Запуск NATS с JetStream
nats-server -js --max_pending=10000000 --write_deadline=30s

# Создание стрима для задач
nats stream add TASKIQ_STREAM \
  --subjects="taskiq.>" \
  --retention=workqueue \
  --max-msgs=1000000 \
  --max-bytes=1GB
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest tests/ -v

# С покрытием кода
pytest --cov=LuminMessageService --cov-report=html

# Конкретные категории
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v

# Тесты с Docker
docker-compose run --rm api pytest tests/

# Генерация отчетов
pytest --cov=LuminMessageService \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-report=xml
```

## 🔧 Конфигурация

### Переменные окружения (.env)

```env
# База данных
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/lumin_messages
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
DATABASE_ECHO=false

# NATS JetStream
NATS_URL=nats://localhost:4222
NATS_QUEUE=message_service
NATS_STREAM=TASKIQ_STREAM

# Redis (кэширование)
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=300

# Приложение
APP_ENV=development
APP_DEBUG=true
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
API_PREFIX=/api
```

### Конфигурация Litestar

```python
# main.py
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.logging import LoggingConfig

app = Litestar(
    route_handlers=[...],
    cors_config=CORSConfig(
        allow_origins=["http://localhost:3000"],
        allow_methods=["*"],
        allow_headers=["*"],
    ),
    logging_config=LoggingConfig(
        loggers={
            "lumin_message_service": {
                "level": "INFO",
                "handlers": ["console"],
            }
        }
    ),
    openapi_config=OpenAPIConfig(
        title="Lumin Message Service",
        version="1.0.0",
        description="Микросервис управления сообщениями",
    ),
)
```

## 📊 Мониторинг и логирование

### Встроенные метрики
```bash
# Health check
curl http://localhost:8000/health

# Метрики Prometheus
curl http://localhost:8000/metrics

# Статус очереди задач
curl http://localhost:8000/api/tasks/status
```

### Внешний мониторинг
```bash
# NATS JetStream monitoring
open http://localhost:8222

# База данных
docker-compose exec postgres psql -U user -d lumin_messages

# Логи в реальном времени
docker-compose logs -f api worker
```

## 🚀 Production развертывание

### Kubernetes

```yaml
# k8s/message-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: message-service
  labels:
    app: message-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: message-service
  template:
    metadata:
      labels:
        app: message-service
    spec:
      containers:
      - name: api
        image: ghcr.io/lumin-team/message-service:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: message-service-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Helm Chart

```bash
# Установка через Helm
helm repo add lumin https://charts.lumin.example.com
helm install message-service lumin/message-service \
  --set database.host=postgres-cluster \
  --set nats.url=nats://nats-cluster:4222 \
  --set replicaCount=3 \
  --set resources.requests.memory=512Mi
```

## 🔒 Безопасность

### Встроенные механизмы
- **Валидация данных** - Pydantic v2 с кастомными валидаторами
- **Авторизация** - JWT токены (интеграция с Auth Service)
- **Rate limiting** - Ограничение запросов по IP/пользователю
- **SQL injection protection** - Параметризованные запросы через SQLAlchemy
- **XSS protection** - Экранирование HTML в сообщениях
- **Аудит** - Логирование всех критических операций

### Конфигурация безопасности
```python
# security.py
from litestar.middleware import RateLimitMiddleware

app = Litestar(
    middleware=[
        RateLimitMiddleware(
            rate_limit=("minute", 100),  # 100 запросов в минуту
            exclude=["/health", "/docs"]
        )
    ]
)
```

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! Пожалуйста, следуйте нашим рекомендациям:

### Процесс разработки
1. **Форкните** репозиторий
2. **Создайте ветку** для вашей фичи (`git checkout -b feature/amazing-feature`)
3. **Зафиксируйте изменения** (`git commit -m 'Add amazing feature'`)
4. **Запушьте ветку** (`git push origin feature/amazing-feature`)
5. **Откройте Pull Request**

### Стандарты кода
```bash
# Автоматическое форматирование
black .

# Сортировка импортов
isort .

# Линтинг
ruff check . --fix

# Проверка типов
mypy LuminMessageService/

# Предварительные проверки
pre-commit run --all-files

# Тестирование перед коммитом
pytest tests/unit/ -v
```

### Коммит-конвенции
- `feat:` Новая функциональность
- `fix:` Исправление ошибок
- `docs:` Изменения в документации
- `style:` Форматирование, отсутствующие точки с запятой
- `refactor:` Рефакторинг кода
- `test:` Добавление тестов
- `chore:` Обновление зависимостей, настройки инструментов

## 📄 Лицензия

Этот проект распространяется под лицензией **MIT**. Смотрите файл [LICENSE](LICENSE) для подробностей.

```
MIT License

Copyright (c) 2024 Lumin Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

...
```

## 👥 Команда

- **Архитектура и разработка** - [Lumin Core Team](https://github.com/lumin-team)
- **DevOps и инфраструктура** - [Infrastructure Team](mailto:infra@lumin.example.com)
- **Тестирование и QA** - [Quality Team](mailto:qa@lumin.example.com)
- **Документация** - [Docs Team](mailto:docs@lumin.example.com)

## 🌟 Поддержка проекта

Если вам нравится этот проект, пожалуйста:

1. ⭐ **Поставьте звезду** на GitHub
2. 🐛 **Сообщайте об ошибках** в Issues
3. 💬 **Присоединяйтесь к обсуждениям**
4. 🔄 **Форкните и улучшайте**
5. 📢 **Расскажите о проекте**

## 📞 Контакты и поддержка

- **Issues**: [GitHub Issues](https://github.com/lumin-team/lumin-message-service/issues)
- **Discussions**: [GitHub Discussions](https://github.com/lumin-team/lumin-message-service/discussions)
- **Документация**: [docs.lumin.example.com](https://docs.lumin.example.com)
- **Email**: support@lumin.example.com
- **Twitter**: [@LuminTeam](https://twitter.com/LuminTeam)

## 🏆 Roadmap

### Q1 2024
- [x] Базовая функциональность сообщений
- [x] Интеграция с NATS JetStream
- [x] Асинхронная обработка через Taskiq
- [ ] Реализация Event Sourcing

### Q2 2024
- [ ] Поддержка групповых чатов
- [ ] Вложения и медиа-файлы
- [ ] Поиск по сообщениям (Elasticsearch)
- [ ] Push-уведомления

### Q3 2024
- [ ] Шифрование end-to-end
- [ ] Голосовые сообщения
- [ ] Видео-звонки (WebRTC)
- [ ] Боты и интеграции

### Q4 2024
- [ ] Машинное обучение (антиспам, модерация)
- [ ] Аналитика и отчеты
- [ ] Мобильные SDK
- [ ] Enterprise-функции

---

<div align="center">

### 🌈 Сделано с ❤️ командой Lumin

**Объединяем людей через технологии**

[![Website](https://img.shields.io/badge/Website-lumin.example.com-blue)](https://lumin.example.com)
[![Twitter](https://img.shields.io/badge/Twitter-@LuminTeam-1DA1F2)](https://twitter.com/LuminTeam)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Lumin_Team-0077B5)](https://linkedin.com/company/lumin-team)
[![Discord](https://img.shields.io/badge/Discord-Join-7289DA)](https://discord.gg/lumin)

</div>
