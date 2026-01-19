from app import db
from models.vehicle import Vehicle
from datetime import datetime

class VehicleService:
    @staticmethod
    def create_vehicle(data):
        required_fields = ['brand', 'model', 'year', 'mileage']
        if not all(field in data for field in required_fields):
            return None, "Missing required vehicle data."
        if data["year"] > datetime.now().year:
            return None, "Invalid year of manufacture"
        new_vehicle = Vehicle(
            brand=data['brand'],
            model=data['model'],
            year=data['year'],
            mileage=data['mileage']
        )
        db.session.add(new_vehicle)
        db.session.commit()
        return new_vehicle, "Vehicle created successfully."
    @staticmethod
    def get_vehicle_by_id(vehicle_id):
        return Vehicle.query.get(vehicle_id)
    @staticmethod
    def update_vehicle(vehicle_id, data):
        vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return False, "Vehicle not found"
        
        vehicle.brand = data.get('brand', vehicle.brand)
        vehicle.model = data.get('model', vehicle.model)
        vehicle.year = data.get('year', vehicle.year)
        vehicle.mileage = data.get('mileage', vehicle.mileage)
        
        db.session.commit()
        return True, "Update vehicle successfully"
    @staticmethod
    def delete_vehicle(vehicle_id):
        vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return False, "Vehicle not found"
        db.session.delete(vehicle)
        db.session.commit()