from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True 

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


from .user import User
from .property import Property
from .listing import Listing
from .application import Application
from .payment import Payment
from .sale import Sale
from .rental import Rental

__all__ = ["db", "User", "Property", "Listing", "Application", "Payment", "Sale", "Rental"]