# 🔗 Referencia Rápida - Commands de Model Cards

**Copia y pega estos comandos según lo que necesites**

---

## 📋 Entrenar Modelos

### Entrenar EfficientNetB0 (con Model Card automático)
```bash
docker-compose exec api python src/train.py --model efficientnet
```

### Entrenar MobileNetV2 (con Model Card automático)
```bash
docker-compose exec api python src/train.py --model mobilenet
```

---

## 🔍 Verificación

### Verificar que todo está instalado
```bash
python verify_model_cards_setup.py
```

### Ver MLflow UI
```bash
# Abrir en navegador:
http://localhost:5001
```

### Listar todos los artifacts de un run
```bash
python -c "
from mlflow.tracking import MlflowClient
client = MlflowClient()
exp = client.get_experiment_by_name('morchella_detection')
runs = client.search_runs(exp.experiment_id)
if runs:
    run_id = runs[0].info.run_id
    artifacts = client.list_artifacts(run_id, 'model_cards')
    for a in artifacts:
        print(a.path)
"
```

---

## ⬇️ Descargar Archivos

### Descargar Model Card de un run específico
```bash
python -c "
from mlflow.tracking import MlflowClient
client = MlflowClient()
path = client.download_artifacts('RUN_ID_AQUI', 'model_cards')
print(f'Descargado en: {path}')
"
```

### Descargar último Model Card
```bash
python -c "
from mlflow.tracking import MlflowClient
client = MlflowClient()
exp = client.get_experiment_by_name('morchella_detection')
runs = client.search_runs(exp.experiment_id)
if runs:
    path = client.download_artifacts(runs[0].info.run_id, 'model_cards')
    print(f'Descargado en: {path}')
"
```

---

## 📖 Compilación Manual

### Compilar un QMD específico a HTML
```bash
quarto render model_cards/model_card_*.qmd --to html
```

### Compilar un QMD específico a PDF
```bash
quarto render model_cards/model_card_*.qmd --to pdf
```

### Compilar todos los QMD
```bash
python src/model_card_utils.py compile-all
```

---

## 🌐 Abrir en Navegador

### Abrir el último HTML generado
```bash
python src/model_card_utils.py open
```

### Abrir un HTML específico
```bash
xdg-open model_cards/model_card_EfficientNetB0_*.html
```

---

## 📊 Comparación de Modelos

### Generar tabla comparativa de todos los modelos
```bash
python src/model_card_utils.py compare-all
```

### Ver archivo de comparación
```bash
python src/model_card_utils.py open-comparison
```

---

## 🛠️ Instalación de Dependencias

### Instalar Quarto (para HTML y PDF)
```bash
sudo apt-get update
sudo apt-get install quarto
```

### Instalar Pandoc (para PDF)
```bash
sudo apt-get install pandoc
```

### Verificar instalaciones
```bash
quarto --version
pandoc --version
```

---

## 🐛 Troubleshooting

### Ver logs de entrenamiento
```bash
docker-compose logs api | tail -100
```

### Reiniciar MLflow
```bash
docker-compose restart mlflow
```

### Limpiar artifacts antiguos
```bash
python src/clean_mlflow.py
```

### Ver configuración de MLflow
```bash
python -c "
import mlflow
print(f'Tracking URI: {mlflow.get_tracking_uri()}')
print(f'Artifact URI: {mlflow.get_artifact_uri()}')
"
```

---

## 📂 Ubicación de Archivos

### Archivos Python del sistema
```
src/
├── model_card_mlflow_logger.py      ← Generador automático
├── model_card_generator.py          ← Motor base
├── model_card_utils.py              ← Herramientas CLI
├── model_card_config.py             ← Configuración
└── example_generate_model_card.py   ← Ejemplo
```

### Documentación
```
model_cards/
├── README.md                        ← Guía completa
├── MODEL_CARDS_FORMATS.md           ← Explicación de formatos
├── ACCESSING_MODEL_CARDS.md         ← Cómo acceder
├── TESTING_MODEL_CARDS.md           ← Pruebas
└── model-card-style.css             ← Estilos
```

### Model Cards generadas
```
model_cards/
├── model_card_EfficientNetB0_*.qmd   ← Fuente
├── model_card_EfficientNetB0_*.html  ← Web
├── model_card_EfficientNetB0_*.pdf   ← Documento
├── model_card_MobileNetV2_*.qmd
├── model_card_MobileNetV2_*.html
└── model_card_MobileNetV2_*.pdf
```

---

## 🎯 Flujo Típico de Trabajo

```bash
# 1. Verificar sistema
python verify_model_cards_setup.py

# 2. Asegurar que MLflow está activo
docker-compose up -d

# 3. Entrenar modelo
docker-compose exec api python src/train.py --model efficientnet

# 4. Esperar a que termine (5-30 min)
# Verás: ✅ Model Card generado

# 5. Abrir MLflow
# http://localhost:5001

# 6. Ver artifacts → model_cards/
# Verás: .qmd, .html, .pdf

# 7. Elegir tu formato:
# - HTML: Ver en navegador
# - PDF: Descargar y compartir
# - QMD: Descargar y editar
```

---

## ⚙️ Variables de Entorno (si necesitas)

```bash
# Cambiar URI de MLflow
export MLFLOW_TRACKING_URI=http://localhost:5001

# Cambiar directorio de artifacts
export MLFLOW_ARTIFACT_URI=s3://bucket/path

# Ver variables actuales
env | grep MLFLOW
```

---

## 📞 Obtener Ayuda

### Lee la documentación correspondiente
```
Quick Start       → QUICKSTART_MODEL_CARDS.md
Resumen           → SUMMARY_MODEL_CARDS.md
Formatos          → model_cards/MODEL_CARDS_FORMATS.md
Acceso            → model_cards/ACCESSING_MODEL_CARDS.md
Pruebas           → model_cards/TESTING_MODEL_CARDS.md
Guía completa     → model_cards/README.md
```

### Busca errores en logs
```bash
# Logs del API
docker-compose logs api

# Logs de MLflow
docker-compose logs mlflow

# Logs de MinIO
docker-compose logs minio
```

### Verifica la instalación
```bash
python verify_model_cards_setup.py
```

---

## 💾 Comandos de Docker Compose

### Ver servicios activos
```bash
docker-compose ps
```

### Iniciar servicios
```bash
docker-compose up -d
```

### Detener servicios
```bash
docker-compose down
```

### Ver logs completos
```bash
docker-compose logs -f
```

### Limpiar volúmenes (⚠️ Borra datos)
```bash
docker-compose down -v
```

---

## 📈 Estadísticas

### Contar modelos entrenados
```bash
python -c "
from mlflow.tracking import MlflowClient
client = MlflowClient()
exp = client.get_experiment_by_name('morchella_detection')
runs = client.search_runs(exp.experiment_id)
print(f'Total runs: {len(runs)}')
"
```

### Ver espacio usado por artifacts
```bash
du -sh mlruns/
du -sh minio-data/
```

---

*Última actualización: 15 de diciembre de 2025*  
*Para dudas, consulta los archivos .md correspondientes*
