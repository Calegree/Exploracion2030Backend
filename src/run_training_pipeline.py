#!/usr/bin/env python3
"""
Script principal para entrenar el modelo de Morchella con MLflow
Este script automatiza todo el proceso de entrenamiento y configuración
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_step(step_num, description):
    """Imprime un paso del proceso"""
    print(f"\n📋 Paso {step_num}: {description}")
    print("-" * 40)

def run_script(script_name, description):
    """Ejecuta un script de Python"""
    print(f"🔄 Ejecutando: {description}")
    print(f"   Script: {script_name}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            print("✅ Ejecutado exitosamente")
            if result.stdout:
                print("   Salida:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        print(f"   {line}")
        else:
            print("❌ Error en la ejecución")
            if result.stderr:
                print("   Error:")
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        print(f"   {line}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando {script_name}: {e}")
        return False
    
    return True

def check_dataset():
    """Verifica que el dataset esté disponible"""
    print_step(1, "Verificando dataset")
    
    dataset_path = Path(__file__).parent / "dataset"
    morchella_path = dataset_path / "morchella"
    no_morchella_path = dataset_path / "no_morchella"
    
    if not dataset_path.exists():
        print("❌ Directorio dataset no encontrado")
        return False
    
    if not morchella_path.exists():
        print("❌ Directorio morchella no encontrado")
        return False
    
    if not no_morchella_path.exists():
        print("❌ Directorio no_morchella no encontrado")
        return False
    
    # Contar imágenes
    morchella_images = len(list(morchella_path.glob("*.jpg")) + list(morchella_path.glob("*.jpeg")))
    no_morchella_images = len(list(no_morchella_path.glob("*.jpg")) + list(no_morchella_path.glob("*.jpeg")))
    
    print(f"✅ Dataset encontrado:")
    print(f"   - Morchella: {morchella_images} imágenes")
    print(f"   - No Morchella: {no_morchella_images} imágenes")
    print(f"   - Total: {morchella_images + no_morchella_images} imágenes")
    
    if morchella_images == 0 or no_morchella_images == 0:
        print("⚠️ Advertencia: Uno de los directorios está vacío")
        return False
    
    return True

def setup_mlflow():
    """Configura MLflow"""
    print_step(2, "Configurando MLflow")
    
    # Limpiar configuración anterior
    if not run_script("clean_mlflow.py", "Limpiando configuración anterior de MLflow"):
        return False
    
    # Verificar configuración
    if not run_script("verify_mlflow_setup.py", "Verificando configuración de MLflow"):
        return False
    
    return True

def train_model():
    """Entrena el modelo"""
    print_step(3, "Entrenando modelo")
    
    if not run_script("train_model.py", "Entrenando modelo de Morchella"):
        return False
    
    return True

def start_ui():
    """Inicia la interfaz de MLflow"""
    print_step(4, "Iniciando MLflow UI")
    
    print("🌐 Iniciando servidor MLflow UI...")
    print("   URL: http://localhost:5000")
    print("   Para detener: Ctrl+C")
    
    try:
        subprocess.run([
            sys.executable, "-m", "mlflow", "ui",
            "--backend-store-uri", "sqlite:///mlflow.db",
            "--host", "0.0.0.0",
            "--port", "5000"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    
    return True

def main():
    """Función principal"""
    print_header("PIPELINE DE ENTRENAMIENTO - MORCHELLA DETECTION")
    
    print("Este script te guiará a través de todo el proceso de entrenamiento")
    print("y configuración de MLflow con SQLite.")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("train_model.py"):
        print("❌ Error: Debes ejecutar este script desde el directorio src/")
        print("   Comando: cd src && python run_training_pipeline.py")
        return
    
    # Paso 1: Verificar dataset
    if not check_dataset():
        print("\n❌ Error en la verificación del dataset")
        print("   Asegúrate de tener imágenes en dataset/morchella/ y dataset/no_morchella/")
        return
    
    # Paso 2: Configurar MLflow
    if not setup_mlflow():
        print("\n❌ Error en la configuración de MLflow")
        return
    
    # Paso 3: Entrenar modelo
    if not train_model():
        print("\n❌ Error en el entrenamiento del modelo")
        return
    
    # Paso 4: Preguntar si quiere iniciar la UI
    print("\n🎉 ¡Entrenamiento completado exitosamente!")
    print("\n¿Quieres iniciar MLflow UI para ver los resultados? (s/n): ", end="")
    
    try:
        response = input().lower().strip()
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            start_ui()
        else:
            print("\n📝 Para ver los resultados más tarde:")
            print("   cd src")
            print("   python start_mlflow_ui.py")
            print("   O ejecuta: mlflow ui --backend-store-uri sqlite:///mlflow.db")
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")

if __name__ == "__main__":
    main() 