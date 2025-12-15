# 🍄 Model Cards para Detección de Morchella

Sistema automático de generación de **Model Cards en Quarto** para documentar, versionar y comparar modelos de detección de hongos Morchella.

## 📋 ¿Qué es un Model Card?

Un **Model Card** es un documento profesional que acompaña a cada modelo y documenta:

- ✅ Arquitectura y parámetros de entrenamiento
- ✅ Métricas de desempeño (accuracy, precision, recall, F1)
- ✅ Matriz de confusión y análisis de errores
- ✅ Datos del dataset usado
- ✅ Limitaciones y riesgos
- ✅ Recomendaciones de uso

Propuesto originalmente por [Google Research](https://arxiv.org/abs/1810.03993), es un estándar en la industria ML moderna (usado por OpenAI, HuggingFace, etc).

---

## 🚀 Flujo de Trabajo Automático

```
1. Entrenas un modelo
   ↓
2. MLflow captura parámetros y métricas
   ↓
3. model_card_generator.py genera automáticamente .qmd
   ↓
4. Quarto compila a HTML profesional
   ↓
5. Comparas modelos con documento comparativo
```

---

## 📂 Estructura

```
proyecto/
├── src/
│   ├── train_model_efficientnet.py     ← Genera Model Card al terminar
│   ├── train_model_mobilenet.py        ← Genera Model Card al terminar
│   ├── model_card_generator.py         ← Generador automático
│   └── model_card_utils.py             ← Herramientas CLI
│
└── model_cards/                        ← Directorio de salida
    ├── model_card_EfficientNetB0_20251215_134500.qmd   ← Fuente
    ├── model_card_EfficientNetB0_20251215_134500.html  ← Compilado
    ├── model_card_MobileNetV2_20251215_141200.qmd
    ├── model_card_MobileNetV2_20251215_141200.html
    ├── model_comparison.qmd             ← Comparativa
    ├── model_comparison.html
    └── model-card-style.css             ← Estilos profesionales
```

---

## 🔧 Instalación de Dependencias

### Paso 1: Instalar Quarto

**En Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install -y quarto

# O descargar desde: https://quarto.org/docs/get-started/
```

**En macOS:**
```bash
brew install quarto
```

**En Windows:**
- Descargar desde [quarto.org/docs/get-started/](https://quarto.org/docs/get-started/)

### Paso 2: Verificar instalación

```bash
quarto --version
# Debe mostrar versión > 1.3
```

### Paso 3: Las dependencias Python ya están en tu proyecto

Los módulos necesarios (`mlflow`, `json`, etc.) ya están instalados en tu entorno.

---

## 🎯 Uso

### Opción 1: Generación Automática (RECOMENDADO)

Al entrenar un modelo, el Model Card se genera automáticamente:

```bash
# Entrenar con EfficientNet
docker-compose exec api python src/train.py --model efficientnet

# En la salida verás:
# ✅ Model Card generado en: /path/to/model_cards/model_card_EfficientNetB0_20251215_134500.qmd
# 💡 Para compilar a HTML: quarto render /path/to/model_cards/model_card_EfficientNetB0_20251215_134500.qmd
```

### Opción 2: Compilar a HTML

Una vez generado el `.qmd`, compílalo a HTML profesional:

```bash
# Compilar el modelo más reciente
python src/model_card_utils.py compile

# Compilar un modelo específico
python src/model_card_utils.py compile /path/to/model_card_EfficientNetB0_*.qmd

# Compilar TODOS los modelos
python src/model_card_utils.py compile-all
```

### Opción 3: Ver Modelos Disponibles

```bash
python src/model_card_utils.py list

# Salida:
# 📊 Model Cards disponibles (2):
# 
# 1. model_card_EfficientNetB0_20251215_134500.qmd
#    📅 Fecha: 2025-12-15 13:45:00
#    📏 Tamaño: 12.5 KB
#
# 2. model_card_MobileNetV2_20251215_141200.qmd
#    📅 Fecha: 2025-12-15 14:12:00
#    📏 Tamaño: 11.8 KB
```

### Opción 4: Crear Documento Comparativo

Compara automáticamente todos tus modelos:

```bash
python src/model_card_utils.py compare

# Genera: model_cards/model_comparison.qmd
# Luego compílalo:
quarto render model_cards/model_comparison.qmd
```

---

## 📊 Contenido del Model Card

Cada Model Card incluye 13 secciones profesionales:

### 1. **Model Overview**
```
✓ ID único del modelo (Run ID de MLflow)
✓ Tipo de arquitectura
✓ Fecha de creación
✓ Estado
```

### 2. **Model Description**
```
✓ Arquitectura (EfficientNetB0, MobileNetV2, etc.)
✓ Transfer learning details
✓ Tamaño de entrada
✓ Activations y capas
```

### 3. **Dataset**
```
✓ Cantidad de imágenes por clase
✓ Split train/val/test
✓ Técnicas de augmentación
✓ Ratio de desbalance
```

### 4. **Training Configuration**
```
✓ Batch size
✓ Learning rate
✓ Optimizer
✓ Número de épocas
✓ Early stopping
```

### 5. **Performance Metrics** ⭐
```
Accuracy                    78.5%
Precision (Morchella)       82.3%
Recall (Morchella)          75.2%
F1-Score                    78.5%
```

### 6. **Confusion Matrix Analysis**
```
                 Predicted: No-Morchella | Predicted: Morchella
Actual: No-Morchella        17                       3
Actual: Morchella           14                       6

✓ True Positives
✓ False Positives (análisis)
✓ False Negatives (análisis)
✓ True Negatives
```

### 7. **Strengths & Weaknesses**
```
✅ Fortalezas del modelo
⚠️ Limitaciones conocidas
```

### 8. **Use Cases & Recommendations**
```
✓ Dónde SÍ usar el modelo
✗ Dónde NO usar el modelo
```

### 9. **Bias & Fairness**
```
✓ Sesgos conocidos
✓ Recomendaciones de mejora
```

### 10. **Technical Details**
```
✓ Framework y versiones
✓ Artifacts en MLflow
✓ Código reproducible
```

### 11. **Model Comparison**
```
Tabla comparativa vs otras arquitecturas
```

### 12. **Changelog**
```
Control de versiones del modelo
```

### 13. **Appendix**
```
Dump completo de parámetros en JSON
```

---

## 📈 Ejemplos de Uso Real

### Ejemplo 1: Entrenar 2 modelos y comparar

```bash
# Entrena EfficientNet
docker-compose exec api python src/train.py --model efficientnet
# ✅ Model Card EfficientNetB0 generado automáticamente

# Entrena MobileNet
docker-compose exec api python src/train.py --model mobilenet
# ✅ Model Card MobileNetV2 generado automáticamente

# Crea documento comparativo
python src/model_card_utils.py compare

# Compila todos
python src/model_card_utils.py compile-all

# Abre el navegador
python src/model_card_utils.py open model_cards/model_comparison.html
```

### Ejemplo 2: Revisar un modelo específico

```bash
# Listar disponibles
python src/model_card_utils.py list

# Compilar el que quieras
python src/model_card_utils.py compile model_cards/model_card_EfficientNetB0_20251215_134500.qmd

# Abrir en navegador
open model_cards/model_card_EfficientNetB0_20251215_134500.html
```

### Ejemplo 3: Workflow de CI/CD

```bash
#!/bin/bash
# Script de entrenamiento con documentación automática

set -e

echo "🍄 Training Pipeline with Automatic Documentation"

# Entrenar modelos
echo "📱 Training MobileNetV2..."
docker-compose exec api python src/train.py --model mobilenet

echo "🎯 Training EfficientNetB0..."
docker-compose exec api python src/train.py --model efficientnet

# Compilar documentación
echo "📋 Compiling Model Cards..."
python src/model_card_utils.py compile-all

# Crear comparativa
echo "📊 Creating Comparison Document..."
python src/model_card_utils.py compare
python src/model_card_utils.py compile model_cards/model_comparison.qmd

echo "✅ Pipeline completed!"
echo "📈 Open: model_cards/model_comparison.html"
```

---

## 🎨 Personalización

### Modificar estilos CSS

Edita `model_cards/model-card-style.css`:

```css
:root {
  --primary-color: #2ecc71;        /* Color principal */
  --secondary-color: #27ae60;      /* Color secundario */
  --accent-color: #3498db;         /* Acentos */
}
```

### Modificar plantilla Quarto

Edita la plantilla dentro de `model_card_generator.py` en la función `create_model_card_qmd()`.

### Agregar más secciones

En `model_card_generator.py`, agrega más secciones al `qmd_content`:

```python
# Ejemplo: agregar sección de API endpoints
qmd_content += """
## 14. API Deployment

### Endpoints
- POST /predict - Predice una imagen
- GET /model/info - Información del modelo
"""
```

---

## 📚 Referencias

### Estándares
- [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993) (Google, 2019)
- [Model Card Toolkit](https://github.com/tensorflow/model-card-toolkit)
- [HuggingFace Model Cards](https://huggingface.co/docs/hub/model-cards)

### Herramientas
- [Quarto Documentation](https://quarto.org/)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)

### Mejores Prácticas
- Siempre incluir matriz de confusión
- Documentar limitaciones conocidas
- Avisos claros sobre bias y fairness
- Ejemplos de casos de uso y anti-casos

---

## 🐛 Troubleshooting

### ❌ "Quarto not found"

```bash
# Instala Quarto
# Linux:
sudo apt-get install quarto
# macOS:
brew install quarto
# Windows: descargar desde quarto.org
```

### ❌ "No module named 'mlflow'"

```bash
# En el contenedor:
docker-compose exec api pip install mlflow
```

### ❌ "Matriz de confusión no aparece"

Verifica que `confusion_matrix.json` esté en los artifacts de MLflow:
1. Abre MLflow UI: `http://localhost:5001`
2. Busca el run
3. Ve a la sección "Artifacts"
4. Debe haber una carpeta `confusion_matrix`

### ❌ "HTML no se ve bien"

Asegúrate de que el archivo CSS está en el mismo directorio:
```bash
ls model_cards/model-card-style.css
```

---

## 💡 Tips Pro

### 1. Automatizar generación en CI/CD

```yaml
# .github/workflows/model-training.yml
name: Train and Document
on: [push]
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Train models
        run: docker-compose exec api python src/train.py --model both
      - name: Generate documentation
        run: python src/model_card_utils.py compile-all
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          path: model_cards/*.html
```

### 2. Comparar modelos por script

```python
# custom_comparison.py
from pathlib import Path
import json

model_cards = Path('model_cards').glob('model_card_*.qmd')
for card in sorted(model_cards):
    print(f"Reviewing {card.name}...")
    # Tu lógica de análisis
```

### 3. Exportar a PDF

```bash
# Si tienes pandoc instalado:
quarto render model_card.qmd --to pdf
```

### 4. Integrar con Notion/Confluence

Copia el HTML generado a tu wiki corporativo para que el equipo revise modelos.

---

## 🤝 Contribuir Mejoras

¿Tienes ideas? Abre un issue o PR en el repositorio.

---

## 📝 Licencia

Este sistema es parte del proyecto Morchella Detection.

---

**Última actualización:** 15 de diciembre de 2025
**Versión:** 1.0
**Estado:** ✅ Producción
