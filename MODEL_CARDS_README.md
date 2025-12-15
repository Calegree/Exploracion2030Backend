# 🍄 Sistema Automático de Model Cards - Morchella Detection

Generación **automática, profesional y centralizada** de Model Cards (documentación de modelos) para detección de Morchella.

---

## 🎯 ¿Qué es?

Un sistema que **automáticamente genera documentación profesional** cada vez que entrenas un modelo:

```
Entrenas modelo → Se genera Model Card → Se sube a MLflow
                      (automático)       (automático)
```

La documentación se genera en **3 formatos diferentes**:
- 📄 **QMD** (fuente, editable)
- 📊 **HTML** (navegador, bonito)
- 📑 **PDF** (compartir, universal)

---

## ✨ Características

✅ **Completamente automático** - Sin pasos manuales  
✅ **3 formatos** - QMD, HTML, PDF generados automáticamente  
✅ **Centralizado** - Todo en MLflow/MinIO  
✅ **Profesional** - Template de 13 secciones  
✅ **Versionado** - Histórico completo de entrenamientos  
✅ **Tolerante a errores** - Funciona incluso si falta Quarto/Pandoc  
✅ **Rápido** - Overhead mínimo (~20-30 seg)  

---

## 🚀 Quick Start (5 minutos)

### 1. Verificar Sistema
```bash
python verify_model_cards_setup.py
```

### 2. Iniciar Servicios
```bash
docker-compose up -d
sleep 10
```

### 3. Entrenar Modelo
```bash
docker-compose exec api python src/train.py --model efficientnet
```

### 4. Ver Resultado
```
http://localhost:5001 → Experiments → morchella_detection → [tu run] → Artifacts → model_cards/
```

Verás 3 archivos:
- 📄 `.qmd` (fuente)
- 📊 `.html` (web)
- 📑 `.pdf` (documento)

**¡Listo!** Sin pasos manuales. Todo automático. 🎉

---

## 📊 Contenido de Cada Model Card

Cada Model Card incluye **13 secciones profesionales**:

1. **Model Card Header** - Título y metadatos
2. **Model Overview** - Descripción general
3. **Intended Use** - Casos de uso
4. **Model Architecture** - Detalles técnicos
5. **Performance Metrics** - Accuracy, Precision, Recall, F1
6. **Confusion Matrix** - TN, FP, FN, TP visualizado
7. **Dataset Information** - Cantidad, clases, balanceo
8. **Data Preprocessing** - Normalización, augmentación
9. **Training Configuration** - Hiperparámetros
10. **Training History** - Gráficos de loss/accuracy
11. **Model Limitations** - Qué NO puede hacer
12. **Recommendations** - Sugerencias de mejora
13. **References & Conclusion** - Links y resumen

---

## 📁 Estructura

```
Exploracion2030Backend/
├── src/
│   ├── train_model_efficientnet.py    ← Entrenar + generar
│   ├── train_model_mobilenet.py       ← Entrenar + generar
│   ├── model_card_mlflow_logger.py    ← ⭐ Motor automático
│   ├── model_card_generator.py        ← Generador base
│   ├── model_card_utils.py            ← Herramientas CLI
│   └── ...
│
├── model_cards/
│   ├── README.md                      ← Guía completa
│   ├── MODEL_CARDS_FORMATS.md         ← Explicación de formatos
│   ├── ACCESSING_MODEL_CARDS.md       ← Cómo acceder
│   ├── TESTING_MODEL_CARDS.md         ← Verificación
│   ├── model-card-style.css           ← Estilos
│   └── model_card_*.{qmd,html,pdf}    ← Generadas automáticamente
│
├── QUICKSTART_MODEL_CARDS.md          ← 5 minutos
├── SUMMARY_MODEL_CARDS.md             ← Resumen ejecutivo
├── ARCHITECTURE.md                    ← Cómo funciona internamente
├── QUICK_REFERENCE.md                 ← Comandos rápidos
├── DEPLOY_CHECKLIST.md                ← Verificación pre-deploy
├── FAQ.md                             ← Preguntas frecuentes
└── docker-compose.yml                 ← MLflow + MinIO

```

---

## 📚 Documentación por Propósito

| Necesidad | Documento | Tiempo |
|-----------|-----------|--------|
| **Quiero empezar** | QUICKSTART_MODEL_CARDS.md | ⚡ 5 min |
| **Entender rápido** | SUMMARY_MODEL_CARDS.md | 🎯 5 min |
| **Ver comandos** | QUICK_REFERENCE.md | 📖 5 min |
| **¿Cómo accedo?** | model_cards/ACCESSING_MODEL_CARDS.md | 📂 5 min |
| **¿Cuáles son los formatos?** | model_cards/MODEL_CARDS_FORMATS.md | 📊 10 min |
| **¿Cómo pruebo?** | model_cards/TESTING_MODEL_CARDS.md | 🧪 10 min |
| **¿Cómo funciona?** | ARCHITECTURE.md | 🏗️ 15 min |
| **¿Cómo depliego?** | DEPLOY_CHECKLIST.md | ✅ 15 min |
| **Dudas generales** | FAQ.md | ❓ Variable |
| **Guía completa** | model_cards/README.md | 📘 30 min |

---

## 🔧 Requisitos

### Instalado
- ✅ Python 3.8+
- ✅ Docker & Docker Compose
- ✅ MLflow
- ✅ TensorFlow 2.x

### Recomendado (para máxima funcionalidad)
- ⚠️ Quarto 1.3+ (para HTML)
- ⚠️ Pandoc (para PDF)

**Instalación automática:**
```bash
bash install_quarto.sh
```

---

## 🎯 Casos de Uso

### 📊 "Quiero ver los resultados rápido"
```
MLflow → Artifacts → model_cards/ → Abre .html en navegador
```
HTML se ve bonito con estilos CSS.

### 💼 "Necesito compartir con mi jefe"
```
MLflow → Artifacts → model_cards/ → Descarga .pdf → Envía por email
```
PDF es universal, no requiere software especial.

### ✏️ "Quiero editar el documento"
```
MLflow → Artifacts → model_cards/ → Descarga .qmd → Edita en VS Code
→ Quarto render [archivo.qmd] → Nuevos HTML/PDF
```

### 📋 "Necesito guardar para auditoría"
```
MLflow → Artifacts → model_cards/ → Descarga .pdf → Archiva seguro
```
PDF es permanente y no se pierde.

### 🔍 "Quiero comparar 5 modelos"
```
python src/model_card_utils.py compare-all
# Genera tabla comparativa de todos
```

---

## 🔄 Flujo Automático

```
┌────────────────────────────┐
│  ENTRENAR MODELO (5-30m)   │
└────────────┬───────────────┘
             ↓
┌────────────────────────────┐
│  REGISTRAR MÉTRICAS (auto) │
│  MLflow: accuracy, loss... │
└────────────┬───────────────┘
             ↓
┌────────────────────────────┐
│  GENERAR MODEL CARD (auto) │
│  • Crear QMD             │
│  • Compilar a HTML       │
│  • Compilar a PDF        │
└────────────┬───────────────┘
             ↓
┌────────────────────────────┐
│  SUBIR A MLFLOW (auto)     │
│  • .qmd                    │
│  • .html                   │
│  • .pdf                    │
└────────────┬───────────────┘
             ↓
┌────────────────────────────┐
│  VER EN NAVEGADOR (tú)     │
│  http://localhost:5001     │
└────────────────────────────┘
```

**⏱️ Tiempo total:** ~20-30 segundos overhead  
**🤖 Manual:** 0% (totalmente automático)

---

## 💾 Formatos Explicados

### QMD (Markdown con Quarto)
- **Extensión:** `.qmd`
- **Propósito:** Archivo fuente
- **Ventaja:** Editable
- **Cuándo:** Necesitas modificar contenido

### HTML (Web)
- **Extensión:** `.html`
- **Propósito:** Visualización en navegador
- **Ventaja:** Bonito, con estilos CSS
- **Cuándo:** Ver en MLflow UI

### PDF (Documento)
- **Extensión:** `.pdf`
- **Propósito:** Compartir/Imprimir
- **Ventaja:** Universal, cualquiera puede abrir
- **Cuándo:** Enviar por email, guardar

---

## 🔐 Almacenamiento

Los Model Cards se guardan automáticamente en **2 lugares**:

### MLflow UI (localhost:5001)
```
Experiments
  └─ morchella_detection
      └─ [run_id_1] (tu entrenamiento 1)
          └─ Artifacts
              └─ model_cards/
                  ├─ *.qmd
                  ├─ *.html
                  └─ *.pdf
      └─ [run_id_2] (tu entrenamiento 2)
          └─ Artifacts
              └─ model_cards/
                  ├─ *.qmd
                  ├─ *.html
                  └─ *.pdf
```

### MinIO S3 (localhost:9001)
```
mlflow/
  └─ [run_id]/
      └─ artifacts/
          └─ model_cards/
              ├─ *.qmd
              ├─ *.html
              └─ *.pdf
```

Ambos sincronizados automáticamente.

---

## ⚙️ Configuración

### Variables de Entorno (Opcional)
```bash
# Cambiar URI de MLflow
export MLFLOW_TRACKING_URI=http://localhost:5001

# Cambiar URI de artifacts
export MLFLOW_ARTIFACT_URI=s3://bucket/path
```

### Personalizar Template
Editar: `src/model_card_generator.py` → `_build_qmd_content()`

El template es **Markdown**, muy fácil de personalizar.

---

## 🧪 Verificación

Verificar que todo funciona:
```bash
# Test 1: Sistema
python verify_model_cards_setup.py

# Test 2: Entrenamiento real (5-15 min)
docker-compose exec api python src/train.py --model efficientnet

# Test 3: Ver en MLflow
# http://localhost:5001
```

---

## 📞 Ayuda

### Rápido
- 📖 Lee: `QUICK_REFERENCE.md`
- 🎯 Resumen: `SUMMARY_MODEL_CARDS.md`

### Problemas
- ❓ Preguntas: `FAQ.md`
- 🔍 Testing: `model_cards/TESTING_MODEL_CARDS.md`
- 🆘 Troubleshooting: `FAQ.md` → Troubleshooting

### Profundo
- 🏗️ Arquitectura: `ARCHITECTURE.md`
- ✅ Checklist: `DEPLOY_CHECKLIST.md`
- 📚 Completo: `model_cards/README.md`

---

## 🎓 Recursos Externos

- **Google Model Cards:** https://modelcards.withgoogle.com/
- **Paper original:** https://arxiv.org/abs/1810.03993
- **Quarto:** https://quarto.org/
- **MLflow:** https://mlflow.org/
- **MinIO:** https://min.io/

---

## 🎉 Características Implementadas

✅ **Generación automática** de Model Cards al entrenar  
✅ **3 formatos** (QMD, HTML, PDF)  
✅ **13 secciones** profesionales en template  
✅ **Integración MLflow** - Artifacts automáticos  
✅ **Integración MinIO** - Almacenamiento persistente  
✅ **CLI tools** - `model_card_utils.py`  
✅ **HTML styling** - CSS profesional  
✅ **Error handling** - Graceful degradation  
✅ **Documentación completa** - 10+ archivos .md  
✅ **Testing framework** - Scripts de verificación  

---

## 🗓️ Timeline

| Hito | Fecha | Estado |
|------|-------|--------|
| Sistema base | 15 Dic | ✅ |
| MLflow integration | 15 Dic | ✅ |
| HTML + PDF output | 15 Dic | ✅ |
| Documentación | 15 Dic | ✅ |
| Testing & validation | 15 Dic | ✅ |

---

## 🚀 Próximas Mejoras (Opcionales)

- [ ] Integración CI/CD (GitLab Actions)
- [ ] Comparación automática de modelos (reporte)
- [ ] Notificaciones por email
- [ ] Dashboard de modelos (Grafana)
- [ ] Exportar a Word/PowerPoint
- [ ] Machine learning interpretability (SHAP, LIME)

---

## 📊 Stats

| Métrica | Valor |
|---------|-------|
| Módulos Python | 4 |
| Documentación | 11 archivos .md |
| Secciones/Card | 13 |
| Formatos | 3 (QMD, HTML, PDF) |
| Tolerancia a errores | Alta (graceful degradation) |
| Overhead tiempo | ~20-30 seg |
| Overhead RAM | < 1 GB |

---

## ⭐ ¿Por qué Model Cards?

### El Problema
- ❌ Modelos sin documentación
- ❌ Difícil saber qué modelos funcionan mejor
- ❌ No reproducible
- ❌ Riesgo de sesgo/limitaciones olvidadas

### La Solución
- ✅ Documentación automática
- ✅ Fácil comparar modelos
- ✅ Completamente reproducible
- ✅ Limitaciones explícitas

### El Resultado
- 📊 Documentación profesional
- 🎯 Decisiones basadas en datos
- 🔒 Cumplimiento legal/auditoría
- 🚀 Mejora continua

---

## 📝 License & Citation

Sistema de Model Cards para Detección de Morchella  
Inspirado en: [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993)

---

## 📧 Contacto & Soporte

Para preguntas o problemas:
1. Consulta `FAQ.md`
2. Revisa `TESTING_MODEL_CARDS.md`
3. Verifica `DEPLOY_CHECKLIST.md`

---

**¿Listo para empezar?** 👉 Lee [`QUICKSTART_MODEL_CARDS.md`](QUICKSTART_MODEL_CARDS.md)

---

*Última actualización: 15 de diciembre de 2025*  
*Estado: ✅ PRODUCCIÓN LISTA*  
*Versión: 1.0*
