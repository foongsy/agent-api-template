# FastAPI → Flask Migration Plan

## 🔄 **Migration Strategy: "All-in-One" Approach**

Since our codebase is relatively small and well-structured, we'll use the all-in-one migration approach rather than gradual migration.

Based on research from:
- [Flask-Pydantic](https://github.com/pallets-eco/flask-pydantic) - Pydantic integration for Flask
- [Forethought's Flask to FastAPI Migration](https://engineering.forethought.ai/blog/2022/12/01/migrating-from-flask-to-fastapi-part-1/) - Migration strategies

---

## **Phase 1: Pre-Migration Preparation** ⚙️

### **Task 1.1: Code Quality & Formatting**
- [ ] **Format codebase with Black** (if not already done)
  ```bash
  uv add --dev black
  uv run black .
  ```
- [ ] **Sort imports with isort** 
  ```bash
  uv add --dev isort
  uv run isort . --profile black
  ```
- [ ] **Remove unused imports with ruff**
  ```bash
  uv add --dev ruff  
  uv run ruff check --select F401 --fix .
  ```

### **Task 1.2: Test Coverage Verification**
- [ ] **Run full test suite** to ensure 100% passing
  ```bash
  uv run pytest tests/ -v
  ```
- [ ] **Document current test coverage**
  ```bash
  uv add --dev pytest-cov
  uv run pytest --cov=. --cov-report=html
  ```
- [ ] **Verify all API endpoints work** with current implementation

### **Task 1.3: Backup & Version Control**
- [ ] **Create migration branch**
  ```bash
  git checkout -b migrate-to-flask
  ```
- [ ] **Tag current FastAPI version**
  ```bash
  git tag fastapi-final-version
  ```

---

## **Phase 2: Dependencies & Environment Setup** 📦

### **Task 2.1: Update Dependencies**
- [ ] **Remove FastAPI dependencies**
  ```bash
  uv remove fastapi uvicorn python-multipart
  ```
- [ ] **Add Flask dependencies**
  ```bash
  uv add flask flask-pydantic flask-cors
  ```
- [ ] **Add async support for Flask**
  ```bash
  uv add gunicorn[gthread] # for production async support
  ```

### **Task 2.2: Verify Compatibility**
- [ ] **Check Python version compatibility** (Flask 3.0+ requires Python 3.8+)
- [ ] **Verify Pydantic compatibility** with Flask-Pydantic
- [ ] **Test import statements**
  ```bash
  uv run python -c "import flask; import flask_pydantic; print('✅ Imports successful')"
  ```

---

## **Phase 3: Core Application Migration** 🔧

### **Task 3.1: Create Flask Application Structure**
- [ ] **Create new `flask_main.py`** (parallel to existing `main.py`)
- [ ] **Set up Flask app with basic configuration**
  ```python
  from flask import Flask
  from flask_pydantic import validate
  from flask_cors import CORS
  
  app = Flask(__name__)
  CORS(app)
  ```

### **Task 3.2: Migrate Configuration**
- [ ] **Update `config.py`** to work with Flask configuration
- [ ] **Add Flask-specific configuration variables**
  ```python
  # Add to config.py
  flask_debug: bool = Field(default=False, description="Flask debug mode")
  flask_host: str = Field(default="0.0.0.0", description="Flask host")
  flask_port: int = Field(default=8000, description="Flask port")
  ```

### **Task 3.3: Migrate Application Lifecycle**
- [ ] **Convert FastAPI lifespan to Flask startup/teardown**
  ```python
  @app.before_first_request
  async def startup():
      # Initialize services
      langfuse_service.initialize()
      await embedding_service.validate_model()
      await agent_service.validate_agent()
  
  @app.teardown_appcontext
  def shutdown(error):
      # Cleanup resources
      pass
  ```

---

## **Phase 4: API Endpoints Migration** 🌐

### **Task 4.1: Create Pydantic Models for Flask**
- [ ] **Create form models for multipart data**
  ```python
  # Add to models.py
  class ChatFormModel(BaseModel):
      message: str = Field(..., min_length=1, max_length=10000)
      session_id: Optional[str] = Field(None)
      # Note: images will be handled separately in Flask
  ```

### **Task 4.2: Migrate Health Endpoint**
- [ ] **Convert `/api/v1/health` endpoint**
  ```python
  @app.route("/api/v1/health", methods=["GET"])
  @validate()
  async def health_check() -> HealthResponse:
      # Same logic as FastAPI version
  ```

### **Task 4.3: Migrate Embeddings Endpoint**
- [ ] **Convert `/api/v1/embeddings` endpoint**
  ```python
  @app.route("/api/v1/embeddings", methods=["POST"])
  @validate()
  async def get_embeddings(body: EmbeddingRequest) -> EmbeddingResponse:
      # Same logic as FastAPI version
  ```

### **Task 4.4: Migrate Chat Endpoint (Complex)**
- [ ] **Convert `/api/v1/agent/chat` with file handling**
  ```python
  @app.route("/api/v1/agent/chat", methods=["POST"])
  @validate()
  async def chat_with_agent(form: ChatFormModel) -> ChatResponse:
      # Handle files separately with request.files
      images = request.files.getlist('images')
      # Convert to existing logic
  ```

### **Task 4.5: Migrate Root Endpoint**
- [ ] **Convert root `/` endpoint**
  ```python
  @app.route("/", methods=["GET"])
  def root():
      return {
          "message": "AI Agent API Service (Flask)",
          "version": settings.app_version,
          "docs": "/docs" if settings.docs_enabled else None,
          "health": "/api/v1/health"
      }
  ```

---

## **Phase 5: Service Layer Compatibility** 🔄

### **Task 5.1: Update Service Imports**
- [ ] **Verify all service classes work unchanged**
  - `AgentService` - should work as-is
  - `EmbeddingService` - should work as-is  
  - `LangfuseService` - should work as-is

### **Task 5.2: Test Service Integration**
- [ ] **Test agent service with Flask context**
- [ ] **Test embedding service with Flask context**
- [ ] **Test Langfuse tracing integration**

---

## **Phase 6: File Upload Handling** 📁

### **Task 6.1: Implement Flask File Upload**
- [ ] **Create file validation utility**
  ```python
  def validate_flask_files(files):
      """Convert Flask FileStorage to bytes and MIME types"""
      image_bytes = []
      mime_types = []
      
      for file in files:
          if file.filename:
              content = file.read()
              image_bytes.append(content)
              mime_types.append(file.content_type)
      
      return image_bytes, mime_types
  ```

### **Task 6.2: Update Chat Endpoint File Handling**
- [ ] **Integrate file validation with existing logic**
- [ ] **Ensure compatibility with `AgentService._validate_images()`**

---

## **Phase 7: Testing & Validation** 🧪

### **Task 7.1: Update Test Suite**
- [ ] **Update test imports**
  ```python
  # Replace in test files
  from fastapi.testclient import TestClient
  # with
  from flask.testing import FlaskClient
  ```

### **Task 7.2: Create Flask Test Client**
- [ ] **Update `conftest.py` or test setup**
  ```python
  @pytest.fixture
  def client():
      app.config['TESTING'] = True
      with app.test_client() as client:
          yield client
  ```

### **Task 7.3: Migrate Test Cases**
- [ ] **Update test assertions for Flask responses**
- [ ] **Update multipart form test data**
- [ ] **Verify all 67 tests pass with Flask**

---

## **Phase 8: Production Configuration** 🚀

### **Task 8.1: Update Dockerfile**
- [ ] **Update CMD to use Gunicorn instead of Uvicorn**
  ```dockerfile
  CMD ["gunicorn", "--worker-class", "gthread", "--workers", "4", "--bind", "0.0.0.0:8000", "flask_main:app"]
  ```

### **Task 8.2: Update Docker Compose**
- [ ] **Update service configuration for Flask**
- [ ] **Verify environment variable passing**

### **Task 8.3: Update Documentation**
- [ ] **Add Flask-specific setup instructions**
- [ ] **Update API documentation references**
- [ ] **Document differences from FastAPI version**

---

## **Phase 9: Final Integration & Testing** ✅

### **Task 9.1: Integration Testing**
- [ ] **Run full test suite**
  ```bash
  uv run pytest tests/ -v
  ```
- [ ] **Test Docker build and run**
  ```bash
  docker build -t agent-api-flask .
  docker run -p 8000:8000 --env-file .env agent-api-flask
  ```

### **Task 9.2: Performance Testing**
- [ ] **Compare response times between FastAPI and Flask versions**
- [ ] **Test concurrent request handling**
- [ ] **Verify memory usage patterns**

### **Task 9.3: Production Readiness**
- [ ] **Test all API endpoints manually**
- [ ] **Verify Langfuse tracing works**
- [ ] **Test error handling and validation**

---

## **Phase 10: Deployment & Cleanup** 🎯

### **Task 10.1: Deployment**
- [ ] **Deploy Flask version to staging environment**
- [ ] **Run smoke tests in staging**
- [ ] **Plan production deployment strategy**

### **Task 10.2: Code Cleanup**
- [ ] **Remove original `main.py` and rename `flask_main.py`**
- [ ] **Remove FastAPI-specific code and comments**
- [ ] **Update README with Flask instructions**

### **Task 10.3: Final Documentation**
- [ ] **Document migration process and learnings**
- [ ] **Update project dependencies documentation**
- [ ] **Create rollback plan if needed**

---

## **📊 Estimated Timeline**

- **Phase 1-2**: 2-3 hours (preparation)
- **Phase 3-4**: 4-5 hours (core migration)  
- **Phase 5-6**: 2-3 hours (services & files)
- **Phase 7**: 3-4 hours (testing)
- **Phase 8-10**: 2-3 hours (production & cleanup)

**Total Estimated Time**: 13-18 hours

---

## **🎯 Success Criteria**

- [ ] All 67 tests pass with Flask implementation
- [ ] All API endpoints return identical responses
- [ ] Performance is comparable to FastAPI version
- [ ] Docker deployment works correctly
- [ ] Langfuse tracing functions properly

---

## **⚠️ Key Considerations**

### **Flask-Pydantic Limitations**
- Form data with file uploads may require custom handling
- Response validation might need manual serialization
- Error handling format may differ from FastAPI

### **Async Support**
- Flask 3.0+ has async support but may need careful configuration
- Gunicorn with async workers for production deployment
- Test async compatibility thoroughly

### **Testing Migration**
- Flask test client behaves differently from FastAPI TestClient
- Form data and file upload tests need significant updates
- Response object structure differences

### **Production Considerations**
- WSGI vs ASGI deployment differences
- Performance implications of Flask vs FastAPI
- Monitoring and logging configuration updates

---

## **📚 References**

- [Flask-Pydantic Documentation](https://github.com/pallets-eco/flask-pydantic)
- [Flask 3.0 Documentation](https://flask.palletsprojects.com/en/stable/)
- [Forethought Migration Blog](https://engineering.forethought.ai/blog/2022/12/01/migrating-from-flask-to-fastapi-part-1/)
- [Flask Async Support](https://flask.palletsprojects.com/en/stable/async-await/)

---

## **📝 Notes**

- This migration maintains the same business logic and validation
- Pydantic models remain unchanged thanks to Flask-Pydantic
- Service layer (`agent.py`, `embeddings.py`, `langfuse_service.py`) should work without changes
- Main changes are in web framework layer and request/response handling 