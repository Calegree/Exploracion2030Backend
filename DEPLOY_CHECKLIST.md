# ✅ Pre-Deploy Checklist - Model Cards System

Antes de usar el sistema en producción, verifica todos estos items.

---

## 🔧 Requisitos Previos

- [ ] Python 3.8+
- [ ] Docker y Docker Compose instalados
- [ ] MLflow instalado: `pip list | grep mlflow`
- [ ] TensorFlow 2.x instalado
- [ ] 5 GB de disco disponible (para entrenamientos + artifacts)

---

## 📦 Instalación de Dependencias

### Opción 1: Instalar Todo Automáticamente
```bash
# Ir al directorio del proyecto
cd /home/charles-darwin/Morchellapp/Exploracion2030Backend

# Instalar Quarto automáticamente
bash install_quarto.sh

# Esperar a que termine
```

### Opción 2: Instalación Manual
```bash
# Actualizar repositorios
sudo apt-get update

# Instalar Quarto
sudo apt-get install quarto

# Instalar Pandoc
sudo apt-get install pandoc

# Verificar instalaciones
quarto --version
pandoc --version
```

- [ ] Quarto instalado
- [ ] Pandoc instalado
- [ ] Versión de Quarto >= 1.3

---

## 🧪 Verificación del Sistema

```bash
# Ejecutar verificador completo
python verify_model_cards_setup.py
```

Resultado esperado:
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

**Checklist:**
- [ ] Verificador ejecutado sin errores
- [ ] Todos los componentes detectados
- [ ] Ninguna advertencia (⚠️)

---

## 🐳 Docker Compose

### Verificar Configuración
```bash
# Ver servicios
cat docker-compose.yml | grep "services:" -A 20

# Verificar puertos
# - MLflow: 5001
# - MinIO: 9001
# - API: 5000
# - PostgreSQL: 5432
```

- [ ] docker-compose.yml existe
- [ ] Puertos: 5001 (MLflow), 9001 (MinIO), 5000 (API) disponibles
- [ ] Volúmenes configurados (mlruns/, minio-data/, pgdata/)

### Iniciar Servicios
```bash
# Ir al directorio root
cd /home/charles-darwin/Morchellapp/Exploracion2030Backend

# Iniciar todos los servicios
docker-compose up -d

# Esperar 10 segundos a que levanten
sleep 10

# Verificar que están activos
docker-compose ps
```

Resultado esperado:
```
NAME                 STATUS
mlflow               Up 10 seconds
minio                Up 10 seconds
postgres             Up 10 seconds
api                  Up 10 seconds
```

- [ ] Todos los servicios: UP
- [ ] Sin errores en `docker-compose logs`

### Verificar Conectividad
```bash
# MLflow disponible
curl http://localhost:5001/health

# MinIO disponible
curl http://localhost:9001/minio/health/live

# API disponible
curl http://localhost:5000/health
```

- [ ] MLflow responde en http://localhost:5001
- [ ] MinIO responde en http://localhost:9001
- [ ] API responde en http://localhost:5000

---

## 📁 Estructura de Directorios

Verificar que existan estos directorios:

```bash
cd /home/charles-darwin/Morchellapp/Exploracion2030Backend

# Verificar directorios clave
[ -d "src" ] && echo "✅ src/" || echo "❌ src/ FALTA"
[ -d "model_cards" ] && echo "✅ model_cards/" || echo "❌ model_cards/ FALTA"
[ -d "mlruns" ] && echo "✅ mlruns/" || echo "❌ mlruns/ FALTA"
[ -d "minio-data" ] && echo "✅ minio-data/" || echo "❌ minio-data/ FALTA"
```

- [ ] Directorio `src/` existe
- [ ] Directorio `model_cards/` existe
- [ ] Directorio `mlruns/` existe (creado por MLflow)
- [ ] Directorio `minio-data/` existe (creado por MinIO)

---

## 📄 Archivos Clave Presentes

```bash
# Verificar Python modules
ls -la src/model_card_*.py | wc -l
# Debería listar >= 4 archivos

# Verificar documentación
ls -la model_cards/*.md | wc -l
# Debería listar >= 4 archivos

# Verificar scripts de entrenamiento
[ -f "src/train_model_efficientnet.py" ] && echo "✅" || echo "❌"
[ -f "src/train_model_mobilenet.py" ] && echo "✅" || echo "❌"
```

- [ ] `src/model_card_mlflow_logger.py` existe
- [ ] `src/model_card_generator.py` existe
- [ ] `src/model_card_utils.py` existe
- [ ] `src/model_card_config.py` existe
- [ ] `src/train_model_efficientnet.py` existe
- [ ] `src/train_model_mobilenet.py` existe
- [ ] `model_cards/README.md` existe
- [ ] `model_cards/MODEL_CARDS_FORMATS.md` existe

---

## 🔌 Verificar Integraciones

### MLflow Integration
```bash
python -c "
import mlflow
print(f'MLflow version: {mlflow.__version__}')
print(f'Tracking URI: {mlflow.get_tracking_uri()}')
"
```

- [ ] MLflow importa correctamente
- [ ] Tracking URI es: `http://localhost:5001`

### Quarto Integration
```bash
quarto --version
# Debería mostrar: Quarto X.X.X

quarto check
# Debería mostrar: ✅ Quarto checks out
```

- [ ] Quarto versión >= 1.3
- [ ] Quarto check pasa sin errores

### Pandoc Integration
```bash
pandoc --version
# Debería mostrar: pandoc X.X.X

# Verificar que puede compilar
echo "# Test" | pandoc -f markdown -t html > /tmp/test.html
```

- [ ] Pandoc versión disponible
- [ ] Pandoc puede compilar documentos

---

## 🧪 Test de Generación (Rápido)

```bash
# Test 1: Importar módulos sin errores
python -c "
from src.model_card_mlflow_logger import ModelCardMLflowLogger
from src.model_card_generator import ModelCardGenerator
print('✅ Módulos importan correctamente')
"

# Test 2: Verificar conectividad con MLflow
python -c "
from mlflow.tracking import MlflowClient
client = MlflowClient()
experiments = client.search_experiments()
print(f'✅ MLflow conectado. Experimentos: {len(experiments)}')
"

# Test 3: Verificar que puede acceder a datasets
python -c "
import os
if os.path.exists('src/dataset'):
    files = os.listdir('src/dataset')
    print(f'✅ Dataset accesible. Carpetas: {files}')
else:
    print('❌ Dataset no encontrado')
"
```

- [ ] Módulos importan sin errores
- [ ] MLflow accesible
- [ ] Datasets encontrados

---

## 🚀 Primer Entrenamiento (Full Test)

```bash
# Ir al directorio del proyecto
cd /home/charles-darwin/Morchellapp/Exploracion2030Backend

# Ensure docker compose is up
docker-compose ps

# Entrenar modelo pequeño (test rápido)
# Nota: Tarda 5-15 minutos
docker-compose exec api python src/train.py --model efficientnet
```

Verificar output:
```
✅ Training started...
✅ Model trained successfully
✅ Saving model...
✅ Generating Model Card...
✅ Model Card QMD generated
✅ Model Card HTML compiled
✅ Model Card PDF compiled
✅ All artifacts uploaded to MLflow
✅ Training complete!
```

- [ ] Entrenamiento completa sin errores
- [ ] Se genera archivo .qmd
- [ ] Se genera archivo .html (si Quarto disponible)
- [ ] Se genera archivo .pdf (si Pandoc disponible)
- [ ] Se suben a MLflow exitosamente

---

## 📊 Verificar Artifacts en MLflow

```bash
# Abrir MLflow UI
# http://localhost:5001

# Navegar a:
# Experiments → morchella_detection → [latest run]
# Section: Artifacts
# Folder: model_cards/
```

Debería ver:
- ✅ `model_card_*.qmd` (fuente)
- ✅ `model_card_*.html` (web)
- ✅ `model_card_*.pdf` (documento)

- [ ] Artifacts accesibles en MLflow UI
- [ ] Los 3 formatos presentes
- [ ] Tamaños razonables (QMD < 100KB, HTML < 500KB, PDF < 5MB)

---

## 🔍 Validación de Contenido

### Validar QMD
```bash
# El archivo debe tener al menos 13 secciones
grep "^##" model_cards/model_card_*.qmd | wc -l
# Debería mostrar: >= 13
```

- [ ] QMD tiene al menos 13 secciones
- [ ] Contiene métricas (accuracy, loss, etc.)
- [ ] Contiene información del modelo

### Validar HTML
```bash
# El archivo debe ser válido HTML
file model_cards/model_card_*.html | grep -i html
# Debería mostrar: "text/html"
```

- [ ] HTML es válido
- [ ] Se puede abrir en navegador
- [ ] Estilos CSS aplicados (no blanco y negro)

### Validar PDF
```bash
# El archivo debe ser PDF válido
file model_cards/model_card_*.pdf | grep -i pdf
# Debería mostrar: "PDF document"
```

- [ ] PDF es válido
- [ ] Se puede abrir en lector PDF
- [ ] Contenido legible

---

## 🔐 Seguridad Básica

- [ ] MLflow configurado sin autenticación en dev (OK)
- [ ] MinIO con credenciales en docker-compose
- [ ] Volúmenes Docker con permisos adecuados
- [ ] No exponer credenciales en code
- [ ] Datasets privados en src/dataset/ (no en repo)

---

## 📈 Performance Baseline

```bash
# Medir tiempo de generación
time python -c "
from src.model_card_mlflow_logger import log_model_card_automatic
# Usar run_id real
log_model_card_automatic('RUN_ID', 'EfficientNetB0', 'src/dataset')
"
```

- [ ] Generación QMD < 2 segundos
- [ ] Compilación HTML < 20 segundos
- [ ] Compilación PDF < 30 segundos
- [ ] Total < 1 minuto

---

## 📚 Documentación Disponible

Verificar que puedas acceder a:

```bash
# Referencia rápida
cat QUICK_REFERENCE.md > /dev/null && echo "✅" || echo "❌"

# Resumen
cat SUMMARY_MODEL_CARDS.md > /dev/null && echo "✅" || echo "❌"

# Quick start
cat QUICKSTART_MODEL_CARDS.md > /dev/null && echo "✅" || echo "❌"

# Formatos
cat model_cards/MODEL_CARDS_FORMATS.md > /dev/null && echo "✅" || echo "❌"

# Testing
cat model_cards/TESTING_MODEL_CARDS.md > /dev/null && echo "✅" || echo "❌"

# Acceso
cat model_cards/ACCESSING_MODEL_CARDS.md > /dev/null && echo "✅" || echo "❌"

# Arquitectura
cat ARCHITECTURE.md > /dev/null && echo "✅" || echo "❌"
```

- [ ] QUICK_REFERENCE.md existe
- [ ] SUMMARY_MODEL_CARDS.md existe
- [ ] QUICKSTART_MODEL_CARDS.md existe
- [ ] model_cards/MODEL_CARDS_FORMATS.md existe
- [ ] model_cards/TESTING_MODEL_CARDS.md existe
- [ ] model_cards/ACCESSING_MODEL_CARDS.md existe
- [ ] ARCHITECTURE.md existe

---

## 🎯 Pre-Deploy Final Checklist

### Infraestructura
- [ ] Python 3.8+ instalado
- [ ] Docker/Docker Compose funcional
- [ ] MLflow accesible (localhost:5001)
- [ ] MinIO accesible (localhost:9001)
- [ ] Quarto instalado
- [ ] Pandoc instalado

### Código
- [ ] Todos los módulos presentes
- [ ] Modificaciones en scripts de entrenamiento aplicadas
- [ ] Sin errores de sintaxis
- [ ] Imports funcionan

### Datos
- [ ] Datasets presentes en src/dataset/
- [ ] Directorios writable (mlruns/, minio-data/)
- [ ] Espacio en disco disponible

### Testing
- [ ] verify_model_cards_setup.py pasa
- [ ] Primer entrenamiento completa
- [ ] Artifacts aparecen en MLflow
- [ ] Los 3 formatos se generan

### Documentación
- [ ] Documentación completa presente
- [ ] Instrucciones claras
- [ ] Ejemplos funcionales

---

## 🚀 Go/No-Go Decision

**GO** si:
- ✅ Todos los checks anteriores pasan
- ✅ MLflow muestra Model Cards
- ✅ Los 3 formatos se generan
- ✅ Sin errores en logs

**NO-GO** si:
- ❌ Falta algún componente
- ❌ Errores en docker-compose
- ❌ Entrenamiento falla
- ❌ No aparecen artifacts en MLflow

---

## 📞 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| MLflow no responde | `docker-compose restart mlflow` |
| Quarto no encontrado | `bash install_quarto.sh` |
| Errores de permisos | `chmod -R 755 mlruns/ minio-data/` |
| Artifacts no aparecen | `docker-compose logs api \| tail -50` |
| Compilación lenta | Normal (20-30s primera vez) |

---

## ✅ Después del Deploy

1. **Primer mes:**
   - Monitor logs regularmente
   - Verificar que artifacts se guardan
   - Revisar tamaños de almacenamiento

2. **Mantenimiento:**
   - Limpiar artifacts antiguos (>6 meses)
   - Actualizar Quarto/Pandoc regularmente
   - Backup de MLflow database

3. **Escalado:**
   - Si múltiples usuarios, usar MLflow Server con DB real
   - Si muchísimos artifacts, aumentar MinIO storage
   - Considerar S3 real en lugar de MinIO local

---

*Última actualización: 15 de diciembre de 2025*  
*Estado: ✅ READY FOR PRODUCTION*
