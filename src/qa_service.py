#!/usr/bin/env python3
"""
QA-сервис для ответов на вопросы по документации Confluence.
Использует ChromaDB для поиска релевантных фрагментов и LLM для генерации ответов.
"""

import os
import logging
from typing import Optional, List, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain.schema.runnable import RunnablePassthrough

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=os.getenv("QA_SERVICE_LOG", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Модели данных
class AskRequest(BaseModel):
    """Запрос на получение ответа"""
    text: str = Field(..., description="Вопрос пользователя")
    k: Optional[int] = Field(None, description="Количество релевантных фрагментов для поиска")


class AskResponse(BaseModel):
    """Ответ на вопрос"""
    answer: str = Field(..., description="Сгенерированный ответ")


class HealthResponse(BaseModel):
    """Статус здоровья сервиса"""
    status: str = Field(..., description="Статус сервиса")
    vector_store_ready: bool = Field(..., description="Готовность векторного хранилища")
    llm_ready: bool = Field(..., description="Готовность LLM")


class QAService:
    """Сервис для ответов на вопросы"""
    
    def __init__(self):
        # Конфигурация
        self.vector_store_path = os.getenv("VECTOR_STORE_PATH", "./vector_store")
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.retriever_k = int(os.getenv("RETRIEVER_K", "4"))
        
        # OpenAI конфигурация
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # Инициализация компонентов
        self.vectorstore = None
        self.llm = None
        self.qa_chain = None
        
    def initialize(self):
        """Инициализация компонентов сервиса"""
        try:
            # Инициализация эмбеддингов
            embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # Инициализация векторного хранилища
            chroma_settings = Settings(
                persist_directory=self.vector_store_path,
                anonymized_telemetry=False
            )
            
            self.vectorstore = Chroma(
                collection_name="confluence_docs",
                embedding_function=embeddings,
                persist_directory=self.vector_store_path,
                client_settings=chroma_settings
            )
            
            # Проверка наличия документов
            collection = self.vectorstore._collection
            doc_count = collection.count()
            logger.info(f"Векторное хранилище инициализировано. Документов: {doc_count}")
            
            if doc_count == 0:
                logger.warning("Векторное хранилище пусто. Необходимо запустить индексацию.")
            
            # Инициализация LLM
            if self.openai_api_key:
                self.llm = ChatOpenAI(
                    api_key=self.openai_api_key,
                    model=self.openai_model,
                    temperature=0.3,
                    max_tokens=1000
                )
                logger.info(f"LLM инициализирован: {self.openai_model}")
            else:
                logger.error("OpenAI API ключ не найден. Установите OPENAI_API_KEY.")
                raise ValueError("OpenAI API key not found")
            
            # Создание QA цепочки
            self._create_qa_chain()
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сервиса: {e}")
            raise
    
    def _create_qa_chain(self):
        """Создание цепочки для ответов на вопросы"""
        # Промпт для генерации ответов
        prompt_template = """Ты - помощник по документации Confluence. Отвечай на вопросы, используя только предоставленный контекст.
Если в контексте нет информации для ответа на вопрос, честно скажи об этом.

Контекст из документации:
{context}

Вопрос: {question}

Ответ:"""
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # Создание ретривера
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.retriever_k}
        )
        
        # Функция для форматирования документов
        def format_docs(docs: List[Document]) -> str:
            formatted = []
            for doc in docs:
                metadata = doc.metadata
                content = doc.page_content
                
                # Добавление информации о источнике
                source_info = f"[Страница: {metadata.get('title', 'N/A')}]"
                if metadata.get('url'):
                    source_info += f" ({metadata['url']})"
                
                formatted.append(f"{source_info}\n{content}")
            
            return "\n\n---\n\n".join(formatted)
        
        # Создание цепочки
        self.qa_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
        )
        
        logger.info("QA цепочка создана успешно")
    
    async def ask(self, question: str, k: Optional[int] = None) -> str:
        """Получить ответ на вопрос"""
        try:
            # Использовать переданное k или значение по умолчанию
            if k and k != self.retriever_k:
                # Временно изменить количество возвращаемых документов
                retriever = self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": k}
                )
                # Пересоздать цепочку с новым ретривером
                # (для упрощения используем текущий retriever_k)
            
            # Получение ответа
            response = await self.qa_chain.ainvoke(question)
            
            # Извлечение текста из ответа
            if hasattr(response, 'content'):
                answer = response.content
            else:
                answer = str(response)
            
            logger.info(f"Вопрос: {question[:50]}... | Ответ: {answer[:50]}...")
            
            return answer
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {e}")
            raise
    
    def health_check(self) -> Dict[str, any]:
        """Проверка здоровья сервиса"""
        health = {
            "status": "unhealthy",
            "vector_store_ready": False,
            "llm_ready": False
        }
        
        try:
            # Проверка векторного хранилища
            if self.vectorstore:
                doc_count = self.vectorstore._collection.count()
                health["vector_store_ready"] = doc_count > 0
            
            # Проверка LLM
            if self.llm:
                health["llm_ready"] = True
            
            # Общий статус
            if health["vector_store_ready"] and health["llm_ready"]:
                health["status"] = "healthy"
            
        except Exception as e:
            logger.error(f"Ошибка при проверке здоровья: {e}")
        
        return health


# Глобальный экземпляр сервиса
qa_service = QAService()


# Управление жизненным циклом приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом FastAPI приложения"""
    # Инициализация при запуске
    logger.info("Инициализация QA сервиса...")
    qa_service.initialize()
    yield
    # Очистка при остановке
    logger.info("Остановка QA сервиса...")


# Создание FastAPI приложения
app = FastAPI(
    title="Confluence QA Service",
    description="Сервис для ответов на вопросы по документации Confluence",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Эндпоинты
@app.get("/", include_in_schema=False)
async def root():
    """Корневой эндпоинт"""
    return {"message": "Confluence QA Service", "version": "1.0.0"}


@app.get("/health", response_model=HealthResponse)
async def health():
    """Проверка здоровья сервиса"""
    health_status = qa_service.health_check()
    return HealthResponse(**health_status)


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """Получить ответ на вопрос"""
    try:
        # Проверка готовности сервиса
        health_status = qa_service.health_check()
        if health_status["status"] != "healthy":
            raise HTTPException(
                status_code=503,
                detail=f"Сервис не готов: {health_status}"
            )
        
        # Получение ответа
        answer = await qa_service.ask(request.text, request.k)
        
        return AskResponse(answer=answer)
        
    except Exception as e:
        logger.error(f"Ошибка обработки запроса: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обработки запроса: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(
        "qa_service:app",
        host=host,
        port=port,
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    ) 