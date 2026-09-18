# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc

db = SQLAlchemy()

class SensorData(db.Model):
    __tablename__ = "sensor_data"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    moisture = db.Column(db.Float, nullable=False)
    lux = db.Column(db.Float, nullable=True, default=0.0)

class Alert(db.Model):
    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    alert_type = db.Column(db.String(80))
    value = db.Column(db.Float)
    sent_via = db.Column(db.String(80))
