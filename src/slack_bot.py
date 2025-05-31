#!/usr/bin/env python3
"""
Slack-бот для ответов на вопросы по документации Confluence.
Использует Socket Mode для подключения к Slack.
"""

import os
import re
import logging
import asyncio
from typing import Optional, Dict, Any

import aiohttp
from dotenv import load_dotenv
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConfluenceQABot:
    """Slack-бот для работы с документацией Confluence"""
    
    def __init__(self):
        # Конфигурация Slack
        self.slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.slack_app_token = os.getenv("SLACK_APP_TOKEN")
        
        if not self.slack_bot_token or not self.slack_app_token:
            raise ValueError("Не заданы токены Slack (SLACK_BOT_TOKEN, SLACK_APP_TOKEN)")
        
        # URL QA-сервиса
        self.qa_service_url = os.getenv("QA_SERVICE_URL", "http://localhost:8000")
        
        # Инициализация Slack App
        self.app = AsyncApp(token=self.slack_bot_token)
        
        # Регистрация обработчиков
        self._register_handlers()
        
        # HTTP сессия для запросов к QA-сервису
        self.http_session: Optional[aiohttp.ClientSession] = None
        
    def _register_handlers(self):
        """Регистрация обработчиков событий Slack"""
        
        # Обработка команды "ask ..."
        @self.app.message(re.compile(r"^ask\s+(.+)", re.IGNORECASE))
        async def handle_ask_command(message, say, context):
            """Обработка команды ask"""
            try:
                # Извлечение вопроса из сообщения
                question = context["matches"][0]
                user_id = message.get("user")
                channel_id = message.get("channel")
                
                logger.info(f"Получен вопрос от {user_id}: {question}")
                
                # Отправка сообщения о начале обработки
                thinking_message = await say(
                    text="🤔 Ищу ответ в документации...",
                    thread_ts=message.get("ts")
                )
                
                # Получение ответа от QA-сервиса
                answer = await self._get_answer(question)
                
                # Форматирование ответа
                if answer:
                    response_text = self._format_response(question, answer)
                else:
                    response_text = "❌ Извините, не удалось получить ответ. Попробуйте позже."
                
                # Обновление сообщения с ответом
                await self.app.client.chat_update(
                    channel=channel_id,
                    ts=thinking_message["ts"],
                    text=response_text,
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": response_text
                            }
                        }
                    ]
                )
                
            except Exception as e:
                logger.error(f"Ошибка обработки команды ask: {e}")
                await say(
                    text=f"❌ Произошла ошибка при обработке запроса: {str(e)}",
                    thread_ts=message.get("ts")
                )
        
        # Обработка упоминаний бота
        @self.app.event("app_mention")
        async def handle_app_mention(event, say):
            """Обработка упоминаний бота"""
            try:
                text = event.get("text", "")
                user_id = event.get("user")
                
                # Проверка на команду ask в упоминании
                ask_match = re.search(r"ask\s+(.+)", text, re.IGNORECASE)
                
                if ask_match:
                    question = ask_match.group(1)
                    logger.info(f"Упоминание с вопросом от {user_id}: {question}")
                    
                    # Отправка ответа в треде
                    thinking_message = await say(
                        text="🤔 Ищу ответ в документации...",
                        thread_ts=event.get("ts")
                    )
                    
                    answer = await self._get_answer(question)
                    
                    if answer:
                        response_text = self._format_response(question, answer)
                    else:
                        response_text = "❌ Извините, не удалось получить ответ."
                    
                    await self.app.client.chat_update(
                        channel=event["channel"],
                        ts=thinking_message["ts"],
                        text=response_text,
                        blocks=[
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": response_text
                                }
                            }
                        ]
                    )
                else:
                    # Отправка справки
                    help_text = self._get_help_text()
                    await say(
                        text=help_text,
                        thread_ts=event.get("ts")
                    )
                    
            except Exception as e:
                logger.error(f"Ошибка обработки упоминания: {e}")
                await say(
                    text=f"❌ Произошла ошибка: {str(e)}",
                    thread_ts=event.get("ts")
                )
        
        # Обработка команды help
        @self.app.message(re.compile(r"^help$", re.IGNORECASE))
        async def handle_help(message, say):
            """Показать справку"""
            help_text = self._get_help_text()
            await say(
                text=help_text,
                thread_ts=message.get("ts")
            )
    
    async def _get_answer(self, question: str) -> Optional[str]:
        """Получить ответ от QA-сервиса"""
        try:
            # Создание HTTP сессии если её нет
            if not self.http_session:
                self.http_session = aiohttp.ClientSession()
            
            # Запрос к QA-сервису
            url = f"{self.qa_service_url}/ask"
            payload = {"text": question}
            
            async with self.http_session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("answer")
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка QA-сервиса: {response.status} - {error_text}")
                    return None
                    
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка подключения к QA-сервису: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе к QA-сервису: {e}")
            return None
    
    def _format_response(self, question: str, answer: str) -> str:
        """Форматирование ответа для Slack"""
        # Экранирование специальных символов Slack
        answer = answer.replace("&", "&amp;")
        answer = answer.replace("<", "&lt;")
        answer = answer.replace(">", "&gt;")
        
        # Форматирование ответа
        response = f"*Вопрос:* {question}\n\n"
        response += f"*Ответ:*\n{answer}"
        
        return response
    
    def _get_help_text(self) -> str:
        """Получить текст справки"""
        return """👋 Привет! Я - бот-помощник по документации Confluence.

*Как мной пользоваться:*
• Напишите `ask <ваш вопрос>` чтобы получить ответ из документации
• Упомяните меня и добавьте `ask <вопрос>` для ответа в треде
• Напишите `help` для показа этой справки

*Примеры:*
• `ask как настроить API?`
• `ask where is health endpoint?`
• `@confluence-bot ask какие есть best practices?`

💡 Я ищу ответы только в проиндексированной документации Confluence."""
    
    async def start(self):
        """Запуск бота"""
        try:
            # Проверка доступности QA-сервиса
            await self._check_qa_service()
            
            # Создание Socket Mode handler
            handler = AsyncSocketModeHandler(self.app, self.slack_app_token)
            
            logger.info("Slack-бот запущен и готов к работе!")
            
            # Запуск бота
            await handler.start_async()
            
        except Exception as e:
            logger.error(f"Ошибка запуска бота: {e}")
            raise
    
    async def _check_qa_service(self):
        """Проверка доступности QA-сервиса"""
        try:
            if not self.http_session:
                self.http_session = aiohttp.ClientSession()
            
            url = f"{self.qa_service_url}/health"
            async with self.http_session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        logger.info("QA-сервис доступен и готов к работе")
                    else:
                        logger.warning(f"QA-сервис не готов: {data}")
                else:
                    logger.error(f"QA-сервис недоступен: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"Не удалось подключиться к QA-сервису: {e}")
            logger.warning("Бот будет работать, но ответы могут быть недоступны")
    
    async def stop(self):
        """Остановка бота"""
        if self.http_session:
            await self.http_session.close()
        logger.info("Slack-бот остановлен")


async def main():
    """Основная функция"""
    bot = ConfluenceQABot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main()) 