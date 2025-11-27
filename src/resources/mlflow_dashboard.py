from flask import Blueprint, jsonify, send_file, current_app
from flasgger import swag_from
import os
import json
from mlflow.tracking import MlflowClient

# usar ORM
from ..extensions import db
from ..models import PredictionCounts, ActiveModel

dashboard_api = Blueprint('dashboard_api', __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
YML_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'flasgger'))

def _ensure_prediction_counts():
    pc = PredictionCounts.query.order_by(PredictionCounts.id.desc()).first()
    if pc is None:
        pc = PredictionCounts(morchella=0, no_morchella=0)
        db.session.add(pc)
        db.session.commit()
    return pc

@dashboard_api.route('/dashboard/prediction_counts', methods=['GET'])
@swag_from(os.path.join(YML_DIR, 'mlflow_prediction_counts.yml'))
def prediction_counts():
    """
    Obtener contador de predicciones (ORM)
    """
    try:
        pc = _ensure_prediction_counts()
        return jsonify({'morchella': int(pc.morchella), 'no_morchella': int(pc.no_morchella)})
    except Exception as e:
        return jsonify({'error': 'DB error', 'detail': str(e)}), 500

@dashboard_api.route('/mlflow/runs', methods=['GET'])
@swag_from(os.path.join(YML_DIR, 'mlflow_runs.yml'))
def mlflow_runs():
    try:
        client = MlflowClient()
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
@swag_from(os.path.join(YML_DIR, 'mlflow_confusion_matrix_current.yml'))
def confusion_matrix_current():
    """
    Matriz de confusión del modelo activo (usa ActiveModel.run_id)
    """
    try:
        active = ActiveModel.query.order_by(ActiveModel.id.desc()).first()
        if not active or not active.run_id:
            return jsonify({'error': 'no hay run activo registrado en la BD'}), 404
        return mlflow_confusion_matrix_run_id(active.run_id)
    except Exception as e:
        return jsonify({'error': 'falló al obtener modelo activo', 'detail': str(e)}), 500

@dashboard_api.route('/mlflow/confusion_matrix/<run_id>', methods=['GET'])
@swag_from(os.path.join(YML_DIR, 'mlflow_confusion_matrix.yml'))
def mlflow_confusion_matrix_run_id(run_id):
    """
    Obtener matriz de confusión de un run de MLflow.
    Prioriza confusion_matrix.json (JSON) y si no existe devuelve confusion_matrix.png.
    """
    try:
        client = MlflowClient()
        tmp_dir = client.download_artifacts(run_id, '')  # descarga todo
        json_path = os.path.join(tmp_dir, 'confusion_matrix.json')
        png_path = os.path.join(tmp_dir, 'confusion_matrix.png')

        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            return jsonify(data)

        if os.path.exists(png_path):
            return send_file(png_path, mimetype='image/png')

        return jsonify({'error': 'artifact confusion_matrix.json/png no encontrado para run_id'}), 404
    except Exception as e:
        return jsonify({'error': 'falló al recuperar artifact', 'detail': str(e)}), 500
