#!/usr/bin/env bash
set -euo pipefail

# Prune orphaned MLflow artifacts in MinIO by comparing existing run directories
# in s3 bucket with MLflow runs stored in Postgres.
#
# Usage:
#   scripts/prune_minio_orphans.sh           # dry-run (shows orphans only)
#   scripts/prune_minio_orphans.sh --apply   # delete orphan folders
#
# Env vars:
#   MLFLOW_EXPERIMENT_NAME (default: morchella_detection)
#   MLFLOW_BUCKET          (default: mlflow)
#   MINIO_ENDPOINT_URL     (default: http://localhost:9000)
#   MINIO_ROOT_USER        (default: minioadmin)
#   MINIO_ROOT_PASSWORD    (default: minioadmin)

EXP_NAME=${MLFLOW_EXPERIMENT_NAME:-morchella_detection}
EXP_ID_ENV=${MLFLOW_EXPERIMENT_ID:-}
BUCKET=${MLFLOW_BUCKET:-mlflow}
ENDPOINT=${MINIO_ENDPOINT_URL:-http://localhost:9000}
ACCESS_KEY=${MINIO_ROOT_USER:-minioadmin}
SECRET_KEY=${MINIO_ROOT_PASSWORD:-minioadmin}

APPLY=${1:-}

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "[Prune] Experiment name: $EXP_NAME"

# 1) Get experiment id and current run_ids from MLflow
#    We execute within the mlflow container and talk to localhost:5001

echo "[Prune] Fetching MLflow runs from server..."
# If EXP_ID is provided via env, we skip querying by name and only collect runs if possible
if [[ -n "$EXP_ID_ENV" ]]; then
  docker compose exec -T mlflow python - <<PY > "$TMPDIR/mlflow_runs_raw.txt"
from mlflow.tracking import MlflowClient
client = MlflowClient("http://localhost:5001")
print("EXP_ID", "${EXP_ID_ENV}")
try:
    runs = client.search_runs("${EXP_ID_ENV}", max_results=100000)
    for r in runs:
        print(r.info.run_id)
except Exception as e:
    # If experiment doesn't exist in backend, treat as no runs
    pass
PY
else
  docker compose exec -T mlflow python - <<'PY' > "$TMPDIR/mlflow_runs_raw.txt"
from mlflow.tracking import MlflowClient
client = MlflowClient("http://localhost:5001")
exp = client.get_experiment_by_name("${EXP_NAME}")
if not exp:
    print("EXP_ID")
else:
    print("EXP_ID", exp.experiment_id)
    for r in client.search_runs(exp.experiment_id, max_results=100000):
        print(r.info.run_id)
PY
fi

EXP_ID="$(head -n1 "$TMPDIR/mlflow_runs_raw.txt" | awk '{print $2}')"
if [[ -z "$EXP_ID" ]]; then
  if [[ -n "$EXP_ID_ENV" ]]; then
    EXP_ID="$EXP_ID_ENV"
    echo "[Prune] Using provided experiment id: $EXP_ID"
    # Ensure MLflow runs list exists even if empty
    : > "$TMPDIR/run_ids_mlflow.txt"
  else
    echo "[Prune] Experiment not found: $EXP_NAME (and MLFLOW_EXPERIMENT_ID not set)"
    echo "        Set MLFLOW_EXPERIMENT_ID (e.g., 1) to target bucket path directly."
    exit 1
  fi
else
  grep -v '^EXP_ID' "$TMPDIR/mlflow_runs_raw.txt" | sort -u > "$TMPDIR/run_ids_mlflow.txt"
fi


MLFLOW_RUN_COUNT=$(wc -l < "$TMPDIR/run_ids_mlflow.txt")
echo "[Prune] MLflow experiment id: $EXP_ID (runs: $MLFLOW_RUN_COUNT)"

# 2) List MinIO directory entries for s3://BUCKET/EXP_ID

echo "[Prune] Listing MinIO bucket contents for s3://$BUCKET/$EXP_ID/ ..."
docker run --rm --network host -e MC_HOST_local="http://${ACCESS_KEY}:${SECRET_KEY}@${ENDPOINT#*://}" minio/mc \
  sh -c "mc ls --json local/${BUCKET}/${EXP_ID}" > "$TMPDIR/minio_ls.json" || true

# 3) Extract run_ids from MinIO listing
awk -v expid="$EXP_ID" -v bucket="$BUCKET" '
  /\"key\":/ {
    # Extract the key value
    match($0, /\"key\":\"([^\"]+)\"/, m);
    if (m[1] != "") {
      key=m[1];
      # Expect format like: <bucket>/<exp_id>/<run_id>/[...]
      n=split(key, parts, "/");
      rid=parts[n];
      sub(/\/$/, "", rid); # remove trailing slash for directories
      # Filter out bucket and expid path components
      if (rid != expid && rid != bucket && rid != "") print rid;
    }
  }
' "$TMPDIR/minio_ls.json" | sort -u > "$TMPDIR/run_ids_minio.txt"

MINIO_RUN_COUNT=$(wc -l < "$TMPDIR/run_ids_minio.txt")
echo "[Prune] MinIO run directories found: $MINIO_RUN_COUNT"

# 4) Compute orphans: present in MinIO, absent in MLflow
comm -23 "$TMPDIR/run_ids_minio.txt" "$TMPDIR/run_ids_mlflow.txt" > "$TMPDIR/orphans.txt" || true

ORPHAN_COUNT=$(wc -l < "$TMPDIR/orphans.txt" || echo 0)
echo "[Prune] Orphan runs detected under s3://${BUCKET}/${EXP_ID}/: $ORPHAN_COUNT"

if [[ "$ORPHAN_COUNT" -gt 0 ]]; then
  echo "[Prune] List of orphan run_ids:"
  cat "$TMPDIR/orphans.txt"
else
  echo "[Prune] No orphan runs detected."
fi

# 5) Delete orphans if --apply provided
if [[ "$APPLY" == "--apply" && "$ORPHAN_COUNT" -gt 0 ]]; then
  echo "[Prune] Deleting orphan run directories..."
  while read -r rid; do
    [[ -z "$rid" ]] && continue
    echo "[Prune] Removing s3://${BUCKET}/${EXP_ID}/${rid}"
    docker run --rm --network host -e MC_HOST_local="http://${ACCESS_KEY}:${SECRET_KEY}@${ENDPOINT#*://}" minio/mc \
      mc rm -r --force "local/${BUCKET}/${EXP_ID}/${rid}"
  done < "$TMPDIR/orphans.txt"
  echo "[Prune] Deletion complete."
else
  echo "[Prune] Dry-run complete. Re-run with --apply to delete."
fi
