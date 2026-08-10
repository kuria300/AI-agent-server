# KingsLanding AI 

AI Agent Server is a FastAPI-based backend for running an extensible AI assistant that integrates a local Ollama LLM, Redis for memory, and PostgreSQL (pgvector) for storing document embeddings. The project provides endpoints for chatting with the agent, managing chat history, and uploading documents which are chunked, embedded, and indexed for semantic search.

Key features

- FastAPI application with a clear router structure for agent, file and home endpoints
- Ollama LLM integration (configured via OLLAMA_BASE_URL and OLLAMA_MODEL)
- Redis-backed chat memory to persist session-based conversations
- PostgreSQL with pgvector for storing embeddings and fast semantic search
- File upload pipeline: save -> split -> embed -> store
- Mode-based behavior: general, coding, research (tools and prompts vary by mode)
- Docker Compose configuration with Redis, fats API and Postgres (pgvector image) included

Repository structure (important files)

- main.py — app entrypoint (creates the FastAPI app instance)
- app/__init__.py — application factory and startup/shutdown lifecycle
- app/config.py — environment-backed configuration via Pydantic settings
- app/db.py — async SQLAlchemy engine & session factory
- app/routes/ — API routes (chat, file upload, home, chat-history)
- app/services/ — business logic (agent orchestration, vector pipeline, redis helper)
- app/models/ — SQLAlchemy models (DocumentChunk for embedding storage)
- docker-compose.yaml — preconfigured docker-compose for app, redis, and postgres
- init.sql — DB init script (creates document_chunks table and pgvector extension)
- uploads/ — directory used to persist uploaded files

Quickstart (Development)

1. Create a Python 3.14+ virtual environment and install dependencies:

   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. Provide configuration via a .env file in the repository root. At minimum set:

   DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:<port>/<db>
   REDIS_PASSWORD=hello123
   REDIS_HOST=redis
   REDIS_PORT=6379
   REDIS_DB=0
   REDIS_TTL=604800 #a week
   OLLAMA_BASE_URL=http://127.0.0.1:11434
   OLLAMA_MODEL=llama3.2:3b
   API_KEY=<your-api-key>
   WEATHER_API_KEY=<optional-if-you-use-weather-tool>

3. Run locally with Uvicorn (if Redis/Postgres are available):

   uvicorn main:app --reload --host 0.0.0.0 --port 8000

4. Or run with Docker Compose (recommended for consistent runtime):

   docker compose up --build

   Docker Compose starts three services:
   - fastapi (the app)
   - redis  (configured with password and healthcheck)
   - postgres (pgvector-enabled image; init.sql runs on first startup)

Configuration notes

- The app reads settings from app/config.py and a .env file. See that file for available settings and defaults.
- Ollama must be reachable at OLLAMA_BASE_URL. When running the app inside Docker and Ollama on the host, docker-compose sets OLLAMA_BASE_URL to "http://host.docker.internal:11434" and maps host.docker.internal through extra_hosts.
- Postgres is expected to support pgvector. The provided docker-compose uses the pgvector image and mounts init.sql to create the extension and table automatically.

API Endpoints

- GET /home/
  - Simple health/welcome endpoint.

- POST /api/agent/chat
  - Query parameter: session_id (string)
  - Body: { "question": "...", "mode": "general" }
  - Headers: x-api-key: <API_KEY>
  - Returns: { "message": "agent reply" }

- GET /api/agent/chat-history
  - Query: session_id, mode (optional; default: general)
  - Returns session message history (reads from Redis)

- DELETE /api/agent/history
  - Query: session_id, mode (optional)
  - Clears chat history for a session+mode

- GET /api/agent/summary
  - Returns a list of recent sessions (scanned from Redis)

- POST /files/upload
  - Query parameter: session_id (string)
  - Form field: file (multipart file upload)
  - Allowed types: PDF, text/markdown, plain text, CSV, JSON
  - Max size: 20 MB
  - The file is saved to uploads/, split into chunks, embedded with nomic-embed-text via Ollama embeddings, and stored in Postgres pgvector table document_chunks.

Example curl (chat)

curl -X POST "http://localhost:8000/api/agent/chat?session_id=abc123" \
  -H "x-api-key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello, who are you?","mode":"general"}'

Example curl (upload)

curl -X POST "http://localhost:8000/files/upload?session_id=abc123" \
  -H "x-api-key: ${API_KEY}" \
  -F "file=@./example.pdf"

Development notes

- The app uses an application factory (create_app) so it can be created in tests or run with Uvicorn.
- The lifecycle creates a ThreadPoolExecutor and an OllamaLLM instance stored in app_state for reuse across requests.
- Vector indexing pipeline uses langchain-community loaders and the OllamaEmbeddings wrapper.
- Chat memory is stored in Redis and integrated via RedisChatMessageHistory so agent runs persist and replay history per session+mode.

License

This project is licensed under the MIT License. See LICENSE for details.

Contributing / Contact

contributor: Eugene Kuria Maina

If you want to contribute, open an issue or a pull request describing your changes. For local development, follow the Quickstart steps above and ensure services (Redis, Postgres, Ollama) are reachable.

Acknowledgements

Built with FastAPI, LangChain components, Ollama integrations, Redis, and Postgres + pgvector for embeddings and semantic search.