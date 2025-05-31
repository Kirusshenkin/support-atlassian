# AI Confluence Assistant - Сводка проекта

## 📌 О проекте
Slack-бот для интеллектуального поиска и ответов на вопросы по документации Confluence с использованием семантического поиска и генеративного ИИ.

## 🎯 Текущая версия: 1.1
- ✅ Полная реализация базового функционала
- ✅ Мультипровайдерная поддержка LLM
- ✅ Docker-контейнеризация
- ✅ GitHub Actions для CI/CD
- ✅ Подробная документация

## 🚀 Ключевые возможности
1. **Семантический поиск** по документации Confluence
2. **Генерация ответов** с использованием лучших LLM
3. **Slack интеграция** через команду `ask`
4. **Автоматическая индексация** документации по расписанию
5. **Отчеты** о проиндексированных и пропущенных страницах

## 💡 Рекомендуемые LLM провайдеры

### Для максимального качества:
- **Anthropic Claude 3 Sonnet** ⭐⭐⭐⭐⭐
- **OpenAI GPT-4o** ⭐⭐⭐⭐⭐

### Для баланса цены и качества:
- **Google Gemini 1.5 Pro** ⭐⭐⭐⭐
- **OpenAI GPT-4o-mini** ⭐⭐⭐⭐

### Для конфиденциальности:
- **Qwen 2.5** (локальная) ⭐⭐⭐⭐
- **Llama 3.1** (локальная) ⭐⭐⭐⭐

📖 См. [Руководство по выбору LLM](docs/LLM_COMPARISON_GUIDE.md)

## 📂 Структура проекта
```
ai-confluence-assistant/
├── src/
│   ├── ingest_with_report.py    # Индексация Confluence
│   ├── qa_service.py            # API для поиска и генерации
│   └── slack_bot.py             # Slack бот
├── docs/
│   ├── LLM_COMPARISON_GUIDE.md  # Как выбрать LLM
│   ├── CLOUD_LLM_OPTIONS.md     # Облачные провайдеры
│   └── LOCAL_LLM_OPTIONS.md      # Локальные модели
├── docker-compose.yml            # Оркестрация сервисов
├── Dockerfile                    # Multi-stage сборка
└── README.md                     # Документация
```

## 🔮 Планы развития (v2.0)
1. **Анализ релизов** из Slack каналов (#releases, #deployments)
2. **Интеграция с GitHub** для анализа Pull Requests
3. **Корреляция релизов** между различными источниками
4. **Timeline визуализация** изменений

Подробнее: [ROADMAP.md](ROADMAP.md)

## ⚡ Быстрый старт
```bash
# 1. Настройка
cp env.example .env
# Отредактируйте .env (рекомендуется Anthropic Claude)

# 2. Индексация
docker compose run --rm ingest

# 3. Запуск
docker compose up -d api bot

# 4. Использование в Slack
ask как настроить API аутентификацию?
```

## 📊 Статус компонентов
| Компонент | Статус | Версия |
|-----------|--------|--------|
| Ingest Service | ✅ Stable | 1.0 |
| QA API | ✅ Stable | 1.0 |
| Slack Bot | ✅ Stable | 1.0 |
| Multi-LLM Support | ✅ Stable | 1.1 |
| Release Tracker | 🚧 Planned | 2.0 |
| GitHub Integration | 🚧 Planned | 2.0 |

## 🤝 Поддержка
- Issues: GitHub Issues
- Документация: [README.md](README.md)
- Выбор LLM: [docs/LLM_COMPARISON_GUIDE.md](docs/LLM_COMPARISON_GUIDE.md) 