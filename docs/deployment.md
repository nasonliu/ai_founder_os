# AI Founder OS - Deployment Guide

This guide covers deploying AI Founder OS using Docker and containerization.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Setup](#docker-setup)
- [Configuration](#configuration)
- [Deployment Options](#deployment-options)
- [Production Deployment](#production-deployment)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- **Docker** 20.10+ installed
- **Docker Compose** 2.0+ (for local development)
- **Python** 3.10+ (for local development)
- **Git** for cloning the repository

### Required Services

- PostgreSQL 14+ (for persistent data)
- Redis 7+ (for caching and task queue)
- Ollama (optional, for local LLM)

---

## Docker Setup

### Dockerfile

Create a `Docker project root:

```file` in thedockerfile
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY frontend/ ./frontend/
COPY prompts/ ./prompts/
COPY schemas/ ./schemas/

# Expose ports
EXPOSE 8000 3000

# Default command
CMD ["python", "-m", "src.planner.planner"]
```

### requirements.txt

```txt
# Core dependencies
pydantic>=2.0.0
dataclasses-json>=0.6.0

# Web server
uvicorn>=0.23.0
fastapi>=0.100.0

# Database
sqlalchemy>=2.0.0
asyncpg>=0.28.0
alembic>=1.11.0

# Redis
redis>=4.5.0
aioredis>=2.0.0

# Utilities
python-dotenv>=1.0.0
httpx>=0.24.0
python-dateutil>=2.8.0

# Testing (dev)
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
```

### Docker Compose

For local development, create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_USER: aifos
      POSTGRES_PASSWORD: ${DB_PASSWORD:-change_me_in_production}
      POSTGRES_DB: aifos
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aifos"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache & Queue
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # AI Founder OS Backend
  backend:
    build: .
    command: uvicorn src.dashboard.api:app --host 0.0.0.0 --port 8000 --reload
    environment:
      - DATABASE_URL=postgresql+asyncpg://aifos:${DB_PASSWORD:-change_me_in_production}@postgres:5432/aifos
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    volumes:
      - ./src:/app/src
      - ./data:/app/data
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Frontend (React)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - VITE_API_URL=http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

  # Ollama (Local LLM - Optional)
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    environment:
      - OLLAMA_HOST=0.0.0.0

volumes:
  postgres_data:
  redis_data:
  ollama_data:
```

---

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# Database
DB_PASSWORD=your_secure_password_here

# API Keys (use secrets in production!)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...

# GitHub (for repo operations)
GITHUB_TOKEN=ghp_...

# Slack (for notifications)
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...

# Execution
MAX_CONCURRENCY=3
RETRY_LIMIT=3

# Logging
LOG_LEVEL=INFO
```

### Configuration File

Create `config.yaml`:

```yaml
system:
  name: "AI Founder OS"
  version: "1.0.0"
  
execution:
  mode: "normal"  # safe, normal, turbo
  max_concurrency: 3
  retry_limit: 3
  slowdown_threshold: 3

database:
  url: "postgresql+asyncpg://aifos:password@localhost:5432/aifos"
  pool_size: 10
  max_overflow: 20

redis:
  url: "redis://localhost:6379"
  max_connections: 50

workers:
  default_types:
    - builder
    - researcher
    - documenter
    - verifier
    - evaluator
  
  models:
    primary: "ollama:deepseek-8b"
    fallback: "openai:gpt-4"

policy:
  execution:
    concurrency_limits:
      safe: 1
      normal: 3
      turbo: 5
    default_retry_limit: 3
    
  safety:
    blocked_domains: []
    allowed_network: ["api.openai.com", "api.anthropic.com"]
    
  quality:
    kpi_thresholds:
      test_coverage: ">=80%"
      latency_p99: "<500ms"

connections:
  routing_rules:
    builder:
      primary: "local_ollama:deepseek-8b"
      fallback: "cloud_openai:gpt-4"
      
  budget:
    default_daily_limit: "10usd"
    warning_threshold: 0.8
```

---

## Deployment Options

### 1. Local Development

```bash
# Clone and setup
git clone https://github.com/your-org/ai-founder-os.git
cd ai-founder-os

# Copy and edit environment
cp .env.example .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Single Container

```bash
# Build image
docker build -t aifos:latest .

# Run with external database
docker run -d \
  --name aifos \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://..." \
  -e REDIS_URL="redis://..." \
  aifos:latest
```

### 3. Kubernetes Deployment

Deploy to Kubernetes with the following manifests:

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aifos-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aifos-backend
  template:
    metadata:
      labels:
        app: aifos-backend
    spec:
      containers:
      - name: backend
        image: aifos:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: aifos-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: aifos-config
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: aifos-backend
spec:
  selector:
    app: aifos-backend
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

Apply with:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

---

## Production Deployment

### Security Checklist

- [ ] Use strong database passwords
- [ ] Enable SSL/TLS for all connections
- [ ] Store secrets in Kubernetes Secrets or Vault
- [ ] Enable Docker content trust
- [ ] Run containers as non-root user
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Set up backup strategy

### Production Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: aifos
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: aifos
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - aifos_network
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - aifos_network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  backend:
    build: .
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql+asyncpg://aifos:${DB_PASSWORD}@postgres:5432/aifos
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - LOG_LEVEL=INFO
    depends_on:
      - postgres
      - redis
    networks:
      - aifos_network
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 2G

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    networks:
      - aifos_network

networks:
  aifos_network:
    driver: bridge
```

### SSL/TLS Setup

Generate SSL certificates:
```bash
# Using Let's Encrypt
certbot certonly --webroot -w /var/www/html -d yourdomain.com

# Or self-signed for testing
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/server.key -out ssl/server.crt
```

Nginx configuration:
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;
    
    location / {
        proxy_pass http://frontend:3000;
    }
    
    location /api {
        proxy_pass http://backend:8000;
    }
}
```

---

## Monitoring

### Health Checks

```python
# Add to your FastAPI app
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/ready")
def readiness_check():
    # Check database and Redis
    return {"status": "ready"}
```

### Prometheus Metrics

Add metrics endpoint:

```python
from fastapi import Response
import prometheus_client

@app.get("/metrics")
def metrics():
    return Response(
        prometheus_client.generate_latest(),
        media_type="text/plain"
    )
```

### Logging

Configure structured logging:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)
```

---

## Troubleshooting

### Common Issues

#### Database Connection Failed

```bash
# Check database logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres pg_isready -U aifos

# Check network
docker network ls
docker network inspect aifos_network
```

#### Redis Connection Issues

```bash
# Check Redis
docker-compose exec redis redis-cli ping

# View Redis logs
docker-compose logs redis
```

#### Worker Not Starting

```bash
# Check environment variables
docker-compose exec backend env | grep -i

# View backend logs
docker-compose logs backend

# Restart service
docker-compose restart backend
```

### Debugging Commands

```bash
# Enter container shell
docker exec -it aifos_backend_1 /bin/bash

# View real-time logs
docker-compose logs -f --tail=100

# Check resource usage
docker stats

# Inspect network
docker network inspect aifos_aifos_network

# Rebuild without cache
docker-compose build --no-cache
```

### Performance Tuning

```yaml
# docker-compose.yml adjustments
services:
  backend:
    environment:
      - UVICORN_WORKERS=4
      - UVICORN_LIMIT_CONNS=1000
      - DATABASE_POOL_SIZE=20
```

---

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U aifos aifos > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose exec -T postgres psql -U aifos aifos < backup_20240101.sql
```

### Automated Backups

```bash
# crontab entry
0 2 * * * docker-compose exec postgres pg_dump -U aifos aifos | gzip > /backups/aifos_$(date +\%Y\%m\%d).sql.gz
```

---

## Scaling

### Horizontal Scaling

```bash
# Scale backend instances
docker-compose up -d --scale backend=3
```

### Load Balancing

Use nginx for load balancing across multiple backend instances.

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-org/ai-founder-os/issues
- Documentation: https://docs.aifounderos.io
- Discord: https://discord.gg/aifounderos
