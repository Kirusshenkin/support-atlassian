# Руководство по использованию AI Confluence Assistant

## Содержание

1. [Установка и настройка](#установка-и-настройка)
2. [Использование бота](#использование-бота)
3. [Администрирование](#администрирование)
4. [FAQ](#faq)
5. [Типовые проблемы и решения](#типовые-проблемы-и-решения)
6. [Оптимизация производительности](#оптимизация-производительности)

## Установка и настройка

### Предварительные требования

- Docker 20.10+ и Docker Compose 2.0+
- Минимум 4GB RAM и 10GB свободного места на диске
- Доступ к интернету для скачивания образов и моделей
- Права администратора в Confluence space
- Права на создание Slack App

### Пошаговая установка

#### 1. Настройка Confluence

1. Создайте API токен:
   - Перейдите на https://id.atlassian.com/manage-profile/security/api-tokens
   - Нажмите "Create API token"
   - Сохраните токен в безопасном месте

2. Определите Space для индексации:
   - Откройте нужное пространство в Confluence
   - Скопируйте ключ пространства из URL (например, PROJ)

#### 2. Настройка Slack App

1. Создайте новое приложение:
   ```
   https://api.slack.com/apps → Create New App → From scratch
   ```

2. Настройте Socket Mode:
   - Settings → Socket Mode → Enable Socket Mode
   - Generate App-Level Token с scope `connections:write`
   - Сохраните `xapp-...` токен

3. Настройте Bot User:
   - Features → OAuth & Permissions
   - Добавьте Bot Token Scopes:
     - `app_mentions:read`
     - `channels:history`
     - `channels:read`
     - `chat:write`
     - `groups:history`
     - `groups:read`
     - `im:history`
     - `im:read`
     - `mpim:history`
     - `mpim:read`
   - Install to Workspace
   - Сохраните `xoxb-...` токен

4. Настройте Events:
   - Features → Event Subscriptions → Enable Events
   - Subscribe to bot events:
     - `app_mention`
     - `message.channels`
     - `message.groups`
     - `message.im`
     - `message.mpim`

#### 3. Конфигурация проекта

1. Скопируйте и отредактируйте `.env`:
   ```bash
   cp env.example .env
   nano .env  # или используйте любой редактор
   ```

2. Обязательные параметры:
   ```env
   # Confluence
   CF_URL=https://your-company.atlassian.net/wiki
   CF_USER=your-email@company.com
   CF_TOKEN=your-api-token
   CF_SPACE=PROJ
   
   # Slack
   SLACK_BOT_TOKEN=xoxb-...
   SLACK_APP_TOKEN=xapp-...
   
   # OpenAI
   OPENAI_API_KEY=sk-...
   ```

#### 4. Первый запуск

```bash
# Сборка образов
docker compose build

# Индексация документации (может занять 5-30 минут)
docker compose run --rm ingest

# Запуск сервисов
docker compose up -d api bot

# Проверка логов
docker compose logs -f
```

## Использование бота

### Основные команды

1. **Задать вопрос**:
   ```
   ask как настроить авторизацию?
   ask what is the API endpoint for users?
   ```

2. **Получить справку**:
   ```
   help
   ```

3. **Упоминание бота**:
   ```
   @confluence-bot ask где найти документацию по API?
   ```

### Примеры использования

#### Поиск конкретной информации
```
ask где находится health check endpoint?
ask какие параметры принимает метод createUser?
ask как настроить CORS?
```

#### Поиск best practices
```
ask какие best practices для обработки ошибок?
ask рекомендации по структуре проекта
```

#### Поиск примеров кода
```
ask пример использования authentication
ask как сделать batch запрос?
```

### Лучшие практики

1. **Формулируйте вопросы конкретно**
   - ❌ "как работает API?"
   - ✅ "как авторизоваться в REST API?"

2. **Используйте ключевые слова из документации**
   - Если знаете термины из документации, используйте их

3. **Задавайте уточняющие вопросы**
   - Если первый ответ неполный, уточните контекст

## Администрирование

### Обновление документации

#### Ручное обновление
```bash
docker compose run --rm ingest
```

#### Автоматическое обновление
```bash
# Включить планировщик
docker compose --profile scheduler up -d scheduler

# Проверить статус
docker compose ps scheduler
docker compose logs scheduler
```

#### Обновление через GitHub Actions
- Настроено автоматически на 01:30 UTC
- Ручной запуск: Actions → Nightly Confluence Indexing → Run workflow

### Мониторинг

#### Проверка здоровья системы
```bash
# API статус
curl http://localhost:8000/health | jq

# Количество документов в индексе
docker compose exec api python -c "
from src.qa_service import qa_service
qa_service.initialize()
print(f'Documents: {qa_service.vectorstore._collection.count()}')
"
```

#### Просмотр отчетов
```bash
# Последние проиндексированные страницы
tail -20 report/ingested.csv

# Пропущенные страницы
cat report/skipped.csv | column -t -s,
```

#### Анализ логов
```bash
# Все логи
docker compose logs

# Только ошибки
docker compose logs | grep ERROR

# Следить за логами в реальном времени
docker compose logs -f --tail=100
```

### Backup и восстановление

#### Создание backup
```bash
# Остановить сервисы
docker compose stop

# Создать backup
tar -czf backup-$(date +%Y%m%d).tar.gz vector_store/ report/

# Запустить сервисы
docker compose start
```

#### Восстановление из backup
```bash
# Остановить сервисы
docker compose stop

# Восстановить данные
tar -xzf backup-20240531.tar.gz

# Запустить сервисы
docker compose start
```

### Обновление системы

#### Обновление кода
```bash
git pull origin main
docker compose build
docker compose up -d
```

#### Обновление зависимостей
```bash
# Обновить requirements.txt
pip-compile --upgrade

# Пересобрать образы
docker compose build --no-cache
```

## FAQ

### Q: Сколько времени занимает индексация?
**A:** Зависит от объема документации:
- 100 страниц: ~5 минут
- 500 страниц: ~20 минут
- 1000+ страниц: ~40 минут

### Q: Можно ли индексировать несколько Space?
**A:** Да, укажите их через запятую в `CF_SPACE`:
```env
CF_SPACE=PROJ,DOCS,API
```

### Q: Как ограничить индексацию конкретными страницами?
**A:** Используйте переменную `CF_PAGES`:
```env
CF_PAGES=API Documentation,User Guide,FAQ
```

### Q: Можно ли использовать локальную LLM вместо OpenAI?
**A:** Да, установите llama-cpp-python и настройте модель. Потребуется минимум 8GB VRAM.

### Q: Как изменить язык ответов?
**A:** Измените промпт в `src/qa_service.py`:
```python
prompt_template = """Ты - помощник по документации. Отвечай на русском языке..."""
```

### Q: Можно ли использовать другую модель эмбеддингов?
**A:** Да, измените `EMBEDDING_MODEL` в `.env`:
```env
EMBEDDING_MODEL=intfloat/multilingual-e5-large
```

## Типовые проблемы и решения

### Проблема: Бот не отвечает на сообщения

**Решение 1:** Проверьте, что бот добавлен в канал:
```
/invite @confluence-bot
```

**Решение 2:** Проверьте подключение к Slack:
```bash
docker compose logs bot | grep "Socket Mode"
```

**Решение 3:** Проверьте токены в `.env`

### Проблема: Ошибка "Service not ready"

**Решение:** Дождитесь полной инициализации:
```bash
# Проверить статус
curl http://localhost:8000/health

# Посмотреть логи инициализации
docker compose logs api | grep "инициализ"
```

### Проблема: Ошибка индексации "Rate limit exceeded"

**Решение:** Добавьте задержку в `src/ingest_with_report.py`:
```python
time.sleep(2)  # Увеличить до 2 секунд
```

### Проблема: Ответы не релевантные

**Решение 1:** Увеличьте количество чанков:
```env
RETRIEVER_K=6  # или 8
```

**Решение 2:** Уменьшите размер чанков:
```env
CHUNK_SIZE=600
CHUNK_OVERLAP=150
```

### Проблема: Out of Memory при индексации

**Решение 1:** Обрабатывайте меньшими батчами:
```python
limit = 25  # вместо 50
```

**Решение 2:** Увеличьте память Docker:
```yaml
# docker-compose.yml
services:
  ingest:
    mem_limit: 4g
```

## Оптимизация производительности

### Ускорение индексации

1. **Используйте GPU для эмбеддингов**:
   ```python
   model_kwargs={'device': 'cuda'}
   ```

2. **Параллельная обработка**:
   ```python
   from concurrent.futures import ThreadPoolExecutor
   with ThreadPoolExecutor(max_workers=4) as executor:
       results = executor.map(process_page, pages)
   ```

### Ускорение поиска

1. **Кэширование частых запросов**:
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def cached_search(query: str):
       return vectorstore.similarity_search(query)
   ```

2. **Использование индексов ChromaDB**:
   ```python
   vectorstore = Chroma(
       collection_name="confluence_docs",
       embedding_function=embeddings,
       persist_directory=path,
       collection_metadata={"hnsw:space": "cosine"}
   )
   ```

### Оптимизация памяти

1. **Очистка после обработки**:
   ```python
   import gc
   gc.collect()
   ```

2. **Streaming для больших файлов**:
   ```python
   for chunk in pd.read_csv('large_file.csv', chunksize=1000):
       process_chunk(chunk)
   ```

## Дополнительные ресурсы

- [LangChain документация](https://python.langchain.com/)
- [ChromaDB документация](https://docs.trychroma.com/)
- [Slack Bolt Python](https://slack.dev/bolt-python/)
- [FastAPI документация](https://fastapi.tiangolo.com/)

## Контакты поддержки

- GitHub Issues: [создать issue](https://github.com/your-org/ai-confluence-assistant/issues/new)
- Email: ai-assistant-support@company.com
- Slack: #ai-assistant-support 