from . import auth_api
from flask import request, jsonify
from firebase_admin import auth, _auth_utils

@auth_api.route("/verify_token", methods=["POST"])
def verify_firebase_token():
    try:
        # Get the Authorization Header
        auth_header = request.headers.get('Authorization')
        
        # Ensure that token is provided
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization header missing or invalid"}), 400
        
        # Extract the token (Format is 'Bearer <token>')
        token = auth_header.split(" ")[1]
        
        # Verify the token with Firebase
        decoded_token = auth.verify_id_token(token)
        return jsonify({
            "isAdmin": decoded_token.get("admin", False),
            "isValid": True,
        })
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500
