FROM python:3.13 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# Create virtual environment
RUN python -m venv .venv

# Copy build metadata first (better layer caching for dependency-only changes)
COPY pyproject.toml README.md ./
# Copy the application package so setuptools can find 'app'
COPY app ./app

# Install project (dependencies + package) into the venv
RUN .venv/bin/pip install --no-cache-dir --upgrade pip && \
    .venv/bin/pip install --no-cache-dir .

FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /app/.venv .venv/
ENV PATH="/app/.venv/bin:${PATH}"

# Copy remaining runtime assets (data, scripts, etc.)
COPY . .

EXPOSE 8000
# Run with uvicorn directly (more stable than fastapi CLI wrapper)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
