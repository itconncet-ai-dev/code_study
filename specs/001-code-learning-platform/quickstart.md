# Quickstart Guide: AI Code Learning Platform

**Last Updated**: 2025-11-15
**For**: Development setup and local testing

## Overview

This guide helps you set up the AI Code Learning Platform development environment. The platform consists of a FastAPI backend, React frontend, PostgreSQL database, and Redis for task queuing.

## Prerequisites

### Required Software

- **Python 3.11+** - Backend language
- **Node.js 18+** - Frontend tooling
- **PostgreSQL 15+** - Database
- **Redis 7+** - Task queue and cache
- **Git** - Version control

### Optional (Recommended)

- **Docker & Docker Compose** - Simplified environment setup
- **VS Code** - IDE with Python and TypeScript extensions

## Quick Start with Docker (Recommended)

### 1. Clone Repository

```bash
git clone <repository-url>
cd code_study
```

### 2. Environment Configuration

Create `.env` file in project root:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/codelearning
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=codelearning

# Redis
REDIS_URL=redis://redis:6379/0

# Google AI (Gemini)
GOOGLE_API_KEY=your-google-ai-api-key-here

# JWT Secrets (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your-secret-key-here
JWT_REFRESH_SECRET=your-refresh-secret-here

# Environment
ENVIRONMENT=development
DEBUG=true
ALLOWED_ORIGINS=http://localhost:5173

# File Storage
UPLOAD_DIR=./storage/uploads
MAX_UPLOAD_SIZE_MB=10
```

### 3. Start Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379
- Backend on port 8000
- Frontend on port 5173
- Celery worker for background tasks

### 4. Access Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **API**: http://localhost:8000/api/v1

## Manual Setup (Without Docker)

### Backend Setup

#### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Unix/MacOS)
source venv/bin/activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt**:
```
fastapi==0.104.0
uvicorn[standard]==0.24.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
alembic==1.12.1
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.25.0
google-generativeai==0.3.0
celery[redis]==5.3.4
redis==5.0.1
pygments==2.16.1
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
```

#### 3. Database Setup

```bash
# Start PostgreSQL (if not using Docker)
# Create database
createdb codelearning

# Run migrations
alembic upgrade head
```

#### 4. Start Redis

```bash
# Install and start Redis
# Windows: Download from https://github.com/microsoftarchive/redis/releases
redis-server
```

#### 5. Start Backend Server

```bash
# Terminal 1: API Server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Celery Worker
celery -A src.tasks.celery_app worker --loglevel=info

# Terminal 3 (Optional): Celery Beat (scheduled tasks)
celery -A src.tasks.celery_app beat --loglevel=info
```

### Frontend Setup

#### 1. Install Dependencies

```bash
cd frontend
npm install
```

**package.json dependencies**:
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@tanstack/react-query": "^5.8.0",
    "zustand": "^4.4.0",
    "@monaco-editor/react": "^4.6.0",
    "axios": "^1.6.0",
    "tailwindcss": "^3.3.0",
    "shadcn-ui": "latest"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.1.0",
    "eslint": "^8.54.0",
    "prettier": "^3.1.0"
  }
}
```

#### 2. Start Development Server

```bash
npm run dev
```

Frontend runs on http://localhost:5173

## Project Structure

```
code_study/
├── backend/
│   ├── src/
│   │   ├── api/           # API endpoints
│   │   ├── models/        # SQLAlchemy models
│   │   ├── services/      # Business logic
│   │   ├── tasks/         # Celery tasks
│   │   ├── db/            # Database config
│   │   └── utils/         # Utilities
│   ├── tests/
│   ├── alembic/           # Database migrations
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── storage/
│   └── uploads/           # Uploaded code files
├── docs/
│   └── task-reports/      # Task completion reports (TDD)
├── docker-compose.yml
└── .env
```

## Development Workflow

### TDD Cycle (REQUIRED by Constitution)

```bash
# 1. RED Phase - Write failing test
pytest tests/test_feature.py -v
git commit -m "test: feature name - RED"

# 2. GREEN Phase - Minimal implementation
# ... write code ...
pytest tests/test_feature.py -v  # Should pass
git commit -m "feat: feature name - GREEN"

# 3. REFACTOR Phase - Improve code
# ... refactor ...
pytest tests/test_feature.py -v  # Should still pass
git commit -m "refactor: feature name - REFACTOR"
```

### Running Tests

```bash
# Backend tests (from backend/)
pytest tests/ -v --cov=src --cov-report=html

# Frontend tests (from frontend/)
npm run test
npm run test:coverage
```

### Database Migrations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Quality

```bash
# Backend linting and formatting
cd backend
ruff check src/
black src/
mypy src/

# Frontend linting and formatting
cd frontend
npm run lint
npm run format
```

## Configuration

### Environment Variables

**Backend (.env)**:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
GOOGLE_API_KEY=your-google-ai-api-key-here
JWT_SECRET_KEY=secret
JWT_REFRESH_SECRET=secret
ENVIRONMENT=development
DEBUG=true
ALLOWED_ORIGINS=http://localhost:5173
UPLOAD_DIR=./storage/uploads
MAX_UPLOAD_SIZE_MB=10
```

**Frontend (.env.local)**:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_ENVIRONMENT=development
```

## Common Tasks

### Create New API Endpoint

1. Define route in `backend/src/api/`
2. Write business logic in `backend/src/services/`
3. Add contract test in `backend/tests/contract/`
4. Update OpenAPI spec in `specs/001-code-learning-platform/contracts/api-spec.yaml`

### Add New Frontend Page

1. Create component in `frontend/src/pages/`
2. Add route in `frontend/src/App.tsx`
3. Create API service in `frontend/src/services/`
4. Add component tests in `frontend/src/pages/__tests__/`

### Trigger Document Generation

Document generation is async via Celery:

```python
# In backend service
from src.tasks.document_generation import generate_learning_document

# Queue task
task = generate_learning_document.delay(task_id)

# Check status
task.status  # 'PENDING', 'STARTED', 'SUCCESS', 'FAILURE'
```

### Gemini API Testing

Test without hitting API using mock:

```python
# In tests
from unittest.mock import patch

@patch('google.generativeai.GenerativeModel.generate_content')
def test_document_generation(mock_gemini):
    mock_gemini.return_value = MagicMock(text='{"chapter1": {...}}')
    # ... test code
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Reset database
dropdb codelearning
createdb codelearning
alembic upgrade head
```

### Redis Connection Issues

```bash
# Check Redis is running
redis-cli ping  # Should return "PONG"

# Clear Redis cache
redis-cli FLUSHALL
```

### Port Already in Use

```bash
# Find and kill process
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Unix/MacOS
lsof -ti:8000 | xargs kill -9
```

### Gemini API Rate Limits

- Check your API usage at https://makersuite.google.com/app/apikey
- Monitor quotas in Google AI Studio
- Implement request queuing with delays
- Gemini 3 Flash Preview has generous rate limits for most use cases
- Use context caching to reduce token usage

### Celery Tasks Not Running

```bash
# Check Celery worker is running
celery -A src.tasks.celery_app inspect active

# Restart worker
celery -A src.tasks.celery_app worker --purge
```

## Testing

### Test User Account

For development, seed a test user:

```bash
cd backend
python scripts/seed_test_user.py
```

**Test Credentials**:
- Email: test@example.com
- Password: TestPass123!

### Test Data

Seed test projects and tasks:

```bash
python scripts/seed_test_data.py
```

## Production Deployment

See separate deployment guide for:
- Environment configuration
- Database backups
- Redis persistence
- File storage (S3)
- HTTPS/SSL setup
- Monitoring and logging

## Next Steps

1. **Set up environment** using Docker or manual setup
2. **Run tests** to verify setup: `pytest` and `npm run test`
3. **Start implementing** following TDD workflow
4. **Review architecture** in `research.md` and `data-model.md`
5. **Check API contracts** in `contracts/api-spec.yaml`
6. **Follow task list** (run `/speckit.tasks` to generate)

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Celery**: https://docs.celeryproject.org/
- **Google Gemini API**: https://ai.google.dev/gemini-api/docs

## Getting Help

- Check API docs: http://localhost:8000/docs
- Review spec: `specs/001-code-learning-platform/spec.md`
- Check constitution: `.specify/memory/constitution.md`
- Run `/speckit.plan` to regenerate this guide

## License

[Your License Here]
