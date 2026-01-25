from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.listingService import ListingService  
from models.listing import Listing
from models.listing_image import ListingImage
from models.watchlist import WatchList
from functools import wraps
from dateutil import parser
import requests  
import logging   
import os
import sys
import traceback
import pytz

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

VEHICLE_SERVICE_URL = os.environ.get('VEHICLE_SERVICE_URL', 'http://vehicle-service:5001')
REQUEST_TIMEOUT = 1

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != "Admin":
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
def get_and_serialize_vehicle_by_id(vehicle_id: int): 
    if not vehicle_id: return None 
    url = f"{VEHICLE_SERVICE_URL}/api/vehicle/{vehicle_id}" 
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200: 
            return response.json() 
        else: 
            logger.warning(f"Listing Service returned status {response.status_code} for vehicle ID {vehicle_id} at {url}")
            return None
    except requests.exceptions.RequestException as e: 
         logger.error(f"Failed to connect to Listing Service at {url} for vehicle details: {e}")
         return None
def serialize_listing(listing):
    if not listing: return None
    data = {
    'listing_id': listing.listing_id,
    'listing_type': listing.listing_type,
    'title': listing.title,
    'description': listing.description,
    'price': str(listing.price),
    'status': listing.status,
    'created_at': listing.created_at.isoformat() if listing.created_at else None,
    'images': [img.image_url for img in listing.images] if hasattr(listing, 'images') and listing.images else []
    }
    if hasattr(listing, 'vehicle_id'):
        data['vehicle_details'] = get_and_serialize_vehicle_by_id(listing.vehicle_id)
    return data

@api_bp.route("/watch-list", methods=['POST'])
@jwt_required()
def add_to_watchlist():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    listing_id = data.get("listing_id")
    watchlist, message = ListingService.add_to_watchlist(current_user_id, listing_id)
    if not watchlist:
        return jsonify({"error": message}), 400
    return jsonify({"message": message}), 200

@api_bp.route("/watch-list", methods = ['GET'])
@jwt_required()
def my_watchlist():
    current_user_id = int(get_jwt_identity())
    watchlists = ListingService.get_watchlist(current_user_id)
    return jsonify([serialize_listing(w) for w in watchlists]), 200

@api_bp.route("/watch-list/by-listing/<int:listing_id>", methods=['DELETE'])
@jwt_required()
def delete_watchlist_by_listing(listing_id):
    current_user_id = int(get_jwt_identity())
    success, message = ListingService.remove_from_watchlist_by_user(current_user_id, listing_id)
    
    if not success:
        return jsonify({"message": message}), 404
    return jsonify({"message": "Đã xóa khỏi danh sách theo dõi"}), 200

@api_bp.route('/listings', methods=['GET'])
def search_listings():
    listings = ListingService.get_all_listings() 
    return jsonify([serialize_listing(l) for l in listings]), 200

@api_bp.route('/listings/filter', methods=['GET'])
def filter_listings():
    filters = {
        "title": request.args.get("title"),
        "min_price": request.args.get("min_price"),
        "max_price": request.args.get("max_price"),

        "brand": request.args.get("brand"),
        "model": request.args.get("model"),
        "year": request.args.get("year"),
        "mileage_min": request.args.get("mileage_min"),
        "mileage_max": request.args.get("mileage_max"),
    }
    try:
        listings = ListingService.filter_listings(filters)
        return jsonify([serialize_listing(l) for l in listings]), 200
    except Exception as e:
        print("❌ Lỗi khi lọc listings:", e)
        return jsonify({"error": "Lỗi khi lọc dữ liệu", "message": str(e)}), 500

@api_bp.route('/listings/<int:listing_id>', methods=['GET'])
def get_listing_details(listing_id):
    listing = ListingService.get_listing_by_id(listing_id)
    if not listing: return jsonify({"error": "Listing not found"}), 404
    return jsonify(serialize_listing(listing)), 200

@api_bp.route('/listings/<int:listing_id>', methods=['PUT'])
@jwt_required()
def update_listing(listing_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data: return jsonify({"error": "Request body must be JSON"}), 400
    listing, message = ListingService.update_listing(listing_id, user_id, data)
    if not listing:
        return jsonify({"error": message}), 403
    return jsonify({"message": message, "listing": serialize_listing(listing)}), 200

@api_bp.route('/compare', methods=['GET'])
def compare_listings():
    listing_ids = request.args.getlist('id', type=int)  

    if not listing_ids:
        return jsonify({"error": "Không có 'id' nào được cung cấp."}), 400

    if len(listing_ids) < 2:
        return jsonify({"error": "Cần ít nhất 2 sản phẩm để so sánh."}), 400

    if len(listing_ids) > 4:  
        return jsonify({"error": "Chỉ có thể so sánh tối đa 4 sản phẩm."}), 400
 
    comparison_type, data, message = ListingService.get_comparison_data(listing_ids)

    if not comparison_type: 
        return jsonify({"error": message}), 400 
    
    return jsonify({
        "message": message,
        "items": data 
    }), 200






