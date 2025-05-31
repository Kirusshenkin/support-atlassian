# Облачные LLM альтернативы для AI Confluence Assistant

## 🏆 Сравнение качества моделей

| Провайдер | Модель | Качество | Русский язык | Скорость | Цена |
|-----------|--------|----------|--------------|----------|------|
| **Anthropic** | Claude 3 Opus | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | $$$$ |
| **Anthropic** | Claude 3 Sonnet | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $$$ |
| **OpenAI** | GPT-4o | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $$$ |
| **Google** | Gemini 1.5 Pro | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $$ |
| **OpenAI** | GPT-4o-mini | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $ |
| **Cohere** | Command R+ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | $$ |
| **YandexGPT** | Pro | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $$ |
| **YandexGPT** | Lite | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $ |

## 🌐 Доступные облачные сервисы

### 1. **Anthropic Claude** ⭐⭐⭐⭐⭐ Лучший выбор
```python
# В requirements.txt
anthropic>=0.25.0

# В .env
ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-3-sonnet-20240229  # оптимальный баланс
# или claude-3-opus-20240229 для максимального качества
```

**Преимущества:**
- Лучшее понимание контекста и инструкций
- Огромное контекстное окно (200K токенов)
- Отлично работает с техническими текстами
- Превосходная работа с русским языком
- Меньше галлюцинаций

**Когда использовать:**
- Когда нужно максимальное качество ответов
- Для работы с большими документами
- Когда важна точность и полнота ответов

### 2. **OpenAI GPT-4** ⭐⭐⭐⭐⭐ Проверенный стандарт
```python
# В requirements.txt
openai>=1.0.0

# В .env
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o  # или gpt-4o-mini для экономии
```

**Преимущества:**
- Индустриальный стандарт
- Стабильное качество
- Большая экосистема
- Хорошая документация

**Когда использовать:**
- Когда нужна проверенная технология
- Для интеграции с существующими OpenAI системами

### 3. **Google Vertex AI (Gemini)** ⭐⭐⭐⭐ Лучшая цена/качество
```python
# В requirements.txt
google-cloud-aiplatform>=1.38.0
langchain-google-vertexai>=0.1.0

# В .env
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
LLM_PROVIDER=vertexai
VERTEX_AI_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-pro
```

**Преимущества:**
- Интеграция с Google Cloud
- Поддержка multimodal (текст + изображения)
- Хорошая цена/качество

### 4. **Amazon Bedrock** ⭐⭐⭐⭐ Гибкий выбор моделей
```python
# В requirements.txt
boto3>=1.28.0
langchain-aws>=0.1.0

# В .env
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_DEFAULT_REGION=us-east-1
LLM_PROVIDER=bedrock
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

**Преимущества:**
- Множество моделей (Claude, Llama, Mistral)
- Pay-per-use
- Интеграция с AWS

### 5. **Azure OpenAI Service** ⭐⭐⭐⭐ Для корпораций
```python
# В requirements.txt
langchain-openai>=0.1.0

# В .env
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-01
LLM_PROVIDER=azure_openai
```

**Преимущества:**
- Корпоративная безопасность
- SLA и поддержка
- Интеграция с Azure экосистемой
- Данные остаются в вашем регионе

### 6. **Cohere** ⭐⭐⭐ Хорошая альтернатива
```python
# В requirements.txt
cohere>=4.0.0
langchain-cohere>=0.1.0

# В .env
COHERE_API_KEY=your-key
LLM_PROVIDER=cohere
COHERE_MODEL=command-r-plus
```

### 7. **Yandex YandexGPT** ⭐⭐ Только если нужны данные в РФ
```python
# В requirements.txt
yandexcloud>=0.250.0

# В .env
YANDEX_CLOUD_API_KEY=your-key
YANDEX_FOLDER_ID=your-folder-id
LLM_PROVIDER=yandexgpt
YANDEX_MODEL=yandexgpt-lite
```

**Преимущества:**
- Данные хранятся в России
- Соответствие 152-ФЗ
- Неплохо работает с русским языком

**Недостатки:**
- Значительно уступает по качеству Claude и GPT-4
- Меньше возможностей
- Склонен к галлюцинациям

**Когда использовать:**
- ТОЛЬКО если критично хранение данных в РФ
- Для простых запросов на русском языке

## 🔧 Как изменить провайдера в проекте

### 1. Обновите `src/qa_service.py`:

```python
from typing import Optional
import os

def create_llm():
    """Фабрика для создания LLM в зависимости от провайдера"""
    provider = os.getenv("LLM_PROVIDER", "openai")
    
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.3
        )
    
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            temperature=0.3
        )
    
    elif provider == "azure_openai":
        from langchain_openai import AzureChatOpenAI
        return AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            temperature=0.3
        )
    
    elif provider == "vertexai":
        from langchain_google_vertexai import ChatVertexAI
        return ChatVertexAI(
            project=os.getenv("VERTEX_AI_PROJECT"),
            location=os.getenv("VERTEX_AI_LOCATION"),
            model=os.getenv("VERTEX_AI_MODEL", "gemini-1.5-pro"),
            temperature=0.3
        )
    
    elif provider == "bedrock":
        from langchain_aws import ChatBedrock
        return ChatBedrock(
            model_id=os.getenv("BEDROCK_MODEL_ID"),
            region_name=os.getenv("AWS_DEFAULT_REGION"),
            model_kwargs={"temperature": 0.3}
        )
    
    elif provider == "yandexgpt":
        from langchain_community.llms import YandexGPT
        return YandexGPT(
            api_key=os.getenv("YANDEX_CLOUD_API_KEY"),
            folder_id=os.getenv("YANDEX_FOLDER_ID"),
            model_name=os.getenv("YANDEX_MODEL", "yandexgpt-lite")
        )
    
    else:
        raise ValueError(f"Неизвестный LLM провайдер: {provider}")
```

### 2. Обновите инициализацию в `QAService`:

```python
def initialize(self):
    """Инициализация компонентов сервиса"""
    try:
        # ... существующий код ...
        
        # Инициализация LLM через фабрику
        self.llm = create_llm()
        logger.info(f"LLM инициализирован: {os.getenv('LLM_PROVIDER', 'openai')}")
        
        # ... остальной код ...
```

## 💰 Сравнение стоимости (на 1М токенов)

| Провайдер | Модель | Input | Output |
|-----------|--------|-------|--------|
| OpenAI | GPT-4o-mini | $0.15 | $0.60 |
| Anthropic | Claude 3 Sonnet | $3.00 | $15.00 |
| Google | Gemini 1.5 Pro | $3.50 | $10.50 |
| Azure OpenAI | GPT-4 | $30.00 | $60.00 |
| YandexGPT | Lite | ₽0.20 | ₽0.40 |
| Cohere | Command R+ | $3.00 | $15.00 |

## 🔒 Безопасность и соответствие

### Для российских компаний:
1. **YandexGPT** - данные в РФ, соответствие 152-ФЗ
2. **Azure OpenAI** - можно выбрать регион (включая Европу)
3. **Приватное развертывание** - см. локальные модели

### Для международных компаний:
1. **Azure OpenAI** - корпоративные SLA
2. **AWS Bedrock** - соответствие различным стандартам
3. **Google Vertex AI** - GDPR compliant

## ✅ Рекомендации

1. **Для максимального качества**: Anthropic Claude 3 Sonnet/Opus
2. **Универсальный выбор**: OpenAI GPT-4o
3. **Для экономии с хорошим качеством**: Google Gemini 1.5 Pro или GPT-4o-mini
4. **Для корпораций**: Azure OpenAI
5. **Для России (если критично)**: Рассмотрите локальные модели вместо YandexGPT

⚠️ **Важно**: Если качество ответов критично для вашего бизнеса, используйте Anthropic Claude или OpenAI GPT-4. Экономия на качестве модели может привести к неточным или вводящим в заблуждение ответам. 