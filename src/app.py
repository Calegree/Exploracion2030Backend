from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from resources.prediction import Prediction
from resources.download_fungis import DownloadImages
from resources.upload import upload_api
from resources.mlflow_dashboard import dashboard_api

app = Flask(__name__)
api = Api(app)

# Asegurar que no haya valores None en la configuración de SWAGGER
app.config.setdefault('SWAGGER', {})
app.config['SWAGGER']['oauth'] = {}  # evita que se inserte "None" en el JS

# Registrar la API RESTful (resources) y blueprints ANTES de instanciar Swagger
api.add_resource(Prediction, '/predict')
api.add_resource(DownloadImages, '/download/fungis')  # <-- registrar resource faltante

# Registrar blueprints
app.register_blueprint(upload_api)
app.register_blueprint(dashboard_api)

# Configuración personalizada de Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json"
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

# Instanciar Swagger DESPUÉS de registrar todas las rutas
swagger = Swagger(app, config=swagger_config)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
