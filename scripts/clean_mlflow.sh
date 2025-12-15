#!/usr/bin/env bash
set -euo pipefail

# Clean MLflow: soft-delete all runs in the given experiment and run GC to purge
# metadata from Postgres and remove corresponding artifacts from MinIO.
#
# Usage:
#   scripts/clean_mlflow.sh                 # cleans default experiment "morchella_detection"
#   MLFLOW_EXPERIMENT="your_exp" scripts/clean_mlflow.sh
#
# Requirements:
# - Docker Compose services running (or at least the mlflow container reachable)
# - This script executes commands inside the mlflow container, so no host deps needed

EXPERIMENT_NAME=${MLFLOW_EXPERIMENT:-morchella_detection}
BACKEND_URI=${MLFLOW_BACKEND_URI:-postgresql://mlflow:mlflowpass@postgres:5432/morchellappdb}

echo "[MLflow] Soft-deleting runs in experiment: ${EXPERIMENT_NAME}"

docker compose exec mlflow python - <<PY
from mlflow.tracking import MlflowClient
client = MlflowClient("http://localhost:5001")
exp = client.get_experiment_by_name("${EXPERIMENT_NAME}")
if not exp:
    print(f"Experiment not found: ${EXPERIMENT_NAME}")
else:
    runs = client.search_runs(exp.experiment_id)
    for r in runs:
        client.delete_run(r.info.run_id)
    print(f"Deleted {len(runs)} runs in '${EXPERIMENT_NAME}'")
PY

echo "[MLflow] Running garbage collection (permanent delete)"
docker compose exec mlflow mlflow gc --backend-store-uri "${BACKEND_URI}"

echo "[MLflow] Cleanup complete."
