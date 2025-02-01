from . import db, BaseModel

class User(BaseModel):
    
    __tablename__ = 'user'
    
    user_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(30), nullable=False)
    user_surname = db.Column(db.String(30), nullable=False)
    user_email = db.Column(db.String(100), unique=True, nullable=False)
    user_phone = db.Column(db.String(20), nullable=False)
    bank_account = db.Column(db.String(16), nullable=False)
    
    properties = db.relationship("Property", backref='owner', lazy='dynamic')
    listings = db.relationship("Listing", backref='author', lazy='dynamic')
    applications = db.relationship("Application", backref='author', lazy='dynamic')
    # payments = db.relationship("Payment", backref="sender", lazy="dynamic")
    
    def __repr__(self):
        return f"<User {self.user_id} {self.user_name} {self.user_surname}>"
    