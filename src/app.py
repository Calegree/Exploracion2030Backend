import os
from dotenv import load_dotenv
from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from flask_cors import CORS
from flask import request
import sqlalchemy  # nuevo import para manejar excepciones

# cargar .env temprano
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from .extensions import db
# importar modelos para que SQLAlchemy los registre
from . import models  # noqa: F401

app = Flask(__name__)

# configurar DB (usar env var DATABASE_URL)
app.config.setdefault('SQLALCHEMY_DATABASE_URI', os.getenv('DATABASE_URL', 'sqlite:///./model_info.db'))
app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)

db.init_app(app)

# crear tablas automáticamente al iniciar la app (solo en desarrollo)
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    # evitar que errores de creación de tablas detengan el proceso (race conditions, duplicados)
    try:
        app.logger.warning("db.create_all() skipped: %s", e)
    except Exception:
        pass

# configurar API, Swagger, CORS, blueprints, etc.
api = Api(app)
#swagger = Swagger(app)
CORS(app)

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
from .resources.prediction import Prediction
from .resources.download_fungis import DownloadImages
from .resources.download_fungis_2 import DownloadImages2
from .resources.upload import upload_api
from .resources.mlflow_dashboard import dashboard_api

# Resources (Flask-RESTful)
api.add_resource(Prediction, '/predict')
api.add_resource(DownloadImages, '/download/fungis')
api.add_resource(DownloadImages2, '/download/fungis2')

# Blueprints (Flask)
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
    # intentar importar flasgger solo aquí
    try:
        from flasgger import Swagger
        _HAS_SWAGGER = True
    except Exception:
        Swagger = None
        _HAS_SWAGGER = False

    YML_DIR = os.path.join(os.path.dirname(__file__), 'flasgger')
    path_map = {
        '/dashboard/prediction_counts': 'mlflow_prediction_counts.yml',
        '/mlflow/runs': 'mlflow_runs.yml',
        '/mlflow/confusion_matrix_current': 'mlflow_confusion_matrix_current.yml',
        '/mlflow/confusion_matrix/{run_id}': 'mlflow_confusion_matrix.yml',
        '/upload/active': 'upload_active.yml',
        '/upload/models': 'upload_models.yml',
        '/download/fungis2': 'download_fungis_2.yml'
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

    if _HAS_SWAGGER:
        swagger = Swagger(app, config=swagger_config, template=swagger_template)
    else:
        # fallback: no flasgger disponible
        swagger = None
except Exception:
    # Fallback: instanciar sin template si algo falla o sin flasgger
    try:
        from flasgger import Swagger
        swagger = Swagger(app, config=swagger_config)
    except Exception:
        swagger = None


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

if __name__ == '__main__':
    # Ejecuta la API Flask en el puerto 5000 (usa FLASK_PORT si quieres cambiarlo)
    app.run(host='0.0.0.0', port=5000, debug=True)
