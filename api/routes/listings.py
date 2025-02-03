from flask import Blueprint, request, jsonify, abort
from api.models import db, Listing, Property
from api.common.utils import validate_pagination, parse_date
from sqlalchemy import and_, or_

listing_blueprint = Blueprint('listings', __name__)

# get all listings (paginated)

@listing_blueprint.route('/', methods=['GET'])
@validate_pagination
def get_listings(page, page_size):
    
    # filters for listing
    
    filters_map = {
        'rooms': Property.rooms,
        'building_type': Property.building_type,
        'city': Property.city,
        'listing_type': Listing.listing_type,
        'listing_status': Listing.listing_status,
        'price_min': lambda v: Listing.listing_price >= int(v),
        'price_max': lambda v: Listing.listing_price <= int(v),
        'created_at_from': lambda v: Listing.created_at >= parse_date(v),
        'created_at_to': lambda v: Listing.created_at <= parse_date(v),
        'build_year_min': lambda v: Property.build_year >= int(v),
        'build_year_max': lambda v: Property.build_year <= int(v),
    }

    # gathering filters to the list
    filters = []
    for filter_name, filter_val in filters_map.items():
        value = request.args.get(filter_name)
        if value:
            # 
            if callable(filter_val):
                filters.append(filter_val(value)) 
            else:
                filters.append(filter_val == value)

    filtered_listings = db.session.query(Listing).join(Property).filter(and_(*filters))

    listings_page = db.paginate(filtered_listings, page=page, per_page=page_size, max_per_page=100)
        
    return jsonify({
        'data': [
            {
                **listing.to_dict(),
                "property": listing.property.to_dict()
            } for listing in listings_page.items
        ],
        'page': page,
        'pageSize': page_size,
        'total': len(listings_page.items)
    }), 200

# get listing

@listing_blueprint.route('/<int:listing_id>', methods=['GET'])
def get_listing(listing_id):
    
    listing = db.get_or_404(Listing, listing_id, description="Listing not found")
    
    return listing.to_dict(), 200       

# get listing author

@listing_blueprint.route('/<int:listing_id>/author', methods=['GET'])
def get_listing_author(listing_id):
    property = db.get_or_404(Listing, listing_id, description="Listing not found")
    return property.author.to_dict(), 200

# get listing property

@listing_blueprint.route('/<int:listing_id>/property', methods=['GET'])
def get_listing_property(listing_id):
    listing = db.get_or_404(Listing, listing_id, description="Listing not found")
    return listing.property.to_dict(), 200

# get listing applications

@listing_blueprint.route('/<int:listing_id>/applications', methods=['GET'])
@validate_pagination
def get_listing_applications(listing_id, page, page_size):
    listing = db.get_or_404(Listing, listing_id, description="Listing not found")
    listing_applications = listing.applications.paginate(page=page, per_page=page_size)
    return jsonify({
        'data': [appl.to_dict() for appl in listing_applications.items],
        'page': page,
        'pageSize': page_size,
        'total': len(listing_applications.items)
    }), 200
