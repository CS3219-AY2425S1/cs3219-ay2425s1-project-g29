from flask import Blueprint
from flask_cors import CORS

main = Blueprint('main', __name__)
CORS(main)

from . import routes