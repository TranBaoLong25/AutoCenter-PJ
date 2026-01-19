from models.review import Review
from app import db  
import logging

logger = logging.getLogger(__name__)

class ReviewService:
    @staticmethod
    def create_review(transaction_id, reviewer_id, rating, comment=None):
        try:
            existing_review = Review.query.filter_by(
                transaction_id=transaction_id,
                reviewer_id=reviewer_id,
            ).first()
            if existing_review:
                return None, "Bạn đã đánh giá san pham này rồi."
            try:
                rating_int = int(rating)
                if not (0 <= rating_int <= 5):
                     raise ValueError("Rating phải từ 0 đến 5.")
            except (ValueError, TypeError):
                 return None, "Rating phải là một số nguyên từ 0 đến 5."

            review = Review(
                transaction_id=transaction_id,
                reviewer_id=reviewer_id,
                rating=rating_int,
                comment=comment
            )
            db.session.add(review)
            db.session.commit()
            return review, None

        except ValueError as ve:
             return None, str(ve)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi DB khi tạo review: {e}", exc_info=True)
            return None, "Lỗi cơ sở dữ liệu khi tạo đánh giá."


    @staticmethod
    def get_reviews_by_transaction(transaction_id):
        return Review.query.filter_by(transaction_id=transaction_id).all()

    @staticmethod
    def get_reviews_by_reviewer(reviewer_id): 
        return Review.query.filter_by(reviewer_id=reviewer_id).order_by(Review.created_at.desc()).all()

    @staticmethod
    def get_review_by_id_and_reviewer(review_id, user_id): 
        return Review.query.filter_by(review_id=review_id, reviewer_id=user_id).first()

    @staticmethod
    def delete_review(review_id, user_id):
        review = Review.query.get(review_id)
        if not review:
            return False, "Không tìm thấy đánh giá."

        if review.reviewer_id != user_id:
            return False, "Bạn không có quyền xóa đánh giá này."

        try:
            db.session.delete(review)
            db.session.commit()
            return True, "Đánh giá đã được xóa thành công."
        except Exception as e:
             db.session.rollback()
             logger.error(f"Lỗi DB khi xóa review {review_id}: {e}", exc_info=True)
             return False, "Lỗi cơ sở dữ liệu khi xóa đánh giá."

    @staticmethod
    def update_review(review_id, user_id, data):
        review = Review.query.get(review_id)
        if not review:
            return None, "Không tìm thấy đánh giá."

        if review.reviewer_id != user_id:
            return None, "Bạn không có quyền sửa đánh giá này."

        updated = False
        try:
            if data["rating"] is not None:
                try:
                    rating_int = int(data["rating"])
                    if not (0 <= rating_int <= 5): raise ValueError()
                    review.rating = rating_int
                    updated = True
                except (ValueError, TypeError):
                     raise ValueError("Rating phải là một số nguyên từ 0 đến 5.") 

            if data["comment"] is not None: 
                review.comment = data["comment"]
                updated = True

            if updated:
                db.session.commit()
                return review, None 
            else:
                 return review, "Không có thông tin nào được cập nhật."

        except ValueError as ve: 
             return None, str(ve)
        except Exception as e:
             db.session.rollback()
             logger.error(f"Lỗi DB khi cập nhật review {review_id}: {e}", exc_info=True)
             return None, "Lỗi cơ sở dữ liệu khi cập nhật đánh giá."