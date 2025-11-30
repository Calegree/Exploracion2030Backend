#!/usr/bin/env bash
# Wait-for script that checks Postgres connectivity using a tiny Python test.
# It attempts to connect as $MLFLOW_PG_USER to $MLFLOW_PG_DB on host 'postgres'.

set -euo pipefail

HOST=${POSTGRES_HOST:-postgres}
PORT=${POSTGRES_PORT:-5432}
USER=${MLFLOW_PG_USER:-mlflow}
PASS=${MLFLOW_PG_PASSWORD:-mlflowpass}
DB=${MLFLOW_PG_DB:-morchellappdb}

echo "Waiting for Postgres at ${HOST}:${PORT} to accept connections for user '${USER}'..."
tries=0
max_tries=60
sleep_time=1

check() {
  python - <<PY
import sys
import psycopg2
try:
    conn = psycopg2.connect(host='${HOST}', port=${PORT}, user='${USER}', password='${PASS}', dbname='${DB}', connect_timeout=2)
    conn.close()
    sys.exit(0)
except Exception as e:
    # Non-zero exit
    #print(e)
    sys.exit(2)
PY
}

until check; do
  tries=$((tries+1))
  if [ "$tries" -ge "$max_tries" ]; then
    echo "Timed out waiting for Postgres to be ready after ${max_tries} tries. Exiting." >&2
    exit 1
  fi
  echo "Postgres not ready yet (attempt ${tries}/${max_tries}). Retrying in ${sleep_time}s..."
  sleep ${sleep_time}
done

echo "Postgres is ready and accepted connection for user '${USER}'. Starting MLflow server..."

# Exec mlflow server with provided env vars; prefer using MLFLOW_PG_* variables if set
exec mlflow server \
  --backend-store-uri "postgresql://${USER}:${PASS}@${HOST}:${PORT}/${DB}" \
  --default-artifact-root "${MLFLOW_DEFAULT_ARTIFACT_ROOT:-s3://mlflow/}" \
  --host 0.0.0.0 --port ${MLFLOW_PORT:-5001} --serve-artifacts
