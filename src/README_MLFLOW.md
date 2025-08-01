# 🍄 Morchella Detection - MLflow con SQLite

Este proyecto utiliza **MLflow** con **SQLite** como backend para el tracking de experimentos de machine learning. Todo se almacena en una base de datos SQLite local en lugar de archivos.

## 📋 Requisitos

- Python 3.7+
- TensorFlow 2.x
- MLflow
- Las dependencias listadas en `requirements.txt`

## 🚀 Inicio Rápido

### Opción 1: Pipeline Automatizado (Recomendado)

```bash
cd src
python run_training_pipeline.py
```

Este script automatiza todo el proceso:
1. ✅ Verifica el dataset
2. 🔧 Configura MLflow con SQLite
3. 🧠 Entrena el modelo
4. 🌐 Inicia MLflow UI (opcional)

### Opción 2: Pasos Manuales

#### 1. Limpiar y Configurar MLflow
```bash
cd src
python clean_mlflow.py
python verify_mlflow_setup.py
```

#### 2. Entrenar el Modelo
```bash
python train_model.py
```

#### 3. Ver Resultados en MLflow UI
```bash
python start_mlflow_ui.py
# O manualmente:
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

## 📊 Estructura de Archivos

```
src/
├── mlflow.db                    # Base de datos SQLite de MLflow
├── train_model.py              # Script de entrenamiento principal
├── clean_mlflow.py             # Limpia configuración anterior
├── verify_mlflow_setup.py      # Verifica configuración
├── start_mlflow_ui.py          # Inicia servidor MLflow UI
├── run_training_pipeline.py    # Pipeline automatizado
├── mlflow_manager.py           # Gestión avanzada de MLflow
└── dataset/
    ├── morchella/              # Imágenes de Morchella
    └── no_morchella/           # Imágenes que no son Morchella
```

## 🔧 Configuración de MLflow

### Backend SQLite
- **Tracking URI**: `sqlite:///mlflow.db`
- **Ventajas**: 
  - No requiere servidor externo
  - Todo se almacena en un archivo
  - Fácil de respaldar y mover
  - No hay archivos temporales

### Experimentos
- **Nombre**: `morchella_detection`
- **Métricas**: accuracy, loss, precision, recall, f1-score
- **Parámetros**: img_size, batch_size, epochs, learning_rate, etc.

## 📈 Qué se Registra en MLflow

### Parámetros
- `img_size`: Tamaño de las imágenes (224x224)
- `batch_size`: Tamaño del batch (32)
- `epochs`: Número de épocas (20)
- `learning_rate`: Tasa de aprendizaje (0.001)
- `model_type`: Tipo de modelo (MobileNetV2)
- `transfer_learning`: Si usa transfer learning (True)
- `data_augmentation`: Si usa data augmentation (True)

### Métricas
- `val_accuracy`: Accuracy en validación
- `val_loss`: Loss en validación
- `final_accuracy`: Accuracy final
- `final_loss`: Loss final

### Artefactos
- **Modelo**: Modelo entrenado en formato Keras
- **Gráficos**: Historial de entrenamiento y matriz de confusión
- **Reportes**: Reporte de clasificación

### Tags
- `model_type`: Tipo de modelo
- `task`: Tipo de tarea (binary_classification)
- `dataset_size`: Tamaño del dataset

## 🌐 MLflow UI

### Acceso
- **URL**: http://localhost:5000
- **Base de datos**: `mlflow.db`

### Funcionalidades
- 📊 Visualización de métricas
- 📈 Gráficos de entrenamiento
- 🔍 Comparación de experimentos
- 📦 Descarga de modelos
- 📋 Historial de parámetros

## 🛠️ Comandos Útiles

### Verificar Configuración
```bash
python verify_mlflow_setup.py
```

### Limpiar Todo
```bash
python clean_mlflow.py
```

### Iniciar UI
```bash
python start_mlflow_ui.py
# O
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

### Ver Experimentos Programáticamente
```bash
python mlflow_manager.py
```

## 🔍 Solución de Problemas

### Error: "Base de datos no encontrada"
```bash
python clean_mlflow.py
python verify_mlflow_setup.py
```

### Error: "Directorio mlruns encontrado"
```bash
python clean_mlflow.py
```

### Error: "MLflow no está instalado"
```bash
pip install mlflow
```

### Error: "Dataset no encontrado"
Asegúrate de tener:
- `src/dataset/morchella/` con imágenes .jpg/.jpeg
- `src/dataset/no_morchella/` con imágenes .jpg/.jpeg

## 📝 Notas Importantes

1. **SQLite vs Archivos**: Todo se almacena en `mlflow.db`, no hay directorio `mlruns/`
2. **Respaldo**: Para respaldar, solo copia `mlflow.db`
3. **Portabilidad**: Puedes mover `mlflow.db` a otra máquina
4. **Concurrencia**: SQLite no maneja múltiples escrituras simultáneas
5. **Tamaño**: La base de datos crece con cada experimento

## 🎯 Próximos Pasos

1. Ejecuta el pipeline de entrenamiento
2. Revisa los resultados en MLflow UI
3. Experimenta con diferentes parámetros
4. Registra el mejor modelo
5. Integra el modelo en tu aplicación Flask

## 📞 Soporte

Si tienes problemas:
1. Ejecuta `python verify_mlflow_setup.py`
2. Revisa los logs de error
3. Ejecuta `python clean_mlflow.py` si hay conflictos
4. Verifica que todas las dependencias estén instaladas 