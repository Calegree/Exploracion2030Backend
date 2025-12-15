# 📄 Model Cards - Formatos Disponibles

Ahora cada Model Card se genera automáticamente en **3 formatos diferentes**:

## 📋 Formatos Generados

### 1️⃣ **QMD (Quarto Markdown)**
- **Extensión:** `.qmd`
- **Propósito:** Archivo fuente, editable
- **Ventaja:** Puedes editarlo después
- **Uso:** Refactorizar el documento, agregar datos

```
model_card_EfficientNetB0_20251215_211743.qmd
```

### 2️⃣ **HTML (Web)**
- **Extensión:** `.html`
- **Propósito:** Visualización en navegador
- **Ventaja:** Bonito, responsive, interactivo
- **Uso:** Ver en MLflow UI o descargarlo

```
model_card_EfficientNetB0_20251215_211743.html
```

### 3️⃣ **PDF (Documento)**
- **Extensión:** `.pdf`
- **Propósito:** Compartir, imprimir, archivar
- **Ventaja:** No requiere navegador, profesional
- **Uso:** Enviarlo por email, guardar copia, imprimir

```
model_card_EfficientNetB0_20251215_211743.pdf
```

---

## 🚀 Cómo acceder a los archivos

### En MLflow UI

1. Ve a: http://localhost:5001
2. **Experiments** → **morchella_detection** → **[tu run]**
3. **Artifacts** → **model_cards/**
4. Verás los 3 archivos:
   - ✅ `.qmd` - Archivo fuente
   - ✅ `.html` - Haz clic para abrir en navegador
   - ✅ `.pdf` - Descárgalo para compartir

### Descargar desde Python

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()
run_id = "e03dea4d55344edf8371cf4fb8d3e3f3"

# Descargar todos los archivos
local_path = client.download_artifacts(run_id, 'model_cards')

print(f"Descargados en: {local_path}")

# Los 3 archivos estarán aquí:
# {local_path}/model_card_EfficientNetB0_*.qmd
# {local_path}/model_card_EfficientNetB0_*.html
# {local_path}/model_card_EfficientNetB0_*.pdf
```

---

## 📊 Cuándo usar cada formato

| Situación | Formato | Razón |
|-----------|---------|-------|
| Ver en navegador | HTML | Interactivo, bonito |
| Compartir con equipo | PDF | Universal, no requiere software |
| Editar documento | QMD | Archivo fuente, editable |
| Imprimir | PDF | Optimizado para papel |
| Archivar | PDF | Portable, sin dependencias |
| Integrar en wiki | HTML | Puedes incrustar en Confluence/Notion |
| Para Git | QMD | Formato de texto, control de versiones |

---

## 🔄 Flujo Automático

```
Entrenar modelo
    ↓
Generar QMD
    ↓
├─→ Compilar a HTML (si Quarto disponible)
└─→ Compilar a PDF (si Quarto + Pandoc disponibles)
    ↓
Subir los 3 a MLflow/MinIO
    ↓
Ver en MLflow UI
```

---

## 💡 Ejemplo de Uso

### Caso 1: Revisar resultados rápidamente
```
MLflow UI → Haz clic en .html → Abrir en navegador
```

### Caso 2: Compartir con jefe/equipo
```
MLflow UI → Descarga .pdf → Envía por email
```

### Caso 3: Editar documento
```
MLflow UI → Descarga .qmd → Edita en VS Code → Quarto render
```

### Caso 4: Archivar para legal
```
MLflow UI → Descarga .pdf → Guardar en carpeta del proyecto
```

---

## ⚙️ Requisitos para generar los formatos

| Formato | Requisitos | Instalado |
|---------|-----------|-----------|
| **QMD** | Nada (siempre se genera) | ✅ Sí |
| **HTML** | Quarto | ⚠️ Depende |
| **PDF** | Quarto + Pandoc | ⚠️ Depende |

### Instalar dependencias faltantes

```bash
# Instalar Quarto (requiere para HTML y PDF)
sudo apt-get install quarto

# Instalar Pandoc (requiere para PDF)
sudo apt-get install pandoc

# O descargar desde:
# Quarto: https://quarto.org/docs/get-started/
# Pandoc: https://pandoc.org/installing.html
```

---

## 📋 Contenido de cada formato

**Todos los formatos contienen:**
- ✓ Model Overview
- ✓ Performance Metrics
- ✓ Confusion Matrix
- ✓ Dataset Information
- ✓ Training Configuration
- ✓ Model Limitations
- ✓ Recommendations

**Diferencias:**
- **QMD:** Código fuente, editable
- **HTML:** Con estilos CSS, interactivo
- **PDF:** Formateado para impresión

---

## 🎯 Ventajas de tener los 3

✅ **Flexibilidad** - Elige el formato según necesites  
✅ **Compartible** - PDF es universal  
✅ **Editable** - QMD es fuente  
✅ **Profesional** - HTML y PDF se ven bien  
✅ **Reproducible** - QMD es texto, entra en Git  

---

## 🐛 Troubleshooting

### ❓ "Solo veo .qmd, no .html ni .pdf"

**Causa:** Quarto no está instalado  
**Solución:**
```bash
sudo apt-get install quarto pandoc
```

### ❓ "Veo .html pero no .pdf"

**Causa:** Pandoc no está instalado  
**Solución:**
```bash
sudo apt-get install pandoc
```

### ❓ "¿Puedo elegir qué formatos generar?"

Sí, puedes editar `model_card_mlflow_logger.py` y comentar las líneas de compilación que no quieras:

```python
# Para desactivar HTML, comenta esta línea:
# html_path = self._compile_to_html(qmd_path)

# Para desactivar PDF, comenta esta línea:
# pdf_path = self._compile_to_pdf(qmd_path)
```

---

## 📈 Ejemplo de Flujo Real

```bash
# 1. Entrenas modelo
docker-compose exec api python src/train.py --model efficientnet

# Output:
# ✅ QMD generado
# ✅ HTML compilado
# ✅ PDF compilado
# ✅ Los 3 subidos a MLflow

# 2. Abre MLflow
http://localhost:5001

# 3. Ve Artifacts → model_cards/ y verás:
# 📄 model_card_EfficientNetB0_20251215_211743.qmd
# 📄 model_card_EfficientNetB0_20251215_211743.html
# 📄 model_card_EfficientNetB0_20251215_211743.pdf

# 4. Elige el formato:
# - HTML para ver en navegador
# - PDF para compartir por email
# - QMD para editar
```

---

*Última actualización: 15 de diciembre de 2025*
