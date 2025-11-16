from flask import Flask
from flask_restful import Api
from flasgger import Swagger
import os
from flask import request
try:
    from resources.prediction import Prediction
except Exception as _e:
    # Si falla la importación (por ejemplo TensorFlow no disponible en el entorno),
    # registramos un recurso placeholder para que la app arranque y Flasgger
    # pueda generar la especificación sin importar módulos pesados.
    from flask_restful import Resource

    class Prediction(Resource):
        def get(self):
            return {'error': 'Prediction endpoint unavailable (import error)'}, 503

        def post(self):
            return {'error': 'Prediction endpoint unavailable (import error)'}, 503

try:
    from resources.download_fungis import DownloadImages
except Exception:
    from flask_restful import Resource

    class DownloadImages(Resource):
        def get(self):
            return {'error': 'DownloadImages endpoint unavailable (import error)'}, 503

from resources.upload import upload_api
from resources.mlflow_dashboard import dashboard_api

app = Flask(__name__)
api = Api(app)

# Asegurar que no haya valores None en la configuración de SWAGGER
app.config.setdefault('SWAGGER', {})
app.config['SWAGGER']['oauth'] = {}  # evita que se inserte "None" en el JS
# Valores por defecto adicionales para evitar que Flasgger reciba None y lo inyecte en las plantillas JS
app.config['SWAGGER'].setdefault('title', 'Exploracion2030Backend API')
app.config['SWAGGER'].setdefault('uiversion', 3)
app.config['SWAGGER'].setdefault('specs_route', '/apidocs/')
app.config['SWAGGER'].setdefault('openapi', '3.0.2')
app.config['SWAGGER'].setdefault('auth', {})

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

# Proveer explícitamente oauth config vacía al config de Flasgger para evitar
# que la plantilla inserte el literal Python `None` en el JS.
swagger_config.setdefault('oauth', {})

# Construir template explícito a partir de los YML locales para asegurar que
# Flasgger reciba objetos válidos (evita inyección accidental de literales Python como None)
try:
    import yaml as _yaml
    YML_DIR = os.path.join(os.path.dirname(__file__), 'flasgger')
    path_map = {
        '/dashboard/prediction_counts': 'mlflow_prediction_counts.yml',
        '/mlflow/runs': 'mlflow_runs.yml',
        '/mlflow/confusion_matrix_current': 'mlflow_confusion_matrix_current.yml',
        '/mlflow/confusion_matrix/{run_id}': 'mlflow_confusion_matrix.yml',
        '/upload/active': 'upload_active.yml',
        '/upload/models': 'upload_models.yml'
    }
    template_paths = {}
    for p, fname in path_map.items():
        fpath = os.path.join(YML_DIR, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as fh:
                doc = _yaml.safe_load(fh) or {}
            template_paths[p] = doc
        except Exception:
            # ignore missing/invalid YAML — Flasgger will still build the spec from other sources
            template_paths[p] = {}

    swagger_template = {
        'openapi': app.config.get('SWAGGER', {}).get('openapi', '3.0.2'),
        'info': {
            'title': app.config.get('SWAGGER', {}).get('title', 'Exploracion2030Backend API'),
            'version': '0.0.1',
            'description': 'powered by Flasgger'
        },
        'paths': template_paths
    }

    # Instanciar Swagger DESPUÉS de registrar todas las rutas
    swagger = Swagger(app, config=swagger_config, template=swagger_template)
except Exception:
    # Fallback: instanciar sin template si algo falla
    swagger = Swagger(app, config=swagger_config)


    # Small runtime fix: some Flasgger templates may render Python None into the
    # generated HTML/JS (e.g. `let auth_config = None;`) which breaks the UI.
    # Intercept the apidocs HTML and replace that token with an empty object.
    @app.after_request
    def _fix_apidocs_none(response):
        try:
            if request.path.startswith('/apidocs') and response.content_type and 'text/html' in response.content_type:
                body = response.get_data(as_text=True)
                if 'let auth_config = None;' in body:
                    body = body.replace('let auth_config = None;', 'let auth_config = {};')
                    response.set_data(body)
        except Exception:
            pass
        return response

if __name__ == "__main__":
    # Run without the reloader/debugger to avoid double-imports and noisy TensorFlow
    app.run(host="0.0.0.0", port=5000, debug=False)
