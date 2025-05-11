# 🧠 Document Embeddings

This project is a Django-based backend for generating and storing document embeddings using [FAISS](https://github.com/facebookresearch/faiss) as a vector database. It integrates with [Ollama](https://ollama.com/) for generating embeddings via LLaMA 3 and `nomic-embed-text`, and uses Celery for asynchronous task processing.

---

## 🚀 Features

- 🔗 Django-powered backend
- ⚙️ Celery for background processing
- 🧠 Ollama integration with `llama3` and `nomic-embed-text` models
- 📦 FAISS for fast and scalable vector similarity search
- 🚀 Redis as the Celery broker
- 🧪 Easy to set up and extend for various embedding use cases

---

## 🛠️ Setup Instructions

Follow these steps to set up the project on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/har200105/document-embeddings-rag
cd document-embeddings-rag
```

### 2.Set Up Virtual Environment

python -m venv env
source env/bin/activate  # For macOS/Linux


### 3. Install Dependencies
pip install -r requirements.txt

### 4. Install and Setup Postgres in your system

### 5. Install Redis (macOS Users)
brew install redis
brew services start redis


### 6. Install Ollama
Visit https://ollama.com and download Ollama for your operating system. Follow the installation instructions provided on the website.

### 7. Pull Required Models
ollama pull llama3
ollama pull nomic-embed-text

### 8. Run Celery Worker
celery -A documentEmbeddings worker --loglevel=info

### 9. Update the environment variables
Create a .env file inside documentEmbeddings folder (the main project) 
and update the env files for the below values:

```
DB_NAME=
DB_PASSWORD=
DB_USERNAME=
DB_HOST=
DB_PORT=
```


### 10. Run the migrations
Activate the virtualenv and migrate the django models to PSQL
python manage.py makemigrations && python manage.py migrate

### 11. Start the Django Server
python manage.py runserver



###  Potential Improvements

- We can leverage Django Channels for efficient real-time streaming and concurrency handling.
- We can  Utilize asyncio and sync_to_async to enable non-blocking I/O operations.
- We can consider migrating to FastAPI for a fully asynchronous backend with better performance.
- Add a user feedback loop to gather responses on chatbot performance and improve retrieval quality.
- Implement user authentication and authorization for secure, user-specific chat sessions.
- We can enhance chunking and context-building strategies to improve LLM comprehension.
-  Integrate function calling or tool use via LangChain Router Agent for multi-modal task handling (e.g., web search, SQL, FAQs).
- Adding rate limiting and request throttling to prevent abuse and ensure system stability under load.
- We can store chat message tokens for usage-based analytics and cost estimation per session.
