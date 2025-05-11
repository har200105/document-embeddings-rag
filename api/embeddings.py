from langchain.embeddings.base import Embeddings
from typing import List
import requests
from .constants import (OLLAMA_EMBEDDING_MODEL,OLLAMA_EMBEDDING_URL,)



def get_embeddings_ollama(texts: List[str]) -> List[List[float]]:
    embeddings = []
    for text in texts:
        payload = {
            "model": OLLAMA_EMBEDDING_MODEL,
            "prompt": text
        }
        response = requests.post(OLLAMA_EMBEDDING_URL, json=payload)
        response.raise_for_status()
        embeddings.append(response.json()["embedding"])
    return embeddings

class DocumentEmbedding(Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return get_embeddings_ollama(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]
