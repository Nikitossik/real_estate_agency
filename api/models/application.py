from . import db, BaseModel
from sqlalchemy import func

class Application(BaseModel):
    __tablename__ = 'application'

    application_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_listing = db.Column(db.BigInteger, db.ForeignKey('listing.listing_id', onupdate="CASCADE", ondelete="CASCADE"))
    id_user = db.Column(db.BigInteger, db.ForeignKey('user.user_id', onupdate="CASCADE", ondelete="SET NULL"))
    application_message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_submitted = db.Column(db.Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<Application {self.application_id} sent by User {self.id_user} creted at {self.created_at}>"