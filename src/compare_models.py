#!/usr/bin/env python3
"""
Script para comparar resultados de modelos MobileNetV2 vs EfficientNetB0
Analiza los runs de MLflow y genera un reporte comparativo
"""

import mlflow
import pandas as pd
from tabulate import tabulate
import os

def setup_mlflow():
    """Configura conexión a MLflow"""
    tracking_uri = os.getenv('MLFLOW_TRACKING_URI', 'http://mlflow:5001')
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("morchella_detection")
    return tracking_uri

def get_recent_runs(model_type=None, limit=5):
    """
    Obtiene los runs recientes filtrados por tipo de modelo
    
    Args:
        model_type: 'MobileNetV2' o 'EfficientNetB0' o None para todos
        limit: Número máximo de runs a retornar
    """
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("morchella_detection")
    
    if not experiment:
        print("❌ No se encontró el experimento 'morchella_detection'")
        return []
    
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"],
        max_results=50
    )
    
    # Filtrar por tipo de modelo si se especifica
    if model_type:
        runs = [r for r in runs if r.data.tags.get('model_type') == model_type]
    
    return runs[:limit]

def extract_run_info(run):
    """Extrae información relevante de un run"""
    return {
        'run_id': run.info.run_id[:8],
        'name': run.data.tags.get('mlflow.runName', 'N/A'),
        'model_type': run.data.tags.get('model_type', 'Unknown'),
        'accuracy': run.data.metrics.get('val_accuracy', 0),
        'loss': run.data.metrics.get('val_loss', 0),
        'precision': run.data.metrics.get('val_precision', 0),
        'recall': run.data.metrics.get('val_recall', 0),
        'f1_score': run.data.metrics.get('val_f1_score', 0),
        'dataset_size': run.data.tags.get('dataset_size', 'N/A'),
        'epochs': run.data.params.get('epochs', 'N/A'),
        'batch_size': run.data.params.get('batch_size', 'N/A'),
        'learning_rate': run.data.params.get('learning_rate', 'N/A')
    }

def compare_models():
    """Compara los mejores runs de cada arquitectura"""
    print("🔧 Configurando MLflow...")
    tracking_uri = setup_mlflow()
    print(f"📊 Tracking URI: {tracking_uri}\n")
    
    print("="*80)
    print("📊 COMPARACIÓN DE MODELOS - MobileNetV2 vs EfficientNetB0")
    print("="*80)
    
    # Obtener runs de MobileNetV2
    print("\n🔍 Buscando runs de MobileNetV2...")
    mobilenet_runs = get_recent_runs('MobileNetV2', limit=5)
    
    # Obtener runs de EfficientNet
    print("🔍 Buscando runs de EfficientNetB0...")
    efficientnet_runs = get_recent_runs('EfficientNetB0', limit=5)
    
    if not mobilenet_runs and not efficientnet_runs:
        print("\n❌ No se encontraron runs para comparar.")
        print("💡 Entrena modelos usando:")
        print("   - python train_model_mobilenet.py")
        print("   - python train_model_efficientnet.py")
        return
    
    # Procesar datos de MobileNetV2
    mobilenet_data = []
    if mobilenet_runs:
        print(f"\n📱 MobileNetV2: {len(mobilenet_runs)} runs encontrados")
        for run in mobilenet_runs:
            mobilenet_data.append(extract_run_info(run))
    
    # Procesar datos de EfficientNet
    efficientnet_data = []
    if efficientnet_runs:
        print(f"🎯 EfficientNetB0: {len(efficientnet_runs)} runs encontrados")
        for run in efficientnet_runs:
            efficientnet_data.append(extract_run_info(run))
    
    # Mostrar tabla comparativa de MobileNetV2
    if mobilenet_data:
        print("\n" + "="*80)
        print("📱 RUNS DE MobileNetV2")
        print("="*80)
        df_mobile = pd.DataFrame(mobilenet_data)
        print(tabulate(
            df_mobile[['run_id', 'accuracy', 'loss', 'precision', 'recall', 'f1_score']],
            headers=['Run ID', 'Accuracy', 'Loss', 'Precision', 'Recall', 'F1-Score'],
            tablefmt='grid',
            floatfmt='.4f'
        ))
        
        best_mobile = max(mobilenet_data, key=lambda x: x['accuracy'])
        print(f"\n🏆 Mejor run MobileNetV2: {best_mobile['run_id']} - Accuracy: {best_mobile['accuracy']:.4f}")
    
    # Mostrar tabla comparativa de EfficientNet
    if efficientnet_data:
        print("\n" + "="*80)
        print("🎯 RUNS DE EfficientNetB0")
        print("="*80)
        df_efficient = pd.DataFrame(efficientnet_data)
        print(tabulate(
            df_efficient[['run_id', 'accuracy', 'loss', 'precision', 'recall', 'f1_score']],
            headers=['Run ID', 'Accuracy', 'Loss', 'Precision', 'Recall', 'F1-Score'],
            tablefmt='grid',
            floatfmt='.4f'
        ))
        
        best_efficient = max(efficientnet_data, key=lambda x: x['accuracy'])
        print(f"\n🏆 Mejor run EfficientNetB0: {best_efficient['run_id']} - Accuracy: {best_efficient['accuracy']:.4f}")
    
    # Comparación directa entre los mejores
    if mobilenet_data and efficientnet_data:
        print("\n" + "="*80)
        print("⚔️  COMPARACIÓN DIRECTA - MEJORES MODELOS")
        print("="*80)
        
        comparison = pd.DataFrame([
            {
                'Modelo': '📱 MobileNetV2',
                'Accuracy': best_mobile['accuracy'],
                'Loss': best_mobile['loss'],
                'Precision': best_mobile['precision'],
                'Recall': best_mobile['recall'],
                'F1-Score': best_mobile['f1_score']
            },
            {
                'Modelo': '🎯 EfficientNetB0',
                'Accuracy': best_efficient['accuracy'],
                'Loss': best_efficient['loss'],
                'Precision': best_efficient['precision'],
                'Recall': best_efficient['recall'],
                'F1-Score': best_efficient['f1_score']
            }
        ])
        
        print(tabulate(
            comparison,
            headers='keys',
            tablefmt='grid',
            floatfmt='.4f',
            showindex=False
        ))
        
        # Calcular diferencias
        acc_diff = best_efficient['accuracy'] - best_mobile['accuracy']
        loss_diff = best_mobile['loss'] - best_efficient['loss']  # Invertido porque menor es mejor
        
        print("\n📊 ANÁLISIS:")
        print(f"   • Diferencia de Accuracy: {acc_diff:+.4f} ({acc_diff*100:+.2f}%)")
        print(f"   • Mejora en Loss: {loss_diff:+.4f}")
        
        if acc_diff > 0.02:
            print(f"\n✅ EfficientNetB0 muestra una mejora significativa en accuracy")
        elif acc_diff < -0.02:
            print(f"\n✅ MobileNetV2 muestra mejor performance (inusual pero posible)")
        else:
            print(f"\n⚖️  Ambos modelos tienen performance similar")
        
        # Recomendación
        print("\n💡 RECOMENDACIÓN:")
        if best_efficient['accuracy'] > best_mobile['accuracy'] + 0.02:
            print("   🎯 Usar EfficientNetB0 para máxima precisión")
        elif best_mobile['accuracy'] > best_efficient['accuracy'] + 0.01:
            print("   📱 Usar MobileNetV2 (mejor performance/recursos)")
        else:
            print("   📱 Usar MobileNetV2 (similar accuracy, más ligero y rápido)")
    
    print("\n" + "="*80)
    print("📈 Para ver detalles completos, ejecuta: mlflow ui")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        compare_models()
    except Exception as e:
        print(f"\n❌ Error durante la comparación: {str(e)}")
        print("\n💡 Asegúrate de que:")
        print("   1. MLflow está corriendo (docker-compose up)")
        print("   2. Has entrenado al menos un modelo")
        print("   3. La variable MLFLOW_TRACKING_URI está configurada")
