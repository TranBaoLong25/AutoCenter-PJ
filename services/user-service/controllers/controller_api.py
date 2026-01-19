from flask import request, Blueprint, jsonify
from flask_jwt_extended import (create_access_token, get_jwt, get_jwt_identity, jwt_required, verify_jwt_in_request)
from app import jwt
from services.userService import UserService
from functools import wraps

api_bp = Blueprint('api', __name__, url_prefix='/api')

def serialize_user(user):
    if not user: return None
    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "status": user.status
    }
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claim = get_jwt()
            if claim.get("role") == "Admin":
                return fn(*args, **kwargs)
            else:
                return jsonify(error="Admin only!"), 403
        return decorator
    return wrapper
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return UserService.get_user_by_id(identity)

@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    user = UserService.get_user_by_id(identity)
    if user:
        return {"role": user.role}
    return {}

@api_bp.route('/login', methods = ["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email_username") or not data.get("password"):
        return jsonify({"error": "Missing email/username or password"}), 400
    user = UserService.get_user_by_name_or_email(data["email_username"])
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401
    if user.status != "Active":
        return jsonify({"error": "Account has been locked"}), 403
    access_token = create_access_token(identity=str(user.user_id))
    return jsonify(access_token = access_token)
@api_bp.route('/register', methods=["GET"])
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ["email", "username", "password"]):
        return jsonify({"error": "Missing required fields: email, username, password"}), 400
    user, error = UserService.create_user(data["email"], data["username"], data["password"])
    if error:
        return jsonify({"error": error}), 409
    return jsonify({"message": "Registration successful!", "user": serialize_user(user)}), 201
@api_bp('/send_otp', methods=["POST"])
def send_otp():
    email = request.json.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400
    success, message = UserService.send_reset_otp(email=email)
    if not success:
        return jsonify(error=message), 404
    return jsonify(message=message), 200
@api_bp.route('/reset-password')
def reset_password():
    data = request.get_json()
    if not data or not all(k in data for k in ["email", "otp", "new_password"]):
        return jsonify({"error": "Missing required fields: email, otp, new_password"}), 400
    success, message = UserService.verify_otp_and_reset_password(data["email"], data["otp"], data["new_password"])
    if not success:
        return jsonify(error=message), 400
    return jsonify(message=message), 200
@api_bp.route('/account', methods = ["PUT"])
def update_my_account():
    current_user_id = get_jwt_identity()
    user, error = UserService.update_user_by_member(current_user_id, request.get_json())
    if error:
        return jsonify({"error": error})
    return jsonify({"message": "Account updated successfully", "user": serialize_user(user)}), 200
@api_bp.route('/account', methods = ["DELETE"])
def delete_my_account():
    current_user_id = get_jwt_identity()
    success, message = UserService.delete_user(current_user_id)
    if not success:
        return jsonify({"error": message}), 404
    return jsonify({"message": message}), 200
