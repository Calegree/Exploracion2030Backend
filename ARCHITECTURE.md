# 🏗️ Arquitectura del Sistema de Model Cards

Visualización de cómo funciona el sistema automáticamente.

---

## 📐 Diagrama de Flujo General

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENTRENAR MODELO                              │
│  docker-compose exec api python src/train.py --model efficientnet
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                   MLFLOW: Registrar Métricas                    │
│  • Accuracy, Loss, Precision, Recall                            │
│  • Confusion Matrix (TN, FP, FN, TP)                            │
│  • Hiperparámetros, Dataset info                               │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│              GENERACIÓN DE MODEL CARD (Automático)              │
│         src/model_card_mlflow_logger.py                         │
│                                                                 │
│  1. Leer datos de MLflow                                       │
│  2. Construir template Quarto (13 secciones)                  │
│  3. Guardar como: model_card_*.qmd                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ↓           ↓           ↓
    ┌────────┐  ┌────────┐  ┌────────┐
    │  QMD   │  │ Quarto │  │ Quarto │
    │(Fuente)│  │→ HTML  │  │→ PDF   │
    └────────┘  └────────┘  └────────┘
         │           │           │
         └───────────┼───────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│              SUBIR A MLFLOW (Automático)                        │
│         src/model_card_mlflow_logger.py                         │
│                                                                 │
│  mlflow.log_artifact(qmd_path, "model_cards")                 │
│  mlflow.log_artifact(html_path, "model_cards")                │
│  mlflow.log_artifact(pdf_path, "model_cards")                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│              ALMACENAMIENTO (MLflow + MinIO)                    │
│                                                                 │
│  localhost:5001 → Artifacts → model_cards/                    │
│    ├── model_card_EfficientNetB0_*.qmd                        │
│    ├── model_card_EfficientNetB0_*.html                       │
│    └── model_card_EfficientNetB0_*.pdf                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│            ACCESO Y DISTRIBUCIÓN (Por Usuario)                  │
│                                                                 │
│  Ver en navegador → .html                                      │
│  Compartir/Imprimir → .pdf                                     │
│  Editar documento → .qmd                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Componentes del Sistema

### 1. **Training Layer** (Tu código)
```
train_model_efficientnet.py
train_model_mobilenet.py
    ↓
    Entrenan la red neuronal
    Registran métricas en MLflow
    Guardan modelo .h5
```

### 2. **Logger Layer** (Automático)
```
model_card_mlflow_logger.py
    ↓
    Extrae datos de MLflow
    Genera template QMD
    Compila a HTML (si Quarto)
    Compila a PDF (si Pandoc)
    Sube artifacts a MLflow
```

### 3. **Storage Layer** (MLflow + MinIO)
```
MLflow Tracking Server (localhost:5001)
    ↓
MinIO S3 Storage (localhost:9001)
    ↓
Artifacts guardados con estructura:
/[run_id]/artifacts/model_cards/
```

### 4. **Access Layer** (Usuarios)
```
MLflow UI
    ↓
Descargar/Ver archivos en navegador
    ↓
.qmd (editar), .html (web), .pdf (compartir)
```

---

## 📊 Flujo de Datos Detallado

### Paso 1: Entrenamiento → Métricas
```
Training Loop
├── Epoch 1: loss=0.5, acc=0.8
├── Epoch 2: loss=0.3, acc=0.85
└── Epoch N: loss=0.1, acc=0.95
    ↓
    mlflow.log_metric("accuracy", 0.95)
    mlflow.log_metric("loss", 0.1)
    mlflow.log_param("batch_size", 32)
    ↓
    MLflow Server: Guarda todo
```

### Paso 2: Lectura de Métricas
```
MLflow Server (localhost:5001)
    ├── Experiment: morchella_detection
    ├── Run ID: abc123...
    ├── Metrics:
    │   ├── accuracy: 0.95
    │   ├── loss: 0.1
    │   └── confusion_matrix: {...}
    ├── Params:
    │   ├── model: EfficientNetB0
    │   ├── epochs: 50
    │   └── batch_size: 32
    └── Artifacts:
        └── model: model.h5
            
model_card_mlflow_logger.py → Lee todo esto
```

### Paso 3: Generación de Template
```
Datos de MLflow
    ↓
Template Quarto (13 secciones):
┌─────────────────────────────┐
│ # Model Card                │
│ ## Model Overview           │
│ Model: EfficientNetB0       │
│ ...                         │
│ ## Performance Metrics      │
│ - Accuracy: 95%             │
│ ...                         │
│ ## Confusion Matrix         │
│ ![matriz.png]               │
│ ...                         │
└─────────────────────────────┘
    ↓
    Guardar como: model_card_EfficientNetB0_*.qmd
```

### Paso 4: Compilación
```
model_card_EfficientNetB0_*.qmd
    ↓
    $ quarto render --to html
    ↓
    model_card_EfficientNetB0_*.html (con CSS)
    
model_card_EfficientNetB0_*.qmd
    ↓
    $ quarto render --to pdf
    ↓
    model_card_EfficientNetB0_*.pdf (formateado)
```

### Paso 5: Upload a MLflow
```
Archivos generados:
├── .qmd (fuente)
├── .html (web)
└── .pdf (documento)
    ↓
    mlflow.log_artifact(qmd_path, "model_cards")
    mlflow.log_artifact(html_path, "model_cards")
    mlflow.log_artifact(pdf_path, "model_cards")
    ↓
MLflow → MinIO S3:
    /mlflow/[run_id]/artifacts/model_cards/
    ├── model_card_*.qmd
    ├── model_card_*.html
    └── model_card_*.pdf
```

---

## 🗂️ Estructura de Directorios

```
/home/charles-darwin/Morchellapp/Exploracion2030Backend/
│
├── src/
│   ├── train_model_efficientnet.py     ← Entrena + genera Model Card
│   ├── train_model_mobilenet.py        ← Entrena + genera Model Card
│   ├── model_card_mlflow_logger.py     ← ✨ CORE: Genera y sube
│   ├── model_card_generator.py         ← Motor base
│   ├── model_card_utils.py             ← Herramientas CLI
│   ├── model_card_config.py            ← Configuración
│   └── example_generate_model_card.py  ← Ejemplo
│
├── model_cards/
│   ├── README.md                       ← Documentación
│   ├── MODEL_CARDS_FORMATS.md          ← Formatos (QMD, HTML, PDF)
│   ├── ACCESSING_MODEL_CARDS.md        ← Cómo acceder
│   ├── TESTING_MODEL_CARDS.md          ← Pruebas
│   ├── model-card-style.css            ← Estilos HTML
│   │
│   ├── model_card_EfficientNetB0_*.qmd  ← Generadas automáticamente
│   ├── model_card_EfficientNetB0_*.html
│   ├── model_card_EfficientNetB0_*.pdf
│   ├── model_card_MobileNetV2_*.qmd
│   ├── model_card_MobileNetV2_*.html
│   └── model_card_MobileNetV2_*.pdf
│
├── mlruns/                             ← MLflow local storage
│   └── 1/                              ← Experiment ID
│       ├── [run_id1]/artifacts/
│       │   └── model_cards/            ← ← ← Model Cards aquí
│       │       ├── *.qmd
│       │       ├── *.html
│       │       └── *.pdf
│       └── [run_id2]/artifacts/
│           └── model_cards/
│
├── minio-data/                         ← MinIO S3 storage
│   └── mlflow/
│       └── [run_id]/artifacts/
│           └── model_cards/            ← ← ← Copia en MinIO
│
└── docker-compose.yml                  ← Servicios (MLflow, MinIO, API)
```

---

## 🔐 Flujo de Autenticación (Automático)

```
Entrenamiento
    ↓
    with mlflow.start_run(run_name="EfficientNetB0_training"):
        # Entrenar...
        run_id = mlflow.active_run().info.run_id
    ↓
Model Card Logger
    ↓
    client = MlflowClient()
    run_info = client.get_run(run_id)
    # Ya está autenticado (conexión local)
    ↓
Log Artifacts
    ↓
    mlflow.log_artifact(path, "model_cards")
    # Automáticamente va a MinIO
    ↓
MLflow UI (localhost:5001)
    ↓
    Ver artifacts en browser
```

**Nota:** No requiere credenciales porque:
- MLflow local (sin autenticación)
- MinIO local (credenciales en docker-compose)
- Todo automático

---

## 🔌 Integraciones Externas

```
┌─────────────────────────────────────────┐
│         Sistemas Externos                │
├─────────────────────────────────────────┤
│                                         │
│  Quarto (compilación a HTML/PDF)       │
│  ├── Convierte .qmd → .html            │
│  └── Convierte .qmd → .pdf (vía Pandoc)│
│                                         │
│  Pandoc (renderizado PDF)              │
│  ├── LaTeX → PDF conversion            │
│  └── Optional (PDF sin él = no genera) │
│                                         │
│  TensorFlow/Keras (training)           │
│  ├── Genera modelo .h5                 │
│  └── Genera métricas                   │
│                                         │
│  Scikit-learn (confusion matrix)       │
│  ├── Calcula TN, FP, FN, TP           │
│  └── Genera visualización              │
│                                         │
└─────────────────────────────────────────┘
         ↓
    Model Card Logger
         ↓
    MLflow + MinIO
```

---

## 📈 Escalabilidad

### Múltiples Modelos
```
Train EfficientNetB0 → Model Card
    ↓
    artifact: model_card_EfficientNetB0_*.{qmd,html,pdf}

Train MobileNetV2 → Model Card
    ↓
    artifact: model_card_MobileNetV2_*.{qmd,html,pdf}

Train ResNet50 → Model Card
    ↓
    artifact: model_card_ResNet50_*.{qmd,html,pdf}
    
MLflow: Todos organizados por run_id
```

### Múltiples Versiones
```
Run 1: model_card_EfficientNetB0_20251215_100000.{qmd,html,pdf}
Run 2: model_card_EfficientNetB0_20251215_110000.{qmd,html,pdf}
Run 3: model_card_EfficientNetB0_20251215_120000.{qmd,html,pdf}

MLflow mantiene histórico completo
MinIO almacena indefinidamente
Comparar versiones: Descargar y comparar PDFs
```

---

## 🚀 Optimizaciones Implementadas

### 1. **Paralización de Compilación**
```
QMD → HTML (en paralelo)
QMD → PDF (en paralelo)

No es: QMD → HTML → PDF (secuencial)
Es:    QMD → {HTML, PDF} simultáneamente
```

### 2. **Manejo de Errores Graceful**
```
Si Quarto no disponible:
    ✅ Generar .qmd (siempre)
    ⚠️ Saltar .html (no falla)
    
Si Pandoc no disponible:
    ✅ Generar .qmd (siempre)
    ✅ Generar .html (si Quarto)
    ⚠️ Saltar .pdf (no falla)
```

### 3. **Logging Detallado**
```
✅ QMD generated at: /path/to/file.qmd
✅ HTML compiled at: /path/to/file.html
⚠️ PDF compilation skipped (Pandoc not found)
✅ All artifacts uploaded to MLflow
```

### 4. **Timeout Protection**
```
if compilation takes > 120 seconds:
    Timeout → Skip that format
    Continue with next format
    No "hanging" processes
```

---

## 🔄 Ciclo de Vida Completo

```
1. INICIALIZACIÓN
   └─ Usuario: docker-compose up -d

2. ENTRENAMIENTO
   └─ Usuario: python src/train.py --model efficientnet
      MLflow: Crea run_id
      MLflow: Registra métricas
      Modelo: Guarda .h5

3. GENERACIÓN (AUTOMÁTICO)
   └─ Logger: Extrae datos de MLflow
      Logger: Crea template QMD
      Logger: Compila a HTML
      Logger: Compila a PDF

4. ALMACENAMIENTO (AUTOMÁTICO)
   └─ Logger: Sube 3 archivos a MLflow
      MLflow: Organiza en /artifacts/model_cards/
      MinIO: Copia para persistencia

5. VISUALIZACIÓN
   └─ Usuario: Abre http://localhost:5001
      Usuario: Ve Model Cards en Artifacts
      Usuario: Descarga el formato que quiere

6. DISTRIBUCIÓN
   └─ Usuario: Comparte PDF por email
      Usuario: Edita QMD en VS Code
      Usuario: Abre HTML en navegador
```

---

## 📊 Performance

### Tiempos Típicos

| Tarea | Tiempo |
|-------|--------|
| Entrenar modelo | 5-30 min |
| Generar QMD | < 1 seg |
| Compilar a HTML | 5-10 seg |
| Compilar a PDF | 10-20 seg |
| Subir a MLflow | < 1 seg |
| **Total overhead** | 15-30 seg |

### Recursos

| Componente | CPU | RAM | Disco |
|-----------|-----|-----|-------|
| MLflow | Low | 200 MB | 100 MB |
| MinIO | Low | 300 MB | Variable |
| Quarto | Medium | 500 MB | 50 MB |
| Docker | Low | 100 MB | 10 MB |

---

## 🎯 Casos de Error Manejados

```
1. Quarto no instalado
   → .html no se genera, pero .qmd sí
   
2. Pandoc no instalado
   → .pdf no se genera, pero .qmd y .html sí
   
3. MLflow no accesible
   → Error claro, facilita debugging
   
4. MinIO lleno
   → Falla al subir, pero .qmd está local
   
5. Timeout en compilación
   → Salta a siguiente formato, no bloquea
   
6. Falta métrica en MLflow
   → Inserta "N/A", documento aún se genera
```

---

*Última actualización: 15 de diciembre de 2025*  
*Sistema: Model Cards Automático para Detección de Morchella*
