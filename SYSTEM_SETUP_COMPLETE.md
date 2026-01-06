# 🎉 Sistema de Model Cards - Setup Completo

## ✅ Lo que hemos creado para ti

He configurado un sistema **automático y profesional** para generar Model Cards en Quarto cada vez que entrenes un modelo. Es como tener un "historiador" de tus modelos que documenta todo automáticamente.

---

## 📦 Archivos creados

### Generadores (Python)
- **`src/model_card_generator.py`** - Motor principal de generación
  - Extrae datos de MLflow
  - Calcula métricas desde matriz de confusión
  - Genera documentos Quarto profesionales

- **`src/model_card_utils.py`** - Interfaz CLI
  - Lista modelos
  - Compila a HTML
  - Crea documentos comparativos

- **`src/model_card_config.py`** - Configuración centralizada
  - Gestión de URIs de MLflow
  - Configuración de datasets y modelos

### Plantillas (Quarto)
- **`model_cards/model-card-style.css`** - Estilos profesionales
  - Colores personalizables
  - Responsive design
  - Tablas y gráficos elegantes

- **`model_cards/README.md`** - Documentación completa
  - Guía de instalación
  - Ejemplos de uso
  - Troubleshooting

### Documentación (Markdown)
- **`QUICKSTART_MODEL_CARDS.md`** - Guía rápida (5 minutos)
- **`install_quarto.sh`** - Script de instalación automática

### Integración con entrenamiento
- **`src/train_model_efficientnet.py`** - ✅ Modificado para generar Model Card
- **`src/train_model_mobilenet.py`** - ✅ Modificado para generar Model Card

---

## 🚀 Cómo Empezar (Ahora Mismo)

### Paso 1️⃣: Instalar Quarto

```bash
# Linux
sudo apt-get install quarto

# macOS
brew install quarto

# O correr script automático
bash install_quarto.sh
```

Verifica: `quarto --version` debe mostrar una versión

### Paso 2️⃣: Entrenar un modelo (automáticamente genera Model Card)

```bash
# Opción A: En Docker
docker-compose exec api python src/train.py --model efficientnet

# Opción B: Localmente
python src/train_model_efficientnet.py
```

### Paso 3️⃣: Compilar a HTML

```bash
python src/model_card_utils.py compile-all
```

### Paso 4️⃣: Abrir en navegador

```bash
python src/model_card_utils.py open
```

**¡Listo!** 🎉 Tienes documentación profesional de tu modelo.

---

## 📊 Flujo Automático

```
Entrenas modelo
      ↓
MLflow guarda params + métricas + artifacts
      ↓
model_card_generator.py crea .qmd automáticamente
      ↓
Quarto compila a HTML hermoso
      ↓
Documento profesional listo
```

---

## 💡 Comandos Principales

```bash
# 1. Listar todos los modelos generados
python src/model_card_utils.py list

# 2. Compilar modelo más reciente
python src/model_card_utils.py compile

# 3. Compilar todos
python src/model_card_utils.py compile-all

# 4. Crear comparativa de modelos
python src/model_card_utils.py compare

# 5. Abrir en navegador
python src/model_card_utils.py open
```

---

## 📈 Qué contendrá cada Model Card

### 📋 13 Secciones profesionales:

1. **Model Overview** - ID, tipo, fecha
2. **Model Description** - Arquitectura, transfer learning, tamaño
3. **Dataset** - Cantidad de imágenes, augmentaciones
4. **Training Configuration** - Hiperparámetros
5. **Performance Metrics** ⭐ - Accuracy, Precision, Recall, F1
6. **Confusion Matrix Analysis** - Errores detallados
7. **Strengths & Weaknesses** - Fortalezas y limitaciones
8. **Use Cases & Recommendations** - Dónde usar/no usar
9. **Bias & Fairness** - Sesgos conocidos
10. **Technical Details** - Framework, reproducibilidad
11. **Model Comparison** - Tabla comparativa
12. **Changelog** - Versionado
13. **Appendix** - Dump de parámetros JSON

---

## 🎯 Caso de Uso Real

### Escenario: Entrenas 3 modelos y quieres compararlos

```bash
# 1. Entrenar modelo 1
docker-compose exec api python src/train.py --model efficientnet
# ✅ Model Card generado automáticamente

# 2. Entrenar modelo 2
docker-compose exec api python src/train.py --model mobilenet
# ✅ Model Card generado automáticamente

# 3. Entrenar modelo 3 (con parámetros diferentes)
docker-compose exec api python src/train.py --model efficientnet
# ✅ Model Card generado automáticamente

# 4. Compilar todos
python src/model_card_utils.py compile-all

# 5. Crear comparativa
python src/model_card_utils.py compare
quarto render model_cards/model_comparison.qmd

# 6. Abrir
python src/model_card_utils.py open model_cards/model_comparison.html
```

Ahora tienes una **bitácora de entrenamiento profesional y comparable** 📊

---

## 🔍 Estructura de Carpetas

```
proyecto/
├── src/
│   ├── train_model_efficientnet.py    ✅ Ahora genera Model Card
│   ├── train_model_mobilenet.py       ✅ Ahora genera Model Card
│   ├── model_card_generator.py        🆕 Generador
│   ├── model_card_utils.py            🆕 Utilidades CLI
│   ├── model_card_config.py           🆕 Configuración
│   └── example_generate_model_card.py 🆕 Ejemplo
│
├── model_cards/                       📁 Salida (se crea automáticamente)
│   ├── model_card_EfficientNetB0_20251215_134500.qmd
│   ├── model_card_EfficientNetB0_20251215_134500.html
│   ├── model_card_MobileNetV2_20251215_141200.qmd
│   ├── model_card_MobileNetV2_20251215_141200.html
│   ├── model_comparison.qmd
│   ├── model_comparison.html
│   ├── README.md                      🆕 Documentación
│   └── model-card-style.css           🆕 Estilos
│
├── QUICKSTART_MODEL_CARDS.md          🆕 Guía rápida
├── install_quarto.sh                  🆕 Instalador
└── README.md                          ✅ Actualizado
```

---

## 📚 Recursos

### Documentación
- 📖 Guía rápida (5 min): `QUICKSTART_MODEL_CARDS.md`
- 📖 Guía completa: `model_cards/README.md`
- 📖 Sobre Model Cards: https://arxiv.org/abs/1810.03993

### Estándares
- Google Model Cards: https://arxiv.org/abs/1810.03993
- HuggingFace Model Cards: https://huggingface.co/docs/hub/model-cards
- Model Card Toolkit: https://github.com/tensorflow/model-card-toolkit

---

## 🐛 Troubleshooting Rápido

### ❌ "Quarto not found"
```bash
bash install_quarto.sh
```

### ❌ "No se genera el Model Card"
Verifica que MLflow está corriendo y tiene datos. Ve a: `http://localhost:5001`

### ❌ "Matriz de confusión en blanco"
Asegúrate de que el modelo genera `confusion_matrix.json` en sus artifacts (revisa en MLflow UI)

### ❌ "CSS no se ve bien"
```bash
ls model_cards/model-card-style.css
# Si no existe, ejecuta nuevamente el generador
```

---

## 💡 Tips Pro

### 1. Integrar con CI/CD
```yaml
# .github/workflows/train.yml
- name: Generate Model Cards
  run: python src/model_card_utils.py compile-all
```

### 2. Comparar por script Python
```python
import json
from pathlib import Path

# Comparar metrics de todos los modelos
for qmd in Path('model_cards').glob('model_card_*.qmd'):
    with open(qmd) as f:
        content = f.read()
        # Tu análisis aquí
```

### 3. Exportar a PDF
```bash
quarto render model_cards/model_card_*.qmd --to pdf
```

### 4. Compartir con equipo
- Copia los archivos `.html` a tu wiki corporativo
- Comparte el `model_comparison.html` en reuniones

---

## 🎓 Conceptos Clave

### ¿Qué es un Model Card?
Es un documento que acompaña a cada modelo ML, documentando:
- Cómo fue entrenado
- Qué datos usó
- Qué tan bien funciona
- Limitaciones conocidas
- Riesgos y sesgos

### ¿Por qué es importante?
- ✅ Reproducibilidad
- ✅ Transparencia
- ✅ Trazabilidad
- ✅ Comparación fácil
- ✅ Documentación profesional

### ¿Quién lo usa?
- Google, OpenAI, HuggingFace
- Reguladores (GDPR, AI Act)
- Equipos responsables de IA

---

## 📞 Próximos Pasos

1. **Ahora:** Instala Quarto (`bash install_quarto.sh`)
2. **Luego:** Entrena un modelo (`docker-compose exec api python src/train.py --model efficientnet`)
3. **Después:** Compila Model Cards (`python src/model_card_utils.py compile-all`)
4. **Finalmente:** Abre y revisa (`python src/model_card_utils.py open`)

---

## 🎉 ¡Listo!

Tienes un sistema profesional de documentación de modelos.

**Características:**
- ✅ Generación automática (sin pasos manuales)
- ✅ Documentación profesional en HTML
- ✅ Comparación de modelos
- ✅ Reproducibilidad garantizada
- ✅ Estándares de industria (Google, OpenAI)

**Qué sigue:**
- 🚀 Entrenar modelos
- 📊 Revisar Model Cards
- 📈 Comparar y decidir cuál usar
- 🎯 Desplegar el mejor

---

**Creado:** 15 de diciembre de 2025
**Sistema:** Completamente automatizado
**Estándar:** Google Model Cards
**Estado:** ✅ Producción
