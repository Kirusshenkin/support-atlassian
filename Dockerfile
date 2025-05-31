# Многоэтапная сборка для оптимизации размера образа
FROM python:3.11-slim as builder

# Установка системных зависимостей для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Установка Python зависимостей
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Финальный образ
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для запуска приложения
RUN useradd -m -u 1000 appuser

# Копирование зависимостей из builder
COPY --from=builder /root/.local /home/appuser/.local

# Установка рабочей директории
WORKDIR /app

# Копирование исходного кода
COPY --chown=appuser:appuser . .

# Создание необходимых директорий
RUN mkdir -p /app/vector_store /app/report && \
    chown -R appuser:appuser /app

# Переключение на пользователя appuser
USER appuser

# Добавление локальных пакетов в PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Переменные окружения по умолчанию
ENV PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO

# Health check для проверки состояния контейнера
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Точка входа по умолчанию (можно переопределить в docker-compose)
CMD ["python", "-m", "src.qa_service"] 