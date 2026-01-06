#!/usr/bin/env bash
set -euo pipefail

# Clean MinIO artifacts for MLflow.
#
# Usage:
#   scripts/clean_minio.sh all             # removes entire bucket (default 'mlflow')
#   scripts/clean_minio.sh <run_id>        # removes artifacts for a specific run_id
#   MLFLOW_BUCKET=mybucket scripts/clean_minio.sh all
#
# This uses a temporary minio/mc container with host network to talk to localhost:9000.

BUCKET=${MLFLOW_BUCKET:-mlflow}
ACCESS_KEY=${MINIO_ROOT_USER:-minioadmin}
SECRET_KEY=${MINIO_ROOT_PASSWORD:-minioadmin}
ENDPOINT=${MINIO_ENDPOINT_URL:-http://localhost:9000}

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <run_id>|all"
  exit 1
fi

TARGET=$1

MC_HOST="${ENDPOINT/http:\/\//http://}${ACCESS_KEY:+}" # keep for message only

if [[ "$TARGET" == "all" ]]; then
  echo "[MinIO] Deleting entire bucket '${BUCKET}' from ${ENDPOINT}"
  docker run --rm --network host -e MC_HOST_local="${ENDPOINT/http:\/\//http://}${ACCESS_KEY}:${SECRET_KEY}@${ENDPOINT#*://}" minio/mc sh -c \
    "mc ls local/${BUCKET} >/dev/null 2>&1 || true; mc rm -r --force local/${BUCKET}"
else
  echo "[MinIO] Deleting run artifacts '${TARGET}' from bucket '${BUCKET}'"
  docker run --rm --network host -e MC_HOST_local="${ENDPOINT/http:\/\//http://}${ACCESS_KEY}:${SECRET_KEY}@${ENDPOINT#*://}" minio/mc sh -c \
    "mc ls local/${BUCKET}/${TARGET} >/dev/null 2>&1 || true; mc rm -r --force local/${BUCKET}/${TARGET}"
fi

echo "[MinIO] Cleanup complete."
