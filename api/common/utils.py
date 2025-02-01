from flask import request, abort
from functools import wraps
import re
from datetime import datetime

# mainly for user

def validate_required_fields(data, fields):
    for field in fields:
        if field not in data:
            abort(400, description=f"Field '{field}' is required")
            
def validate_email(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        abort(400, description="Invalid email format")

def validate_phone(phone):
    if not re.match(r"^\+?\d{1,3}?\(?\d{1,4}?\)?[\d\s\-]{6,15}$", phone):
        abort(400, description="Invalid phone number format")

def validate_bank_account(bank_account):
    if len(bank_account) != 16 or not bank_account.isdigit():
        abort(400, description="Invalid bank account format")
        
# validating pagination params

def validate_pagination(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 50, type=int)
        
        if page < 1 or page_size < 1:
            abort(400, description="'page' and 'page_size' must be positive integers.")
        if page_size > 100:
            abort(400, description="'page_size' cannot exceed 100.")
        
        kwargs['page'] = page
        kwargs['page_size'] = page_size
        return f(*args, **kwargs)
    return wrapper

# iso date parsing

def parse_date(date_str):
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        abort(400, description=f"Invalid date format for {date_str}. Use 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS'.")