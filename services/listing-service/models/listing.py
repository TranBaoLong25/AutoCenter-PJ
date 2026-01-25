from app import db
from datetime import datetime, timezone

class Listing(db.Model):
    __tablename__ = 'listings'

    listing_id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('available', 'sold', 'rejected', name='listing_statuses'), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
     
    images = db.relationship('ListingImage', back_populates='listing', cascade='all, delete-orphan')
    watchlists = db.relationship("WatchList", back_populates="listing", cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Listing {self.title} (ID: {self.listing_id})>"

