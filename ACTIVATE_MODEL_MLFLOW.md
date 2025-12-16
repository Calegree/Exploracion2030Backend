# 🎯 Guía Rápida: Activar Modelos desde MLflow

## ✅ Nuevo Endpoint Creado

**POST** `/upload/model/{run_id}`

Activa un modelo entrenado directamente desde MLflow/MinIO sin necesidad de descargarlo.

---

## 🚀 Uso Rápido

### 1. Activar tu modelo EfficientNetB0

```bash
# Activar el modelo con tu run_id
curl -X POST http://localhost:5000/upload/model/f8b433193fcd4f6c91c632f83423ec5d

# O con docker-compose
docker-compose exec api curl -X POST http://localhost:5000/upload/model/f8b433193fcd4f6c91c632f83423ec5d
```

### 2. Verificar modelo activo

```bash
curl http://localhost:5000/upload/active
```

### 3. Hacer una predicción

```bash
curl -X POST -F "imagen=@tu_imagen.jpg" http://localhost:5000/predict
```

---

## 🔧 Script de Prueba

Usa el script de prueba para listar y activar modelos:

```bash
# Listar todos los modelos disponibles en MLflow
python3 test_activate_mlflow_model.py

# Activar un modelo específico
python3 test_activate_mlflow_model.py f8b433193fcd4f6c91c632f83423ec5d

# Desde docker
docker-compose exec api python test_activate_mlflow_model.py
```

---

## 📋 ¿Qué hace el endpoint?

1. **Busca el run** en MLflow usando el `run_id`
2. **Verifica artifacts** del modelo (.keras) en MinIO
3. **Valida** que el modelo sea cargable
4. **Registra** en la base de datos
5. **Activa** para que se use en predicciones

---

## ✅ Respuesta Exitosa

```json
{
  "status": "success",
  "message": "Modelo model_morchella_efficientnet.keras activado desde MLflow",
  "model": {
    "name": "model_morchella_efficientnet.keras",
    "run_id": "f8b433193fcd4f6c91c632f83423ec5d",
    "model_uri": "runs:/f8b433193fcd4f6c91c632f83423ec5d/model",
    "size": 45432832,
    "model_type": "EfficientNetB0",
    "input_shape": "(None, 224, 224, 3)",
    "output_shape": "(None, 1)"
  },
  "metrics": {
    "val_accuracy": 0.9269,
    "val_loss": 0.2301,
    "val_precision": 0.9237,
    "val_recall": 0.9308
  }
}
```

---

## 🎯 Ventajas

- ✅ **Sin descargas**: Acceso directo a MinIO
- ✅ **Validación automática**: Verifica que el modelo funcione
- ✅ **Métricas incluidas**: Retorna info del entrenamiento
- ✅ **Inmediato**: Listo para predicciones al instante

---

## 📚 Documentación Swagger

Accede a la documentación completa en:
http://localhost:5000/apidocs/#/Model%20Upload%20%26%20Activation/post_upload_model__run_id_

---

## 🔍 Troubleshooting

### Error: "Run no encontrado"
```bash
# Verifica que el run_id existe
docker-compose exec mlflow mlflow runs list --experiment-id 1
```

### Error: "No se encontró archivo .keras"
El run no tiene un modelo guardado en los artifacts. Asegúrate de que el entrenamiento haya completado correctamente.

### Error: "Error al cargar el modelo"
Verifica la conectividad con MinIO:
```bash
docker-compose ps minio
docker-compose logs minio
```

---

## 📖 Archivos Modificados/Creados

1. ✅ `src/resources/upload.py` - Nuevo endpoint agregado
2. ✅ `src/flasgger/upload_model_from_mlflow.yml` - Documentación Swagger
3. ✅ `test_activate_mlflow_model.py` - Script de prueba
4. ✅ `README.md` - Documentación actualizada
5. ✅ `ACTIVATE_MODEL_MLFLOW.md` - Esta guía

---

## 🎉 ¡Listo!

Tu modelo EfficientNetB0 puede activarse con:

```bash
curl -X POST http://localhost:5000/upload/model/f8b433193fcd4f6c91c632f83423ec5d
```

Y estará inmediatamente disponible para predicciones en `/predict` 🚀
