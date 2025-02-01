from api.models import db
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:nikita2004@localhost:5432/real_estate_agency"

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    response = {
        "code": e.code,
        "error": e.name,
        "description": e.description
    }
    return jsonify(response), e.code

db.init_app(app)
