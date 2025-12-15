# ✅ Testing - Verificar que Model Cards Funcionan

Después de hacer cambios, verifica que todo funciona correctamente.

---

## 🧪 Test 1: Verificar Sistema (2 min)

```bash
cd /home/charles-darwin/Morchellapp/Exploracion2030Backend

# Ejecutar verificador
python verify_model_cards_setup.py
```

**Resultado esperado:**
```
✅ Python 3.8+ detected
✅ MLflow installed
✅ Quarto installed
✅ Pandoc installed
✅ Datasets found
✅ Training scripts found
✅ Model Card modules found

✨ Sistema listo para Model Cards
```

---

## 🧪 Test 2: Generar una Model Card Manual (5 min)

Si quieres probar sin entrenar un modelo completo:

```bash
cd /home/charles-darwin/Morchellapp/Exploracion2030Backend

# Generar manualmente (requiere un run_id válido)
python -c "
from src.model_card_mlflow_logger import log_model_card_automatic

# Reemplaza con un run_id real de MLflow
run_id = 'YOUR_RUN_ID_HERE'
log_model_card_automatic(
    run_id=run_id,
    model_type='EfficientNetB0',
    dataset_path='src/dataset'
)
"
```

---

## 🧪 Test 3: Entrenar Modelo Real (10-30 min)

El **mejor test** es entrenar un modelo de verdad:

```bash
# Start MLflow + MinIO (si no está corriendo)
docker-compose up -d

# Espera 10 segundos a que levante MLflow
sleep 10

# Entrena modelo
docker-compose exec api python src/train.py --model efficientnet

# Output esperado:
# ✅ Training started...
# ✅ Model Card QMD generado
# ✅ Model Card HTML compilado
# ✅ Model Card PDF compilado
# ✅ Subido a MLflow
```

**Verificar resultado:**

1. Abre MLflow UI: http://localhost:5001
2. Ve a: **Experiments** → **morchella_detection**
3. Haz clic en el último run
4. En la sección **Artifacts** busca **model_cards/**
5. Deberías ver:
   - ✅ `model_card_EfficientNetB0_YYYYMMDD_HHMMSS.qmd`
   - ✅ `model_card_EfficientNetB0_YYYYMMDD_HHMMSS.html`
   - ✅ `model_card_EfficientNetB0_YYYYMMDD_HHMMSS.pdf`

---

## 🧪 Test 4: Verificar Formatos (2 min)

```bash
# Descargar los archivos generados
python -c "
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Obtener experimento
exp = client.get_experiment_by_name('morchella_detection')
runs = client.search_runs(exp.experiment_id)

if runs:
    latest_run = runs[0]
    print(f'Latest run: {latest_run.info.run_id}')
    
    # Descargar artifacts
    path = client.download_artifacts(latest_run.info.run_id, 'model_cards')
    print(f'Artifacts downloaded to: {path}')
    
    # Listar archivos
    import os
    files = os.listdir(path)
    print('\nArchivos generados:')
    for f in files:
        print(f'  - {f}')
else:
    print('No runs found')
"
```

**Resultado esperado:**
```
Latest run: abc123def456...
Artifacts downloaded to: /tmp/mlruns/...

Archivos generados:
  - model_card_EfficientNetB0_20251215_211743.qmd
  - model_card_EfficientNetB0_20251215_211743.html
  - model_card_EfficientNetB0_20251215_211743.pdf
```

---

## 🧪 Test 5: Abrir HTML en Navegador (1 min)

```bash
# Opción 1: Abrir archivo local directamente
python src/model_card_utils.py open

# Opción 2: Abrir desde MLflow UI
# 1. MLflow → Artifacts → model_cards
# 2. Haz clic en .html
# 3. Debería abrir en navegador
```

**Verificar:**
- ✅ Documento se abre
- ✅ Tiene estilos CSS (bonito, no blanco y negro)
- ✅ Muestra métricas, matriz de confusión, recomendaciones

---

## 🧪 Test 6: Verificar PDF (1 min)

```bash
# Opción 1: Descargar desde MLflow
# MLflow → Artifacts → model_cards → [archivo.pdf] → Download

# Opción 2: Buscar localmente
find . -name "*.pdf" -type f | grep model_card

# Opción 3: Abrir con
python -c "
import os
import subprocess
pdfs = list(os.path.abspath('model_cards').glob('*.pdf'))
if pdfs:
    subprocess.Popen(['xdg-open', pdfs[-1]])
"
```

**Verificar:**
- ✅ PDF existe
- ✅ Se abre en lector PDF
- ✅ Contiene toda la información
- ✅ Se puede imprimir

---

## 🧪 Test 7: Verificar Que Ambos Modelos Funcionen

```bash
# Test EfficientNetB0
docker-compose exec api python src/train.py --model efficientnet

# Espera a que termine

# Test MobileNetV2
docker-compose exec api python src/train.py --model mobilenet
```

**Verificar:**
- ✅ Ambos generan Model Cards
- ✅ Cada uno tiene su propio nombre (`model_card_EfficientNetB0_*` vs `model_card_MobileNetV2_*`)
- ✅ Ambos aparecen en MLflow

---

## 🔧 Troubleshooting

### ❌ "No veo los archivos en MLflow"

**Posible causa 1:** MLflow no está corriendo
```bash
docker-compose up -d
docker-compose logs mlflow
```

**Posible causa 2:** El training no completó
```bash
# Verifica logs de entrenamiento
docker-compose logs api | tail -100
```

**Posible causa 3:** Ruta artifact incorrecta
```bash
# Verifica que MLflow track_artifact_uri esté bien
python -c "
import mlflow
print(f'Artifact URI: {mlflow.get_artifact_uri()}')
print(f'Tracking URI: {mlflow.get_tracking_uri()}')
"
```

---

### ❌ "Veo .qmd pero no .html ni .pdf"

**Causa:** Quarto no instalado
```bash
# Instalar Quarto
sudo apt-get update
sudo apt-get install quarto

# Verificar
quarto --version

# Si sigue sin funcionar, usar script:
bash install_quarto.sh
```

---

### ❌ "Veo .html pero no .pdf"

**Causa:** Pandoc no instalado
```bash
# Instalar Pandoc
sudo apt-get install pandoc

# Verificar
pandoc --version
```

---

### ❌ "El HTML no se ve bonito (sin estilos CSS)"

**Posible causa:** CSS no se cargó
```bash
# Verificar que CSS esté en MLflow
# MLflow → Artifacts → model_cards → model-card-style.css

# Si falta, copiar manualmente:
cp model_cards/model-card-style.css src/model_cards/
```

---

## ✅ Checklist de Verificación

Marca cada item después de verificar:

- [ ] `verify_model_cards_setup.py` pasa sin errores
- [ ] MLflow está corriendo (http://localhost:5001 abre)
- [ ] Entrenar un modelo genera .qmd automáticamente
- [ ] El .qmd aparece en MLflow artifacts
- [ ] Si Quarto está instalado, se genera .html
- [ ] Si Pandoc está instalado, se genera .pdf
- [ ] El .html se abre en navegador y se ve bonito
- [ ] El .pdf se abre en lector PDF
- [ ] Ambos modelos (EfficientNet + MobileNet) funcionan
- [ ] MLflow muestra los 3 formatos en artifacts

**Si todos marcas ✅, ¡todo funciona perfecto!**

---

## 📞 ¿Necesitas ayuda?

1. **Lee primero:** [`MODEL_CARDS_FORMATS.md`](MODEL_CARDS_FORMATS.md)
2. **Verifica:** `python verify_model_cards_setup.py`
3. **Revisa logs:** `docker-compose logs api | tail -50`
4. **Busca en:** `src/model_card_mlflow_logger.py` (línea de error)

---

*Última actualización: 15 de diciembre de 2025*
