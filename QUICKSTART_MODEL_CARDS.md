# 🚀 Quick Start: Model Cards

**Para impaciosos que quieren empezar YA** 😉

---

## ⚡ 3 Pasos para tener Model Cards en MLflow/MinIO

### Paso 1: Entrenar un modelo ✅ Se genera automáticamente

```bash
# EfficientNet (genera automáticamente Model Card en MLflow)
docker-compose exec api python src/train.py --model efficientnet

# O MobileNet
docker-compose exec api python src/train.py --model mobilenet
```

Al terminar verás:
```
✅ Modelo EfficientNetB0 guardado
📋 Generando Model Card y guardando en MLflow...
✅ QMD (fuente) subido a MLflow/MinIO
✅ HTML (navegador) compilado y subido
✅ PDF (documento) compilado y subido
```

### Paso 2: Abre MLflow UI en navegador

```
http://localhost:5001
```

### Paso 3: Ve a tu Model Card

1. **Experiments** → **morchella_detection**
2. Click en el run que entrenaste
3. **Artifacts** → **model_cards**
4. **Elige tu formato:**
   - 📄 `.qmd` - Archivo fuente (editable)
   - 📊 `.html` - Para ver en navegador (bonito)
   - 📑 `.pdf` - Para compartir/imprimir (universal)

## 🎯 ¡Eso es todo!

Tienes documentación profesional de tu modelo **en 3 formatos diferentes** (QMD, HTML, PDF), **almacenada automáticamente en MLflow/MinIO**.

---

## 📋 Entender los 3 Formatos

| Formato | Cuándo usarlo | Dónde encontrarlo |
|---------|---------------|-------------------|
| **QMD** | Editar documento | MLflow artifacts |
| **HTML** | Ver en navegador | MLflow artifacts |
| **PDF** | Compartir/Imprimir | MLflow artifacts |

👉 **Detalles:** `model_cards/MODEL_CARDS_FORMATS.md`

---

## 📚 Acceso a Model Cards

### En MLflow UI (Recomendado)
```
localhost:5001 
→ Experiments 
→ morchella_detection 
→ [tu run] 
→ Artifacts 
→ model_cards/
```

### Descargar desde Python
```python
from mlflow.tracking import MlflowClient

client = MlflowClient()
local_path = client.download_artifacts('[RUN_ID]', 'model_cards')
```

### Más detalles
👉 Ver: `model_cards/ACCESSING_MODEL_CARDS.md`

---

## 💡 ¿Por qué está en MLflow/MinIO?

| Ventaja | Beneficio |
|---------|-----------|
| 🔒 Centralizado | Un único lugar para todo |
| 📦 Versionado | Cada entrenamiento tiene sus docs |
| 🔗 Trazable | Regresa a cualquier versión |
| 👥 Compartible | Descargar y compartir fácilmente |
| ⚡ Automático | Sin pasos manuales |

---

## 🎓 ¿Qué contiene cada Model Card?

```
✓ Arquitectura del modelo
✓ Parámetros de entrenamiento
✓ Dataset info (cantidad imágenes)
✓ Accuracy, Precision, Recall, F1
✓ Matriz de confusión (análisis detallado)
✓ Limitaciones conocidas
✓ Recomendaciones de uso
✓ Run ID para trazabilidad
```

---

## 📂 Dónde se guarda

```
MLflow/MinIO
└── Experimento: morchella_detection
    └── Run [ID]
        └── artifacts/
            └── model_cards/  ← AQUI ESTAN
                ├── model_card_EfficientNetB0_*.qmd
                ├── model_card_EfficientNetB0_*.html
```

---

## 🔗 Más info

- **Acceso detallado:** `model_cards/ACCESSING_MODEL_CARDS.md`
- **Documentación completa:** `model_cards/README.md`
- **Sobre Model Cards:** https://arxiv.org/abs/1810.03993

---

**¡Listo!** 🎉 Ahora tienes bitácoras profesionales de tus modelos automáticamente en MLflow/MinIO.

