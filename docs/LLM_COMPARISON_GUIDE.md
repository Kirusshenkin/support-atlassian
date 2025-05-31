# Руководство по выбору LLM для AI Confluence Assistant

## 🎯 Быстрый выбор

### У меня есть бюджет и нужно лучшее качество
→ **Anthropic Claude 3 Sonnet**

### Нужен баланс качества и цены
→ **Google Gemini 1.5 Pro** или **OpenAI GPT-4o-mini**

### Данные не должны покидать инфраструктуру
→ **Локальная модель Qwen 2.5** (14B или 32B)

### Нужна максимальная скорость ответов
→ **Локальная модель на GPU** или **GPT-4o-mini**

## 📊 Детальное сравнение

### По качеству понимания технической документации:
1. **Claude 3 Opus** - эталон качества
2. **GPT-4o** - очень близко к Claude
3. **Claude 3 Sonnet** - отличный баланс
4. **Gemini 1.5 Pro** - хорошее качество
5. **Qwen 2.5 32B** (локальная) - приближается к GPT-3.5
6. **GPT-4o-mini** - достаточно для большинства задач

### По работе с русским языком:
1. **Claude 3 (любая версия)** - превосходно
2. **Qwen 2.5** - отлично, особенно для технических текстов
3. **GPT-4o** - очень хорошо
4. **Saiga-Llama3** - хорошо для локальной модели
5. **YandexGPT Pro** - приемлемо, но уступает всем выше

## 🧪 Как протестировать модели на ваших данных

### 1. Создайте тестовый набор вопросов
Создайте файл `test_questions.txt`:
```
Как настроить аутентификацию в API?
Какие есть ограничения по rate limiting?
Опиши процесс деплоя на production
Какие метрики нужно мониторить?
Как откатить релиз в случае проблем?
```

### 2. Скрипт для сравнения моделей
Создайте `scripts/compare_llms.py`:
```python
import os
import time
from datetime import datetime
import pandas as pd

# Импортируйте вашу фабрику create_llm из qa_service

def test_llm(provider, model, questions):
    """Тестирует LLM на наборе вопросов"""
    os.environ["LLM_PROVIDER"] = provider
    os.environ[f"{provider.upper()}_MODEL"] = model
    
    results = []
    for question in questions:
        start = time.time()
        
        # Здесь вызов вашего QA сервиса
        answer = call_qa_service(question)
        
        duration = time.time() - start
        
        results.append({
            "provider": provider,
            "model": model,
            "question": question,
            "answer": answer,
            "duration": duration
        })
    
    return results

# Конфигурация моделей для теста
models_to_test = [
    ("anthropic", "claude-3-sonnet-20240229"),
    ("openai", "gpt-4o-mini"),
    ("ollama", "qwen2.5:14b"),
    # Добавьте другие модели
]

# Запуск тестов
all_results = []
for provider, model in models_to_test:
    print(f"Тестирую {provider}/{model}...")
    results = test_llm(provider, model, questions)
    all_results.extend(results)

# Сохранение результатов
df = pd.DataFrame(all_results)
df.to_csv(f"llm_comparison_{datetime.now():%Y%m%d_%H%M}.csv")
```

### 3. Критерии оценки

При выборе модели оцените:

✅ **Точность ответов**
- Правильно ли модель поняла вопрос?
- Полный ли ответ?
- Есть ли галлюцинации?

✅ **Полезность**
- Можно ли использовать ответ без правок?
- Достаточно ли деталей?

✅ **Скорость**
- Приемлемо ли время ответа?
- Как масштабируется при нагрузке?

✅ **Стоимость**
- Сколько стоит обработка среднего вопроса?
- Как растут затраты с объемом?

## 💡 Практические советы

### 1. Начните с малого
- Запустите с GPT-4o-mini или Claude Sonnet
- Соберите реальные вопросы пользователей
- Оцените, достаточно ли качества

### 2. Гибридный подход
```python
def smart_llm_selection(question: str):
    # Простые вопросы - быстрая модель
    if len(question.split()) < 10:
        return "gpt-4o-mini"
    
    # Сложные технические вопросы - лучшая модель
    if any(word in question.lower() for word in ["архитектура", "дизайн", "почему"]):
        return "claude-3-sonnet"
    
    # По умолчанию - баланс
    return "gemini-1.5-pro"
```

### 3. Мониторинг качества
- Логируйте все вопросы и ответы
- Собирайте обратную связь пользователей
- Регулярно анализируйте неудачные ответы

## ⚠️ Чего избегать

### ❌ YandexGPT для критичных систем
- Качество значительно ниже альтернатив
- Используйте только если критично хранение в РФ
- Лучше рассмотрите локальную Qwen 2.5

### ❌ Слишком маленькие модели
- Модели меньше 7B параметров часто галлюцинируют
- Для русского языка минимум 14B

### ❌ Экономия на неправильном месте
- Разница в стоимости между GPT-4o-mini и Claude Sonnet небольшая
- Но разница в качестве может быть критичной

## 📈 Рекомендуемая стратегия миграции

1. **Неделя 1-2**: Тестирование с Claude Sonnet
2. **Неделя 3-4**: Параллельное тестирование локальных моделей
3. **Месяц 2**: Оптимизация и выбор финальной конфигурации
4. **Месяц 3**: Внедрение гибридного подхода при необходимости

## 🔗 Полезные ссылки

- [Anthropic Claude](https://www.anthropic.com/claude) - документация
- [OpenAI Platform](https://platform.openai.com/) - консоль и цены
- [Ollama Models](https://ollama.ai/library) - каталог локальных моделей
- [LLM Leaderboard](https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard) - сравнение моделей 