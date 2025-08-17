FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
        PYTHONDONTWRITEBYTECODE=1 \
        PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install build tools only if needed for deps (kept minimal; remove if unnecessary)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy application code (only what we need)
COPY app ./app
COPY frontend_dist ./frontend_dist
COPY export_data.py recreate_db.py create_mock_data.py insert_image_url.py mock-skin-images.txt ./

EXPOSE 8000

# Default command (can be overridden by Fly) - serves API + static frontend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
