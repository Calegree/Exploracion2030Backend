import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
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
    Crea un modelo de clasificación usando transfer learning con EfficientNetB0
    
    EfficientNet es una familia de modelos más eficientes que MobileNet,
    con mejor balance entre precisión y tamaño del modelo.
    """
    # Modelo base pre-entrenado (EfficientNetB0 es el más pequeño y rápido)
    base_model = EfficientNetB0(
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
        Dropout(0.4),
        Dense(256, activation='relu'),
        Dropout(0.3),
        Dense(128, activation='relu'),
        Dropout(0.2),
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
    ax1.set_title('Model Accuracy - EfficientNetB0')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    
    # Loss
    ax2.plot(history.history['loss'], label='Training Loss')
    ax2.plot(history.history['val_loss'], label='Validation Loss')
    ax2.set_title('Model Loss - EfficientNetB0')
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
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', 
                xticklabels=['No Morchella', 'Morchella'],
                yticklabels=['No Morchella', 'Morchella'])
    plt.title('Confusion Matrix - EfficientNetB0')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    
    if save_path:
        plt.savefig(save_path)
    return plt.gcf()

def train_model():
    """
    Función principal de entrenamiento con MLflow usando EfficientNetB0
    """
    # Configurar MLflow
    print("🔧 Configurando MLflow...")
    tracking_uri = setup_mlflow()
    print(f"📊 Tracking URI: {tracking_uri}")
    
    # Parámetros del experimento
    params = {
        'img_size': 224,
        'batch_size': 32,
        'epochs': 25,  # EfficientNet puede beneficiarse de más épocas
        'learning_rate': 0.001,
        'dropout_rate': 0.4,
        'model_type': 'EfficientNetB0',
        'transfer_learning': True,
        'data_augmentation': True
    }
    
    with mlflow.start_run(run_name=f"EfficientNetB0_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
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
        
        # Data augmentation para entrenamiento (más agresivo para EfficientNet)
        datagen = ImageDataGenerator(
            rotation_range=30,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            vertical_flip=True,
            zoom_range=0.2,
            shear_range=0.15,
            fill_mode='nearest'
        )
        
        # Crear modelo
        print("🏗️ Creando modelo EfficientNetB0...")
        model = create_model((params['img_size'], params['img_size'], 3))
        
        # Compilar modelo
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=params['learning_rate']),
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
        )
        
        print("🚀 Iniciando entrenamiento con EfficientNetB0...")
        print("💡 EfficientNet suele ofrecer mejor precisión que MobileNet con tamaño similar")
        
        # Entrenar modelo
        history = model.fit(
            datagen.flow(X_train, y_train, batch_size=params['batch_size']),
            epochs=params['epochs'],
            validation_data=(X_val, y_val),
            callbacks=[
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_accuracy',
                    patience=5, 
                    restore_best_weights=True,
                    verbose=1
                ),
                tf.keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5, 
                    patience=3,
                    min_lr=1e-7,
                    verbose=1
                )
            ],
            verbose=1
        )
        
        # Evaluar modelo
        print("📊 Evaluando modelo...")
        results = model.evaluate(X_val, y_val, verbose=0)
        val_loss = results[0]
        val_accuracy = results[1]
        val_precision = results[2] if len(results) > 2 else 0
        val_recall = results[3] if len(results) > 3 else 0
        
        y_pred = (model.predict(X_val) > 0.5).astype(int)
        
        # Log de métricas
        mlflow.log_metric("val_accuracy", val_accuracy)
        mlflow.log_metric("val_loss", val_loss)
        mlflow.log_metric("val_precision", val_precision)
        mlflow.log_metric("val_recall", val_recall)
        
        # Calcular F1-Score
        if val_precision > 0 and val_recall > 0:
            f1_score = 2 * (val_precision * val_recall) / (val_precision + val_recall)
            mlflow.log_metric("val_f1_score", f1_score)
        
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
        
        # Guardar modelo
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'model_morchella_efficientnet.h5')
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        model.save(model_path)
        
        # Log del modelo en MLflow
        mlflow.keras.log_model(model, "model")
        
        # Log de información adicional
        mlflow.log_metric("final_accuracy", val_accuracy)
        mlflow.log_metric("final_loss", val_loss)
        mlflow.set_tag("model_type", "EfficientNetB0")
        mlflow.set_tag("task", "binary_classification")
        mlflow.set_tag("dataset_size", len(X))
        mlflow.set_tag("base_model", "EfficientNetB0")
        
        print(f"\n{'='*60}")
        print(f"✅ Modelo EfficientNetB0 guardado en: {model_path}")
        print(f"📊 Accuracy de validación: {val_accuracy:.4f}")
        print(f"📊 Loss de validación: {val_loss:.4f}")
        print(f"📊 Precision de validación: {val_precision:.4f}")
        print(f"📊 Recall de validación: {val_recall:.4f}")
        print(f"🔗 Run ID: {mlflow.active_run().info.run_id}")
        print(f"📈 Ver resultados en: mlflow ui")
        print(f"{'='*60}\n")
        
        return model, history

if __name__ == "__main__":
    train_model()
