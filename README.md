# AI Confluence Assistant

Slack-бот для ответов на вопросы по документации Confluence с использованием семантического поиска и LLM.

## 🚀 Быстрый старт (5 команд)

```bash
# 1. Клонирование репозитория
git clone https://github.com/your-org/ai-confluence-assistant.git
cd ai-confluence-assistant

# 2. Копирование и настройка переменных окружения
cp env.example .env
# Отредактируйте .env и заполните все необходимые значения

# 3. Первичная индексация документации
docker compose run --rm ingest

# 4. Запуск QA-сервиса и Slack-бота
docker compose up -d api bot

# 5. Проверка статуса
docker compose ps
curl http://localhost:8000/health
```

## 📋 Требования

- Docker и Docker Compose
- Confluence API токен
- Slack Bot и App токены
- LLM на выбор:
  - **Anthropic Claude API** (⭐ рекомендуется для лучшего качества)
  - OpenAI API ключ (проверенный стандарт)
  - Google Gemini (лучшая цена/качество)
  - Локальная модель (Llama, Qwen) - для конфиденциальности
  - [Другие облачные провайдеры](docs/CLOUD_LLM_OPTIONS.md)
- Python 3.11 (для локальной разработки)

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` на основе `.env.example`:

```env
# Confluence
CF_URL=https://your-company.atlassian.net/wiki
CF_USER=bot@company.com
CF_TOKEN=your-confluence-api-token
CF_SPACE=DOCS
CF_PAGES=  # Пусто = все страницы в пространстве

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...

# LLM (рекомендуется Anthropic Claude)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Или используйте OpenAI
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-...
# OPENAI_MODEL=gpt-4o-mini

# Настройки поиска
RETRIEVER_K=4
CHUNK_SIZE=800
CHUNK_OVERLAP=120
```

📖 **Подробнее о выборе LLM:** 
- [Облачные LLM провайдеры](docs/CLOUD_LLM_OPTIONS.md) - сравнение качества и цен
- [Локальные LLM](docs/LOCAL_LLM_OPTIONS.md) - для конфиденциальности и экономии

### Настройка Slack App

1. Создайте новое Slack App на https://api.slack.com/apps
2. Включите Socket Mode и получите App Token
3. Добавьте Bot User и получите Bot Token
4. Добавьте следующие Bot Token Scopes:
   - `app_mentions:read`
   - `channels:history`
   - `chat:write`
   - `im:history`
   - `groups:history`
5. Включите Event Subscriptions для:
   - `app_mention`
   - `message.channels`
   - `message.groups`
   - `message.im`

## 🏗️ Архитектура

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Slack     │────▶│  Slack Bot  │────▶│ QA Service  │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Confluence  │────▶│   Ingest    │────▶│  ChromaDB   │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 📦 Компоненты

### 1. Ingest Service (`src/ingest_with_report.py`)
- Выгружает страницы из Confluence
- Конвертирует HTML в текст
- Создает эмбеддинги и сохраняет в ChromaDB
- Генерирует CSV-отчеты

### 2. QA Service (`src/qa_service.py`)
- FastAPI приложение с endpoint `/ask`
- Семантический поиск по ChromaDB
- Генерация ответов через LLM

### 3. Slack Bot (`src/slack_bot.py`)
- Обрабатывает команды `ask ...`
- Отправляет запросы к QA Service
- Форматирует ответы для Slack

## 🔄 Обновление данных

### Ручное обновление
```bash
docker compose run --rm ingest
```

### Автоматическое обновление (cron)
```bash
docker compose --profile scheduler up -d scheduler
```

### GitHub Actions
Настроен автоматический запуск каждую ночь в 01:30 UTC.

## 📊 Мониторинг

### Проверка здоровья сервисов
```bash
curl http://localhost:8000/health
```

### Просмотр логов
```bash
docker compose logs -f api
docker compose logs -f bot
```

### Просмотр отчетов
```bash
cat report/ingested.csv
cat report/skipped.csv
```

## 🧪 Тестирование

### Локальное тестирование API
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"text": "Where is health endpoint?"}'
```

### Тестирование в Slack
Напишите в любом канале, где есть бот:
```
ask как настроить API?
```

## 🚨 Решение проблем

### Бот не отвечает
1. Проверьте логи: `docker compose logs bot`
2. Проверьте здоровье API: `curl http://localhost:8000/health`
3. Убедитесь, что бот добавлен в канал

### Ошибки индексации
1. Проверьте доступ к Confluence API
2. Проверьте лимиты API (50 req/min)
3. Посмотрите `report/skipped.csv` для деталей

### Пустые ответы
1. Убедитесь, что индексация прошла успешно
2. Проверьте наличие документов в ChromaDB
3. Увеличьте `RETRIEVER_K` для большего контекста

## 📈 Масштабирование

### Увеличение производительности
- Используйте GPU для эмбеддингов
- Переключитесь на Postgres-backed ChromaDB
- Запустите несколько экземпляров QA Service

### Большие объемы документации
- Настройте батчевую обработку в ingest
- Используйте более мощную модель эмбеддингов
- Рассмотрите использование ClickHouse

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Commit изменений
4. Push в branch
5. Создайте Pull Request

## 🚀 Планы развития

См. [ROADMAP.md](ROADMAP.md) для детального плана развития проекта.

Основные направления v2.0:
- 📊 Анализ релизов из Slack каналов
- 🔀 Интеграция с GitHub для анализа Pull Requests
- 🔗 Сопоставление релизов между различными источниками

## 📄 Лицензия

MIT License - см. файл LICENSE

## 📞 Поддержка

- Issues: https://github.com/your-org/ai-confluence-assistant/issues
- Wiki: https://github.com/your-org/ai-confluence-assistant/wiki
- Email: support@company.com # support-atlassian
