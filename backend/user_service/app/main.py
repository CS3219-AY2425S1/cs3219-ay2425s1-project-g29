from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin SDK
cred_path = os.getenv('CRED_PATH')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
firebase_app = firebase_admin.initialize_app()

# Create Flask app
app = Flask(__name__)
CORS(app)

def user_to_dict(user):
    return {
        'uid': user.uid,
        'email': user.email,
        'display_name': user.display_name,
        'phone_number': user.phone_number,
        'email_verified': user.email_verified,
    }

@app.route('/users', methods=['GET'])
def users():
    try:
        users = auth.list_users().iterate_all()
        user_list = [user_to_dict(user) for user in users]
        return jsonify(users=user_list)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/users/<uid>', methods=['GET'])
def get_user(uid):
    try:
        user = auth.get_user(uid)
        # user = user_to_dict(user)
        return jsonify(user=user._data)
    except auth.UserNotFoundError:
        return jsonify(error="User not found"), 404

@app.route('/users/active', methods=['GET'])
def active_users():
    try:
        # Define the threshold for active users (e.g., active in the last 15 minutes)
        threshold = datetime.now() - timedelta(minutes=15)

        # Get all users
        all_users = auth.list_users().iterate_all()
        
        active_users = []
        for user in all_users:
            user_data = user._data  # Access the nested user data
            last_login_at = user_data["lastLoginAt"]
            if last_login_at:
                # Convert Unix timestamp to datetime
                last_login_datetime = datetime.fromtimestamp(int(last_login_at) / 1000)
                if last_login_datetime > threshold:
                    active_users.append({
                        'displayName': user_data["displayName"],
                        'email': user_data["email"],
                        'lastLoginAt': last_login_at,
                        'uid': user_data["localId"]
                    })

        return jsonify(active_users=active_users)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/users/<uid>', methods=['DELETE'])
def delete_user(uid):
    try:
        # Delete the user using Firebase Auth
        auth.delete_user(uid)

        return jsonify({"message": f"User with UID {uid} deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Failed to delete user", "details": str(e)}), 500

# TODO: GET PATCHING USER TO WORK
@app.route('/users/<uid>', methods=['PATCH'])
def patch_user(uid):
    try:
        # Extract fields to update from the request body
        data = request.json

        # Prepare arguments for updating the user
        user_updates = {}

        if 'displayName' in data:
            user_updates['displayName'] = data['displayName']
        if 'email' in data:
            user_updates['email'] = data['email']
        
        # Update user with the given fields
        updated_user = auth.update_user(uid, **user_updates)

        return jsonify({
            "message": f"User with UID {uid} updated successfully",
            "updated_user": {
                "displayName": updated_user.display_name,
                "email": updated_user.email
            }
        }), 200

    except Exception as e:
        return jsonify({"error": "Failed to update user", "details": str(e)}), 500

if __name__ == '__main__':
  app.run(debug=True)