#!/usr/bin/env python3
"""
Script para configurar el modelo para predicciones
"""

import os
import sys
import mlflow
from mlflow_manager import MLflowManager

def setup_model_for_prediction():
    """
    Configura el modelo para ser usado en predicciones
    """
    print("🔧 Configurando modelo para predicciones...")
    print("=" * 50)
    
    # Configurar MLflow
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    manager = MLflowManager()
    
    # Verificar experimentos disponibles
    experiments = manager.list_experiments()
    print(f"📊 Experimentos disponibles: {len(experiments)}")
    
    for exp in experiments:
        print(f"   - {exp.name} (ID: {exp.experiment_id})")
    
    # Verificar runs disponibles
    runs = manager.list_runs()
    print(f"\n📈 Runs disponibles: {len(runs)}")
    
    if len(runs) == 0:
        print("❌ No hay runs disponibles")
        print("   Ejecuta primero: python train_model.py")
        return False
    
    # Mostrar los últimos 5 runs
    print("\n�� Últimos 5 runs:")
    for i, run in runs.head(5).iterrows():
        run_id = run['run_id']
        accuracy = run.get('metrics.val_accuracy', 'N/A')
        loss = run.get('metrics.val_loss', 'N/A')
        print(f"   {i+1}. Run {run_id[:8]}... | Accuracy: {accuracy} | Loss: {loss}")
    
    # Obtener el mejor run
    best_run = manager.get_best_run()
    if best_run is not None:
        print(f"\n🏆 Mejor run encontrado:")
        print(f"   - Run ID: {best_run['run_id']}")
        print(f"   - Accuracy: {best_run.get('metrics.val_accuracy', 'N/A')}")
        print(f"   - Loss: {best_run.get('metrics.val_loss', 'N/A')}")
        
        # Registrar el modelo
        try:
            manager.register_model(best_run['run_id'], "morchella_model")
            print("✅ Modelo registrado exitosamente")
        except Exception as e:
            print(f"⚠️ Error registrando modelo: {e}")
        
        # Exportar información del modelo
        model_info = manager.export_model_info()
        if model_info:
            print("✅ Información del modelo exportada")
    
    # Verificar que el modelo se puede cargar
    print("\n�� Probando carga del modelo...")
    try:
        # Intentar cargar el mejor modelo
        run_id = best_run['run_id']
        model_uri = f"runs:/{run_id}/model"
        model = mlflow.keras.load_model(model_uri)
        print("✅ Modelo cargado exitosamente desde MLflow")
        print(f"   - Input shape: {model.input_shape}")
        print(f"   - Output shape: {model.output_shape}")
        
        # Probar predicción con datos dummy
        import numpy as np
        dummy_input = np.random.random((1, 224, 224, 3))
        prediction = model.predict(dummy_input, verbose=0)
        print(f"   - Predicción de prueba: {prediction[0][0]:.4f}")
        
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Configuración completada exitosamente!")
    print("=" * 50)
    print("📝 El modelo está listo para ser usado en predicciones")
    print("🌐 Puedes usar el endpoint /predict en tu API Flask")
    
    return True

if __name__ == "__main__":
    setup_model_for_prediction() 