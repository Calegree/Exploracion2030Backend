# 👋 ¡Bienvenido! Sistema de Model Cards Morchella

**Hola** 👋 Estás en el directorio del Sistema de Model Cards Automático para tu proyecto de detección de Morchella.

---

## ⚡ Empezar en 3 Pasos (5 minutos)

### Paso 1: Verifica que todo funcione
```bash
python verify_model_cards_setup.py
```

### Paso 2: Lee el Quick Start
```bash
cat QUICKSTART_MODEL_CARDS.md
```

### Paso 3: Entrena un modelo
```bash
docker-compose exec api python src/train.py --model efficientnet
```

**¡Listo!** Tu Model Card se generó automáticamente en MLflow 🎉

---

## 📚 ¿Por dónde empiezo?

### 🎯 "Tengo 5 minutos"
👉 Lee: `QUICKSTART_MODEL_CARDS.md`

### 🎯 "Tengo 5 minutos y quiero entender TODO"
👉 Lee: `SUMMARY_MODEL_CARDS.md`

### 🎯 "Necesito comandos rápidos"
👉 Lee: `QUICK_REFERENCE.md`

### 🎯 "Quiero entender cómo funciona"
👉 Lee: `ARCHITECTURE.md`

### 🎯 "Tengo dudas"
👉 Lee: `FAQ.md`

### 🎯 "No sé nada, guíame"
👉 Lee: `MODEL_CARDS_README.md`

---

## 🗂️ Estructura Rápida

```
Este directorio contiene:

📁 src/                          → Código Python
   ├─ model_card_mlflow_logger.py   ⭐ Core del sistema
   ├─ train_model_efficientnet.py   ✅ Entrena + genera docs
   ├─ train_model_mobilenet.py      ✅ Entrena + genera docs
   └─ ...

📁 model_cards/                  → Documentación y generados
   ├─ model_card_*.qmd             ✅ Documentos fuente
   ├─ model_card_*.html            ✅ Documentos web
   ├─ model_card_*.pdf             ✅ Documentos PDF
   └─ README.md                     📖 Guía completa

📄 COMPLETED.md                  → Estado actual (este proyecto)
📄 QUICKSTART_MODEL_CARDS.md     → 5 minutos para empezar
📄 SUMMARY_MODEL_CARDS.md        → Resumen ejecutivo
📄 QUICK_REFERENCE.md            → Comandos rápidos
📄 ARCHITECTURE.md               → Cómo funciona
📄 DEPLOY_CHECKLIST.md           → Verificación
📄 FAQ.md                        → Preguntas frecuentes
📄 INDEX.md                      → Índice de documentación
```

---

## ✨ ¿Qué es esto?

Un **sistema que automáticamente genera documentación profesional** cada vez que entrenan un modelo:

```
Entrenas modelo → Se genera documentación → Se sube a MLflow
                       (automático)          (automático)
```

La documentación tiene **3 formatos**:
- 📄 **QMD** (fuente, editable)
- 📊 **HTML** (web, bonito)
- 📑 **PDF** (compartible, universal)

---

## 🚀 Flujo Típico

```bash
# 1. Instalar (primera vez)
bash install_quarto.sh

# 2. Entrenar
docker-compose exec api python src/train.py --model efficientnet

# 3. Ver resultados
# Abre: http://localhost:5001
# → Experiments → morchella_detection → [tu run] → Artifacts → model_cards/
# → Verás .qmd, .html, .pdf
```

---

## 📋 Documentación Principal

| Documento | Para | Tiempo |
|-----------|------|--------|
| `QUICKSTART_MODEL_CARDS.md` | Empezar YA | ⚡ 5 min |
| `SUMMARY_MODEL_CARDS.md` | Resumen rápido | 🎯 5 min |
| `QUICK_REFERENCE.md` | Comandos copy-paste | 📌 5 min |
| `MODEL_CARDS_README.md` | Entender el sistema | 📘 5 min |
| `model_cards/README.md` | Guía completa | 📚 30 min |
| `ARCHITECTURE.md` | Cómo funciona | 🏗️ 15 min |
| `FAQ.md` | Preguntas frecuentes | ❓ Variable |
| `DEPLOY_CHECKLIST.md` | Antes de usar en prod | ✅ 15 min |
| `INDEX.md` | Índice general | 📍 Referencia |

---

## 🎯 Ahora Qué?

### Opción A: Empezar inmediatamente (recomendado)
```bash
# 1. Verificar
python verify_model_cards_setup.py

# 2. Entrenar
docker-compose exec api python src/train.py --model efficientnet

# 3. Ver resultados en MLflow
http://localhost:5001
```

### Opción B: Leer primero (prudente)
```bash
# Lee:
cat QUICKSTART_MODEL_CARDS.md

# Luego:
python verify_model_cards_setup.py
docker-compose exec api python src/train.py --model efficientnet
```

### Opción C: Entender a fondo (completo)
```bash
# Lee todos:
cat SUMMARY_MODEL_CARDS.md
cat ARCHITECTURE.md
cat model_cards/README.md

# Luego entrena:
docker-compose exec api python src/train.py --model efficientnet
```

---

## ❓ Preguntas Frecuentes Rápidas

**P: ¿Qué necesito instalar?**
A: Solo Quarto: `bash install_quarto.sh`

**P: ¿Es automático?**
A: 100% automático. Entrenas → Se genera todo.

**P: ¿Necesito hacer algo especial?**
A: No. El sistema está integrado en los scripts de entrenamiento.

**P: ¿Dónde están los documentos?**
A: En MLflow (localhost:5001) → Artifacts → model_cards/

**P: ¿Puedo editar un documento?**
A: Sí. Descarga .qmd, edita, y recompila.

**P: ¿Más dudas?**
A: Lee `FAQ.md` - tiene 30+ preguntas respondidas.

---

## 📞 Soporte Rápido

| Problema | Solución |
|----------|----------|
| "¿Cómo empiezo?" | Ejecuta: `python verify_model_cards_setup.py` |
| "¿No funciona?" | Lee: `FAQ.md` → Troubleshooting |
| "¿Comandos?" | Lee: `QUICK_REFERENCE.md` |
| "¿Cómo funciona?" | Lee: `ARCHITECTURE.md` |
| "¿Dudas?" | Lee: `FAQ.md` |

---

## 🎉 Listo para Empezar

**Próximo paso:** Abre `QUICKSTART_MODEL_CARDS.md` o ejecuta:

```bash
python verify_model_cards_setup.py
```

---

*Bienvenido al Sistema de Model Cards 🎉*  
*¡Documenta tus modelos automáticamente!* 📊

---

**Estado:** ✅ Totalmente operacional  
**Versión:** 1.0  
**Fecha:** 15 de diciembre de 2025
