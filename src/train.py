#!/usr/bin/env python3
"""
Script unificado para entrenar modelos de clasificación de Morchella
Permite elegir entre MobileNetV2 y EfficientNetB0
"""

import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(
        description='🍄 Entrenamiento de modelos para detección de Morchella',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  
  Entrenar con MobileNetV2 (ligero y rápido):
    python train.py --model mobilenet
  
  Entrenar con EfficientNetB0 (mayor precisión):
    python train.py --model efficientnet
  
  Entrenar ambos modelos secuencialmente:
    python train.py --model both
  
  Comparar resultados después del entrenamiento:
    python compare_models.py
        """
    )
    
    parser.add_argument(
        '--model',
        type=str,
        choices=['mobilenet', 'efficientnet', 'both'],
        default='mobilenet',
        help='Arquitectura del modelo a entrenar (default: mobilenet)'
    )
    
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Comparar resultados después del entrenamiento'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("🍄 ENTRENAMIENTO DE MODELOS PARA DETECCIÓN DE MORCHELLA")
    print("="*80)
    
    # Verificar que existe el dataset
    dataset_path = os.path.join(os.path.dirname(__file__), 'dataset')
    if not os.path.exists(dataset_path):
        print("\n❌ Error: No se encontró el directorio 'dataset'")
        print("💡 Descarga el dataset primero usando el endpoint /download/fungis2")
        sys.exit(1)
    
    morchella_path = os.path.join(dataset_path, 'morchella')
    no_morchella_path = os.path.join(dataset_path, 'no_morchella')
    
    if not os.path.exists(morchella_path) or not os.path.exists(no_morchella_path):
        print("\n❌ Error: Faltan las carpetas 'morchella' o 'no_morchella' en dataset/")
        print("💡 Estructura esperada:")
        print("   dataset/")
        print("   ├── morchella/")
        print("   └── no_morchella/")
        sys.exit(1)
    
    # Contar imágenes
    import glob
    morchella_count = len(glob.glob(os.path.join(morchella_path, '*.jpg')) + 
                         glob.glob(os.path.join(morchella_path, '*.jpeg')))
    no_morchella_count = len(glob.glob(os.path.join(no_morchella_path, '*.jpg')) + 
                             glob.glob(os.path.join(no_morchella_path, '*.jpeg')))
    
    print(f"\n📊 Dataset detectado:")
    print(f"   • Morchella: {morchella_count} imágenes")
    print(f"   • NO-Morchella: {no_morchella_count} imágenes")
    print(f"   • Total: {morchella_count + no_morchella_count} imágenes")
    
    if morchella_count < 50 or no_morchella_count < 50:
        print("\n⚠️  Advertencia: Dataset pequeño (recomendado: >100 imágenes por clase)")
        print("💡 Considera descargar más imágenes para mejor entrenamiento")
    
    print("\n" + "="*80)
    
    # Entrenar según la opción seleccionada
    if args.model == 'mobilenet':
        print("📱 Entrenando con MobileNetV2...")
        print("="*80 + "\n")
        from train_model_mobilenet import train_model
        model, history = train_model()
        
    elif args.model == 'efficientnet':
        print("🎯 Entrenando con EfficientNetB0...")
        print("="*80 + "\n")
        from train_model_efficientnet import train_model
        model, history = train_model()
        
    elif args.model == 'both':
        print("🔄 Entrenando ambos modelos secuencialmente...")
        print("="*80 + "\n")
        
        print("1️⃣ Fase 1: MobileNetV2")
        print("-"*80)
        from train_model_mobilenet import train_model as train_mobilenet
        model_mobile, history_mobile = train_mobilenet()
        
        print("\n" + "="*80)
        print("2️⃣ Fase 2: EfficientNetB0")
        print("-"*80)
        from train_model_efficientnet import train_model as train_efficientnet
        model_efficient, history_efficient = train_efficientnet()
        
        print("\n" + "="*80)
        print("✅ Ambos modelos entrenados exitosamente")
        print("="*80)
    
    # Comparar si se solicitó
    if args.compare:
        print("\n" + "="*80)
        print("📊 Generando comparación de modelos...")
        print("="*80 + "\n")
        
        try:
            from compare_models import compare_models
            compare_models()
        except ImportError as e:
            print(f"⚠️  No se pudo cargar el módulo de comparación: {e}")
            print("💡 Ejecuta manualmente: python compare_models.py")
    
    print("\n" + "="*80)
    print("🎉 ENTRENAMIENTO COMPLETADO")
    print("="*80)
    print("📈 Para ver los resultados en MLflow:")
    print("   mlflow ui")
    print("   http://localhost:5001")
    print("\n📊 Para comparar modelos:")
    print("   python compare_models.py")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Entrenamiento interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante el entrenamiento: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
