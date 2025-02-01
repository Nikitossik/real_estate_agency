from flask import Blueprint, request, jsonify, abort
from api.models import db, Application

from api.common.utils import validate_pagination

application_blueprint = Blueprint('applications', __name__)

# get all applications (paginated)

@application_blueprint.route('/', methods=['GET'])
@validate_pagination
def get_applications(page, page_size):
    
    application_page = db.paginate(db.select(Application), page=page, per_page=page_size, max_per_page=100)
        
    return jsonify({
        'data': [appl.to_dict() for appl in application_page.items],
        'page': page,
        'pageSize': page_size,
        'total': len(application_page.items)
    }), 200

# get application

@application_blueprint.route('/<int:application_id>', methods=['GET'])
def get_application(application_id):
    
    property = db.get_or_404(Application, application_id, description="Application not found")
    
    return property.to_dict(), 200       

# get application author

@application_blueprint.route('/<int:application_id>/author', methods=['GET'])
def get_application_author(application_id):
    application = db.get_or_404(Application, application_id, description="Application not found")
    return application.author.to_dict(), 200

# get application listing

@application_blueprint.route('/<int:application_id>/listing', methods=['GET'])
def get_application_listing(application_id):
    application = db.get_or_404(Application, application_id, description="Application not found")
    return application.listing.to_dict(), 200