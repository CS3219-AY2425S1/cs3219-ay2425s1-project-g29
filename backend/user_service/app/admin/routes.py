from . import admin
from flask import jsonify
from firebase_admin import auth, _auth_utils


# Assign the admin role to a specific UID
@admin.route("/users/<uid>/roles/admin", methods=["POST"])
def add_admin(uid):
    try:
        auth.set_custom_user_claims(uid, {"admin": True})
        return jsonify({"message": f"User with UID {uid} promoted to admin"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Remove the admin role from a specific UID
@admin.route("/users/<uid>/roles/admin", methods=["DELETE"])
def remove_admin(uid):
    try:
        auth.set_custom_user_claims(uid, {"admin": False})
        return jsonify({"message": f"User with UID {uid} demoted from admin"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Retrieve all roles assigned to a specific UID
@admin.route("/users/<uid>/roles", methods=["GET"])
def get_roles(uid):
    try:
        user = auth.get_user(uid)
        custom_claims = user.custom_claims or {}
        return jsonify(custom_claims), 200
    except _auth_utils.UserNotFoundError:
        return jsonify({"error": "User not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Check if a specific UID is an admin TODO: Might not need this function in the future
@admin.route("/users/<uid>/is_admin", methods=["GET"])
def is_admin(uid):
    try:
        user = auth.get_user(uid)
        custom_claims = user.custom_claims or {}  # Assume if no custom claims, not admin
        result = custom_claims.get("admin", False)
        return jsonify(result), 200
    except _auth_utils.UserNotFoundError:
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Retrieve a list of all users who have the admin role
@admin.route("/roles/admin/users", methods=["GET"])
def get_admin_users():
    try:
        admin_users = []
        
        # Iterate through a list of all users
        for user in auth.list_users().iterate_all():
            # Get custom claims from a user, assume empty if not initiated
            custom_claims = user.custom_claims or {}
            
            # Check if a user is an admin
            if custom_claims.get("admin") == True:
                user_details = {
                    'uid': user.uid,
                    'email': user.email,
                    'display_name': user.display_name
                }
                admin_users.append(user_details)
        return jsonify(admin_users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
