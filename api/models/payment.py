from . import db, BaseModel
from sqlalchemy import func

class Payment(BaseModel):
    tablename = 'payment'

    payment_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    payment_amount = db.Column(db.Float, nullable=False)
    id_sender = db.Column(db.BigInteger, db.ForeignKey('user.user_id', onupdate="CASCADE", ondelete="CASCADE"))
    id_sale = db.Column(db.UUID(as_uuid=True), db.ForeignKey('sale.sale_id', onupdate="CASCADE", ondelete="CASCADE"))
    sent_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Payment {self.payment_id} from User {self.id_sender} at {self.sent_at}>"