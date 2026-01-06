#!/usr/bin/env python3
"""
Script para verificar el estado actual de los runs en MLflow
"""
import os
import sys
sys.path.insert(0, '/home/charles-darwin/Morchellapp/Exploracion2030Backend/src')

import mlflow

# Configurar tracking URI
tracking_uri = 'http://mlflow:5001'
mlflow.set_tracking_uri(tracking_uri)

print(f"📊 Tracking URI: {tracking_uri}")
print(f"="*80)

# Obtener experimento
experiment = mlflow.get_experiment_by_name("morchella_detection")
if experiment:
    exp_id = experiment.experiment_id
    print(f"✅ Experimento encontrado: {experiment.name} (ID: {exp_id})")
    print(f"="*80)
    
    # Obtener todos los runs
    runs = mlflow.search_runs(experiment_ids=[exp_id], order_by=["start_time desc"], max_results=5)
    
    if len(runs) > 0:
        print(f"\n📝 Últimos {len(runs)} runs:")
        print("="*80)
        
        for idx, run in enumerate(runs, 1):
            print(f"\n{idx}. Run ID: {run.run_id}")
            print(f"   Status: {run.status}")
            print(f"   Timestamp: {run.start_time}")
            print(f"   Métricas:")
            for key, value in run.data.metrics.items():
                print(f"     - {key}: {value:.4f}" if isinstance(value, float) else f"     - {key}: {value}")
            print(f"   Artifacts: {len(run.data.tags)} tags, {len(run.data.params)} params")
            
            # Intentar obtener la lista de artifacts
            client = mlflow.tracking.MlflowClient(tracking_uri)
            artifacts = client.list_artifacts(run.run_id)
            if artifacts:
                print(f"   Archivos en artifacts:")
                for artifact in artifacts:
                    print(f"     - {artifact.path} (isdir={artifact.is_dir})")
    else:
        print("❌ No hay runs registrados en este experimento")
else:
    print("❌ Experimento no encontrado")

print("\n" + "="*80)
print("✅ Verificación completada")
