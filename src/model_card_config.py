"""
Configuración e integración de Model Card Generator con Docker y MLflow

Este módulo proporciona utilidades para:
- Obtener información de MLflow (local o remoto)
- Manejo de artifacts
- Logging automático de datos
"""

import os
from typing import Optional

# Configuración por defecto
DEFAULT_MLFLOW_URI = "http://mlflow:5001"  # Para Docker
LOCAL_MLFLOW_URI = "http://127.0.0.1:5001"  # Para local

# Directorio de Model Cards (relativo a src/)
MODEL_CARDS_DIR = "../model_cards"


def get_mlflow_tracking_uri() -> str:
    """
    Obtiene la URI de MLflow desde variable de entorno o defaults
    
    Order de precedencia:
    1. MLFLOW_TRACKING_URI (variable de entorno)
    2. LOCAL_MLFLOW_URI si hay conexión local
    3. DEFAULT_MLFLOW_URI
    """
    
    # 1. Variable de entorno explícita
    uri = os.getenv('MLFLOW_TRACKING_URI')
    if uri:
        return uri
    
    # 2. Intentar local primero
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 5001))
        sock.close()
        if result == 0:
            return LOCAL_MLFLOW_URI
    except:
        pass
    
    # 3. Default (Docker)
    return DEFAULT_MLFLOW_URI


def ensure_mlflow_connection(tracking_uri: Optional[str] = None) -> bool:
    """
    Verifica que hay conexión con MLflow
    
    Args:
        tracking_uri: URI a verificar (si es None, usa get_mlflow_tracking_uri)
    
    Returns:
        bool: True si la conexión es exitosa
    """
    import mlflow
    
    if tracking_uri is None:
        tracking_uri = get_mlflow_tracking_uri()
    
    try:
        mlflow.set_tracking_uri(tracking_uri)
        # Intentar obtener un experimento para verificar conexión
        mlflow.get_experiments()
        return True
    except Exception as e:
        print(f"⚠️ No se pudo conectar a MLflow en {tracking_uri}: {e}")
        return False


def setup_mlflow_for_model_cards(experiment_name: str = "morchella_detection") -> str:
    """
    Configura MLflow para trabajar con Model Cards
    
    Args:
        experiment_name: Nombre del experimento
    
    Returns:
        str: Experimento ID
    """
    import mlflow
    
    tracking_uri = get_mlflow_tracking_uri()
    mlflow.set_tracking_uri(tracking_uri)
    
    # Crear o obtener experimento
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        mlflow.create_experiment(experiment_name)
        experiment = mlflow.get_experiment_by_name(experiment_name)
    
    return experiment.experiment_id


# Configuración de dataset
DATASET_CONFIG = {
    'classes': ['morchella', 'no_morchella'],
    'class_names': ['No Morchella', 'Morchella'],
    'train_split': 0.7,
    'val_split': 0.15,
    'test_split': 0.15,
}

# Configuración de augmentación
AUGMENTATION_CONFIG = {
    'rotation_range': 30,
    'width_shift_range': 0.2,
    'height_shift_range': 0.2,
    'horizontal_flip': True,
    'vertical_flip': True,
    'zoom_range': 0.2,
    'shear_range': 0.15,
    'fill_mode': 'nearest',
}

# Configuración de modelos
MODELS_CONFIG = {
    'efficientnet': {
        'name': 'EfficientNetB0',
        'description': 'Efficient and accurate neural network',
        'input_size': 224,
    },
    'mobilenet': {
        'name': 'MobileNetV2',
        'description': 'Lightweight mobile-friendly network',
        'input_size': 224,
    },
}

# Tags por defecto para MLflow
DEFAULT_MLFLOW_TAGS = {
    'task': 'binary_classification',
    'project': 'morchella_detection',
    'framework': 'tensorflow',
    'author': 'morchella-team',
}


if __name__ == '__main__':
    # Test de configuración
    print("🧪 Probando configuración de Model Cards...")
    print()
    
    uri = get_mlflow_tracking_uri()
    print(f"📍 MLflow URI: {uri}")
    
    connected = ensure_mlflow_connection(uri)
    print(f"🔗 Conexión a MLflow: {'✅ OK' if connected else '❌ FAIL'}")
    print()
    
    if connected:
        exp_id = setup_mlflow_for_model_cards()
        print(f"📊 Experimento 'morchella_detection': {exp_id}")
    
    print()
    print("✅ Configuración lista!")
