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



para correr la app en linux 
##crea el env
python3 -m venv .venv
##corre el env y la app
source .venv/bin/activate
python3 src/app.py

pip install -r src/requirements.txt



