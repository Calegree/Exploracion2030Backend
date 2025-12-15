# ❓ FAQ - Preguntas Frecuentes sobre Model Cards

Respuestas a las preguntas más comunes.

---

## 🚀 Instalación y Setup

### P: ¿Necesito instalar Quarto?
**R:** No es obligatorio, pero es **muy recomendado**:
- **Sin Quarto:** Solo se genera `.qmd` (fuente)
- **Con Quarto:** Se generan `.qmd` + `.html` + `.pdf`

👉 Instalar: `bash install_quarto.sh` (automático)

---

### P: ¿Y si no instalo Pandoc?
**R:** Sin Pandoc:
- ✅ Se genera `.qmd`
- ✅ Se genera `.html` (con Quarto)
- ❌ No se genera `.pdf`

Pandoc se necesita **solo para PDF**. Si no lo instalas, el sistema funciona igual, solo sin PDFs.

---

### P: ¿Cuánto espacio necesito en disco?
**R:** Depende del dataset y cantidad de entrenamientos:
- **Mínimo:** 2 GB (para un par de modelos)
- **Recomendado:** 10 GB (para múltiples entrenamientos)
- **Producción:** 50+ GB

Cada entrenamiento ocupa ~500 MB - 2 GB (modelo + artifacts)

---

### P: ¿Puedo usar esto en Windows/Mac?
**R:** Sí, pero con limitaciones:

**Windows:**
- ✅ Docker Desktop funciona
- ✅ MLflow funciona
- ⚠️ Quarto: Descargar de https://quarto.org/
- ⚠️ Pandoc: Descargar de https://pandoc.org/

**Mac:**
- ✅ Todo funciona igual
- ✅ Instalar con: `brew install quarto pandoc`

**Linux:**
- ✅ Todo funciona perfecto
- ✅ Instalar con: `sudo apt-get install quarto pandoc`

---

## 📊 Model Cards

### P: ¿Qué es una Model Card?
**R:** Un documento profesional que explica:
- Qué es tu modelo
- Cómo funciona
- Qué tan bien funciona (métricas)
- En qué se puede usar
- Qué limitaciones tiene
- Recomendaciones de mejora

Es como un "carnet de identidad" del modelo.

---

### P: ¿Por qué 3 formatos diferentes?
**R:** Porque cada uno sirve para algo diferente:

| Formato | Cuándo | Ventaja |
|---------|--------|---------|
| **QMD** | Editar | Archivo fuente, cambiar contenido |
| **HTML** | Ver en navegador | Bonito, con estilos, interactivo |
| **PDF** | Compartir/Imprimir | Universal, no requiere software |

---

### P: ¿Puedo editar una Model Card después?
**R:** Sí, de varias formas:

1. **Descargar `.qmd`** → Editar en VS Code → `quarto render` → Nuevos HTML/PDF
2. **Editar en Excel/Google Sheets** → Modificar valores en template
3. **Usar CLI:** `python src/model_card_utils.py compile-all`

---

### P: ¿Se pueden comparar dos Model Cards?
**R:** Sí:
```bash
# Generar tabla comparativa
python src/model_card_utils.py compare-all

# O descargar ambas en PDF y compararlas manualmente
```

---

## 🔄 Entrenamiento

### P: ¿El Model Card se genera automáticamente?
**R:** Sí, completamente automático:
1. Entrenas modelo
2. Al terminar → Se genera QMD automáticamente
3. Se compila a HTML (si Quarto disponible)
4. Se compila a PDF (si Pandoc disponible)
5. Se suben los 3 a MLflow automáticamente

**Cero pasos manuales.**

---

### P: ¿Qué pasa si falla la compilación de PDF?
**R:** El sistema es **tolerante a fallos**:
- ❌ PDF no se genera
- ✅ Pero .qmd y .html sí
- ✅ No se detiene el entrenamiento
- ℹ️ Ver logs para saber por qué

No es un error fatal, el sistema continúa.

---

### P: ¿Cuánto tiempo tarda entrenar + generar Model Card?
**R:** Aproximadamente:

| Actividad | Tiempo |
|-----------|--------|
| Entrenar modelo | 5-30 min |
| Generar QMD | < 1 seg |
| Compilar HTML | 5-10 seg |
| Compilar PDF | 10-20 seg |
| Subir a MLflow | < 1 seg |
| **Total overhead** | ~20-30 seg |

El overhead es mínimo.

---

## 📁 Almacenamiento

### P: ¿Dónde se guardan los Model Cards?
**R:** En **2 lugares simultáneamente**:

1. **MLflow** (localhost:5001)
   ```
   Experiments → morchella_detection → [run] → Artifacts → model_cards/
   ```

2. **MinIO S3** (localhost:9001)
   ```
   mlflow/ → [run_id] → artifacts → model_cards/
   ```

Ambos sincronizados automáticamente.

---

### P: ¿Puedo descargar desde Python?
**R:** Sí:
```python
from mlflow.tracking import MlflowClient

client = MlflowClient()
path = client.download_artifacts('RUN_ID', 'model_cards')
print(f'Descargado en: {path}')
```

---

### P: ¿Y si MLflow se cae?
**R:** Sin problema:
- ✅ Los archivos se generan localmente primero
- ✅ Se guardan en `mlruns/` y `model_cards/`
- ✅ Al reiniciar MLflow, se sincroniza automáticamente

---

### P: ¿Puedo acceder desde MinIO directamente?
**R:** Sí:
```bash
# Abrir MinIO UI
http://localhost:9001

# Credenciales (por defecto):
# Usuario: minioadmin
# Password: minioadmin

# Navegar a:
# mlflow/ → [run_id] → artifacts → model_cards/
```

---

## 🐛 Troubleshooting

### P: "No veo Model Cards en MLflow"
**R:** Verificar en este orden:

1. ¿MLflow está activo?
   ```bash
   docker-compose ps | grep mlflow
   ```

2. ¿El entrenamiento completó?
   ```bash
   docker-compose logs api | grep "Model Card"
   ```

3. ¿MLflow tiene datos?
   ```bash
   http://localhost:5001 → Experiments
   ```

---

### P: "El HTML no tiene estilos (está blanco y negro)"
**R:** Falta el CSS. Solución:

```bash
# Copiar CSS a la carpeta correcta
cp model_cards/model-card-style.css src/model_cards/

# O regenerar las Model Cards
python src/model_card_utils.py compile-all
```

---

### P: "Quarto compilation timeout"
**R:** La compilación tardó más de 120 segundos. Posibles causas:

1. Computadora lenta
2. Disco lento
3. RAM insuficiente

Solución:
- Aumentar timeout en `model_card_mlflow_logger.py`
- Cerrar otras aplicaciones
- Usar SSD más rápido

---

### P: "ERROR: mlflow.entities.RunNotFoundError"
**R:** El run_id no existe en MLflow.

Verificar:
```python
from mlflow.tracking import MlflowClient
client = MlflowClient()
runs = client.search_runs(exp_id=1)
for run in runs:
    print(run.info.run_id)
```

Usar un run_id válido.

---

## 🔐 Seguridad

### P: ¿Son seguros los Model Cards en MinIO?
**R:** Para desarrollo, sí:
- MLflow local (no expuesto)
- MinIO local (credenciales simples)
- Dentro de Docker Compose

**Para producción:**
- Usar S3 real con encryption
- Configurar auth en MLflow
- HTTPS en todos lados

---

### P: ¿Las credenciales de MinIO están seguras?
**R:** En desarrollo está bien. Las credenciales están en:
```
docker-compose.yml (credenciales por defecto)
```

**Para producción:**
- Generar credenciales nuevas
- Guardar en variables de entorno
- No commitear a Git

---

## 💾 Datos

### P: ¿Los Model Cards cuentan como datos sensibles?
**R:** No, son públicos:
- ✅ Se pueden compartir sin problema
- ✅ No contienen datos de entrenamiento
- ✅ Solo contienen métricas y configuración
- ✅ Se pueden commitear a Git (¿quizás?)

---

### P: ¿Puedo guardar Model Cards en GitHub?
**R:** Sí, pero con cuidado:

✅ Puedes guardar:
- `.qmd` (fuente, texto)
- `.pdf` (documento final)

⚠️ Mejor en:
- `.pdf` en GitHub
- `.qmd` en GitHub (opcional)
- No en GitHub: HTML (muy grande)

---

## 🎯 Casos de Uso

### P: "Necesito mostrar resultados a mi jefe"
**R:** Descargar PDF de MLflow y enviar por email:

```bash
# MLflow UI → Artifacts → model_cards/ → [.pdf] → Download
```

El PDF se ve profesional y se abre en cualquier lado.

---

### P: "Necesito guardar para auditoría/legal"
**R:** Descargar PDF:

```bash
# Guarda en carpeta del proyecto:
/home/charles-darwin/Morchellapp/Exploracion2030Backend/archived_models/
model_card_EfficientNetB0_[fecha].pdf
```

El PDF es permanente y no se pierde.

---

### P: "Necesito comparar 5 modelos"
**R:** Dos opciones:

1. **Tabla comparativa automática:**
   ```bash
   python src/model_card_utils.py compare-all
   ```

2. **Manual (más control):**
   - Descargar 5 PDFs
   - Abrir lado a lado
   - Comparar metrics

---

### P: "Necesito editar el template"
**R:** Editar el archivo:
```python
# Archivo: src/model_card_generator.py
# Función: _build_qmd_content()
# Ahí está el template de 13 secciones

# Cambiar y regenerar:
python src/model_card_utils.py compile-all
```

---

## 📈 Performance

### P: "¿Ralentiza el entrenamiento?"
**R:** Casi nada:
- Overhead: ~20-30 segundos
- El training tarda 5-30 minutos
- Overhead es < 1% del tiempo

Negligible.

---

### P: "¿Cuánta RAM usa?"
**R:** Muy poco:
- MLflow: ~200 MB
- Quarto: ~500 MB (durante compilación)
- Total: < 1 GB

Si tienes RAM para entrenar, tienes para Model Cards.

---

### P: "¿Se puede paralelizar?"
**R:** Sí, el sistema es paralelo:

```
QMD → HTML (paralelo)
QMD → PDF (paralelo)

No espera a que HTML termine para compilar PDF
```

Ambas compilaciones ocurren simultáneamente.

---

## 🔄 Versioning

### P: "¿Puedo guardar múltiples versiones?"
**R:** Sí, automáticamente:

```
Run 1: model_card_EfficientNetB0_20251215_100000.{qmd,html,pdf}
Run 2: model_card_EfficientNetB0_20251215_110000.{qmd,html,pdf}
Run 3: model_card_EfficientNetB0_20251215_120000.{qmd,html,pdf}
```

MLflow guarda histórico de **todos los runs**.

---

### P: "¿Cómo sé cuál es la mejor versión?"
**R:** Comparar métricas:

```python
from mlflow.tracking import MlflowClient
client = MlflowClient()

exp = client.get_experiment_by_name('morchella_detection')
runs = client.search_runs(
    exp.experiment_id,
    order_by=["metrics.accuracy DESC"]  # Ordena por accuracy
)

for run in runs[:5]:  # Top 5
    print(f"{run.info.run_id}: {run.data.metrics['accuracy']}")
```

---

## 📚 Documentación

### P: "Hay mucha documentación, ¿por dónde empiezo?"
**R:** Según tu tiempo:

- ⚡ **5 minutos:** [`QUICKSTART_MODEL_CARDS.md`](QUICKSTART_MODEL_CARDS.md)
- 🎯 **Resumen:** [`SUMMARY_MODEL_CARDS.md`](SUMMARY_MODEL_CARDS.md)
- 📖 **30 minutos:** [`MODEL_CARDS_IMPLEMENTATION_SUMMARY.md`](MODEL_CARDS_IMPLEMENTATION_SUMMARY.md)
- 📚 **Completo:** [`model_cards/README.md`](model_cards/README.md)

---

### P: "¿Qué documento debo leer para [X]?"

| Necesidad | Documento |
|-----------|-----------|
| Empezar rápido | QUICKSTART_MODEL_CARDS.md |
| Ver resumen | SUMMARY_MODEL_CARDS.md |
| Entender formatos | model_cards/MODEL_CARDS_FORMATS.md |
| Acceder a Model Cards | model_cards/ACCESSING_MODEL_CARDS.md |
| Hacer tests | model_cards/TESTING_MODEL_CARDS.md |
| Arquitectura | ARCHITECTURE.md |
| Comandos rápidos | QUICK_REFERENCE.md |
| Deploy | DEPLOY_CHECKLIST.md |

---

## 🎓 Aprendizaje

### P: "¿Dónde aprender más sobre Model Cards?"
**R:** Recursos:
- Google: https://modelcards.withgoogle.com/
- Paper: https://arxiv.org/abs/1810.03993
- Video: Buscar "Model Cards" en YouTube

---

### P: "¿Puedo personalizar el template?"
**R:** Sí, completamente editable:

```python
# Archivo: src/model_card_generator.py
# Función: _build_qmd_content()
# Añadir/quitar/cambiar secciones
```

El template es Markdown (fácil de editar).

---

## 🆘 Soporte

### P: "¿Dónde reporto un bug?"
**R:** Verificar:

1. ¿Está en el FAQ?
2. ¿Está en la documentación?
3. ¿Puedes reproducirlo?

Si pasas los 3:
- Abrir issue en GitHub (si aplica)
- O contactar al equipo de desarrollo

---

### P: "¿Hay ejemplos funcionales?"
**R:** Sí:
- `src/example_generate_model_card.py` - Ejemplo básico
- Scripts de training tienen integración - Ejemplos reales

---

## ✅ Conclusión

**¿Está todo claro?**

Si no encontraste tu pregunta:
1. Lee el documento correspondiente
2. Busca en los logs: `docker-compose logs api`
3. Ejecuta verificador: `python verify_model_cards_setup.py`

---

*Última actualización: 15 de diciembre de 2025*  
*¿Pregunta no resuelta? Consulta la documentación completa.*
