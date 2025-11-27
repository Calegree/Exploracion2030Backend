from flask import request
from flask_restful import Resource
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
from flasgger import swag_from
from datetime import datetime
import os
import io
import numpy as np
import mlflow

# usar importaciones relativas dentro del paquete 'src'
from ..extensions import db
from ..models import PredictionCounts, ActiveModel

# configuración por defecto
mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'sqlite:///mlflow.db'))

# simple cache para modelo cargado
class ModelLoader:
    _model = None
    _path = None

    @classmethod
    def load_local_model(cls, path):
        if not path:
            return None
        if cls._model is None or cls._path != path:
            cls._model = load_model(path)
            cls._path = path
        return cls._model

def _ensure_prediction_counts():
    pc = PredictionCounts.query.order_by(PredictionCounts.id.desc()).first()
    if pc is None:
        pc = PredictionCounts(morchella=0, no_morchella=0)
        db.session.add(pc)
        db.session.commit()
    return pc

def _increment_prediction_count(is_morchella: bool):
    try:
        pc = _ensure_prediction_counts()
        if is_morchella:
            pc.morchella = (pc.morchella or 0) + 1
        else:
            pc.no_morchella = (pc.no_morchella or 0) + 1
        db.session.commit()
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass

class Prediction(Resource):
    def __init__(self):
        pass

    @swag_from(os.path.join(os.path.dirname(__file__), '..', 'flasgger', 'prediction.yml'))
    def post(self):
        """
        Recibe una imagen (form-data key 'imagen'), hace predicción y actualiza contadores en BD.
        """
        if 'imagen' not in request.files:
            return {'error': 'campo "imagen" no enviado'}, 400
        img_file = request.files['imagen']
        try:
            img = Image.open(img_file.stream).convert('RGB')
            img = img.resize((224, 224))
            arr = np.array(img) / 255.0
            arr = np.expand_dims(arr, axis=0).astype(np.float32)
        except Exception as e:
            return {'error': 'imagen inválida', 'detail': str(e)}, 400

        # intentar cargar modelo local activo
        active = ActiveModel.query.order_by(ActiveModel.id.desc()).first()
        model = None
        model_source = None
        if active and active.local_path and os.path.exists(active.local_path):
            model = ModelLoader.load_local_model(active.local_path)
            model_source = 'local'
        else:
            # intentar cargar desde MLflow si run_id existe
            if active and active.run_id:
                try:
                    model_uri = f"runs:/{active.run_id}/model"
                    model = mlflow.keras.load_model(model_uri)
                    model_source = f"mlflow_run:{active.run_id}"
                except Exception:
                    model = None

        if model is None:
            return {'error': 'no se encontró modelo activo'}, 500

        try:
            pred = model.predict(arr, verbose=0)
            prob = float(pred[0][0]) if hasattr(pred[0], '__len__') else float(pred[0])
            is_morchella = prob >= 0.5
            label = "Morchella" if is_morchella else "No Morchella"

            # actualizar contadores
            _increment_prediction_count(is_morchella)

            return {
                'model_source': model_source,
                'prediction': label,
                'confidence': prob
            }
        except Exception as e:
            return {'error': 'falló la predicción', 'detail': str(e)}, 500

    def get(self):
        """
        Endpoint para verificar el estado del modelo
        """
        return self.get_model_status(), 200

    def put(self):
        """
        Endpoint para recargar el modelo
        """
        print("🔄 Recargando modelo...")
        self.load_model()
        return self.get_model_status(), 200
