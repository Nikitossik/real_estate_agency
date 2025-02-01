from . import db, BaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from sqlalchemy import func

class Listing(BaseModel):
    __tablename__ = 'listing' 
    
    listing_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    listing_type = db.Column(db.String(4), nullable=False)
    listing_price = db.Column(db.Float, nullable=False)
    listing_status = db.Column(db.String(10), default='active', nullable=False)
    listing_description = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=func.now(), nullable=False)
    id_property = db.Column(UUID(as_uuid=True), db.ForeignKey('property.property_id',onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    id_user = db.Column(db.BigInteger, db.ForeignKey('user.user_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    
    applications = db.relationship("Application", backref='listing', lazy='dynamic')
    
    def __repr__(self):
        return f"<Listing {self.listing_id} {self.listing_type} {self.listing_price} created at {self.created_at}> "