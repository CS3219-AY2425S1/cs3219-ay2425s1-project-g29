from flask import Blueprint

auth_api = Blueprint('auth_api', __name__)

from . import routes