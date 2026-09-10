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

EXPOSE 8000 

HEALTHCHECK --interval=10s --timeout=3s --retries=3 CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["sh", "-c", "exec uvicorn main:app --app-dir /backend/src --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS:-2} --log-level info --no-access-log"]
