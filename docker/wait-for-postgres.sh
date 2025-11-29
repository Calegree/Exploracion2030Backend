#!/bin/sh
set -e

# Extraer host y puerto de DATABASE_URL si está definida, fallback a postgres:5432
DB_URL="${DATABASE_URL:-postgresql://morchellappusr:morchellapppass@postgres:5432/morchellappdb}"

# Parse host and port (simple)
DB_HOST=$(echo "$DB_URL" | sed -E 's#.*@([^:/]+).*$#\1#')
DB_PORT=$(echo "$DB_URL" | sed -E 's#.*:([0-9]+)/.*#\1#' || true)
DB_PORT=${DB_PORT:-5432}

echo "Waiting for postgres at ${DB_HOST}:${DB_PORT}..."

# Espera hasta que pg_isready confirme
until pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; do
  echo "Postgres not ready, sleeping 1s..."
  sleep 1
done

echo "Postgres is ready. Starting app..."
exec "$@"
