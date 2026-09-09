FROM python:3.13-alpine

WORKDIR /backend

COPY requirements.txt requirements.txt

RUN apk add --no-cache \
    postgresql-dev \
    postgresql-client \
    build-base \
    curl \
    git

RUN pip install pip-tools && \
    pip-sync requirements.txt

COPY . .

RUN chmod +x /backend/entrypoint.sh

EXPOSE 8000 

HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD curl -f http://localhost:8000/api/health || exit 1

ENTRYPOINT ["/backend/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--app-dir", "/backend/src", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info", "--access-log"]
