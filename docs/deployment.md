# Deployment Guide

This guide covers deploying AI Founder OS using Docker and environment configuration.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (for local development)

## Quick Start

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/your-org/ai-founder-os.git
cd ai-founder-os

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Docker Setup

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY schemas/ ./schemas/
COPY prompts/ ./prompts/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "-m", "src.dashboard.api"]
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - LOG_LEVEL=INFO
      - DB_PATH=/data/ai_founder_os.db      - ./data
    volumes:
:/data
      - ./configs:/configs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/status"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Ollama for local models
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama_data:
```

### Build and Run

```bash
# Build the image
docker build -t ai-founder-os:latest .

# Run the container
docker run -d \
  --name ai-founder-os \
  -p 8000:8000 \
  -v ./data:/data \
  -e ENV=production \
  ai-founder-os:latest
```

## Environment Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment (development/production) | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DB_PATH` | Path to SQLite database | `./data/ai_founder_os.db` |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `CONNECTION_CONFIG` | Path to connection config | `./configs/connections.json` |
| `SKILLS_PATH` | Path to skills directory | `./skills` |

### Connection Configuration

Create a `configs/connections.json` file:

```json
{
  "routing_rules": {
    "builder": {
      "primary": "local_ollama:deepseek-8b",
      "fallback": "cloud_openai:gpt-4",
      "retry_on_failure": true
    },
    "researcher": {
      "primary": "brave_search",
      "fallback": "cloud_anthropic:claude-3",
      "retry_on_failure": true
    }
  },
  "budget_rules": {
    "default_daily_limit": "10usd",
    "warning_threshold": 0.8,
    "hard_limit_action": "pause_all_tasks"
  }
}
```

### Managing API Keys

**Never commit API keys to version control!**

Use environment variables or a secrets manager:

```python
import os

# Read from environment
openai_key = os.environ.get("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("OPENAI_API_KEY not set")
```

In Docker:

```bash
docker run -d \
  -e OPENAI_API_KEY=sk-... \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  ai-founder-os:latest
```

## Deployment Options

### Local Development

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Start development server
python -m src.dashboard.api
```

### Production Deployment

1. **Using Docker Swarm**:

```bash
docker stack deploy -c docker-compose.yml ai-founder-os
```

2. **Using Kubernetes** (advanced):

See `k8s/` directory for Kubernetes manifests.

### Security Considerations

- **Never expose secrets** in Dockerfiles or config files
- Use Docker secrets or Kubernetes secrets for sensitive data
- Run containers as non-root user
- Enable HTTPS in production
- Use a reverse proxy (nginx, traefik) for SSL termination

```yaml
# Example with Traefik
services:
  api:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=PathPrefix(`/api`)"
      - "traefik.http.routers.api.tls=true"
```

## Monitoring

### Health Check

```bash
# Check API health
curl http://localhost:8000/api/status

# Check Docker health
docker inspect --format='{{.State.Health.Status}}' ai-founder-os
```

### Logs

```bash
# View API logs
docker logs ai-founder-os

# Follow logs
docker logs -f ai-founder-os
```

### Metrics

The API exposes Prometheus-compatible metrics at `/api/metrics`:

```bash
curl http://localhost:8000/api/metrics
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs ai-founder-os

# Verify environment variables
docker exec ai-founder-os env
```

### Database Issues

```bash
# Reset database
rm -rf ./data/ai_founder_os.db
docker restart ai-founder-os
```

### Connection Problems

1. Verify Ollama is running: `curl http://localhost:11434`
2. Check API keys are set: `echo $OPENAI_API_KEY`
3. Review connection manager logs

## Backup and Restore

### Backup

```bash
# Backup database and configs
tar -czf backup.tar.gz ./data ./configs
```

### Restore

```bash
# Stop services
docker-compose down

# Restore files
tar -xzf backup.tar.gz

# Restart services
docker-compose up -d
```

## CI/CD Integration

See `.github/workflows/` for GitHub Actions configuration.

```yaml
# Example production deployment
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build and push
        run: |
          docker build -t ai-founder-os:${{ github.sha }} .
          docker push registry/ai-founder-os:${{ github.sha }}
      
      - name: Deploy to production
        run: |
          kubectl set image deployment/api api=registry/ai-founder-os:${{ github.sha }}
```
