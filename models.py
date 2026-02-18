from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PackagingHistory(db.Model):
    __tablename__ = "packaging_history"

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100))
    weight_kg = db.Column(db.Float)
    fragility = db.Column(db.String(10))
    packaging_used = db.Column(db.String(200))


class Material(db.Model):
    __tablename__ = "materials"

    id = db.Column(db.Integer, primary_key=True)
    material_name = db.Column(db.String(200))
    category = db.Column(db.String(100))
    tensile_strength = db.Column(db.Float)
    co2_emission = db.Column(db.Float)
    cost_per_kg = db.Column(db.Float)
    biodegradable = db.Column(db.String(10))
