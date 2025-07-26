# Project Plan: AI Agent API Service

## 1. Objective
Build a generic AI agent service with:
- API endpoints for agent interaction and text embedding
- Integration with Hugging Face models
- Prompt management via Langfuse
- Tracing and observability using OpenTelemetry and Langfuse

## 2. Key Components
- **AI Agent Core**: A generic, extensible agent using pydantic-ai framework capable of handling various tasks
- **API Layer**: Minimal RESTful endpoints for agent interaction and query embedding
- **Text Embedding Service**: Single endpoint for generating query embeddings using LlamaIndex with Hugging Face models
- **Prompt Management**: Fetch and manage prompts from Langfuse
- **Tracing & Observability**: Integrate OpenTelemetry and Langfuse for tracing agent actions and API calls

## 3. Implementation Milestones

### Milestone 1: Project Foundation & Dependencies
- Update project dependencies and setup environment configuration
- Create basic project structure and validate development environment

### Milestone 2: Embedding Service Implementation
- Implement LlamaIndex + BAAI/bge-m3 embedding service in `embeddings.py`
- Create `/api/v1/embeddings` endpoint in `main.py`

### Milestone 3: Agent Core with pydantic-ai & Langfuse
- Implement pydantic-ai agent with OpenRouter integration in `agent.py`
- Add basic Langfuse tracing and tool framework

### Milestone 4: Agent Chat API Endpoint
- Create `/api/v1/agent/chat` endpoint in `main.py`
- Integrate agent core with FastAPI for complete workflow

### Milestone 5: Health Monitoring & Final Integration
- Implement `/api/v1/health` endpoint in `main.py`
- Complete integration testing and production readiness

### Milestone 6: Documentation & Deployment Prep
- Generate API documentation and create deployment configuration
- Finalize README and setup instructions

## 4. Key Technical Decisions
- **Framework**: pydantic-ai for agent orchestration and tool management
- **Models**: LlamaIndex with Hugging Face for embeddings (BAAI/bge-m3 default), LLM models from openrouter.ai (OpenAI compatible)
- **Tracing**: OpenTelemetry + Langfuse for observability
- **API**: FastAPI for REST endpoints with minimal endpoints (agent chat, embeddings, health)
- **Security**: Firebase authentication handled by API gateway
- **Session Management**: External session management via Firebase
- **Dependency Management**: uv (as per workspace rules)

## 5. Success Criteria
- Three core API endpoints are functional and documented
- Embedding endpoint returns results from LlamaIndex with BAAI/bge-m3 model for query embedding
- Prompts are managed via Langfuse
- Tracing is visible in both OpenTelemetry and Langfuse dashboards
- Clean, modular architecture with pydantic-ai
- Private API design suitable for specific app integration

## 6. Current Phase Task List: Milestone 1

### Dependency Management Tasks
- [x] Add `pydantic-ai-slim[logfire,openai]` (already exists in pyproject.toml)
- [x] Add `llama-index` and `llama-index-embeddings-huggingface` 
- [x] Add `sentence-transformers` for BAAI/bge-m3 model support
- [x] Add `langfuse` for tracing integration
- [x] Add `uvicorn` for ASGI server
- [x] Add `python-dotenv` for environment variable management
- [x] Run `uv sync` to validate all dependencies install correctly

### Project Structure Tasks
- [x] Create `agent.py` for pydantic-ai agent implementation
- [x] Create `embeddings.py` for LlamaIndex embedding service
- [x] Create `config.py` for configuration management
- [x] Update `.gitignore` to exclude `.env`, `__pycache__/`, `.venv/`

### Environment Configuration Tasks
- [x] Create `.env.example` with required environment variables:
  ```
  OPENROUTER_API_KEY=your_openrouter_key_here
  LANGFUSE_PUBLIC_KEY=pk-lf-your_public_key
  LANGFUSE_SECRET_KEY=sk-lf-your_secret_key
  LANGFUSE_HOST=https://cloud.langfuse.com
  ```
- [x] Create `config.py` for environment variable validation using Pydantic Settings
- [x] Add environment variable loading and validation with proper type safety
- [x] Implement secure secret handling using `SecretStr` for API keys

### Basic Application Setup Tasks
- [x] Update `main.py` to initialize FastAPI app with all three endpoints:
  - `POST /api/v1/agent/chat` (placeholder)
  - `POST /api/v1/embeddings` (placeholder)
  - `GET /api/v1/health` (placeholder)
- [x] Add basic error handling and CORS configuration
- [x] Test FastAPI server starts successfully with `uv run uvicorn main:app --reload`

### Validation Tasks
- [x] Verify all dependencies resolve without conflicts
- [x] Test environment variable loading works correctly
- [x] Confirm FastAPI server starts and serves basic endpoints
- [x] Validate project structure is clean and simple
- [x] Test basic import statements work: `from agent import ...`, `from embeddings import ...`

### Completion Criteria
- FastAPI server runs successfully with all 3 endpoint placeholders
- All dependencies install without conflicts
- Simple, flat project structure is ready for development
- Environment configuration works properly 