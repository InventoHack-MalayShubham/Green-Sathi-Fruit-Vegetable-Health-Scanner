from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    diet_goal = db.Column(db.String(100), nullable=True)
    diet_type = db.Column(db.String(50), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    activity_level = db.Column(db.String(50), nullable=True)
    allergies = db.Column(db.String(200), nullable=True)
    scans = db.relationship('ScanHistory', backref='user', lazy=True)

class ScanHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_filename = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    fruit_name = db.Column(db.String(100), nullable=True)
    health_status = db.Column(db.String(50), nullable=True)
    nutrition = db.Column(db.Text, nullable=True)  # JSON string
    recommendations = db.Column(db.Text, nullable=True)
    synergic_fruits = db.Column(db.Text, nullable=True) 