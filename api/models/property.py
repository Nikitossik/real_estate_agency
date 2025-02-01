from . import db, BaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Property(BaseModel):
    __tablename__ = 'property' 

    property_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    rooms = db.Column(db.Integer, nullable=False)
    square_meters = db.Column(db.Float, nullable=False)
    building_type = db.Column(db.String(20), nullable=False)
    floor_value = db.Column(db.Integer)
    floor_count = db.Column(db.Integer)
    centre_distance = db.Column(db.Float)
    owner_id = db.Column(db.BigInteger, db.ForeignKey('user.user_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    build_year = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(30), nullable=False)
    
    listings = db.relationship('Listing', backref='property', lazy='dynamic')
    
    def __repr__(self):
        return f"<Property {self.property_id} with latitude {self.latitude}, longitude {self.longitude}>"