# TODO API - Backend

FastAPI backend for the multi-user TODO application with JWT authentication and Neon PostgreSQL persistence.

## Quick Start

### Prerequisites

- Python 3.13+
- Neon PostgreSQL database (create at [console.neon.tech](https://console.neon.tech))

### Setup

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   ```

2. **Activate virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set:
   - `DATABASE_URL`: Your Neon PostgreSQL connection string
   - `BETTER_AUTH_SECRET`: Shared secret for JWT validation (32+ characters)

5. **Run database migrations** (after migrations are created):
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── models/          # SQLModel database entities
│   ├── routers/         # API endpoint definitions
│   ├── schemas/         # Pydantic request/response models
│   ├── auth/            # Authentication utilities
│   ├── config.py        # Environment configuration
│   ├── database.py      # Database connection
│   └── main.py          # FastAPI application
├── alembic/             # Database migrations (created by alembic init)
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (not committed)
```

## Health Check

Test the API is running:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "app": "TODO API",
  "version": "0.1.0"
}
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black app/

# Lint
ruff check app/
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `BETTER_AUTH_SECRET` | JWT validation secret (shared with frontend) | 32+ character string |
| `APP_NAME` | Application name | `TODO API` |
| `DEBUG` | Enable debug mode | `false` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |

## Next Steps

- ✅ Backend structure created
- ⏳ Run Alembic migrations to create database tables
- ⏳ Implement authentication endpoints
- ⏳ Implement task CRUD endpoints

Refer to `specs/phases/phase2-web/plan.md` for the complete implementation roadmap.
