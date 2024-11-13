from flask import request
from firebase_admin import auth

# Utility function to verify the Firebase token
def verify_token():
    try:
        # Get the Authorization Header
        auth_header = request.headers.get('Authorization')
        
        # Ensure that token is provided
        if not auth_header or not auth_header.startswith("Bearer "):
            return None, "Authorization header missing or invalid", 400
        
        # Extract the token (Format is 'Bearer <token>')
        token = auth_header.split(" ")[1]
        
        # Verify the token with Firebase
        decoded_token = auth.verify_id_token(token)
        return decoded_token, None, 200
    except Exception as e:
        print(str(e))
        return None, str(e), 500
