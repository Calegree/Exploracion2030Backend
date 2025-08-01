#Crear enviroment proyecto Python
py -3 -m venv .venv

#Activar el enviroment 
.venv\Scripts\activate

#Dependencias
pip install -r requirements.txt

#Actualizar dependencias
pip freeze >> requirements.txt

#Corre el pipeline
python run_training_pipeline.py

#O hazlo manual
python clean_mlflow.py
python verify_mlflow_setup.py
python train_model.py
python start_mlflow_ui.py



