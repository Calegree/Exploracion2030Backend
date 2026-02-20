# MorchellApp - Backend (Resumen)

## ✅ Información clave
- **API + Flasgger (docs endpoints):** http://localhost:5000/apidocs/#/
- **MLflow UI:** http://localhost:5001
- **MinIO Console (S3):** http://localhost:9001

## 🍄 Hongos reconocidos (según endpoints de descarga)
Esta lista corresponde a los hongos usados en los datasets descargables (ver en Flasgger):

**Morchella (positivos):**
- Morchella andinensis
- Morchella aysenina
- Morchella tridentina
- Morchella esculenta
- Morchella spp (sin ID específico)

**No-Morchella (negativos):**
- Ascomicetes: Gyromitra, Helvella, Verpa
- Agaricales: Amanita, Agaricus
- Boletus patagónicos: Boletus, Suillus, Lactarius
- Políporos: Trametes, Ganoderma, Fomes
- Gasteroides: Lycoperdon, Calvatia, Phallus

## 🧪 Crear entorno virtual (venv)

### Windows
```bash
py -3.10 -m venv .venv310
.venv310\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Linux
```bash
python3.10 -m venv .venv310
source .venv310/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## 🐳 Levantar infraestructura (Docker)
```bash
docker compose up -d
```

## 🚀 Ejecutar la API (sin Docker)
```bash
python -m src.app
```

## 🧠 Entrenar modelos (comandos variables)

### Opción recomendada (script unificado)
```bash
# MobileNetV2 (ligero y rápido)
docker-compose exec api python src/train.py --model mobilenet

# EfficientNetB0 (mayor precisión)
docker-compose exec api python src/train.py --model efficientnet

# Entrenar ambos y comparar
docker-compose exec api python src/train.py --model both --compare
```

### Scripts individuales
```bash
docker-compose exec api python src/train_model_mobilenet.py
docker-compose exec api python src/train_model_efficientnet.py
docker-compose exec api python src/compare_models.py
```

## 📦 Descarga de datasets (endpoints)
```bash
curl -X POST http://localhost:5000/download/balanced_650
curl -X POST http://localhost:5000/download/balanced_600
curl -X POST http://localhost:5000/download/balanced_500
curl -X POST http://localhost:5000/download/fungis
curl -X POST http://localhost:5000/download/fungis2
```
⚠️ Estos endpoints sobrescriben la carpeta src/dataset/.

## 🔎 Accesos rápidos
- Flasgger (docs endpoints): http://localhost:5000/apidocs/#/
- MLflow UI: http://localhost:5001
- MinIO Console: http://localhost:9001

## 📚 Referencias
- Entrenamiento: [src/README_TRAINING.md](src/README_TRAINING.md)
- Model Cards: [model_cards/README.md](model_cards/README.md)
