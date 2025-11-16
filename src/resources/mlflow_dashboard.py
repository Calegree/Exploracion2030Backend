from flask import Blueprint, jsonify, send_file, current_app
from flasgger import swag_from
import os
import json
import yaml

dashboard_api = Blueprint('dashboard_api', __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODEL_INFO_PATH = os.path.join(BASE_DIR, 'model_info.json')
YML_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'flasgger'))


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


@dashboard_api.route('/dashboard/prediction_counts', methods=['GET'])
@swag_from(yaml.safe_load(open(os.path.join(YML_DIR, 'mlflow_prediction_counts.yml'), 'r', encoding='utf-8')))
def prediction_counts():
    info = _load_model_info()
    return jsonify(info.get('prediction_counts', {'morchella': 0, 'no_morchella': 0}))


@dashboard_api.route('/mlflow/runs', methods=['GET'])
@swag_from(yaml.safe_load(open(os.path.join(YML_DIR, 'mlflow_runs.yml'), 'r', encoding='utf-8')))
def mlflow_runs():
    try:
        from mlflow.tracking import MlflowClient
    except Exception as e:
        return jsonify({'error': 'mlflow no disponible', 'detail': str(e)}), 501
    try:
        client = MlflowClient()
        experiments = client.list_experiments()
        out = []
        for exp in experiments:
            runs = client.search_runs(exp.experiment_id, max_results=10)
            for r in runs:
                out.append({
                    'run_id': r.info.run_id,
                    'status': r.info.status,
                    'start_time': r.info.start_time
                })
        return jsonify(out)
    except Exception as e:
        return jsonify({'error': 'falló al listar runs', 'detail': str(e)}), 500


@dashboard_api.route('/mlflow/confusion_matrix_current', methods=['GET'])
@swag_from(yaml.safe_load(open(os.path.join(YML_DIR, 'mlflow_confusion_matrix_current.yml'), 'r', encoding='utf-8')))
def confusion_matrix_current():
    info = _load_model_info()
    run_id = info.get('active_run_id')
    if not run_id:
        return jsonify({'error': 'no hay active_run_id configurado en model_info'}), 404
    # reusar la ruta por run_id
    return mlflow_confusion_matrix_run_id(run_id)


@dashboard_api.route('/mlflow/confusion_matrix/<run_id>', methods=['GET'])
@swag_from(yaml.safe_load(open(os.path.join(YML_DIR, 'mlflow_confusion_matrix.yml'), 'r', encoding='utf-8')))
def mlflow_confusion_matrix_run_id(run_id):
    try:
        from mlflow.tracking import MlflowClient
    except Exception as e:
        return jsonify({'error': 'mlflow no disponible', 'detail': str(e)}), 501
    try:
        client = MlflowClient()
        tmp_dir = client.download_artifacts(run_id, '')
        local_path = os.path.join(tmp_dir, 'confusion_matrix.png')
        if os.path.exists(local_path):
            return send_file(local_path, mimetype='image/png')
        return jsonify({'error': 'artifact confusion_matrix.png no encontrado para run_id'}), 404
    except Exception as e:
        return jsonify({'error': 'falló al recuperar artifact', 'detail': str(e)}), 500
