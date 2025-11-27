from datetime import datetime
from .extensions import db

class PredictionCounts(db.Model):
    __tablename__ = 'prediction_counts'
    id = db.Column(db.Integer, primary_key=True)
    morchella = db.Column(db.BigInteger, default=0, nullable=False)
    no_morchella = db.Column(db.BigInteger, default=0, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ActiveModel(db.Model):
    __tablename__ = 'active_model'
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Text)
    model_name = db.Column(db.Text)
    local_path = db.Column(db.Text)
    size = db.Column(db.BigInteger)
    uploaded_at = db.Column(db.DateTime)
    set_at = db.Column(db.DateTime, default=datetime.utcnow)

class UploadedModel(db.Model):
    __tablename__ = 'uploaded_models'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    path = db.Column(db.Text)
    size = db.Column(db.BigInteger)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)