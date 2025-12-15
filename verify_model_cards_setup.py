#!/usr/bin/env python3
"""
Script de verificación del sistema de Model Cards

Verifica que todo está instalado y configurado correctamente
"""

import sys
import os
import subprocess
from pathlib import Path


def check_python_modules():
    """Verifica que los módulos Python necesarios están disponibles"""
    print("🔍 Verificando módulos Python...")
    
    required_modules = [
        ('mlflow', 'MLflow'),
        ('tensorflow', 'TensorFlow'),
        ('sklearn', 'Scikit-learn'),
        ('PIL', 'Pillow'),
    ]
    
    all_ok = True
    for module_name, display_name in required_modules:
        try:
            __import__(module_name)
            print(f"   ✅ {display_name}")
        except ImportError:
            print(f"   ❌ {display_name} NO ENCONTRADO")
            all_ok = False
    
    return all_ok


def check_quarto():
    """Verifica que Quarto está instalado"""
    print("\n🔍 Verificando Quarto...")
    
    try:
        result = subprocess.run(['quarto', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"   ✅ Quarto instalado: {version}")
        return True
    except FileNotFoundError:
        print(f"   ❌ Quarto NO ENCONTRADO")
        print(f"   💡 Instala con: bash install_quarto.sh")
        return False


def check_files():
    """Verifica que todos los archivos necesarios existen"""
    print("\n🔍 Verificando archivos...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        ('src/model_card_generator.py', 'Generador principal'),
        ('src/model_card_utils.py', 'Utilidades CLI'),
        ('src/model_card_config.py', 'Configuración'),
        ('model_cards/model-card-style.css', 'Estilos CSS'),
        ('model_cards/README.md', 'Documentación'),
        ('QUICKSTART_MODEL_CARDS.md', 'Guía rápida'),
    ]
    
    all_ok = True
    for filepath, description in required_files:
        full_path = os.path.join(script_dir, filepath)
        if os.path.exists(full_path):
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} NO ENCONTRADO: {filepath}")
            all_ok = False
    
    return all_ok


def check_mlflow_connection():
    """Verifica que MLflow está accesible"""
    print("\n🔍 Verificando MLflow...")
    
    try:
        import mlflow
        from model_card_config import ensure_mlflow_connection
        
        if ensure_mlflow_connection():
            print(f"   ✅ MLflow accesible")
            return True
        else:
            print(f"   ⚠️ MLflow no se puede alcanzar (opcional para setup)")
            print(f"   💡 Asegúrate de que MLflow esté corriendo en:")
            print(f"       http://localhost:5001 (local)")
            print(f"       http://mlflow:5001 (Docker)")
            return True  # No es crítico en esta fase
    except Exception as e:
        print(f"   ⚠️ Error al verificar MLflow: {e}")
        return True  # No es crítico en esta fase


def check_imports():
    """Verifica que los módulos de Model Cards se pueden importar"""
    print("\n🔍 Verificando importes de Model Cards...")
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    all_ok = True
    
    try:
        import model_card_generator
        print(f"   ✅ model_card_generator")
    except ImportError as e:
        print(f"   ❌ model_card_generator: {e}")
        all_ok = False
    
    try:
        import model_card_utils
        print(f"   ✅ model_card_utils")
    except ImportError as e:
        print(f"   ❌ model_card_utils: {e}")
        all_ok = False
    
    try:
        import model_card_config
        print(f"   ✅ model_card_config")
    except ImportError as e:
        print(f"   ❌ model_card_config: {e}")
        all_ok = False
    
    return all_ok


def print_summary(results):
    """Imprime resumen de verificación"""
    print("\n" + "="*60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*60)
    
    all_ok = all(results.values())
    
    if all_ok:
        print("""
✅ ¡SISTEMA LISTO PARA FUNCIONAR!

🚀 Próximos pasos:

1. Entrenar un modelo:
   docker-compose exec api python src/train.py --model efficientnet

2. Compilar Model Cards:
   python src/model_card_utils.py compile-all

3. Abrir en navegador:
   python src/model_card_utils.py open

📖 Para más información:
   - QUICKSTART_MODEL_CARDS.md (5 minutos)
   - model_cards/README.md (documentación completa)
        """)
    else:
        print("""
⚠️ FALTAN ALGUNOS COMPONENTES

Soluciona los errores marcados con ❌:

1. Si falta Quarto:
   bash install_quarto.sh

2. Si faltan módulos Python:
   pip install -r requirements.txt

3. Si faltan archivos:
   Asegúrate de tener todos los .py en src/

📖 Para más ayuda:
   Ver SYSTEM_SETUP_COMPLETE.md
        """)
    
    print("="*60)
    return all_ok


def main():
    """Ejecuta todas las verificaciones"""
    
    print("""
╔═══════════════════════════════════════════════════════╗
║  🍄 Verificador de Sistema de Model Cards           ║
║     Morchella Detection Project                       ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    results = {
        'Python modules': check_python_modules(),
        'Quarto': check_quarto(),
        'Files': check_files(),
        'MLflow connection': check_mlflow_connection(),
        'Model Card imports': check_imports(),
    }
    
    all_ok = print_summary(results)
    
    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()
