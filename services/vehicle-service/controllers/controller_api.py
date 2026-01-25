from flask import request, jsonify, Blueprint
from functools import wraps
from app import jwt
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from services.vehicleService import VehicleService

api_dp = Blueprint('api', __name__, url_prefix='/api')

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claim = get_jwt()
            if claim.get("role") != "admin":
                return jsonify({"error": "Admin access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
def role_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != "Admin" or claims.get("role") != "Staff":
                return jsonify({"error": "Admin or Staff access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
def serialize_vehicle(vehicle):
    if not vehicle: return None
    return {
        'vehicle_id': vehicle.vehicle_id,
        'brand': vehicle.brand,
        'model': vehicle.model,
        'year': vehicle.year,
        'mileage': vehicle.mileage
    }
@api_dp.route('/create-vehicle', methods = ["POST"])
@admin_required()
def create_vehicle():
    vehicle, message = VehicleService.create_vehicle(request.get_json())
    if not vehicle:
        return jsonify({"error": message})
    return jsonify({"message": "create vehicle successful", "vehicle": serialize_vehicle(vehicle)}), 201
@api_dp.route('/vehicle/<int:vehicle_id>', methods = ["PUT"])
def update_vehicle(vehicle_id):
    vehicle, message = VehicleService.update_vehicle(vehicle_id, request.get_json())
    if not vehicle:
        return jsonify({"error": message})
    return jsonify({"message": message, "vehicle" :serialize_vehicle(vehicle)})
@api_dp.route('/vehicle/<int:vehicle_id>', methods = ["DELETE"])
@admin_required()
def delete_vehicle(vehicle_id):
    success, message = VehicleService.delete_vehicle(vehicle_id)
    if not success:
        return jsonify({"error": message})
    return jsonify({"message": message}), 200
@api_dp.route('/vehicle/<int:vehicle_id>', methods = ["GET"])
def get_vehicle(vehicle_id):
    vehicle, message = VehicleService.get_vehicle_by_id(vehicle_id)
    if not vehicle:
        return jsonify({"error": message})
    return jsonify({"message": message, "vehicle": serialize_vehicle(vehicle)}), 200