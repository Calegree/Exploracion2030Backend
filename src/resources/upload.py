from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flasgger import swag_from
import os
import json
import yaml

upload_api = Blueprint('upload_api', __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
MODEL_INFO_PATH = os.path.join(BASE_DIR, 'model_info.json')
YML_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'flasgger'))
os.makedirs(MODELS_DIR, exist_ok=True)


def _load_model_info():
    if os.path.exists(MODEL_INFO_PATH):
        try:
            with open(MODEL_INFO_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_model_info(data):
    try:
        with open(MODEL_INFO_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return True
    except Exception:
        return False


@upload_api.route('/upload/model', methods=['POST'])
@swag_from(os.path.join(YML_DIR, 'upload_model.yml'))
def upload_model():
    if 'model' not in request.files:
        return jsonify({'error': 'campo "model" no enviado'}), 400
    f = request.files['model']
    filename = secure_filename(f.filename)
    if filename == '':
        return jsonify({'error': 'nombre de archivo inválido'}), 400
    dest = os.path.join(MODELS_DIR, filename)
    f.save(dest)
    return jsonify({'filename': filename}), 201


@upload_api.route('/upload/models', methods=['GET'])
@swag_from(yaml.safe_load(open(os.path.join(YML_DIR, 'upload_models.yml'), 'r', encoding='utf-8')))
def list_models():
    files = sorted(os.listdir(MODELS_DIR))
    return jsonify({'models': files})


@upload_api.route('/upload/activate', methods=['POST'])
@swag_from(os.path.join(YML_DIR, 'upload_activate.yml'))
def activate_model():
    data = request.get_json(silent=True) or {}
    model_name = data.get('model')
    if not model_name:
        return jsonify({'error': 'campo "model" requerido'}), 400
    model_path = os.path.join(MODELS_DIR, secure_filename(model_name))
    if not os.path.exists(model_path):
        return jsonify({'error': 'modelo no encontrado'}), 404
    info = _load_model_info()
    info['active_model'] = model_name
    _save_model_info(info)
    return jsonify({'active_model': model_name})


@upload_api.route('/upload/active', methods=['GET'])
@swag_from(yaml.safe_load(open(os.path.join(YML_DIR, 'upload_active.yml'), 'r', encoding='utf-8')))
def active_model():
    info = _load_model_info()
    return jsonify({'active_model': info.get('active_model')})
