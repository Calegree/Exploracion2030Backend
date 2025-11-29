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
        archivo = request.files['imagen']

        # Validar filename y extensión
        if archivo.filename == '':
            return {'error': 'No se seleccionó ningún archivo'}, 400
        allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp'}
        if not ('.' in archivo.filename and archivo.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return {'error': 'Formato de imagen no válido'}, 400

        try:
            img = Image.open(archivo.stream).convert('RGB')
            img = img.resize((224, 224))
            arr = img_to_array(img) / 255.0
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
            raw_pred = model.predict(arr, verbose=0)
            # manejar distintas formas de salida
            if hasattr(raw_pred[0], '__len__'):
                prob = float(raw_pred[0][0])
            else:
                prob = float(raw_pred[0])
            es_morchella = prob > 0.5
            resultado = "Es morchella" if es_morchella else "No es morchella"
            confianza = prob if es_morchella else 1.0 - prob

            # Log mínimo en MLflow (opcional, anidado)
            try:
                with mlflow.start_run(nested=True):
                    mlflow.log_metric("prediction_confidence", float(round(confianza, 4)))
                    mlflow.log_param("prediction_class", resultado)
                    mlflow.log_param("input_filename", archivo.filename)
            except Exception:
                pass

            # actualizar contadores en BD
            _increment_prediction_count(es_morchella)

            return {
                'resultado': resultado,
                'confianza': round(float(confianza), 4),
                'probabilidad_morchella': round(float(prob), 4),
                'probabilidad_no_morchella': round(float(1.0 - prob), 4),
                'model_source': model_source
            }, 200
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
