from . import db, BaseModel
from sqlalchemy import func
import uuid

class Rental(BaseModel):
    tablename = 'rental'

    rental_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_date = db.Column(db.Date, nullable=False, server_default=func.now())
    end_date = db.Column(db.Date, nullable=False, server_default=func.now())
    rental_status = db.Column(db.String(10), nullable=False, default='active')
    rental_amount = db.Column(db.Float, nullable=False)
    id_landlord = db.Column(db.BigInteger, db.ForeignKey('user.user_id', onupdate="CASCADE", ondelete="SET NULL"))
    id_tenant = db.Column(db.BigInteger, db.ForeignKey('user.user_id', onupdate="CASCADE", ondelete="SET NULL"))
    id_property = db.Column(db.UUID(as_uuid=True), db.ForeignKey('property.property_id', onupdate="CASCADE", ondelete="CASCADE"))
    id_listing = db.Column(db.BigInteger, db.ForeignKey('listing.listing_id', onupdate="CASCADE", ondelete="SET NULL"))
    termination_reason = db.Column(db.String(20))
    termination_details = db.Column(db.Text)
    terminated_at = db.Column(db.DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Rental {self.rental_id} status {self.rental_status} landlord {self.id_landlord} tenant {self.id_tenant}>"