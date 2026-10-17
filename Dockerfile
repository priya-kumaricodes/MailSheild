# Stage 1: Build the React web frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /build

COPY apps/web/package*.json ./apps/web/
RUN npm --prefix apps/web ci

COPY apps/web ./apps/web
RUN npm --prefix apps/web run build

# Stage 2: Python production runtime
FROM python:3.11-slim AS runtime
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:/app/ml/src \
    ENVIRONMENT=production \
    PORT=8000

# Install minimal OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application backend, ML models, and dataset metadata
COPY backend ./backend
COPY ml/src ./ml/src
COPY ml/artifacts ./ml/artifacts
COPY ml/data ./ml/data

# Copy built frontend assets from stage 1
COPY --from=frontend-builder /build/apps/web/dist ./apps/web/dist

# Expose service port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

# Launch production server
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
