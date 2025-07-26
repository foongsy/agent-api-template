# AI Agent API Service

A generic AI agent service with multimodal support, text embedding capabilities, and comprehensive tracing using pydantic-ai, FastAPI, and Langfuse.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Setup
1. **Clone and install dependencies:**
   ```bash
   git clone <repository-url>
   cd agent-api-template
   uv sync
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

3. **Run the service:**
   ```bash
   uv run uvicorn main:app --reload
   ```

### API Endpoints
- `POST /api/v1/agent/chat` - Chat with AI agent (supports text + images)
- `POST /api/v1/embeddings` - Generate text embeddings
- `GET /api/v1/health` - Service health check

### Example Usage
```bash
# Chat with agent
curl -X POST "http://localhost:8000/api/v1/agent/chat" \
  -F "message=Hello, how are you?" \
  -F "session_id=user123"

# Generate embeddings
curl -X POST "http://localhost:8000/api/v1/embeddings" \
  -H "Content-Type: application/json" \
  -d '{"text": "Sample text for embedding"}'

# Check health
curl "http://localhost:8000/api/v1/health"
```

## 📋 Project Overview

### Objective
Build a generic AI agent service with:
- API endpoints for agent interaction and text embedding
- Integration with Hugging Face models
- Prompt management via Langfuse
- Tracing and observability using OpenTelemetry and Langfuse

### Key Components
- **AI Agent Core**: A generic, extensible agent using pydantic-ai framework capable of handling various tasks
- **API Layer**: Minimal RESTful endpoints for agent interaction and query embedding
- **Text Embedding Service**: Single endpoint for generating query embeddings using LlamaIndex with Hugging Face models
- **Prompt Management**: Fetch and manage prompts from Langfuse
- **Tracing & Observability**: Integrate OpenTelemetry and Langfuse for tracing agent actions and API calls

## 🏗️ Architecture

### Implementation Milestones

#### ✅ Milestone 1: Project Foundation & Dependencies
- Update project dependencies and setup environment configuration
- Create basic project structure and validate development environment

#### ✅ Milestone 2: Embedding Service Implementation
- Implement LlamaIndex + BAAI/bge-m3 embedding service in `embeddings.py`
- Create `/api/v1/embeddings` endpoint in `main.py`
- **Architecture Improvement**: Implemented modern FastAPI lifespan events for proper startup validation and service lifecycle management

#### ✅ Milestone 3: Agent Core with pydantic-ai & Multimodal Support
- ✅ Implement pydantic-ai agent with OpenRouter + Google Gemini integration in `agent.py`
- ✅ Add multimodal support (text + images: JPEG, PNG, GIF, 8MB limit)
- ✅ Add structured output preparation with Pydantic models
- ✅ Fix Google Gemini compatibility issues (additionalProperties warning)
- ✅ Implement proper model configuration (temperature, max_tokens) via agent.run()
- ✅ Add basic Langfuse tracing and tool framework preparation

#### ✅ Milestone 4: Agent Chat API Endpoint
- ✅ Create `/api/v1/agent/chat` endpoint in `main.py`
- ✅ Integrate agent core with FastAPI for complete workflow
- ✅ Add multimodal input support via FastAPI Form + UploadFile
- ✅ Implement comprehensive error handling and validation

#### ✅ Milestone 5: Health Monitoring & Final Integration
- ✅ Implement `/api/v1/health` endpoint in `main.py`
- ✅ Complete integration testing and production readiness
- ✅ Add agent service validation to FastAPI lifespan
- ✅ Implement comprehensive health checks for all services

#### 🔄 Milestone 6: Documentation & Deployment Prep
- Generate API documentation and create deployment configuration
- Finalize README and setup instructions

## 🔧 Technical Decisions

### Framework & Models
- **Framework**: pydantic-ai for agent orchestration and tool management
- **Models**: 
  - LlamaIndex with Hugging Face for embeddings (BAAI/bge-m3 default)
  - Google Gemini 2.5 Flash Lite via OpenRouter for agent
- **Tracing**: OpenTelemetry + Langfuse for observability
- **API**: FastAPI for REST endpoints with minimal endpoints (agent chat, embeddings, health)

### Security & Management
- **Security**: Firebase authentication handled by API gateway
- **Session Management**: External session management via Firebase (optional for Phase 3)
- **Dependency Management**: uv (as per workspace rules)
- **Application Lifecycle**: Modern FastAPI lifespan events for startup/shutdown management
- **Multimodal Support**: Text + image input (JPEG, PNG, GIF, 8MB limit)

## ✅ Implementation Status

### Core Agent Setup - COMPLETED
- ✅ **Create basic pydantic-ai agent with OpenRouter + Gemini integration**:
  - ✅ Configure agent with `google/gemini-2.5-flash-lite` model via OpenRouter
  - ✅ Set up proper dependency injection for OpenRouter API keys
  - ✅ Implement basic system prompts/instructions
  - ✅ Add structured output types for responses
  - ✅ Fix Google Gemini compatibility issues (additionalProperties warning)

- ✅ **Implement agent service class**:
  - ✅ Create `AgentService` class to manage agent lifecycle
  - ✅ Add proper initialization and validation
  - ✅ Implement message processing with error handling
  - ✅ Add retry logic and model error handling
  - ✅ Implement proper model configuration (temperature, max_tokens) via agent.run()

### Multimodal Support - COMPLETED
- ✅ **Add multimodal input support**:
  - ✅ Support text + image input combinations
  - ✅ Implement image processing and validation
  - ✅ Support JPEG, PNG, GIF formats only
  - ✅ Add 8MB size limit validation for images
  - ✅ Add proper MIME type handling for images
  - ✅ Update request models to handle both text and image inputs

### Structured Output Preparation - COMPLETED
- ✅ **Define structured output models**:
  - ✅ Create Pydantic models for agent responses (JSON output)
  - ✅ Support different response types (text, structured data, etc.)
  - ✅ Add output validation and error handling
  - ✅ Prepare for future tool integration

### Configuration & Dependencies - COMPLETED
- ✅ **Update configuration for agent settings**:
  - ✅ Add OpenRouter API key configuration (reuse existing `openrouter_api_key`)
  - ✅ Add agent-specific settings (temperature, max tokens, etc.)
  - ✅ Add multimodal settings (8MB image limit, supported formats: JPEG/PNG/GIF)
  - ✅ Ensure proper secret management for API keys

- ✅ **Add agent dependencies to project**:
  - ✅ Ensure `pydantic-ai-slim[openai]` is properly configured
  - ✅ Add `python-multipart` for form data handling

### API Integration - COMPLETED
- ✅ **Enhance `/api/v1/agent/chat` endpoint**:
  - ✅ Replace placeholder with actual agent processing
  - ✅ Add support for multimodal input (text + images)
  - ✅ Add proper request/response validation
  - ✅ **No session management for Phase 3** - focus on basic request/response
  - ✅ Add comprehensive error handling and logging

- ✅ **Add agent health checks**:
  - ✅ Update health endpoint to include agent status
  - ✅ Add agent validation in startup lifecycle
  - ✅ Implement agent readiness checks

## 🧪 Testing

### Test Coverage Summary
- **Total Tests**: 68 tests (67 passed, 1 skipped)
- **Unit Tests**: 21 agent service tests, 10 embedding service tests
- **Integration Tests**: 16 agent API tests, 10 embedding API tests
- **End-to-End Tests**: 11 comprehensive workflow tests

### Test Categories
- Agent initialization and configuration
- Message processing (text-only and multimodal)
- Image validation (format, size, edge cases)
- Error handling and validation
- API response structure validation
- Processing time measurement
- Session management
- Concurrent request handling

### Running Tests
```bash
# Run all tests
uv run pytest tests/

# Run specific test categories
uv run pytest tests/test_agent_unit.py
uv run pytest tests/test_embeddings_integration.py
uv run pytest tests/test_api_e2e.py
```

## 📁 Project Structure

```
agent-api-template/
├── main.py              # FastAPI application entry point
├── agent.py             # AI agent service implementation
├── embeddings.py        # Text embedding service
├── config.py            # Application configuration
├── models.py            # Pydantic models for API
├── pyproject.toml       # Project dependencies and metadata
├── uv.lock              # Locked dependency versions
├── .env.example         # Environment variables template
├── tests/               # Test suite
│   ├── test_agent_unit.py
│   ├── test_agent_integration.py
│   ├── test_embeddings_unit.py
│   ├── test_embeddings_integration.py
│   └── test_api_e2e.py
└── README.md            # This file
```

## 🎯 Success Criteria

- Three core API endpoints are functional and documented
- Embedding endpoint returns results from LlamaIndex with BAAI/bge-m3 model for query embedding
- Agent endpoint supports multimodal input (text + images)
- Prompts are managed via Langfuse
- Tracing is visible in both OpenTelemetry and Langfuse dashboards
- Clean, modular architecture with pydantic-ai
- Private API design suitable for specific app integration
- Robust startup validation and error handling

## 🚀 Production Readiness

- All core functionality implemented and working
- API endpoints functional and validated
- Error handling and logging in place
- Ready for testing and deployment preparation

## 📝 Environment Variables

Create a `.env` file based on `.env.example` with the following variables:

```bash
# API Keys
OPENROUTER_API_KEY=your_openrouter_api_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com

# Application Settings
APP_NAME=AI Agent API
APP_VERSION=1.0.0
APP_DESCRIPTION=Generic AI Agent API Service
DEBUG=false

# Embedding Configuration
EMBEDDING_MODEL_NAME=BAAI/bge-m3
EMBEDDING_DEVICE=cpu

# Agent Configuration
AGENT_MODEL_NAME=google/gemini-2.5-flash-lite
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=1000

# Multimodal Settings
MAX_IMAGE_SIZE_MB=8
SUPPORTED_IMAGE_FORMATS=image/jpeg,image/png,image/gif
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

[Add your license information here] 