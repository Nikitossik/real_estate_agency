from . import db, BaseModel
from sqlalchemy import func
import uuid

class Sale(BaseModel):
    tablename = 'sale'

    sale_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_status = db.Column(db.String(10), nullable=False, default='active')
    sale_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    id_owner = db.Column(db.BigInteger, db.ForeignKey('user.user_id', onupdate="CASCADE", ondelete="SET NULL"))
    id_buyer = db.Column(db.BigInteger, db.ForeignKey('user.user_id', onupdate="CASCADE", ondelete="SET NULL"))
    id_property = db.Column(db.UUID(as_uuid=True), db.ForeignKey('property.property_id', onupdate="CASCADE", ondelete="CASCADE"))
    id_listing = db.Column(db.BigInteger, db.ForeignKey('listing.listing_id', onupdate="CASCADE", ondelete="SET NULL"))
    termination_reason = db.Column(db.String(20))
    termination_details = db.Column(db.Text)
    terminated_at = db.Column(db.DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Sale {self.sale_id} status {self.sale_status} buyer {self.id_buyer} owner {self.id_owner} at {self.created_at}>"