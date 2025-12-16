#Hongos Reconocidos
Morchella rufobrunnea
Morchella andinensis
Morchella tridentina
Morchella Aysenina 

#Documentación
http://localhost:5000/apidocs/#/

#Crear enviroment proyecto Python
py -3 -m venv .venv

linux
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-distutils

Crear venv y preparar pip:
python3.10 -m venv .venv310
.venv310/bin/python -m pip install --upgrade pip setuptools wheel

Instalar paquetes mínimos + mlflow:
.venv310/bin/pip install Flask Flask-RESTful flasgger mlflow flask-cors

Instalar tensorflow (necesario para resources/prediction):
.venv310/bin/pip install tensorflow==2.19.0

#Activar el enviroment 
windows .venv\Scripts\activate
linux source .venv/bin/activate
#Dependencias
pip install -r requirements.txt


#Correr la API para hacer predicciones
python src/app.py

#Actualizar dependencias
pip freeze >> requirements.txt

#Corre el pipeline para crear el modelo
python run_training_pipeline.py

#O hazlo manual
python clean_mlflow.py
python verify_mlflow_setup.py
python train_model.py
python start_mlflow_ui.py

#
python setup_model_for_prediction.py
python app.py
curl http://localhost:5000/predict
curl -X POST -F "imagen=@tu_imagen.jpg" http://localhost:5000/predict

tener instalado python 3.10 
para correr la api en windows 
##crea el env
py -3.10 -m venv .venv310
##corre el env y la app
.venv\Scripts\activate 
##instala las dependencias (como npm i pero python)
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt



para correr la api en linux 
##crea el env
python3 -m venv .venv
##corre el env y la app
source .venv/bin/activate
##instala las depedencias (npm i pero python)
python -m pip install -r requirements.txt
pip install -r requirements.txt
python -m src.app

para correr MLFlow UI en el puerto 5001

python -m mlflow ui --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5001


##Para ver cual es la URI actual que conecta mlflow con la api
echo $MLFLOW_TRACKING_URI
##Para regular la URI que conecta mlflow con la api 
export MLFLOW_TRACKING_URI=http://127.0.0.1:5001


##Para entrenar un modelo

### Opción 1: Script unificado (Recomendado)
```bash
# Entrenar con MobileNetV2 (ligero y rápido)
docker-compose exec api python src/train.py --model mobilenet

# Entrenar con EfficientNetB0 (mayor precisión)
docker-compose exec api python src/train.py --model efficientnet

# Entrenar ambos modelos y comparar
docker-compose exec api python src/train.py --model both --compare
```

### Opción 2: Scripts individuales
```bash
# MobileNetV2
docker-compose exec api python src/train_model_mobilenet.py

# EfficientNetB0
docker-compose exec api python src/train_model_efficientnet.py

# Comparar resultados
docker-compose exec api python src/compare_models.py
```

### Opción 3: Entrenamiento manual desde contenedor
```bash
docker compose exec -T api bash -lc "cd /app/src && python train_model_mobilenet.py"
# o
docker-compose exec api python -u src/train_model_efficientnet.py
```

📖 **Documentación completa:** Ver `src/README_TRAINING.md`


pip install -r src/requirements-linux.txt

pip install -r src/requirements.txt

---

## 📦 Dataset Download - Descarga de Datasets

La API incluye endpoints para descargar datasets balanceados desde iNaturalist:

### Endpoints Disponibles

#### `/download/balanced_650` - **Recomendado para producción**
Dataset balanceado 1300 imágenes (650 + 650) con alta diversidad:

**Morchella (650 fotos):**
- 25 Morchella andinensis
- 6 Morchella aysenina  
- 100 Morchella tridentina
- 100 Morchella esculenta
- 419 Morchella spp (sin ID específico)

**No-Morchella (650 fotos) - 5 grupos diversos:**
- **Ascomicetes** (330): Gyromitra, Helvella, Verpa
- **Agaricales** (160): Amanita, Agaricus
- **Boletus patagónicos** (90): Boletus, Suillus, Lactarius
- **Políporos** (40): Trametes, Ganoderma, Fomes
- **Gasteroides** (30): Lycoperdon, Calvatia, Phallus

```bash
# Descargar dataset completo (sobrescribe dataset actual)
curl -X POST http://localhost:5000/download/balanced_650

# Con docker-compose
docker-compose exec api curl -X POST http://localhost:5000/download/balanced_650
```

#### Otros endpoints disponibles
- `/download/balanced_600` - Dataset 1000 imágenes (600 + 400)
- `/download/balanced_500` - Dataset 1000 imágenes (500 + 500)
- `/download/fungis` - Dataset básico
- `/download/fungis2` - Dataset alternativo

⚠️ **IMPORTANTE:** Todos los endpoints de descarga sobrescriben la carpeta `src/dataset/`

---

## 📋 Model Cards - Documentación Automática de Modelos

Cada modelo entrenado genera automáticamente un **Model Card en Quarto** con:
- Parámetros y arquitectura
- Métricas (accuracy, precision, recall, F1-score)
- Matriz de confusión y análisis de errores
- Dataset information
- Limitaciones y recomendaciones

### 🚀 Uso Rápido

```bash
# 1. Entrenar un modelo (genera Model Card automáticamente)
docker-compose exec api python src/train.py --model efficientnet

# 2. Ver modelos disponibles
python src/model_card_utils.py list

# 3. Compilar a HTML profesional
python src/model_card_utils.py compile-all

# 4. Crear documento comparativo
python src/model_card_utils.py compare

# 5. Abrir en navegador
python src/model_card_utils.py open model_cards/model_comparison.html
```

### 📚 Documentación Completa

Ver [`model_cards/README.md`](model_cards/README.md) para:
- Instalación de Quarto
- Guía completa de uso
- Ejemplos de workflows
- Personalización
- Troubleshooting

### 📊 Estructura de Resultados

```
model_cards/
├── model_card_EfficientNetB0_20251215_134500.qmd   ← Fuente (editable)
├── model_card_EfficientNetB0_20251215_134500.html  ← HTML compilado
├── model_card_MobileNetV2_20251215_141200.qmd
├── model_card_MobileNetV2_20251215_141200.html
├── model_comparison.qmd                              ← Comparativa
├── model_comparison.html
└── model-card-style.css                              ← Estilos
```

---



