#!/usr/bin/env python3
"""
Script para configurar el modelo para predicciones
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

import mlflow
from .mlflow_manager import MLflowManager
from .extensions import db
from .models import ActiveModel

def setup_model_for_prediction():
    """
    Configura el modelo para ser usado en predicciones
    """
    print("🔧 Configurando modelo para predicciones...")
    print("=" * 50)
    
    # Configurar MLflow desde .env si está definido
    mlflow_uri = os.getenv('MLFLOW_TRACKING_URI', 'sqlite:///mlflow.db')
    mlflow.set_tracking_uri(mlflow_uri)
    manager = MLflowManager()

    # Obtener el mejor run y registrar como activo en la BD
    best_run = manager.get_best_run()
    if best_run is None:
        print("❌ No se encontró mejor run")
        return False

    run_id = best_run.get('run_id')
    try:
        # crear entrada activa (histórico)
        am = ActiveModel(run_id=run_id, model_name=f"run_{run_id}", local_path=None, size=None)
        db.session.add(am)
        db.session.commit()
        print(f"✅ run {run_id} guardado como activo en la BD")
    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        print(f"⚠️ No se pudo guardar ActiveModel en BD: {e}")
        return False

    # exportar info (opcional)
    manager.export_model_info()
    return True

if __name__ == "__main__":
    setup_model_for_prediction()