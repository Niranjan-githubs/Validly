# FoundrScan Backend

A modular FastAPI backend for startup idea analysis and validation.

## 🏗️ Architecture Overview

The backend is organized into a clean, modular structure with clear separation of concerns:

```
backend/
├── api/                    # FastAPI application layer
│   ├── main.py            # FastAPI app entry point
│   ├── models/            # Pydantic models for request/response validation
│   ├── routes/            # API route handlers
│   └── services/          # External service integrations
├── core/                  # Core business logic
│   ├── pipeline.py        # Main analysis pipeline
│   └── idea_extractor.py  # Startup idea extraction logic
├── agents/                # AI agents for different analysis tasks
├── utils/                 # Utility functions and helpers
├── services/              # Internal service abstractions
├── routes/                # Additional route modules
├── outputs/               # Generated analysis outputs
└── requirements.txt       # Python dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Tests

```bash
python test_backend.py
```

### 3. Start the Server

```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Directory Structure

### `/api` - FastAPI Application Layer

**Purpose**: Handles HTTP requests, validation, and routing.

#### `main.py`

- FastAPI application entry point
- CORS configuration
- Route registration
- Middleware setup

#### `/models` - Pydantic Models

- `chat.py`: Chat request/response models
- `analysis.py`: Analysis request/response models

#### `/routes` - API Route Handlers

- `chat.py`: Chat-related endpoints
- Additional route modules for different features

#### `/services` - External Service Integrations

- `firebase.py`: Firebase service abstraction
- `redis.py`: Redis service abstraction

### `/core` - Core Business Logic

**Purpose**: Contains the main business logic and analysis pipeline.

#### `pipeline.py`

- `StartupAnalysisPipeline`: Main analysis orchestration
- Handles the complete startup analysis workflow
- Coordinates between different agents and services

#### `idea_extractor.py`

- `IdeaExtractor`: Extracts and validates startup ideas
- Processes user input and identifies key components

### `/agents` - AI Agents

**Purpose**: AI-powered analysis components.

**Planned Agents**:

- Competitor Analysis Agent
- Market Research Agent
- Financial Analysis Agent
- Technical Feasibility Agent

### `/utils` - Utility Functions

**Purpose**: Shared utility functions and helpers.

### `/services` - Internal Services

**Purpose**: Internal service abstractions and business logic services.

### `/outputs` - Generated Outputs

**Purpose**: Stores analysis results and generated files.

## 🔧 API Endpoints

### Chat Endpoints

- `POST /chat`: Send a message and get a response
- `GET /chat/history/{session_id}`: Get chat history for a session

### Analysis Endpoints

- `POST /analysis/startup`: Analyze a startup idea
- `GET /analysis/{analysis_id}`: Get analysis results
- `POST /analysis/competitor`: Perform competitor analysis
- `POST /analysis/market`: Perform market research

## 📊 Data Models

### Chat Models

```python
class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str
```

### Analysis Models

```python
class AnalysisRequest(BaseModel):
    idea: str
    analysis_type: str
    session_id: str

class AnalysisResponse(BaseModel):
    idea: str
    analysis_type: str
    results: Dict[str, Any]
    session_id: str
    status: str
```

## 🔌 Services

### Firebase Service

Handles user authentication, session management, and data persistence.

```python
class FirebaseService:
    def __init__(self):
        # Initialize Firebase connection

    async def save_session(self, session_id: str, data: dict):
        # Save session data

    async def get_session(self, session_id: str):
        # Retrieve session data
```

### Redis Service

Handles caching and temporary data storage.

```python
class RedisService:
    def __init__(self):
        # Initialize Redis connection

    async def cache_result(self, key: str, data: dict, ttl: int = 3600):
        # Cache analysis results

    async def get_cached_result(self, key: str):
        # Retrieve cached results
```

## 🔄 Analysis Pipeline

The `StartupAnalysisPipeline` orchestrates the complete analysis workflow:

1. **Idea Extraction**: Extract and validate the startup idea
2. **Competitor Analysis**: Identify and analyze competitors
3. **Market Research**: Research market size and trends
4. **Financial Analysis**: Assess financial feasibility
5. **Technical Analysis**: Evaluate technical requirements
6. **Risk Assessment**: Identify potential risks and challenges
7. **Recommendations**: Generate actionable recommendations

## 🧪 Testing

### Running Tests

```bash
# Run comprehensive backend tests
python test_backend.py

# Run specific test modules
python test_imports.py
python test_structure.py
```

### Test Coverage

- ✅ Import validation
- ✅ Structure verification
- ✅ Model creation
- ✅ Service initialization
- ✅ Pipeline instantiation

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
FIREBASE_CLIENT_ID=your-client-id

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Together AI Configuration
TOGETHER_API_KEY=your-together-api-key
```

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🔍 Monitoring and Logging

The application includes comprehensive logging for:

- API requests and responses
- Analysis pipeline execution
- Error tracking and debugging
- Performance metrics

## 🤝 Contributing

1. Follow the modular structure
2. Add tests for new functionality
3. Update documentation
4. Use type hints and docstrings
5. Follow PEP 8 style guidelines

## 📝 TODO

- [ ] Implement missing AI agents
- [ ] Add comprehensive error handling
- [ ] Implement rate limiting
- [ ] Add authentication middleware
- [ ] Create deployment scripts
- [ ] Add performance monitoring
- [ ] Implement caching strategies
- [ ] Add API documentation with Swagger

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all `__init__.py` files exist
2. **Missing Dependencies**: Run `pip install -r requirements.txt`
3. **Service Connection Errors**: Check environment variables and service configurations
4. **Model Validation Errors**: Verify request data matches Pydantic models

### Getting Help

1. Run the test script: `python test_backend.py`
2. Check the logs for error messages
3. Verify environment variables are set correctly
4. Ensure all required services are running
