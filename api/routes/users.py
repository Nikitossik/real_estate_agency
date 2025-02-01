from flask import Blueprint, request, jsonify, abort
from api.models import User, db
from api.common.utils import *

user_blueprint = Blueprint('users', __name__)

def validate_user_data(data):

    required_fields = ['user_name', 'user_surname', 'user_email', 'user_phone', 'bank_account']
    
    if not data:
        abort(400, description="No data provided")
    
    validate_required_fields(data=data, fields=required_fields)
    
    if data['user_name'] == '' or data['user_surname'] == '':
        abort(400, description="Name and surname must not be empty")
    
    validate_email(data['user_email'])    
    validate_phone(data['user_phone'])
    validate_bank_account(data['bank_account'])
    
# get all users (paginated)

@user_blueprint.route('/', methods=['GET'])
@validate_pagination
def get_users(page, page_size):
    
    users_page = db.paginate(db.select(User), page=page, per_page=page_size, max_per_page=100)
        
    return jsonify({
        'data': [user.to_dict() for user in users_page.items],
        'page': page,
        'pageSize': page_size,
        'total': len(users_page.items)
    }), 200

# adding a user

@user_blueprint.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    
    validate_user_data(data=data)
    
    if db.session.query(User).filter(User.user_email == data['user_email']).first():
        abort(400, description=f"Email {data['user_email']} already exists")
        
    new_user = User(
        user_name=data['user_name'],
        user_surname=data['user_surname'],
        user_email=data['user_email'],
        user_phone=data['user_phone'],
        bank_account=data['bank_account']
    )
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Error creating user: {str(e)}")

    return new_user.to_dict(), 201

# full data modification for user

@user_blueprint.route('/<int:user_id>', methods=["PUT"])
def modify_user(user_id):
    data = request.get_json()
    
    user = db.get_or_404(User, user_id, description="User not found")
    
    validate_user_data(data=data)
    
    # if another user has the same email in data
    
    if db.session.query(User).filter(User.user_email == data['user_email'], User.user_id != user_id).first():
        abort(400, description=f"Email {data['user_email']} already exists")
    
    user.user_name = data.get('user_name', user.user_name)
    user.user_surname = data.get('user_surname', user.user_surname)
    user.user_email = data.get('user_email', user.user_email)
    user.user_phone = data.get('user_phone', user.user_phone)
    user.bank_account = data.get('bank_account', user.bank_account)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Error updating user: {str(e)}")

    return user.to_dict(), 200
    

# delete user

@user_blueprint.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = db.get_or_404(User, user_id, description="User not found")
    user_data = user.to_dict()
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Error deleting user: {str(e)}")
        
    return user_data, 200


# get user by id

@user_blueprint.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    
    user = db.get_or_404(User, user_id, description="User not found")
    
    return user.to_dict(), 200       

# get properties of the user

@user_blueprint.route('/<int:user_id>/properties', methods=['GET'])
@validate_pagination
def get_user_properties(user_id, page, page_size):
    user = db.get_or_404(User, user_id, description="User not found")
    user_properties = user.properties.paginate(page=page, per_page=page_size)
        
    return jsonify({
        'data': [prop.to_dict() for prop in user_properties.items],
        'page': page,
        'pageSize': page_size,
        'total': len(user_properties.items)
    }), 200
    

# get listings of the user

@user_blueprint.route('/<int:user_id>/listings', methods=['GET'])
@validate_pagination
def get_user_listings(user_id, page, page_size):
    user = db.get_or_404(User, user_id, description="User not found")
    user_listings = user.listings.paginate(page=page, per_page=page_size)
        
    return jsonify({
        'data': [listing.to_dict() for listing in user_listings.items],
        'page': page,
        'pageSize': page_size,
        'total': len(user_listings.items)
    }), 200
    
# get applications of the user

@user_blueprint.route('/<int:user_id>/applications', methods=['GET'])
@validate_pagination
def get_user_applications(user_id, page, page_size):
    user = db.get_or_404(User, user_id, description="User not found")
    user_applications = user.applications.paginate(page=page, per_page=page_size)
        
    return jsonify({
        'data': [appl.to_dict() for appl in user_applications.items],
        'page': page,
        'pageSize': page_size,
        'total': len(user_applications.items)
    }), 200