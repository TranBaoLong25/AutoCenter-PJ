from app import db
from models.listing import Listing
from models.listing_image import ListingImage
from models.watchlist import WatchList
import traceback
from sqlalchemy import and_, or_
import logging

logger = logging.getLogger(__name__)

class ListingService:
    @staticmethod
    def create_listing(vehicle_id, data):
        required_fields = ['title', 'description', 'price']
        if not all(field in data for field in required_fields):
            return None, "Missing title, description, or price."
        if data['price'] >= 100000000 or data['price'] <= 0:
            return None, "Giá phải trong khoảng 0 đến 100 triệu"
        new_listing = Listing(
                vehicle_id=vehicle_id,
                title=data['title'],
                description=data['description'],
                price=data['price'],
                status='available'
            )
        db.session.add(new_listing)
        db.session.commit()
            
        return new_listing, "Listing created successfully, awaiting approval."    
    @staticmethod
    def delete_listing(listing_id, user_id, user_role):
        listing = Listing.query.get(listing_id)
        if not listing:
            return False, "Listing not found."
        db.session.delete(listing)
        db.session.commit()
        return True, "Listing removed successfully."
    @staticmethod
    def update_listing(listing_id, user_id, data): 
        listing = Listing.query.get(listing_id)
        if not listing:
            return None, "Listing not found."

        listing.title = data.get('title', listing.title)
        listing.description = data.get('description', listing.description)
        listing.price = data.get('price', listing.price)
        
        db.session.commit()
        return listing, "Listing updated successfully."
    @staticmethod
    def get_all_listings(): 
        return Listing.query.filter(Listing.status == 'available').order_by(Listing.created_at.desc()).all()
    @staticmethod
    def filter_listings(filters: dict): 
        query = Listing.query.filter(Listing.status == 'available')
 
        if filters.get("title"):
            title = f"%{filters['title']}%"
            query = query.filter(Listing.title.ilike(title))
 
        min_price = filters.get("min_price")
        max_price = filters.get("max_price")
        if min_price:
            query = query.filter(Listing.price >= float(min_price))
        if max_price:
            query = query.filter(Listing.price <= float(max_price))
 
        query = query.order_by(Listing.created_at.desc()) 
        return query.all()
    @staticmethod
    def get_listing_by_id(listing_id):
        return Listing.query.get(listing_id)
    @staticmethod
    def add_to_watchlist(user_id, listing_id):
        listing = Listing.query.get(listing_id)
        if not listing: return None, "Listing not found."
        if WatchList.query.filter_by(user_id=user_id, listing_id=listing_id).first():
            return None, "Listing is already in your watchlist."
        
        new_entry = WatchList(user_id=user_id, listing_id=listing_id)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry, "Added to watchlist."

    @staticmethod
    def remove_from_watchlist(user_id, listing_id):
        watchlist_item = WatchList.query.filter_by(
            user_id=user_id, 
            listing_id=listing_id
        ).first()
        
        if not watchlist_item: 
            return False, "watch lish not found"
        
        db.session.delete(watchlist_item)
        db.session.commit()
        return True, "Removed from watchlist."

    @staticmethod
    def get_watchlist_by_id(watchlist_id):
        return WatchList.query.get(watchlist_id)
    @staticmethod
    def get_watchlist(user_id):
        return [
            ListingService.get_listing_by_id(item.listing_id)
            for item in WatchList.query.filter_by(user_id=user_id).all()
        ]
    @staticmethod
    def get_comparison_data(listing_ids: list):
        if not listing_ids:
            return None, None, "Không có ID nào được cung cấp."

        try:
            query = (
                Listing.query
                .filter(Listing.listing_id.in_(listing_ids))
            )
            listings = query.all()

            if not listings:
                return None, None, "Không tìm thấy tin đăng nào."
        
            serialized_data = [
                ListingService._serialize_for_compare(l) for l in listings
            ]

            return serialized_data, "Lấy dữ liệu so sánh thành công."

        except Exception as e:
            logger.error(f"Lỗi khi lấy dữ liệu so sánh: {e}", exc_info=True)
            return None, None, "Lỗi máy chủ nội bộ."

    @staticmethod
    def _serialize_for_compare(listing): 
        if not listing: return None 
        v = listing.vehicle
        vehicle_details = {
            'brand': v.brand,
            'model': v.model,
            'year': v.year,
            'mileage': v.mileage
        }
        return {
            'listing_id': listing.listing_id,
            'listing_type': listing.listing_type,
            'title': listing.title,
            'price': str(listing.price),
            'status': listing.status,
            'images': [img.image_url for img in listing.images] if listing.images else [],
            'vehicle_details': vehicle_details
        }

