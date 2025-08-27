#Hongos Reconocidos
Morchella rufobrunnea
Morchella andinensis
Morchella tridentina
Morchella Aysenina 

#Documentación
http://localhost:5000/apidocs/#/

#Crear enviroment proyecto Python
py -3 -m venv .venv

#Activar el enviroment 
.venv\Scripts\activate

#Dependencias
pip install -r requirements.txt

#Actualizar dependencias
pip freeze >> requirements.txt

#Correr la API para hacer predicciones
python src/app.py


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


