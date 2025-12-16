#!/usr/bin/env python3
"""
test_activate_mlflow_model.py - Script para probar la activación de modelos desde MLflow

Uso:
    python test_activate_mlflow_model.py [run_id]
    
Si no se proporciona run_id, lista los runs disponibles.
"""

import sys
import requests
import json
from mlflow.tracking import MlflowClient
from datetime import datetime

BASE_URL = "http://localhost:5000"

def list_available_runs():
    """Lista los runs disponibles en MLflow"""
    try:
        client = MlflowClient()
        experiments = client.search_experiments()
        
        print("=" * 80)
        print("📋 RUNS DISPONIBLES EN MLFLOW")
        print("=" * 80)
        
        all_runs = []
        
        for exp in experiments:
            runs = client.search_runs(
                experiment_ids=[exp.experiment_id],
                filter_string="attributes.status = 'FINISHED'",
                order_by=["start_time DESC"],
                max_results=20
            )
            
            if runs:
                print(f"\n🔬 Experimento: {exp.name} (ID: {exp.experiment_id})")
                print("-" * 80)
                
                for run in runs:
                    all_runs.append(run)
                    metrics = run.data.metrics
                    params = run.data.params
                    
                    model_type = params.get('model_type', 'N/A')
                    val_acc = metrics.get('val_accuracy', metrics.get('accuracy', 0))
                    val_loss = metrics.get('val_loss', metrics.get('loss', 0))
                    
                    start_time = datetime.fromtimestamp(run.info.start_time/1000.0)
                    
                    print(f"\n  🔗 Run ID: {run.info.run_id}")
                    print(f"     📁 Modelo: {model_type}")
                    print(f"     📊 Val Accuracy: {val_acc:.4f}")
                    print(f"     📊 Val Loss: {val_loss:.4f}")
                    print(f"     📅 Fecha: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"     ⏱️  Duración: {run.data.params.get('duration', 'N/A')}")
        
        print("\n" + "=" * 80)
        print(f"Total de runs encontrados: {len(all_runs)}")
        print("=" * 80)
        
        return all_runs
        
    except Exception as e:
        print(f"❌ Error al listar runs: {e}")
        return []

def test_activate_model(run_id):
    """Prueba activar un modelo usando el run_id"""
    url = f"{BASE_URL}/upload/model/{run_id}"
    
    print("=" * 80)
    print(f"🔄 ACTIVANDO MODELO DESDE MLFLOW")
    print("=" * 80)
    print(f"URL: {url}")
    print(f"Run ID: {run_id}")
    print("-" * 80)
    
    try:
        response = requests.post(url, timeout=60)
        
        print(f"\n📡 Respuesta HTTP: {response.status_code}")
        print("-" * 80)
        
        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
        
        if response.status_code == 200:
            print("\n" + "=" * 80)
            print("✅ MODELO ACTIVADO EXITOSAMENTE")
            print("=" * 80)
            
            if 'model' in data:
                model_info = data['model']
                print(f"\n📦 Información del Modelo:")
                print(f"   • Nombre: {model_info.get('name', 'N/A')}")
                print(f"   • Tipo: {model_info.get('model_type', 'N/A')}")
                print(f"   • Input Shape: {model_info.get('input_shape', 'N/A')}")
                print(f"   • Output Shape: {model_info.get('output_shape', 'N/A')}")
                print(f"   • Tamaño: {model_info.get('size', 0) / (1024*1024):.2f} MB")
            
            if 'metrics' in data:
                print(f"\n📊 Métricas de Validación:")
                for key, value in sorted(data['metrics'].items()):
                    print(f"   • {key}: {value:.4f}")
            
            print("\n🚀 El modelo está listo para hacer predicciones!")
            print(f"   Prueba: curl -X POST -F 'imagen=@tu_imagen.jpg' {BASE_URL}/predict")
            
        else:
            print("\n" + "=" * 80)
            print("❌ ERROR AL ACTIVAR MODELO")
            print("=" * 80)
            
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar a la API")
        print(f"   Verifica que la API esté corriendo en {BASE_URL}")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_active_model():
    """Verifica qué modelo está actualmente activo"""
    url = f"{BASE_URL}/upload/active"
    
    print("\n" + "=" * 80)
    print("🔍 VERIFICANDO MODELO ACTIVO")
    print("=" * 80)
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('active_model'):
                print(f"\n✅ Modelo activo encontrado:")
                print(f"   • Nombre: {data.get('active_model', 'N/A')}")
                print(f"   • Run ID: {data.get('run_id', 'N/A')}")
                print(f"   • Path: {data.get('local_path', 'N/A')}")
                print(f"   • Activado: {data.get('set_at', 'N/A')}")
            else:
                print("\n⚠️  No hay ningún modelo activo")
        else:
            print(f"\n❌ Error al verificar modelo activo: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("=" * 80)

def main():
    if len(sys.argv) < 2:
        print("\n📋 Listando runs disponibles en MLflow...\n")
        runs = list_available_runs()
        
        if runs:
            print("\n💡 Para activar un modelo, usa:")
            print(f"   python {sys.argv[0]} <run_id>")
            print("\nEjemplo:")
            if runs:
                print(f"   python {sys.argv[0]} {runs[0].info.run_id}")
        
        check_active_model()
        return
    
    run_id = sys.argv[1]
    
    # Verificar estado inicial
    check_active_model()
    
    # Activar modelo
    success = test_activate_model(run_id)
    
    # Verificar estado final
    if success:
        check_active_model()

if __name__ == "__main__":
    main()
