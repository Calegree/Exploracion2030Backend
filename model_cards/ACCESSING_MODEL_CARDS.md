# 📊 Acceso a Model Cards en MLflow/MinIO

Ahora los Model Cards se guardan automáticamente en **MLflow/MinIO como artifacts** al terminar cada entrenamiento.

## 🚀 Cómo acceder a los Model Cards

### **Opción 1: Desde MLflow UI (Recomendado)**

1. Abre MLflow en tu navegador:
   ```
   http://localhost:5001
   ```

2. Ve a **"Experiments"** → **"morchella_detection"**

3. Haz clic en el run que quieras ver

4. Busca la sección **"Artifacts"** en la esquina izquierda

5. Abre la carpeta **"model_cards"**

6. Verás los archivos:
   - `model_card_EfficientNetB0_TIMESTAMP.qmd` ← Fuente Quarto
   - `model_card_EfficientNetB0_TIMESTAMP.html` ← HTML compilado
   - (si Quarto está disponible)

7. Haz clic en el `.html` para abrirlo en el navegador

### **Opción 2: Desde MinIO Console (para administradores)**

1. Abre MinIO Console:
   ```
   http://localhost:9001
   ```

2. Ve a **"Object Browser"**

3. Busca el bucket **"mlflow"** 

4. Navega a:
   ```
   1/
   └── [RUN_ID]/
       └── artifacts/
           └── model_cards/
               ├── model_card_*.qmd
               └── model_card_*.html
   ```

5. Descarga los archivos que necesites

### **Opción 3: Programáticamente (Python)**

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Listar todos los runs del experimento
runs = client.search_runs(experiment_ids=['1'])

for run in runs:
    run_id = run.info.run_id
    print(f"Run ID: {run_id}")
    
    # Listar artifacts de model_cards
    artifacts = client.list_artifacts(run_id, 'model_cards')
    
    for artifact in artifacts:
        print(f"  - {artifact.path}")
        
    # Descargar archivos
    local_path = client.download_artifacts(run_id, 'model_cards')
    print(f"Descargados en: {local_path}")
```

### **Opción 4: Línea de comandos (MLflow CLI)**

```bash
# Ver todos los runs
mlflow runs list --experiment-id 1

# Descargar artifacts de un run específico
mlflow artifacts download -s [RUN_ID] -d ./my_artifacts

# Ver estructura de un run
mlflow runs list --experiment-id 1 | grep [RUN_ID]
```

---

## 📁 Estructura de archivos guardados

```
MLflow/MinIO
└── mlflow bucket
    └── 1/                                    ← Experiment ID
        ├── [RUN_ID_1]/
        │   └── artifacts/
        │       ├── model/                    ← Modelo entrenado
        │       ├── confusion_matrix/         ← Matriz de confusión
        │       └── model_cards/              ← ✨ AQUI ESTAN LOS CARDS
        │           ├── model_card_EfficientNetB0_20251215_123456.qmd
        │           └── model_card_EfficientNetB0_20251215_123456.html
        │
        ├── [RUN_ID_2]/
        │   └── artifacts/
        │       └── model_cards/
        │           ├── model_card_MobileNetV2_20251215_124500.qmd
        │           └── model_card_MobileNetV2_20251215_124500.html
```

---

## 🎯 Flujo automático

```
┌─────────────────────────────────────────┐
│ 1. ENTRENAS MODELO                      │
│    docker-compose exec api               │
│    python src/train.py --model efficient │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 2. MLflow CAPTURA MÉTRICAS              │
│    • Parámetros                         │
│    • Métricas (accuracy, loss, etc)     │
│    • Artifacts (modelo, confusión)      │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 3. GENERADOR AUTOMÁTICO CREA CARD       │
│    model_card_mlflow_logger.py          │
│    • Lee todos los datos de MLflow      │
│    • Genera .qmd                        │
│    • Compila a .html (si Quarto)        │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 4. SUBE A MLflow/MinIO AUTOMÁTICAMENTE  │
│    • .qmd → artifacts/model_cards/      │
│    • .html → artifacts/model_cards/     │
│                                         │
│ ✅ COMPLETADO (sin intervención manual) │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 5. ACCEDE DESDE MLflow UI               │
│    localhost:5001                       │
│    → Experiments                        │
│    → morchella_detection                │
│    → [tu run]                           │
│    → Artifacts                          │
│    → model_cards/                       │
│    → model_card_*.html                  │
└─────────────────────────────────────────┘
```

---

## ✨ Ventajas de guardar en MLflow/MinIO

| Ventaja | Descripción |
|---------|-------------|
| 🔒 **Centralizado** | Un único lugar para todo (modelos, métricas, docs) |
| 📦 **Versionado** | Cada run tiene sus propios artifacts |
| 🔗 **Trazabilidad** | Puedes regresar a cualquier versión anterior |
| 👥 **Compartible** | Descargar y compartir fácilmente |
| 🌐 **Web UI** | Acceso desde navegador sin CLI |
| 🔐 **Seguridad** | Control de acceso centralizado |
| ⚡ **Automatizado** | Sin pasos manuales |

---

## 🔍 Ejemplo: Descargar un Model Card

### Desde MLflow UI:
1. http://localhost:5001
2. Click en un run
3. Artifacts → model_cards → model_card_*.html
4. Click derecho → "Download"

### Desde Python:
```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Especifica el run_id que quieras
run_id = "e03dea4d55344edf8371cf4fb8d3e3f3"

# Descarga todos los model_cards
local_path = client.download_artifacts(run_id, 'model_cards')

print(f"Descargados en: {local_path}")

# Abre el HTML
import webbrowser
webbrowser.open(f'file://{local_path}/model_card_EfficientNetB0_*.html')
```

---

## 📊 Comparar modelos entrenados

Una vez tengas múltiples model_cards en MLflow:

```bash
# Ver todos los runs
python src/model_card_utils.py list

# Esto mostrará todos los runs con sus Model Cards en MLflow
```

---

## 🐛 Troubleshooting

### ❓ "No veo los model_cards en MLflow"

**Solución:**
1. Verifica que MLflow esté corriendo: `http://localhost:5001`
2. Revisa que el entrenamiento terminó correctamente
3. Busca mensajes de error en el log de entrenamiento
4. Asegúrate de estar mirando el experimento correcto

### ❓ "Veo .qmd pero no .html"

**Causa:** Quarto no está instalado  
**Solución:** 
- Los .qmd se generan siempre
- El .html solo se genera si Quarto está disponible
- Puedes compilar manualmente: `quarto render archivo.qmd`

### ❓ "¿Dónde está MinIO exactamente?"

**Ubicación física:**
- Los datos están en: `./minio-data/mlflow/`
- También en: `./mlruns/1/[RUN_ID]/artifacts/`
- Y sincronizados en MinIO: `http://localhost:9001`

---

## 📝 Resumen

✅ **Los Model Cards se guardan automáticamente en MLflow/MinIO**  
✅ **Accesibles desde MLflow UI (sin CLI)**  
✅ **Versionados (uno por cada run de entrenamiento)**  
✅ **Descargables y compartibles**  
✅ **Sincronizados con el backup local**

**Acceso principal:** http://localhost:5001 (MLflow UI)

---

*Última actualización: 15 de diciembre de 2025*
