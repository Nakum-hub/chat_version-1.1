FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CYBERFYX_RUN_MIGRATIONS_ON_START=true
ENV CYBERFYX_RUN_SEED_ON_START=true

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic ./alembic
COPY scripts ./scripts

RUN python -m pip install --upgrade pip && \
    python -m pip install . && \
    chmod +x /app/scripts/docker-entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=3)"

ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
