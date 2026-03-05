# Deployment Guide

## Quick Start with Docker

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY src/ ./src/
COPY tests/ ./tests/
COPY schemas/ ./schemas/

# Expose port
EXPOSE 8000

# Run
CMD ["python", "-m", "src.planner.planner"]
```

### 2. Build and Run

```bash
# Build
docker build -t ai-founder-os .

# Run
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  ai-founder-os
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `ANTHROPIC_API_KEY` | No | Anthropic API key |
| `DEEPSEEK_API_KEY` | No | DeepSeek API key |
| `GITHUB_TOKEN` | No | GitHub token |
| `DATABASE_URL` | No | PostgreSQL URL |

## Local Development

```bash
# Clone
git clone https://github.com/nasonliu/ai_founder_os.git
cd ai_founder_os

# Create venv
python -m venv venv
source venv/bin/activate

# Install
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Start
python -m src.planner.planner
```

## Production Deployment

### Using Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/aios
    depends_on:
      - db
      
  db:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### Cloud Deployment

#### Railway
```bash
railway init
railway up
```

#### Render
```bash
render.yaml:
services:
  - type: python
    buildCommand: pip install -r requirements.txt
    startCommand: python -m src.planner.planner
```

## Configuration

Create `config.json`:

```json
{
  "max_concurrency": 3,
  "retry_limit": 3,
  "connections": {
    "openai": {
      "provider": "openai",
      "api_key": "${OPENAI_API_KEY}"
    }
  }
}
```

## Health Check

```bash
curl http://localhost:8000/health
```

## Monitoring

- Use PM2 for process management
- Set up Prometheus + Grafana for metrics
- Use Sentry for error tracking
