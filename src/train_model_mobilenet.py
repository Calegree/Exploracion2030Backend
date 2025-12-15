import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import mlflow
import mlflow.keras
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import glob
import sqlite3
from datetime import datetime

# Configuración mejorada de MLflow para SQLite
def setup_mlflow():
    """
    Configura MLflow para usar SQLite como backend
    """
    # Configurar tracking URI para SQLite
    tracking_uri = os.getenv('MLFLOW_TRACKING_URI', 'http://mlflow:5001')
    mlflow.set_tracking_uri(tracking_uri)
    
    # Crear experimento si no existe
    experiment_name = "morchella_detection"
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            mlflow.create_experiment(experiment_name)
            print(f"✅ Experimento '{experiment_name}' creado")
        else:
            print(f"✅ Experimento '{experiment_name}' encontrado")
    except Exception as e:
        print(f"⚠️ Error configurando experimento: {e}")
    
    mlflow.set_experiment(experiment_name)
    return tracking_uri

def load_and_preprocess_data(dataset_path, img_size=(224, 224)):
    """
    Carga y preprocesa las imágenes del dataset
    """
    images = []
    labels = []
    
    # Cargar imágenes de Morchella (clase 1)
    morchella_path = os.path.join(dataset_path, 'morchella')
    for img_path in glob.glob(os.path.join(morchella_path, '*.jpg')) + glob.glob(os.path.join(morchella_path, '*.jpeg')):
        try:
            img = Image.open(img_path).convert('RGB')
            img = img.resize(img_size)
            img_array = np.array(img) / 255.0
            images.append(img_array)
            labels.append(1)  # Morchella = 1
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
    
    # Cargar imágenes de No-Morchella (clase 0)
    no_morchella_path = os.path.join(dataset_path, 'no_morchella')
    for img_path in glob.glob(os.path.join(no_morchella_path, '*.jpg')) + glob.glob(os.path.join(no_morchella_path, '*.jpeg')):
        try:
            img = Image.open(img_path).convert('RGB')
            img = img.resize(img_size)
            img_array = np.array(img) / 255.0
            images.append(img_array)
            labels.append(0)  # No-Morchella = 0
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
    
    return np.array(images), np.array(labels)

def create_model(input_shape=(224, 224, 3)):
    """
    Crea un modelo de clasificación usando transfer learning con MobileNetV2
    """
    # Modelo base pre-entrenado
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=input_shape
    )
    
    # Congelar las capas del modelo base
    base_model.trainable = False
    
    # Crear el modelo completo
    model = Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dense(512, activation='relu'),
        Dropout(0.5),
        Dense(256, activation='relu'),
        Dropout(0.3),
        Dense(1, activation='sigmoid')  # Clasificación binaria
    ])
    
    return model

def plot_training_history(history):
    """
    Grafica el historial de entrenamiento
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Accuracy
    ax1.plot(history.history['accuracy'], label='Training Accuracy')
    ax1.plot(history.history['val_accuracy'], label='Validation Accuracy')
    ax1.set_title('Model Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    
    # Loss
    ax2.plot(history.history['loss'], label='Training Loss')
    ax2.plot(history.history['val_loss'], label='Validation Loss')
    ax2.set_title('Model Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    
    plt.tight_layout()
    return fig

def plot_confusion_matrix(y_true, y_pred, save_path=None):
    """
    Grafica la matriz de confusión
    """
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['No Morchella', 'Morchella'],
                yticklabels=['No Morchella', 'Morchella'])
    plt.title('Confusion Matrix - MobileNetV2')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    
    if save_path:
        plt.savefig(save_path)
    return plt.gcf()

def train_model():
    """
    Función principal de entrenamiento con MLflow usando MobileNetV2
    """
    # Configurar MLflow
    print("🔧 Configurando MLflow...")
    tracking_uri = setup_mlflow()
    print(f"📊 Tracking URI: {tracking_uri}")
    
    # Parámetros del experimento
    params = {
        'img_size': 224,
        'batch_size': 32,
        'epochs': 20,
        'learning_rate': 0.001,
        'dropout_rate': 0.5,
        'model_type': 'MobileNetV2',
        'transfer_learning': True,
        'data_augmentation': True
    }
    
    with mlflow.start_run(run_name=f"MobileNetV2_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        # Log de parámetros
        mlflow.log_params(params)
        
        print("🔍 Cargando dataset...")
        dataset_path = os.path.join(os.path.dirname(__file__), 'dataset')
        X, y = load_and_preprocess_data(dataset_path, (params['img_size'], params['img_size']))
        
        print(f"📦 Dataset cargado: {len(X)} imágenes")
        print(f"   - Morchella: {np.sum(y == 1)} imágenes")
        print(f"   - No Morchella: {np.sum(y == 0)} imágenes")
        
        # Split train/validation
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"📈 Datos de entrenamiento: {len(X_train)} imágenes")
        print(f"📊 Datos de validación: {len(X_val)} imágenes")
        
        # Data augmentation para entrenamiento
        datagen = ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
            fill_mode='nearest'
        )
        
        # Crear modelo
        print("🏗️ Creando modelo MobileNetV2...")
        model = create_model((params['img_size'], params['img_size'], 3))
        
        # Compilar modelo
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=params['learning_rate']),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        print("🚀 Iniciando entrenamiento con MobileNetV2...")
        
        # Entrenar modelo
        history = model.fit(
            datagen.flow(X_train, y_train, batch_size=params['batch_size']),
            epochs=params['epochs'],
            validation_data=(X_val, y_val),
            callbacks=[
                tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
                tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3)
            ]
        )
        
        # Evaluar modelo
        print("📊 Evaluando modelo...")
        val_loss, val_accuracy = model.evaluate(X_val, y_val)
        y_pred = (model.predict(X_val) > 0.5).astype(int)
        
        # Log de métricas
        mlflow.log_metric("val_accuracy", val_accuracy)
        mlflow.log_metric("val_loss", val_loss)
        
        # Reporte de clasificación
        report = classification_report(y_val, y_pred, target_names=['No Morchella', 'Morchella'])
        print("\n📋 Reporte de Clasificación:")
        print(report)
        
        # Log del reporte
        mlflow.log_text(report, "classification_report.txt")
        
        # Graficar historial de entrenamiento
        history_fig = plot_training_history(history)
        mlflow.log_figure(history_fig, "training_history.png")
        
        # Graficar matriz de confusión
        cm_fig = plot_confusion_matrix(y_val, y_pred)
        mlflow.log_figure(cm_fig, "confusion_matrix.png")

        # Guardar matriz de confusión como JSON
        try:
            import json
            cm = confusion_matrix(y_val, y_pred).tolist()
            cm_json_path = os.path.join(os.path.dirname(__file__), 'model', 'confusion_matrix.json')
            os.makedirs(os.path.dirname(cm_json_path), exist_ok=True)
            with open(cm_json_path, 'w', encoding='utf-8') as fh:
                json.dump({'confusion_matrix': cm}, fh)
            mlflow.log_artifact(cm_json_path, artifact_path="confusion_matrix")
        except Exception as e:
            print(f"⚠️ No se pudo guardar/loggear confusion_matrix.json: {e}")
        
        # Guardar modelo localmente en formato .keras (recomendado)
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'model_morchella_mobilenet.keras')
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        print("💾 Guardando modelo localmente...")
        try:
            model.save(model_path)
            print(f"✅ Modelo guardado localmente en: {model_path}")
            # Subir el .keras como artifact simple para garantizar que quede en el run
            mlflow.log_artifact(model_path, artifact_path="model")
            print("✅ Archivo .keras subido como artifact en model/")
        except Exception as e:
            print(f"❌ Error guardando modelo local: {e}")
        
        # Log del modelo en MLflow CON manejo de errores y verificación
        print("📤 Subiendo modelo a MLflow...")
        try:
            # IMPORTANTE: registered_model_name=None evita auto-registro en Model Registry
            # El modelo se guardará SOLO en mlflow/1/<run_id>/artifacts/model/
            # Nota: No usamos input_example/signature por bug en MLflow con paths temporales
            mlflow.keras.log_model(
                model, 
                "model",
                registered_model_name=None  # NO registrar automáticamente en Model Registry
            )
            print("✅ Modelo logueado en MLflow correctamente")
            print(f"📁 Ubicación: mlflow/1/{mlflow.active_run().info.run_id}/artifacts/model/")
            
            # Verificar que se guardó en artifacts
            from mlflow.tracking import MlflowClient
            client = MlflowClient()
            run_id = mlflow.active_run().info.run_id
            artifacts = client.list_artifacts(run_id, "model")
            if artifacts:
                print(f"✅ Verificado: modelo tiene {len(artifacts)} archivos en MLflow")
                for art in artifacts[:5]:  # Mostrar primeros 5
                    print(f"   - {art.path}")
            else:
                print("⚠️ ADVERTENCIA: No se encontraron artifacts del modelo en MLflow")
                
        except Exception as e:
            print(f"❌ ERROR al loguear modelo en MLflow: {e}")
            import traceback
            traceback.print_exc()
        
        # Log de información adicional
        mlflow.log_metric("final_accuracy", val_accuracy)
        mlflow.log_metric("final_loss", val_loss)
        mlflow.set_tag("model_type", "MobileNetV2")
        mlflow.set_tag("task", "binary_classification")
        mlflow.set_tag("dataset_size", len(X))
        
        print(f"\n{'='*60}")
        print(f"✅ Modelo MobileNetV2 guardado en: {model_path}")
        print(f"📊 Accuracy de validación: {val_accuracy:.4f}")
        print(f"📊 Loss de validación: {val_loss:.4f}")
        print(f"🔗 Run ID: {mlflow.active_run().info.run_id}")
        print(f"📈 Ver resultados en: mlflow ui")
        print(f"{'='*60}\n")
        
        return model, history

if __name__ == "__main__":
    train_model()
