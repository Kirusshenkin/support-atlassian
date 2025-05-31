#!/usr/bin/env python3
"""
Скрипт валидации настройки окружения для AI Confluence Assistant
"""

import os
import sys
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

def check_env_var(name: str, required: bool = True) -> bool:
    """Проверка переменной окружения"""
    value = os.getenv(name)
    
    if not value and required:
        print(f"❌ {name}: не задано (обязательно)")
        return False
    elif not value:
        print(f"⚠️  {name}: не задано (опционально)")
        return True
    else:
        # Маскирование чувствительных данных
        if "TOKEN" in name or "KEY" in name:
            masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            print(f"✅ {name}: {masked}")
        else:
            print(f"✅ {name}: {value}")
        return True

def main():
    """Основная функция валидации"""
    print("🔍 Проверка настройки окружения для AI Confluence Assistant\n")
    
    errors = 0
    
    print("=== Confluence ===")
    if not check_env_var("CF_URL"):
        errors += 1
    if not check_env_var("CF_USER"):
        errors += 1
    if not check_env_var("CF_TOKEN"):
        errors += 1
    if not check_env_var("CF_SPACE"):
        errors += 1
    check_env_var("CF_PAGES", required=False)
    
    print("\n=== Slack ===")
    if not check_env_var("SLACK_BOT_TOKEN"):
        errors += 1
    if not check_env_var("SLACK_APP_TOKEN"):
        errors += 1
    
    print("\n=== OpenAI ===")
    if not check_env_var("OPENAI_API_KEY"):
        errors += 1
    check_env_var("OPENAI_MODEL", required=False)
    
    print("\n=== Настройки поиска ===")
    check_env_var("RETRIEVER_K", required=False)
    check_env_var("CHUNK_SIZE", required=False)
    check_env_var("CHUNK_OVERLAP", required=False)
    check_env_var("EMBEDDING_MODEL", required=False)
    
    print("\n=== Пути ===")
    check_env_var("VECTOR_STORE_PATH", required=False)
    check_env_var("REPORT_DIR", required=False)
    
    print("\n=== API ===")
    check_env_var("API_HOST", required=False)
    check_env_var("API_PORT", required=False)
    check_env_var("QA_SERVICE_URL", required=False)
    
    print("\n=== Логирование ===")
    check_env_var("LOG_LEVEL", required=False)
    check_env_var("QA_SERVICE_LOG", required=False)
    
    print("\n" + "="*50)
    
    if errors > 0:
        print(f"\n❌ Обнаружено ошибок: {errors}")
        print("\n📝 Скопируйте env.example в .env и заполните обязательные параметры:")
        print("   cp env.example .env")
        print("   nano .env")
        sys.exit(1)
    else:
        print("\n✅ Все обязательные переменные окружения настроены!")
        print("\n🚀 Можете запускать проект:")
        print("   docker compose run --rm ingest  # Индексация документации")
        print("   docker compose up -d api bot     # Запуск сервисов")
        
    # Проверка доступности директорий
    print("\n=== Проверка директорий ===")
    dirs_to_check = ["src", "report", "vector_store", ".github/workflows"]
    for dir_name in dirs_to_check:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"⚠️  {dir_name}/ - не найдено (будет создано автоматически)")

if __name__ == "__main__":
    main() 