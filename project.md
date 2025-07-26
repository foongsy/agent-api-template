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

### Milestone 1: Project Foundation & Dependencies ✅
- Update project dependencies and setup environment configuration
- Create basic project structure and validate development environment

### Milestone 2: Embedding Service Implementation ✅
- Implement LlamaIndex + BAAI/bge-m3 embedding service in `embeddings.py`
- Create `/api/v1/embeddings` endpoint in `main.py`
- **Architecture Improvement**: Implemented modern FastAPI lifespan events for proper startup validation and service lifecycle management

### Milestone 3: Agent Core with pydantic-ai & Multimodal Support ✅
- ✅ Implement pydantic-ai agent with OpenRouter + Google Gemini integration in `agent.py`
- ✅ Add multimodal support (text + images: JPEG, PNG, GIF, 8MB limit)
- ✅ Add structured output preparation with Pydantic models
- ✅ Fix Google Gemini compatibility issues (additionalProperties warning)
- ✅ Implement proper model configuration (temperature, max_tokens) via agent.run()
- ✅ Add basic Langfuse tracing and tool framework preparation

### Milestone 4: Agent Chat API Endpoint ✅
- ✅ Create `/api/v1/agent/chat` endpoint in `main.py`
- ✅ Integrate agent core with FastAPI for complete workflow
- ✅ Add multimodal input support via FastAPI Form + UploadFile
- ✅ Implement comprehensive error handling and validation

### Milestone 5: Health Monitoring & Final Integration ✅
- ✅ Implement `/api/v1/health` endpoint in `main.py`
- ✅ Complete integration testing and production readiness
- ✅ Add agent service validation to FastAPI lifespan
- ✅ Implement comprehensive health checks for all services

### Milestone 6: Documentation & Deployment Prep
- Generate API documentation and create deployment configuration
- Finalize README and setup instructions

## 4. Key Technical Decisions
- **Framework**: pydantic-ai for agent orchestration and tool management
- **Models**: LlamaIndex with Hugging Face for embeddings (BAAI/bge-m3 default), Google Gemini 2.5 Flash Lite via OpenRouter for agent
- **Tracing**: OpenTelemetry + Langfuse for observability
- **API**: FastAPI for REST endpoints with minimal endpoints (agent chat, embeddings, health)
- **Security**: Firebase authentication handled by API gateway
- **Session Management**: External session management via Firebase (optional for Phase 3)
- **Dependency Management**: uv (as per workspace rules)
- **Application Lifecycle**: Modern FastAPI lifespan events for startup/shutdown management
- **Multimodal Support**: Text + image input (JPEG, PNG, GIF, 8MB limit)

## 5. Success Criteria
- Three core API endpoints are functional and documented
- Embedding endpoint returns results from LlamaIndex with BAAI/bge-m3 model for query embedding
- Agent endpoint supports multimodal input (text + images)
- Prompts are managed via Langfuse
- Tracing is visible in both OpenTelemetry and Langfuse dashboards
- Clean, modular architecture with pydantic-ai
- Private API design suitable for specific app integration
- Robust startup validation and error handling

## 6. Completed Implementation Summary

### ✅ Core Agent Setup - COMPLETED
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

### ✅ Multimodal Support - COMPLETED
- ✅ **Add multimodal input support**:
  - ✅ Support text + image input combinations
  - ✅ Implement image processing and validation
  - ✅ Support JPEG, PNG, GIF formats only
  - ✅ Add 8MB size limit validation for images
  - ✅ Add proper MIME type handling for images
  - ✅ Update request models to handle both text and image inputs

### ✅ Structured Output Preparation - COMPLETED
- ✅ **Define structured output models**:
  - ✅ Create Pydantic models for agent responses (JSON output)
  - ✅ Support different response types (text, structured data, etc.)
  - ✅ Add output validation and error handling
  - ✅ Prepare for future tool integration

### ✅ Configuration & Dependencies - COMPLETED
- ✅ **Update configuration for agent settings**:
  - ✅ Add OpenRouter API key configuration (reuse existing `openrouter_api_key`)
  - ✅ Add agent-specific settings (temperature, max tokens, etc.)
  - ✅ Add multimodal settings (8MB image limit, supported formats: JPEG/PNG/GIF)
  - ✅ Ensure proper secret management for API keys

- ✅ **Add agent dependencies to project**:
  - ✅ Ensure `pydantic-ai-slim[openai]` is properly configured
  - ✅ Add `python-multipart` for form data handling

### ✅ API Integration - COMPLETED
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

### Testing & Validation - COMPLETED ✅
- ✅ **Embedding service tests completed**:
  - ✅ Unit tests for `EmbeddingService` class
  - ✅ Integration tests for `/api/v1/embeddings` endpoint
  - ✅ Error handling and validation tests

- ✅ **Agent service tests completed**:
  - ✅ Test agent initialization and configuration
  - ✅ Test message processing with various inputs
  - ✅ Test multimodal input handling (text + images)
  - ✅ Test image format validation (JPEG, PNG, GIF)
  - ✅ Test image size validation (8MB limit)
  - ✅ Test error handling and retry logic
  - ✅ Test structured output validation

- ✅ **Agent integration tests completed**:
  - ✅ Test `/api/v1/agent/chat` endpoint with text input
  - ✅ Test `/api/v1/agent/chat` endpoint with multimodal input
  - ✅ Test image upload and processing
  - ✅ Test agent health checks
  - ✅ Test error scenarios and edge cases

- ✅ **End-to-End API testing completed**:
  - ✅ Complete API workflow testing
  - ✅ Cross-endpoint integration testing
  - ✅ Performance and concurrent request testing

### Test Coverage Summary
- **Total Tests**: 68 tests (67 passed, 1 skipped)
- **Unit Tests**: 21 agent service tests, 10 embedding service tests
- **Integration Tests**: 16 agent API tests, 10 embedding API tests
- **End-to-End Tests**: 11 comprehensive workflow tests
- **Test Categories**:
  - Agent initialization and configuration
  - Message processing (text-only and multimodal)
  - Image validation (format, size, edge cases)
  - Error handling and validation
  - API response structure validation
  - Processing time measurement
  - Session management
  - Concurrent request handling

### Documentation & Examples - PARTIALLY COMPLETED
- ✅ **Project documentation updated**:
  - ✅ Document agent configuration and usage
  - ✅ Update API documentation for new request/response formats
  - ✅ Document multimodal input handling
  - ✅ Document error handling and validation

### Validation Criteria - COMPLETED
- ✅ Agent service successfully loads Google Gemini 2.5 Flash Lite model via OpenRouter
- ✅ `/api/v1/agent/chat` endpoint processes text input correctly
- ✅ `/api/v1/agent/chat` endpoint processes multimodal input (text + images) correctly
- ✅ Image validation works for supported formats (JPEG, PNG, GIF) and size limits (8MB)
- ✅ Structured output validation works correctly
- ✅ Error handling works for various failure scenarios
- ✅ Performance is acceptable (reasonable response times)
- ✅ Logging provides useful debugging information
- ✅ Application startup validation includes agent service

### Completion Criteria - COMPLETED
- ✅ Agent service loads Google Gemini 2.5 Flash Lite model successfully via OpenRouter
- ✅ `/api/v1/agent/chat` endpoint returns structured responses
- ✅ Multimodal input processing works correctly
- ✅ Error handling works for various scenarios
- ✅ Basic logging and monitoring in place
- ✅ API endpoint tested and validated
- ✅ Agent service integrated into FastAPI lifespan for robust startup validation

## 7. Current Status & Next Steps

### ✅ COMPLETED MILESTONES
- **Milestone 1**: Project Foundation & Dependencies ✅
- **Milestone 2**: Embedding Service Implementation ✅
- **Milestone 3**: Agent Core with pydantic-ai & Multimodal Support ✅
- **Milestone 4**: Agent Chat API Endpoint ✅
- **Milestone 5**: Health Monitoring & Final Integration ✅

### 🔄 CURRENT FOCUS
- **Milestone 6**: Documentation & Deployment Prep
  - [ ] Create comprehensive API documentation
  - [ ] Add deployment configuration (Docker, etc.)
  - [ ] Create usage examples and tutorials
  - [ ] Finalize README with setup instructions

### 🧪 TESTING COMPLETED ✅
- ✅ Agent service unit tests (21 tests)
- ✅ Agent integration tests (16 tests)
- ✅ End-to-end API testing (11 tests)
- ✅ Total: 68 tests (67 passed, 1 skipped)

### 🚀 PRODUCTION READINESS
- All core functionality implemented and working
- API endpoints functional and validated
- Error handling and logging in place
- Ready for testing and deployment preparation 