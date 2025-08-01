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
import sys

# Agregar el directorio padre al path para importar mlflow_manager
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from mlflow_manager import MLflowManager

# Configurar MLflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")

class Prediction(Resource):
    def __init__(self):
        self.model = None
        self.mlflow_manager = MLflowManager()
        self.model_info = None
        self.load_model()
    
    def load_model(self):
        """
        Carga el modelo desde MLflow con múltiples estrategias de fallback
        """
        print("🔍 Cargando modelo desde MLflow...")
        
        # Estrategia 1: Intentar cargar el mejor modelo registrado
        try:
            best_run = self.mlflow_manager.get_best_run()
            if best_run is not None:
                run_id = best_run['run_id']
                model_uri = f"runs:/{run_id}/model"
                self.model = mlflow.keras.load_model(model_uri)
                self.model_info = {
                    'source': 'mlflow_best_run',
                    'run_id': run_id,
                    'accuracy': best_run.get('metrics.val_accuracy', 'N/A'),
                    'loss': best_run.get('metrics.val_loss', 'N/A')
                }
                print(f"✅ Modelo cargado desde MLflow (mejor run: {run_id[:8]}...)")
                print(f"   Accuracy: {self.model_info['accuracy']}")
                return
        except Exception as e:
            print(f"⚠️ Error cargando mejor modelo: {e}")
        
        # Estrategia 2: Intentar cargar el último modelo registrado
        try:
            runs = self.mlflow_manager.list_runs()
            if len(runs) > 0:
                latest_run = runs.iloc[0]  # El más reciente
                run_id = latest_run['run_id']
                model_uri = f"runs:/{run_id}/model"
                self.model = mlflow.keras.load_model(model_uri)
                self.model_info = {
                    'source': 'mlflow_latest_run',
                    'run_id': run_id,
                    'accuracy': latest_run.get('metrics.val_accuracy', 'N/A'),
                    'loss': latest_run.get('metrics.val_loss', 'N/A')
                }
                print(f"✅ Modelo cargado desde MLflow (último run: {run_id[:8]}...)")
                print(f"   Accuracy: {self.model_info['accuracy']}")
                return
        except Exception as e:
            print(f"⚠️ Error cargando último modelo: {e}")
        
        # Estrategia 3: Intentar cargar modelo registrado
        try:
            self.model = self.mlflow_manager.load_registered_model("morchella_model")
            self.model_info = {
                'source': 'mlflow_registered_model',
                'model_name': 'morchella_model'
            }
            print("✅ Modelo cargado desde MLflow (modelo registrado)")
            return
        except Exception as e:
            print(f"⚠️ Error cargando modelo registrado: {e}")
        
        # Estrategia 4: Fallback a archivo local
        try:
            model_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'model_morchella.h5')
            if os.path.exists(model_path):
                self.model = load_model(model_path)
                self.model_info = {
                    'source': 'local_file',
                    'path': model_path
                }
                print("✅ Modelo cargado desde archivo local")
                return
            else:
                print("❌ Archivo local no encontrado")
        except Exception as e:
            print(f"❌ Error cargando archivo local: {e}")
        
        # Si llegamos aquí, no se pudo cargar ningún modelo
        print("❌ No se pudo cargar ningún modelo")
        self.model = None
        self.model_info = None

    def get_model_status(self):
        """
        Obtiene información detallada del estado del modelo
        """
        if self.model is None:
            return {
                'status': 'error',
                'message': 'Modelo no disponible',
                'model_loaded': False,
                'model_info': None
            }
        
        return {
            'status': 'ok',
            'message': 'Modelo cargado correctamente',
            'model_loaded': True,
            'model_info': self.model_info,
            'model_input_shape': self.model.input_shape,
            'model_output_shape': self.model.output_shape
        }

    @swag_from('../flasgger/prediction.yml')
    def post(self):
        if self.model is None:
            return {
                'error': 'Modelo no disponible. Ejecuta el entrenamiento primero.',
                'model_info': self.model_info
            }, 500
            
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
                    mlflow.log_param("input_filename", archivo.filename)
            except Exception as e:
                print(f"⚠️ No se pudo loggear en MLflow: {e}")

            return {
                'resultado': resultado,
                'confianza': round(float(confianza), 3),
                'probabilidad_morchella': round(float(prediccion), 3),
                'probabilidad_no_morchella': round(float(1 - prediccion), 3),
                'model_info': self.model_info
            }, 200

        except Exception as e:
            return {'error': f'Error procesando imagen: {str(e)}'}, 500

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
