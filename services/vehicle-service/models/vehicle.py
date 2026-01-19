from app import db

class Vehicle(db.Model):
    __table__ = "vehicles"
    
    vehicle_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)
    