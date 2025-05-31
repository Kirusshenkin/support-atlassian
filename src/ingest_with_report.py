#!/usr/bin/env python3
"""
Модуль выгрузки и индексации страниц Confluence в векторную БД ChromaDB.
Генерирует CSV-отчеты о проиндексированных и пропущенных страницах.
"""

import os
import sys
import csv
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

from dotenv import load_dotenv
from atlassian import Confluence
from bs4 import BeautifulSoup
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class PageInfo:
    """Информация о странице Confluence"""
    page_id: str
    title: str
    url: str
    space_key: str
    labels: List[str]
    last_modified: str


@dataclass
class ProcessingResult:
    """Результат обработки страницы"""
    page_id: str
    title: str
    url: str
    status: str  # "success" или "skipped"
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    chunks_count: Optional[int] = None


class ConfluenceIngester:
    """Класс для выгрузки и индексации страниц Confluence"""
    
    def __init__(self):
        # Конфигурация из переменных окружения
        self.cf_url = os.getenv("CF_URL", "").rstrip("/")
        self.cf_user = os.getenv("CF_USER")
        self.cf_token = os.getenv("CF_TOKEN")
        self.cf_space = os.getenv("CF_SPACE")
        self.cf_pages = [p.strip() for p in os.getenv("CF_PAGES", "").split(",") if p.strip()]
        
        # Параметры чанкинга
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "800"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "120"))
        
        # Пути
        self.vector_store_path = os.getenv("VECTOR_STORE_PATH", "./vector_store")
        self.report_dir = os.getenv("REPORT_DIR", "./report")
        
        # Модель эмбеддингов
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        
        # Инициализация клиентов
        self._init_confluence()
        self._init_vectorstore()
        
        # Результаты обработки
        self.results: List[ProcessingResult] = []
        
    def _init_confluence(self):
        """Инициализация клиента Confluence"""
        if not all([self.cf_url, self.cf_user, self.cf_token]):
            raise ValueError("Не заданы обязательные параметры Confluence (CF_URL, CF_USER, CF_TOKEN)")
        
        self.confluence = Confluence(
            url=self.cf_url,
            username=self.cf_user,
            password=self.cf_token,
            cloud=True
        )
        logger.info(f"Подключен к Confluence: {self.cf_url}")
        
    def _init_vectorstore(self):
        """Инициализация векторного хранилища ChromaDB"""
        os.makedirs(self.vector_store_path, exist_ok=True)
        
        # Настройки ChromaDB
        chroma_settings = Settings(
            persist_directory=self.vector_store_path,
            anonymized_telemetry=False
        )
        
        # Инициализация эмбеддингов
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Инициализация векторного хранилища
        self.vectorstore = Chroma(
            collection_name="confluence_docs",
            embedding_function=self.embeddings,
            persist_directory=self.vector_store_path,
            client_settings=chroma_settings
        )
        logger.info(f"Инициализировано векторное хранилище: {self.vector_store_path}")
        
    def get_pages(self) -> List[PageInfo]:
        """Получение списка страниц для обработки"""
        pages = []
        
        if self.cf_pages:
            # Загрузка конкретных страниц
            for page_title in self.cf_pages:
                try:
                    page = self.confluence.get_page_by_title(
                        space=self.cf_space,
                        title=page_title
                    )
                    if page:
                        pages.append(self._parse_page_info(page))
                except Exception as e:
                    logger.error(f"Ошибка получения страницы '{page_title}': {e}")
        else:
            # Загрузка всех страниц из пространства
            if not self.cf_space:
                raise ValueError("Не задано пространство Confluence (CF_SPACE)")
            
            start = 0
            limit = 50
            
            while True:
                try:
                    result = self.confluence.get_all_pages_from_space(
                        space=self.cf_space,
                        start=start,
                        limit=limit,
                        expand="metadata.labels"
                    )
                    
                    for page in result:
                        pages.append(self._parse_page_info(page))
                    
                    if len(result) < limit:
                        break
                        
                    start += limit
                    time.sleep(0.5)  # Защита от rate limiting
                    
                except Exception as e:
                    logger.error(f"Ошибка получения страниц из пространства: {e}")
                    break
                    
        logger.info(f"Найдено {len(pages)} страниц для обработки")
        return pages
        
    def _parse_page_info(self, page_data: Dict) -> PageInfo:
        """Парсинг информации о странице"""
        page_id = page_data.get("id", "")
        title = page_data.get("title", "")
        
        # Формирование URL
        url = f"{self.cf_url}/spaces/{self.cf_space}/pages/{page_id}"
        
        # Извлечение меток
        labels = []
        if "metadata" in page_data and "labels" in page_data["metadata"]:
            labels = [label["name"] for label in page_data["metadata"]["labels"]["results"]]
            
        # Дата последнего изменения
        last_modified = page_data.get("version", {}).get("when", "")
        
        return PageInfo(
            page_id=page_id,
            title=title,
            url=url,
            space_key=self.cf_space,
            labels=labels,
            last_modified=last_modified
        )
        
    def process_page(self, page_info: PageInfo) -> ProcessingResult:
        """Обработка одной страницы"""
        try:
            # Получение содержимого страницы
            content = self.confluence.get_page_by_id(
                page_info.page_id,
                expand="body.storage"
            )
            
            if not content or "body" not in content:
                return ProcessingResult(
                    page_id=page_info.page_id,
                    title=page_info.title,
                    url=page_info.url,
                    status="skipped",
                    error_type="NoContent",
                    error_message="Страница не содержит контента"
                )
                
            # Извлечение HTML содержимого
            html_content = content["body"]["storage"]["value"]
            
            # Проверка на неподдерживаемый контент
            if self._has_unsupported_content(html_content):
                return ProcessingResult(
                    page_id=page_info.page_id,
                    title=page_info.title,
                    url=page_info.url,
                    status="skipped",
                    error_type="UnsupportedContentType",
                    error_message="Страница содержит неподдерживаемый контент (draw.io, вложения и т.д.)"
                )
                
            # Конвертация HTML в текст
            text_content = self._html_to_text(html_content)
            
            if not text_content.strip():
                return ProcessingResult(
                    page_id=page_info.page_id,
                    title=page_info.title,
                    url=page_info.url,
                    status="skipped",
                    error_type="EmptyContent",
                    error_message="Страница не содержит текстового контента"
                )
                
            # Добавление метаданных в начало текста
            metadata_text = f"Страница: {page_info.title}\n"
            if page_info.labels:
                metadata_text += f"Метки: {', '.join(page_info.labels)}\n"
            metadata_text += "\n"
            
            full_text = metadata_text + text_content
            
            # Разбиение на чанки
            chunks = self._split_text(full_text)
            
            # Создание документов для векторного хранилища
            documents = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({
                    "page_id": page_info.page_id,
                    "title": page_info.title,
                    "url": page_info.url,
                    "space_key": page_info.space_key,
                    "labels": ", ".join(page_info.labels),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "last_modified": page_info.last_modified
                })
                
            # Добавление в векторное хранилище
            self.vectorstore.add_texts(
                texts=documents,
                metadatas=metadatas
            )
            
            return ProcessingResult(
                page_id=page_info.page_id,
                title=page_info.title,
                url=page_info.url,
                status="success",
                chunks_count=len(chunks)
            )
            
        except Exception as e:
            logger.error(f"Ошибка обработки страницы '{page_info.title}': {e}")
            return ProcessingResult(
                page_id=page_info.page_id,
                title=page_info.title,
                url=page_info.url,
                status="skipped",
                error_type="ProcessingError",
                error_message=str(e)[:120]
            )
            
    def _has_unsupported_content(self, html: str) -> bool:
        """Проверка на наличие неподдерживаемого контента"""
        unsupported_patterns = [
            "ac:name=\"drawio\"",
            "ac:name=\"gliffy\"",
            "ri:attachment",
            "ac:structured-macro",
            "ac:name=\"excel\"",
            "ac:name=\"pdf\"",
            "ac:name=\"viewpdf\""
        ]
        
        html_lower = html.lower()
        return any(pattern in html_lower for pattern in unsupported_patterns)
        
    def _html_to_text(self, html: str) -> str:
        """Конвертация HTML в текст"""
        soup = BeautifulSoup(html, "lxml")
        
        # Удаление скриптов и стилей
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Обработка блоков кода
        for code in soup.find_all("ac:structured-macro", attrs={"ac:name": "code"}):
            code_text = code.get_text(strip=True)
            code.replace_with(f"\n```\n{code_text}\n```\n")
            
        # Обработка PlantUML/Mermaid как текст
        for macro in soup.find_all("ac:structured-macro", attrs={"ac:name": ["plantuml", "mermaid"]}):
            macro_text = macro.get_text(strip=True)
            macro.replace_with(f"\n[Диаграмма {macro.get('ac:name', 'diagram')}]\n{macro_text}\n")
            
        # Извлечение текста
        text = soup.get_text(separator="\n", strip=True)
        
        # Очистка лишних переносов строк
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        text = "\n".join(lines)
        
        return text
        
    def _split_text(self, text: str) -> List[str]:
        """Разбиение текста на чанки"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
        
        return splitter.split_text(text)
        
    def generate_reports(self):
        """Генерация CSV-отчетов"""
        os.makedirs(self.report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Отчет об успешно проиндексированных страницах
        ingested_path = os.path.join(self.report_dir, f"ingested_{timestamp}.csv")
        with open(ingested_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["page_id", "title", "url", "chunks_count", "timestamp"])
            writer.writeheader()
            
            for result in self.results:
                if result.status == "success":
                    writer.writerow({
                        "page_id": result.page_id,
                        "title": result.title,
                        "url": result.url,
                        "chunks_count": result.chunks_count,
                        "timestamp": timestamp
                    })
                    
        # Отчет о пропущенных страницах
        skipped_path = os.path.join(self.report_dir, f"skipped_{timestamp}.csv")
        with open(skipped_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["page_id", "title", "url", "error_type", "error_message"])
            writer.writeheader()
            
            for result in self.results:
                if result.status == "skipped":
                    writer.writerow({
                        "page_id": result.page_id,
                        "title": result.title,
                        "url": result.url,
                        "error_type": result.error_type,
                        "error_message": result.error_message
                    })
                    
        # Создание символических ссылок на последние отчеты
        latest_ingested = os.path.join(self.report_dir, "ingested.csv")
        latest_skipped = os.path.join(self.report_dir, "skipped.csv")
        
        if os.path.exists(latest_ingested):
            os.remove(latest_ingested)
        if os.path.exists(latest_skipped):
            os.remove(latest_skipped)
            
        os.symlink(os.path.basename(ingested_path), latest_ingested)
        os.symlink(os.path.basename(skipped_path), latest_skipped)
        
        logger.info(f"Отчеты сохранены: {ingested_path}, {skipped_path}")
        
    def run(self):
        """Основной процесс выгрузки и индексации"""
        logger.info("Начало процесса индексации Confluence")
        
        try:
            # Получение списка страниц
            pages = self.get_pages()
            
            if not pages:
                logger.warning("Не найдено страниц для обработки")
                return
                
            # Обработка страниц
            success_count = 0
            for i, page in enumerate(pages, 1):
                logger.info(f"Обработка [{i}/{len(pages)}]: {page.title}")
                
                result = self.process_page(page)
                self.results.append(result)
                
                if result.status == "success":
                    success_count += 1
                    logger.info(f"✅ Проиндексировано: {page.title} ({result.chunks_count} чанков)")
                else:
                    logger.warning(f"⚠️ Пропущено: {page.title} - {result.error_type}")
                    
                # Защита от rate limiting
                if i % 10 == 0:
                    time.sleep(1)
                    
            # Сохранение векторного хранилища
            self.vectorstore.persist()
            
            # Генерация отчетов
            self.generate_reports()
            
            # Итоговая статистика
            logger.info(f"\n{'='*50}")
            logger.info(f"Обработка завершена!")
            logger.info(f"Всего страниц: {len(pages)}")
            logger.info(f"Успешно проиндексировано: {success_count}")
            logger.info(f"Пропущено: {len(pages) - success_count}")
            logger.info(f"{'='*50}\n")
            
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            sys.exit(1)


def main():
    """Точка входа"""
    ingester = ConfluenceIngester()
    ingester.run()


if __name__ == "__main__":
    main() 