from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from flask_swagger_ui import get_swaggerui_blueprint

from api.routes import *
from api.models import *

# initializing the Flask app

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:nikita2004@localhost:5432/real_estate_agency"

#global error handler

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    response = {
        "code": e.code,
        "error": e.name,
        "description": e.description
    }
    return jsonify(response), e.code

db.init_app(app)

# swaggerui route

SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Real Estate Agency API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# api routes

app.register_blueprint(user_blueprint, url_prefix='/api/users')
app.register_blueprint(property_blueprint, url_prefix='/api/properties')
app.register_blueprint(listing_blueprint, url_prefix='/api/listings')
app.register_blueprint(application_blueprint, url_prefix='/api/applications')


if __name__ == '__main__':
    app.run(debug=True)
