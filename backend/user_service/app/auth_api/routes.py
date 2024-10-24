from . import auth_api
from flask import request, jsonify
from firebase_admin import auth, _auth_utils
from .helper import verify_token

@auth_api.route("/verify_token", methods=["POST"])
def verify_token_endpoint():
    decoded_token, error, status_code = verify_token()

    if error:
        return jsonify({"error", error}), status_code
    
    return jsonify({
        "isAdmin": decoded_token.get("admin", False),
        "isValid": True
    }), 200
