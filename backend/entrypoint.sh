#!/bin/sh
set -eu

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; do
    echo "Ожидание доступности PostgreSQL..."
    sleep 1
done

alembic upgrade head

exec "$@"
