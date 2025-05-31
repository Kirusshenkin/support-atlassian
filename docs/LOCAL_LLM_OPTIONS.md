# Локальные LLM для AI Confluence Assistant

## 🏠 Зачем локальные модели?

1. **Конфиденциальность** - данные не покидают вашу инфраструктуру
2. **Экономия** - нет платы за API после развертывания
3. **Контроль** - полный контроль над моделью и её настройками
4. **Скорость** - нет задержек на сетевые запросы
5. **Качество** - современные локальные модели превосходят YandexGPT

## 🆚 Локальные модели vs YandexGPT

| Критерий | Локальные модели | YandexGPT |
|----------|------------------|-----------|
| Качество ответов | ⭐⭐⭐⭐ (Llama 3.1, Qwen 2.5) | ⭐⭐ |
| Русский язык | ⭐⭐⭐⭐⭐ (Qwen 2.5, Saiga) | ⭐⭐⭐⭐ |
| Конфиденциальность | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Стоимость | Только железо | Платно за токены |
| Скорость (с GPU) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Простота настройки | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Вывод**: Если у вас есть GPU сервер или мощный CPU, локальные модели (особенно Qwen 2.5 для русского) дадут лучшее качество, чем YandexGPT.

## 🤖 Рекомендуемые локальные модели

### 1. **Llama 3.1** ⭐ Лучший выбор
```python
# Размеры: 8B, 70B параметров
# Требования: 
# - 8B: минимум 16GB RAM или 8GB VRAM
# - 70B: минимум 64GB RAM или 48GB VRAM

# В requirements.txt
llama-cpp-python>=0.2.0

# В .env
LLM_PROVIDER=llamacpp
MODEL_PATH=./models/llama-3.1-8b-instruct.Q4_K_M.gguf
```

### 2. **Mistral 7B**
```python
# Компактная и эффективная модель
# Требования: 8-16GB RAM

# В .env
LLM_PROVIDER=llamacpp
MODEL_PATH=./models/mistral-7b-instruct-v0.3.Q4_K_M.gguf
```

### 3. **Qwen 2.5** 🌟 Лучший выбор для русского языка
```python
# Превосходно работает с русским и английским
# Качество сопоставимо с GPT-3.5, превосходит YandexGPT
# Размеры: 7B, 14B, 32B, 72B

# В .env
LLM_PROVIDER=llamacpp
MODEL_PATH=./models/qwen2.5-14b-instruct.Q4_K_M.gguf  # рекомендуется 14B
```

**Почему Qwen для русского:**
- Обучена на большом корпусе русских текстов
- Понимает контекст и нюансы русского языка
- Генерирует грамматически правильные ответы
- Работает лучше, чем YandexGPT Pro

### 4. **Saiga (Llama-based)** 🇷🇺
```python
# Оптимизирована для русского языка
# Базируется на Llama 3

# В .env
LLM_PROVIDER=llamacpp
MODEL_PATH=./models/saiga-llama3-8b.Q4_K_M.gguf
```

## 🔧 Настройка локальной модели

### 1. Установка llama-cpp-python:

```bash
# CPU версия
pip install llama-cpp-python

# GPU версия (NVIDIA)
CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python

# GPU версия (Apple Metal)
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
```

### 2. Скачивание модели:

```bash
# Создаем директорию
mkdir -p models

# Скачиваем модель (пример для Llama 3.1)
wget https://huggingface.co/TheBloke/Llama-3.1-8B-Instruct-GGUF/resolve/main/llama-3.1-8b-instruct.Q4_K_M.gguf -O models/llama-3.1-8b-instruct.Q4_K_M.gguf
```

### 3. Обновление qa_service.py:

```python
def create_llm():
    """Фабрика для создания LLM"""
    provider = os.getenv("LLM_PROVIDER", "openai")
    
    if provider == "llamacpp":
        from langchain_community.llms import LlamaCpp
        
        model_path = os.getenv("MODEL_PATH", "./models/llama-3.1-8b-instruct.Q4_K_M.gguf")
        
        # Параметры для GPU
        n_gpu_layers = int(os.getenv("N_GPU_LAYERS", "-1"))  # -1 = все слои на GPU
        
        return LlamaCpp(
            model_path=model_path,
            temperature=0.3,
            max_tokens=2048,
            n_ctx=4096,  # Размер контекста
            n_gpu_layers=n_gpu_layers,
            n_batch=512,
            f16_kv=True,  # Использовать float16 для кэша
            verbose=False
        )
    
    elif provider == "ollama":
        from langchain_community.llms import Ollama
        
        return Ollama(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            temperature=0.3
        )
    
    # ... остальные провайдеры
```

## 🐳 Развертывание через Ollama (проще)

### 1. Установка Ollama:
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Или через Docker
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

### 2. Загрузка модели:
```bash
# Загрузка модели
ollama pull llama3.1:8b

# Или Mistral
ollama pull mistral:7b-instruct

# Или Qwen
ollama pull qwen2.5:7b
```

### 3. Настройка в .env:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

## 📊 Сравнение производительности

| Модель | Размер | RAM/VRAM | Токенов/сек (CPU) | Токенов/сек (GPU) |
|--------|--------|----------|-------------------|-------------------|
| Llama 3.1 8B Q4 | 4.7GB | 8GB | 5-10 | 30-50 |
| Mistral 7B Q4 | 4.1GB | 6GB | 8-15 | 40-60 |
| Qwen 2.5 7B Q4 | 4.5GB | 8GB | 6-12 | 35-55 |
| Llama 3.1 70B Q4 | 40GB | 48GB | 0.5-2 | 10-20 |

## 🚀 Оптимизация производительности

### 1. Квантизация:
- **Q4_K_M** - оптимальный баланс качества и скорости
- **Q5_K_M** - лучше качество, медленнее
- **Q3_K_S** - быстрее, но хуже качество

### 2. Использование GPU:
```env
# Все слои на GPU (если помещается)
N_GPU_LAYERS=-1

# Частично на GPU (если не хватает VRAM)
N_GPU_LAYERS=20
```

### 3. Батчинг:
```python
# Увеличить размер батча для GPU
n_batch=1024  # вместо 512
```

## ⚖️ Облако vs Локально

### Используйте облако если:
- ✅ Нужно максимальное качество (GPT-4, Claude)
- ✅ Нет мощного железа
- ✅ Нужна простота развертывания
- ✅ Переменная нагрузка

### Используйте локально если:
- ✅ Критична конфиденциальность
- ✅ Большой объем запросов
- ✅ Есть GPU сервер
- ✅ Нужен полный контроль

## 🎯 Рекомендации

### Для русскоязычных проектов:
1. **Первый выбор**: Qwen 2.5 14B или 32B (превосходит YandexGPT)
2. **Альтернатива**: Saiga-Llama3 8B (специально для русского)
3. **Если мало памяти**: Qwen 2.5 7B или Mistral 7B

### Общие рекомендации:
1. **Начните с облака** для прототипа (Anthropic Claude)
2. **Тестируйте локальные модели** параллельно
3. **Гибридный подход**: 
   - Локальная модель для базовых вопросов
   - Облачная для сложных случаев

```python
def create_hybrid_llm():
    """Гибридный подход - локальная + облачная модель"""
    
    # Локальная модель для простых запросов
    local_llm = create_local_llm()
    
    # Облачная модель для сложных запросов
    cloud_llm = create_cloud_llm()
    
    # Логика выбора модели
    def select_llm(question: str) -> Any:
        # Простые вопросы - локально
        if len(question) < 50 and "?" in question:
            return local_llm
        # Сложные - в облако
        return cloud_llm
    
    return select_llm 
```
