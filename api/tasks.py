from celery import shared_task
from .models import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from .embeddings import (DocumentEmbedding,)
from .constants import (ASSET_DIR,)
import logging
import os

logger = logging.getLogger(__name__)


@shared_task
def generate_document_embeddings(asset_id: str, text: str):
    try:
        logger.info("Task started")
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_text(text)

        embedding_model = DocumentEmbedding()
        faiss_index = FAISS.from_texts(chunks, embedding_model)

        file_path = os.path.join(ASSET_DIR, asset_id)
        faiss_index.save_local(file_path)
        
        Document.objects.filter(asset_id=asset_id).update(processed=True,file_path=file_path)

        logger.info(f"Document embeddings generated successfully")

    except Exception as e:
        logger.error(f"Failed to process document {asset_id}: {e}")
