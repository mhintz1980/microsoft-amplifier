# AI Career Copilot

An intelligent career development assistant powered by Claude AI that provides personalized resume analysis, skill gap identification, career coaching, and job matching within the Microsoft Amplifier framework.

## Features

### Core Capabilities

- **Resume Parsing & Analysis**: Multi-format support (PDF, DOCX, TXT, JSON) with AI-powered extraction
- **Skill Gap Analysis**: Comprehensive skill assessment with learning recommendations
- **Career Coaching**: Personalized guidance, networking strategies, and personal branding
- **Job Matching**: AI-powered job matching with relevance scoring and application strategies
- **Real-time Chat**: Interactive career coaching sessions with context awareness
- **Profile Management**: Unified profile system with analytics and progress tracking

### Technical Features

- **Multi-Model AI Support**: Fast, Default, and Thinking Claude models for different use cases
- **Fallback Mechanisms**: Rule-based processing when AI services are unavailable
- **Background Processing**: Asynchronous analysis with progress tracking
- **Caching Strategy**: Redis integration with TTL for performance optimization
- **Security**: File upload validation, rate limiting, and JWT authentication
- **Comprehensive API**: RESTful design with OpenAPI documentation

## Architecture

### Directory Structure

```
career_copilot/
├── __init__.py              # Module exports and initialization
├── main.py                  # FastAPI application entry point
├── config.py                # Configuration management
├── models/                  # Data models with Pydantic validation
│   ├── __init__.py
│   ├── resume_data.py       # Resume data structures
│   ├── user_preferences.py  # User preferences and goals
│   └── master_profile.py    # Unified profile model
├── services/                # Core business logic
│   ├── __init__.py
│   ├── resume_parser.py     # Resume parsing service
│   ├── skill_analyzer.py    # Skill gap analysis
│   ├── enrichment_coach.py  # Career coaching
│   └── job_matcher.py       # Job matching
├── api/                     # FastAPI layer
│   ├── __init__.py
│   ├── endpoints.py         # API route definitions
│   └── middleware.py        # CORS, security, rate limiting
├── prompts/                 # AI prompt templates
│   ├── resume_parsing.md    # Resume analysis prompts
│   ├── skill_suggestions.md # Skill development prompts
│   └── enrichment_chat.md   # Coaching conversation prompts
├── frontend/                # React application
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   ├── src/
│   │   ├── App.tsx          # Main application component
│   │   ├── main.tsx         # Application entry point
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── types/           # TypeScript type definitions
│   │   └── utils/           # Frontend utilities
│   └── public/              # Static assets
└── tests/                   # Test suite
    ├── __init__.py
    ├── conftest.py          # Test configuration
    ├── test_models.py       # Model validation tests
    ├── test_services.py     # Service logic tests
    ├── test_api.py          # API endpoint tests
    └── fixtures/            # Test data
```

### Data Flow

1. **User Interaction**: React frontend → FastAPI endpoints
2. **File Processing**: Upload → Validation → Parsing → Analysis
3. **AI Integration**: Services → Claude API → Response Processing
4. **Data Storage**: Temporary files → Database → Cache
5. **Real-time Updates**: SSE connections → Frontend updates

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (optional, for caching)
- Docker (optional, for containerization)

### Setup

1. **Install Python Dependencies**
   ```bash
   cd amplifier/career_copilot
   make install  # or: uv sync
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start Services**
   ```bash
   # Backend API
   cd amplifier/career_copilot
   python -m uvicorn main:app --reload --port 8000

   # Frontend Development Server
   cd frontend
   npm run dev
   ```

### Environment Variables

```bash
# Service Configuration
CAREER_COPILOT_ENVIRONMENT=development
CAREER_COPILOT_API_HOST=0.0.0.0
CAREER_COPILOT_API_PORT=8000

# AI Models
ANTHROPIC_API_KEY=your_anthropic_api_key
CAREER_COPILOT_CLAUDE_MODEL_FAST=claude-3-5-haiku-20241022
CAREER_COPILOT_CLAUDE_MODEL_DEFAULT=claude-sonnet-4-20250514
CAREER_COPILOT_CLAUDE_MODEL_THINKING=claude-opus-4-1-20250805

# External Services
CAREER_COPILOT_REDIS_URL=redis://localhost:6379
CAREER_COPILOT_DATABASE_URL=sqlite:///./career_copilot.db

# Security
CAREER_COPILOT_JWT_SECRET_KEY=your_jwt_secret_key
CAREER_COPILOT_REQUIRE_AUTHENTICATION=false
```

## Usage

### Basic Usage

1. **Upload Resume**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/resume/upload" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@resume.pdf"
   ```

2. **Analyze Skills**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/analysis/skills" \
        -H "Content-Type: application/json" \
        -d '{"target_roles": ["Senior Software Engineer"]}'
   ```

3. **Start Coaching Chat**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/chat/coach" \
        -H "Content-Type: application/json" \
        -d '{"message": "How can I transition to data science?"}'
   ```

### Frontend Application

Access the web application at `http://localhost:5173` (development) or `http://localhost:8000` (production).

Key features:
- **Resume Upload**: Drag-and-drop interface with progress tracking
- **Dashboard**: Profile overview with analytics and insights
- **Skill Analysis**: Visual skill gap representation with learning paths
- **Career Coach**: Interactive chat interface for personalized guidance
- **Job Matches**: Curated job recommendations with application strategies

## API Documentation

### Core Endpoints

#### Resume Management
- `POST /api/v1/resume/upload` - Upload and parse resume
- `GET /api/v1/resume/current` - Get current resume data
- `PUT /api/v1/resume/current` - Update resume data

#### Profile & Analysis
- `GET /api/v1/profile` - Get complete user profile
- `POST /api/v1/analysis/skills` - Analyze skill gaps
- `POST /api/v1/analysis/career` - Career path analysis
- `GET /api/v1/analytics/progress` - Progress analytics

#### Coaching & Chat
- `POST /api/v1/chat/coach` - Send message to career coach
- `GET /api/v1/chat/history` - Get conversation history
- `DELETE /api/v1/chat/history` - Clear chat history

#### Job Matching
- `POST /api/v1/jobs/search` - Search for matching jobs
- `GET /api/v1/jobs/recommendations` - Get job recommendations
- `POST /api/v1/jobs/{job_id}/apply` - Generate application strategy

### Authentication

When authentication is enabled:
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password"}'

# Use token
curl -X GET "http://localhost:8000/api/v1/profile" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Rate Limiting

- Default: 60 requests per minute
- Burst: 10 requests per second
- Configurable via environment variables

## Configuration

### Service Configuration

```python
from career_copilot.config import config

# Access configuration values
api_port = config.api_port
claude_model = config.get_model("default")
is_production = config.is_production()
```

### Model Selection

Choose appropriate Claude models based on use case:

- **Fast Model** (`claude-3-5-haiku`): Quick operations, simple queries
- **Default Model** (`claude-sonnet-4`): General analysis, coaching
- **Thinking Model** (`claude-opus-4-1`): Complex analysis, strategic planning

### Feature Flags

Control feature availability via configuration:

```python
# Enable/disable features
config.enable_background_processing = True
config.enable_email_notifications = False
config.enable_analytics = True
config.rate_limit_enabled = True
```

## Development

### Local Development

1. **Setup Development Environment**
   ```bash
   make install
   make dev-setup  # Creates dev database, cache directories
   ```

2. **Run Tests**
   ```bash
   make test           # Run all tests
   make test-unit      # Unit tests only
   make test-integration # Integration tests only
   make test-coverage  # With coverage report
   ```

3. **Code Quality**
   ```bash
   make check          # Lint, format, type check
   make format         # Format code with ruff
   make lint           # Lint code
   make typecheck      # Type checking with pyright
   ```

4. **Development Servers**
   ```bash
   # Backend with auto-reload
   make run-backend

   # Frontend development server
   make run-frontend

   # Both together
   make run-dev
   ```

### Testing Strategy

- **Unit Tests**: Individual component testing with mocks
- **Integration Tests**: API endpoint testing with test database
- **End-to-End Tests**: Full workflow testing with real services
- **Performance Tests**: Load testing and optimization validation

### Adding New Features

1. **Define Data Models**: Add to `models/` directory
2. **Implement Service Logic**: Add to `services/` directory
3. **Create API Endpoints**: Add to `api/endpoints.py`
4. **Update Frontend**: Add components and pages
5. **Write Tests**: Comprehensive test coverage
6. **Update Documentation**: README and API docs

## Deployment

### Production Deployment

1. **Environment Configuration**
   ```bash
   export CAREER_COPILOT_ENVIRONMENT=production
   export CAREER_COPILOT_REDIS_URL=redis://prod-redis:6379
   export CAREER_COPILOT_DATABASE_URL=postgresql://user:pass@db:5432/career_copilot
   export CAREER_COPILOT_REQUIRE_AUTHENTICATION=true
   ```

2. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   ```

3. **Run Application**
   ```bash
   cd amplifier/career_copilot
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY . .
RUN cd frontend && npm install && npm run build

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  career-copilot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CAREER_COPILOT_ENVIRONMENT=production
      - CAREER_COPILOT_REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: career_copilot
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Monitoring & Observability

- **Health Checks**: `/health` endpoint for service status
- **Metrics**: Prometheus-compatible metrics at `/metrics`
- **Logging**: Structured JSON logging with configurable levels
- **Error Tracking**: Integration with Sentry for error monitoring

## Security Considerations

### Data Protection

- **File Upload Security**: Type validation, size limits, virus scanning
- **Data Encryption**: Encryption at rest and in transit
- **PII Protection**: Automatic detection and redaction of sensitive information
- **Data Retention**: Configurable retention policies for user data

### Access Control

- **Authentication**: JWT-based authentication with configurable providers
- **Authorization**: Role-based access control (RBAC)
- **Rate Limiting**: Configurable rate limits per user and endpoint
- **CORS**: Configurable CORS policies for frontend integration

### API Security

- **Input Validation**: Comprehensive request validation with Pydantic
- **SQL Injection Prevention**: Parameterized queries and ORM usage
- **XSS Protection**: Input sanitization and output encoding
- **CSRF Protection**: CSRF tokens for state-changing operations

## Performance Optimization

### Caching Strategy

- **Redis Integration**: Multi-level caching with TTL
- **Response Caching**: API response caching for expensive operations
- **Session Caching**: User session and context caching
- **Cache Invalidation**: Intelligent cache invalidation strategies

### Async Processing

- **Background Tasks**: Celery integration for long-running operations
- **Streaming Responses**: SSE for real-time progress updates
- **Connection Pooling**: Efficient database connection management
- **Async/Await**: Full async stack for optimal performance

### Scalability

- **Horizontal Scaling**: Stateless design for easy scaling
- **Load Balancing**: Multiple instance support with session affinity
- **Database Optimization**: Query optimization and indexing strategies
- **CDN Integration**: Static asset delivery via CDN

## Troubleshooting

### Common Issues

1. **Resume Parsing Fails**
   - Check file format support (PDF, DOCX, TXT, JSON)
   - Verify file size limits (default 10MB)
   - Check Claude API availability and credentials

2. **AI Analysis Timeout**
   - Increase timeout values in configuration
   - Check network connectivity to Claude API
   - Monitor token usage and rate limits

3. **Frontend Build Errors**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility (18+)
   - Verify environment variables are set

4. **Database Connection Issues**
   - Check database URL format and credentials
   - Verify database server is running
   - Check network connectivity and firewall rules

### Debug Mode

Enable debug mode for detailed error information:

```bash
export CAREER_COPILOT_LOG_LEVEL=DEBUG
export CAREER_COPILOT_DEBUG=true
```

### Health Monitoring

Monitor service health:

```bash
# Service health
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/api/v1/status

# Debug configuration (development only)
curl http://localhost:8000/debug/config
```

## Contributing

### Development Workflow

1. **Fork Repository** and create feature branch
2. **Make Changes** with comprehensive tests
3. **Run Quality Checks**: `make check`
4. **Update Documentation** for API changes
5. **Submit Pull Request** with detailed description

### Code Standards

- **Python**: Follow PEP 8, use type hints, comprehensive docstrings
- **TypeScript**: Strict type checking, consistent formatting
- **Testing**: Minimum 80% coverage, integration tests for new features
- **Documentation**: Update README and API docs for all changes

### Review Process

- **Code Review**: Required for all changes
- **Security Review**: Required for authentication and data handling changes
- **Performance Review**: Required for database and API changes
- **Documentation Review**: Required for public API changes

## License

This project is part of the Microsoft Amplifier framework. See the main project license for details.

## Support

- **Documentation**: See `/docs` directory for detailed guides
- **Issues**: Report bugs and feature requests via GitHub issues
- **Community**: Join discussions in the project Discord/Slack
- **Email**: Contact the development team for enterprise support

## Changelog

### Version 1.0.0 (Current)

- Initial release with core functionality
- Resume parsing and analysis
- Skill gap identification
- Career coaching chat
- Job matching recommendations
- React frontend application
- Comprehensive API documentation
- Docker deployment support

### Planned Features

- **Integration APIs**: LinkedIn, GitHub, job board APIs
- **Advanced Analytics**: Career progression tracking
- **Team Features**: Multi-user support for organizations
- **Mobile App**: React Native mobile application
- **AI Enhancements**: Advanced reasoning and personalization
- **Enterprise Features**: SSO, audit logs, compliance