from flask import request
from flask_restful import Resource
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
import numpy as np
import io
import os

# Carga el modelo una sola vez
MODEL_PATH = os.path.join("model", "model_morchella.h5")
if os.path.exists(MODEL_PATH):
    model = load_model(MODEL_PATH)
else:
    model = None

class Prediction(Resource):
    def post(self):
        if 'imagen' not in request.files:
            return {'error': 'No se envió ninguna imagen'}, 400

        archivo = request.files['imagen']

        try:
            # Convertir imagen a formato compatible con Keras
            imagen = Image.open(archivo).convert('RGB')
            imagen = imagen.resize((224, 224))  # usa el tamaño que usaste para entrenar
            imagen_array = img_to_array(imagen) / 255.0
            imagen_array = np.expand_dims(imagen_array, axwis=0)

            prediccion = model.predict(imagen_array)[0][0]
            resultado = "Es morchella" if prediccion > 0.5 else "No es morchella"

            return {
                'resultado': resultado,
                'confianza': round(float(prediccion), 3)
            }, 200

        except Exception as e:
            return {'error': str(e)}, 500
