from flask import Blueprint, request, jsonify, abort
from api.models import db, Property
from api.common.utils import validate_pagination

property_blueprint = Blueprint('properties', __name__)

# get all properties (paginated)

@property_blueprint.route('/', methods=['GET'])
@validate_pagination
def get_properties(page, page_size):
    
    property_page = db.paginate(db.select(Property), page=page, per_page=page_size, max_per_page=100)
        
    return jsonify({
        'data': [prop.to_dict() for prop in property_page.items],
        'page': page,
        'pageSize': page_size,
        'total': len(property_page.items)
    }), 200

# get property by uuid

@property_blueprint.route('/<uuid:property_id>', methods=['GET'])
def get_property(property_id):
    
    property = db.get_or_404(Property, property_id, description="Property not found")
    
    return property.to_dict(), 200       

# get property owner by uuid

@property_blueprint.route('/<uuid:property_id>/owner', methods=['GET'])
def get_property_owner(property_id):
    property = db.get_or_404(Property, property_id, description="Property not found")
    owner = property.owner
    return owner.to_dict(), 200

# get property listings by uuid

@property_blueprint.route('/<uuid:property_id>/listings', methods=['GET'])
@validate_pagination
def get_property_listings(property_id, page, page_size):
    property = db.get_or_404(Property, property_id, description="Property not found")
    property_listings = property.listings.paginate(page=page, per_page=page_size)
    return jsonify({
        'data': [listing.to_dict() for listing in property_listings.items],
        'page': page,
        'pageSize': page_size,
        'total': len(property_listings.items)
    }), 200