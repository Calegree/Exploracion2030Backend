from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from resources.prediction import Prediction
from resources.download_fungis import DownloadImages

app = Flask(__name__)
api = Api(app)
#swagger = Swagger(app)  # 👈 Activa Swagger/flasgger sin configuración

# Configuración personalizada de Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "MorchellaAPP",  # 👈 Cambia el título aquí
        "description": "API para detección de hongos Morchella usando machine learning",
        "version": "1.0.0",  # 👈 Cambia la versión aquí
        "contact": {
            "name": "Exploración 2030",
            "email": "contacto@exploracion2030.com"
        }
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": [
        "http"
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)



# Endpoints en Flask las rutas se llaman resources (Routes)
api.add_resource(Prediction, '/predict')
api.add_resource(DownloadImages, '/download')

if __name__ == '__main__':
    app.run(debug=True)
