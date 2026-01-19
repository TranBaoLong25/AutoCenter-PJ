from flask import request, jsonify, Blueprint
from services.reviewService import ReviewService
from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request, jwt_required, get_jwt_identity

api_bp = Blueprint('api', __name__, url_prefix='/api')

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claim = get_jwt()
            if claim.get("role")!= "Admin":
                return jsonify({"error": "Admin access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
def serialize_review(review):
    if not review: return None
    return {
        'review_id': review.review_id,
        'transaction_id': review.transaction_id,
        'reviewer_id': review.reviewer_id,
        'rating': review.rating,
        'comment': review.comment,
        'created_at': review.created_at.isoformat() if review.created_at else None
    }
@api_bp.route('/create-review')
@jwt_required()
def create_review():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data:
        return jsonify(error="Thiếu JSON body"), 400
    transaction_id = data.get('transaction_id')
    reviewer_id = current_user_id
    rating = data.get('rating')
    comment = data.get('comment') 
    if not all([transaction_id, reviewer_id, rating is not None]):
         return jsonify(error="Thiếu các trường bắt buộc: transaction_id, reviewer_user, rating"), 400
    review, error_message = ReviewService.create_review(
            transaction_id=transaction_id,
            reviewer_id=reviewer_id,
            reviewer_id=current_user_id,
            rating=rating,
            comment=comment
        )
    if not review:
        status_code = 409 if "đã tồn tại" in (error_message or "") else 400
        return jsonify(error=error_message or "Không thể tạo đánh giá."), status_code
    return jsonify(review=serialize_review(review)), 201
@api_bp.route('/review/<int:review_id>', methods = ["PUT"])
@jwt_required()
def update_review(review_id):
    current_user_id = int(get_jwt_identity())
    review, message = ReviewService.update_review(review_id, current_user_id, request.get_json())
    if not review:
        return jsonify({"error": message})
    return jsonify({"message": message, "review": serialize_review(review)})
@api_bp('/review/<int:review_id>', methods = ["DELETE"])
@jwt_required()
def delete_review(review_id):
    current_user_id = int(get_jwt_identity())
    success, message = ReviewService.delete_review(review_id, current_user_id)
    if not success:
        return jsonify({"error": message})
    return jsonify({"message": message})