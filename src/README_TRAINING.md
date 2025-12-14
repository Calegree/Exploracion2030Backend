# 🤖 Scripts de Entrenamiento de Modelos

Este directorio contiene scripts para entrenar modelos de clasificación de hongos Morchella usando diferentes arquitecturas de redes neuronales.

## 📋 Scripts Disponibles

### 1. `train_model_mobilenet.py` - MobileNetV2
**Características:**
- 🚀 Modelo ligero y rápido
- 📱 Optimizado para dispositivos móviles y edge computing
- 💾 Tamaño pequeño (~14MB)
- ⚡ Inferencia rápida
- 🎯 Buena precisión para clasificación binaria

**Ventajas:**
- Ideal para despliegue en producción con recursos limitados
- Menor tiempo de entrenamiento
- Menor consumo de memoria RAM

**Uso:**
```bash
cd src
python train_model_mobilenet.py
```

**Modelo guardado:**
- `src/model/model_morchella_mobilenet.h5`

---

### 2. `train_model_efficientnet.py` - EfficientNetB0
**Características:**
- 🎯 Mejor balance precisión/eficiencia
- 🏆 Arquitectura state-of-the-art
- 📊 Mayor precisión que MobileNet
- 💾 Tamaño medio (~29MB)
- 🔬 Mejor para datasets complejos

**Ventajas:**
- Mayor accuracy en validación
- Mejor generalización
- Métricas adicionales (Precision, Recall, F1-Score)
- Data augmentation más agresiva

**Uso:**
```bash
cd src
python train_model_efficientnet.py
```

**Modelo guardado:**
- `src/model/model_morchella_efficientnet.h5`

---

## 📊 Comparación de Arquitecturas

| Característica | MobileNetV2 | EfficientNetB0 |
|---------------|-------------|----------------|
| Tamaño del modelo | ~14MB | ~29MB |
| Velocidad de inferencia | Muy rápida | Rápida |
| Precisión esperada | Buena (85-90%) | Excelente (90-95%) |
| Consumo de memoria | Bajo | Medio |
| Tiempo de entrenamiento | 15-25 min | 20-35 min |
| Mejor para | Producción móvil | Máxima precisión |

## 🎯 ¿Cuál Script Usar?

### Usa `train_model_mobilenet.py` si:
- ✅ Necesitas desplegar en dispositivos móviles o edge
- ✅ Tienes recursos limitados (RAM, GPU)
- ✅ Requieres inferencia muy rápida
- ✅ El tamaño del modelo es crítico
- ✅ Dataset relativamente simple

### Usa `train_model_efficientnet.py` si:
- ✅ Buscas la máxima precisión posible
- ✅ Tienes suficientes recursos de cómputo
- ✅ El tiempo de inferencia no es crítico
- ✅ Dataset complejo o con muchas variaciones
- ✅ Necesitas mejores métricas de validación

## 📦 Dataset Requerido

Ambos scripts esperan la siguiente estructura de carpetas:

```
src/dataset/
├── morchella/
│   ├── imagen1.jpg
│   ├── imagen2.jpg
│   └── ...
└── no_morchella/
    ├── imagen1.jpg
    ├── imagen2.jpg
    └── ...
```

## 🔧 Configuración de Parámetros

### MobileNetV2
```python
params = {
    'img_size': 224,
    'batch_size': 32,
    'epochs': 20,
    'learning_rate': 0.001,
    'dropout_rate': 0.5
}
```

### EfficientNetB0
```python
params = {
    'img_size': 224,
    'batch_size': 32,
    'epochs': 25,
    'learning_rate': 0.001,
    'dropout_rate': 0.4
}
```

## 📈 MLflow Tracking

Ambos scripts registran automáticamente en MLflow:
- ✓ Parámetros de entrenamiento
- ✓ Métricas de validación
- ✓ Gráficos de accuracy y loss
- ✓ Matriz de confusión
- ✓ Reporte de clasificación
- ✓ Modelo entrenado

**Ver resultados:**
```bash
mlflow ui
# Visita: http://localhost:5000
```

## 🎨 Data Augmentation

### MobileNetV2 (Moderado)
- Rotación: ±20°
- Desplazamiento: 20%
- Zoom: 20%
- Flip horizontal

### EfficientNetB0 (Agresivo)
- Rotación: ±30°
- Desplazamiento: 20%
- Zoom: 20%
- Flip horizontal y vertical
- Shear: 15%

## 🏗️ Arquitectura de las Redes

### MobileNetV2
```
Input (224x224x3)
    ↓
MobileNetV2 Base (pre-trained)
    ↓
GlobalAveragePooling2D
    ↓
Dense(512) + ReLU + Dropout(0.5)
    ↓
Dense(256) + ReLU + Dropout(0.3)
    ↓
Dense(1) + Sigmoid
```

### EfficientNetB0
```
Input (224x224x3)
    ↓
EfficientNetB0 Base (pre-trained)
    ↓
GlobalAveragePooling2D
    ↓
Dense(512) + ReLU + Dropout(0.4)
    ↓
Dense(256) + ReLU + Dropout(0.3)
    ↓
Dense(128) + ReLU + Dropout(0.2)
    ↓
Dense(1) + Sigmoid
```

## 🚀 Mejores Prácticas

1. **Probar ambos modelos**: Entrena con los dos scripts y compara resultados en MLflow
2. **Validar en producción**: Prueba con imágenes reales antes de desplegar
3. **Monitorear métricas**: Revisa no solo accuracy, sino también precision/recall
4. **Fine-tuning**: Después del entrenamiento inicial, considera descongelar capas del modelo base

## 📊 Ejemplo de Comparación de Runs

Después de entrenar con ambos scripts, compara en MLflow:
```
┌────────────────┬──────────┬──────────┬─────────┐
│ Modelo         │ Accuracy │ Loss     │ F1      │
├────────────────┼──────────┼──────────┼─────────┤
│ MobileNetV2    │ 0.8745   │ 0.3120   │ 0.8634  │
│ EfficientNetB0 │ 0.9231   │ 0.2154   │ 0.9187  │
└────────────────┴──────────┴──────────┴─────────┘
```

## 🔄 Script Original

El script `train_model.py` original sigue funcionando, pero ahora recomendamos usar los scripts específicos para mayor claridad.

## 💡 Tips de Optimización

### Para mejorar MobileNetV2:
- Aumentar epochs a 25-30
- Probar batch_size de 16
- Fine-tune últimas capas del modelo base

### Para mejorar EfficientNetB0:
- Usar EfficientNetB1 o B2 para mayor precisión
- Aumentar tamaño de imagen a 240x240
- Ajustar learning rate con warmup

## 📝 Logs de Entrenamiento

Ambos scripts generan logs detallados:
```
🔧 Configurando MLflow...
📊 Tracking URI: http://mlflow:5001
🔍 Cargando dataset...
📦 Dataset cargado: 200 imágenes
   - Morchella: 100 imágenes
   - No Morchella: 100 imágenes
📈 Datos de entrenamiento: 160 imágenes
📊 Datos de validación: 40 imágenes
🏗️ Creando modelo...
🚀 Iniciando entrenamiento...
```

## 🐛 Troubleshooting

**Error: Out of Memory**
- Reduce batch_size a 16 o 8
- Usa MobileNetV2 en lugar de EfficientNet

**Error: No se encuentra el dataset**
- Verifica que existan las carpetas `dataset/morchella` y `dataset/no_morchella`
- Descarga imágenes con el endpoint `/download/fungis2`

**Accuracy bajo (<70%)**
- Descarga más imágenes para el dataset
- Aumenta epochs
- Revisa que las imágenes estén bien etiquetadas

---

¿Preguntas? Revisa la documentación de MLflow o el código fuente de los scripts.
