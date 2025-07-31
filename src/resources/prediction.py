from flask import request
from flask_restful import Resource
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
import numpy as np
import io
import os
import mlflow
from flasgger import swag_from

# Configurar MLflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")

class Prediction(Resource):
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """
        Carga el modelo desde MLflow o desde archivo local
        """
        try:
            # Intentar cargar desde MLflow (último modelo registrado)
            try:
                logged_model = 'runs:/latest/model'
                self.model = mlflow.keras.load_model(logged_model)
                print("✅ Modelo cargado desde MLflow")
            except:
                # Si falla MLflow, cargar desde archivo local
                model_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'model_morchella.h5')
                if os.path.exists(model_path):
                    self.model = load_model(model_path)
                    print("✅ Modelo cargado desde archivo local")
                else:
                    print("❌ No se encontró el modelo")
                    self.model = None
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            self.model = None

    @swag_from('../flasgger/prediction.yml')
    def post(self):
        if self.model is None:
            return {'error': 'Modelo no disponible. Ejecuta el entrenamiento primero.'}, 500
            
        if 'imagen' not in request.files:
            return {'error': 'No se envió ninguna imagen'}, 400

        archivo = request.files['imagen']
        
        # Validar tipo de archivo
        if archivo.filename == '':
            return {'error': 'No se seleccionó ningún archivo'}, 400
            
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
        if not ('.' in archivo.filename and 
                archivo.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return {'error': 'Formato de imagen no válido'}, 400

        try:
            # Convertir imagen a formato compatible con Keras
            imagen = Image.open(archivo).convert('RGB')
            imagen = imagen.resize((224, 224))  # Tamaño del modelo
            imagen_array = img_to_array(imagen) / 255.0
            imagen_array = np.expand_dims(imagen_array, axis=0)

            # Hacer predicción
            prediccion = self.model.predict(imagen_array, verbose=0)[0][0]
            
            # Determinar resultado
            es_morchella = prediccion > 0.5
            resultado = "Es morchella" if es_morchella else "No es morchella"
            confianza = prediccion if es_morchella else 1 - prediccion
            
            # Log de la predicción en MLflow
            try:
                with mlflow.start_run(nested=True):
                    mlflow.log_metric("prediction_confidence", confianza)
                    mlflow.log_param("prediction_class", resultado)
            except:
                pass  # Si MLflow no está disponible, continuar sin logging

            return {
                'resultado': resultado,
                'confianza': round(float(confianza), 3),
                'probabilidad_morchella': round(float(prediccion), 3),
                'probabilidad_no_morchella': round(float(1 - prediccion), 3)
            }, 200

        except Exception as e:
            return {'error': f'Error procesando imagen: {str(e)}'}, 500

    def get(self):
        """
        Endpoint para verificar el estado del modelo
        """
        if self.model is None:
            return {
                'status': 'error',
                'message': 'Modelo no disponible',
                'model_loaded': False
            }, 500
        
        return {
            'status': 'ok',
            'message': 'Modelo cargado correctamente',
            'model_loaded': True,
            'model_input_shape': self.model.input_shape,
            'model_output_shape': self.model.output_shape
        }, 200
