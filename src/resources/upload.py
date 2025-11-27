from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from werkzeug.utils import secure_filename
from flasgger import swag_from
import os
import json

from ..extensions import db
from ..models import UploadedModel, ActiveModel

upload_api = Blueprint('upload_api', __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODELS_DIR = os.path.join(BASE_DIR, 'model_uploads') if os.path.exists(os.path.join(BASE_DIR, 'model_uploads')) else os.path.join(BASE_DIR, 'models')
YML_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'flasgger'))

os.makedirs(MODELS_DIR, exist_ok=True)

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
    try:
        f.save(dest)
    except Exception as e:
        return jsonify({'error': 'no se pudo guardar archivo', 'detail': str(e)}), 500

    try:
        stat = os.stat(dest)
        size = stat.st_size
        uploaded_at = datetime.utcfromtimestamp(stat.st_mtime)
    except Exception:
        size = None
        uploaded_at = None

    # Registrar en UploadedModel (mantener historial)
    try:
        um = UploadedModel(name=filename, path=dest, size=size, uploaded_at=uploaded_at)
        db.session.add(um)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'DB error al guardar metadata', 'detail': str(e)}), 500

    # Activar automáticamente el modelo subido: crear entrada ActiveModel (histórico)
    try:
        am = ActiveModel(run_id=None, model_name=filename, local_path=dest, size=size, uploaded_at=uploaded_at)
        db.session.add(am)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'DB error al activar modelo', 'detail': str(e)}), 500

    return jsonify({'filename': filename, 'size': size, 'uploaded_at': uploaded_at.isoformat() if uploaded_at else None}), 201

@upload_api.route('/upload/models', methods=['GET'])
@swag_from(os.path.join(YML_DIR, 'upload_models.yml'))
def list_models():
    try:
        rows = UploadedModel.query.order_by(UploadedModel.uploaded_at.desc()).all()
        out = []
        for r in rows:
            out.append({'name': r.name, 'size': int(r.size) if r.size is not None else None, 'uploaded_at': r.uploaded_at.isoformat() if r.uploaded_at else None})
        return jsonify({'models': out})
    except Exception as e:
        return jsonify({'error': 'DB error', 'detail': str(e)}), 500

@upload_api.route('/upload/activate', methods=['POST'])
@swag_from(os.path.join(YML_DIR, 'upload_activate.yml'))
def activate_model():
    data = request.get_json(silent=True) or {}
    model_name = data.get('model')
    if not model_name:
        return jsonify({'error': 'campo "model" requerido'}), 400

    um = UploadedModel.query.filter_by(name=model_name).order_by(UploadedModel.uploaded_at.desc()).first()
    if not um:
        return jsonify({'error': 'modelo no encontrado'}), 404

    try:
        am = ActiveModel(run_id=None, model_name=um.name, local_path=um.path, size=um.size, uploaded_at=um.uploaded_at)
        db.session.add(am)
        db.session.commit()
        return jsonify({'active_model': um.name, 'size': int(um.size) if um.size is not None else None, 'uploaded_at': um.uploaded_at.isoformat() if um.uploaded_at else None})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'DB error al activar modelo', 'detail': str(e)}), 500

@upload_api.route('/upload/active', methods=['GET'])
@swag_from(os.path.join(YML_DIR, 'upload_active.yml'))
def active_model():
    try:
        am = ActiveModel.query.order_by(ActiveModel.id.desc()).first()
        if not am:
            return jsonify({'active_model': None})
        return jsonify({
            'active_model': am.model_name,
            'run_id': am.run_id,
            'local_path': am.local_path,
            'size': int(am.size) if am.size is not None else None,
            'uploaded_at': am.uploaded_at.isoformat() if am.uploaded_at else None,
            'set_at': am.set_at.isoformat() if am.set_at else None
        })
    except Exception as e:
        return jsonify({'error': 'DB error', 'detail': str(e)}), 500
