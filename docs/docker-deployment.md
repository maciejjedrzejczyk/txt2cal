# Docker Deployment Guide for txt2cal

This guide provides instructions for deploying txt2cal using Docker and Docker Compose.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Development Deployment](#development-deployment)
5. [Production Deployment](#production-deployment)
6. [Scaling](#scaling)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

- Docker Engine (version 20.10.0 or later)
- Docker Compose (version 2.0.0 or later)
- At least 4GB of RAM for running Ollama
- At least 10GB of free disk space

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/maciejjedrzejczyk/txt2cal.git
   cd txt2cal
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Access the application at [http://localhost:3000](http://localhost:3000)

## Configuration

### Environment Variables

The Docker Compose files use environment variables to configure the services. You can modify these in the `docker-compose.yml` file or create a `.env` file in the project root.

#### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_OLLAMA_API_URL` | URL for the Ollama API | `http://ollama:11434/api` |
| `REACT_APP_API_URL` | URL for the backend API | `http://localhost:3001/api` |
| `REACT_APP_OLLAMA_MODEL` | Ollama model to use | `llama3.2` |

#### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Port for the backend server | `3001` |
| `OLLAMA_API_URL` | URL for the Ollama API | `http://ollama:11434/api` |
| `OLLAMA_MODEL` | Ollama model to use | `llama3.2` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `RATE_LIMIT` | Rate limit (requests per 15 minutes) | `100` |

### Volumes

The Docker Compose configuration includes two volumes:

- `ollama-data`: Stores Ollama models and data
- `backend-logs`: Stores backend server logs

## Development Deployment

The default `docker-compose.yml` file is configured for development:

```bash
# Start the services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the services
docker-compose down
```

## Production Deployment

For production deployment, use the `docker-compose.prod.yml` file:

```bash
# Start the services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop the services
docker-compose -f docker-compose.prod.yml down
```

### Production Considerations

1. **Security**: The production configuration doesn't expose the Ollama and backend ports to the host, only the frontend port 80.

2. **Resource Limits**: The production configuration includes resource limits for each service:
   - Frontend: 0.5 CPU, 256MB RAM
   - Backend: 1.0 CPU, 512MB RAM
   - Ollama: 2.0 CPU, 4GB RAM

3. **Restart Policy**: All services are configured to always restart in case of failure.

## Scaling

The backend service can be scaled horizontally:

```bash
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

Note: When scaling the backend, you'll need to add a load balancer in front of the backend services.

## Troubleshooting

### Common Issues

#### Ollama Model Download Fails

If the Ollama model download fails during container startup:

1. Start just the Ollama service:
   ```bash
   docker-compose up -d ollama
   ```

2. Manually pull the model:
   ```bash
   docker-compose exec ollama ollama pull llama3.2
   ```

3. Start the remaining services:
   ```bash
   docker-compose up -d
   ```

#### Connection Issues Between Services

If services can't connect to each other:

1. Check if all services are running:
   ```bash
   docker-compose ps
   ```

2. Check the Docker network:
   ```bash
   docker network inspect txt2cal_txt2cal-network
   ```

3. Check service logs:
   ```bash
   docker-compose logs backend
   docker-compose logs ollama
   ```

#### Out of Memory Errors

If you see out of memory errors, especially for the Ollama service:

1. Increase the memory allocation in `docker-compose.yml` or `docker-compose.prod.yml`
2. Ensure your Docker host has enough available memory

### Accessing Logs

Logs are stored in Docker volumes and can be accessed from the containers:

```bash
# Backend logs
docker-compose exec backend ls -la /app/logs
docker-compose exec backend cat /app/logs/access.log

# Ollama logs
docker-compose logs ollama
```
