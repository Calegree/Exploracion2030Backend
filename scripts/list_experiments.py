#!/usr/bin/env python3
"""List MLflow experiments using MlflowClient pointing at localhost:5001.
Run: python scripts/list_experiments.py
"""
from mlflow.tracking import MlflowClient
import os

# Ensure we point to the docker mlflow server exposed on localhost
os.environ.setdefault("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001")

if __name__ == "__main__":
    client = MlflowClient()
    exps = client.list_experiments()
    if not exps:
        print("No experiments found")
    else:
        for e in exps:
            print(f"{e.experiment_id}\t{e.name}\t(lifecycle_stage={e.lifecycle_stage})")
