from app.auth_api.helper import verify_token
from flask import Blueprint, request, jsonify
from firebase_admin import firestore

history = Blueprint('attempt_history', __name__)

firebase_db = firestore.client()

@history.route("/history", methods=["POST"])
def record_attempt():
    try:
        match_data = request.json
        
        user1_id = match_data['user1_id']
        user2_id = match_data['user2_id']
        session_id = match_data['uid']
        question_id = match_data['question_id']
        timestamp = match_data['timestamp']
        
        user1_ref = firebase_db.collection('attempt_history').document(user1_id).collection('attempts').document(session_id)
        user2_ref = firebase_db.collection('attempt_history').document(user2_id).collection('attempts').document(session_id)

        attempt_user1 = {
            "matched_user": user2_id,
            "question_id": question_id,
            "timestamp": timestamp
        }
        
        attempt_user2 = {
            "matched_user": user1_id,
            "question_id": question_id,
            "timestamp": timestamp
        }
        
        user1_ref.set(attempt_user1)
        user2_ref.set(attempt_user2)
        
        return jsonify({"message": "Success!"}), 200

    except Exception as e:
        return jsonify({"error": "Failed to record match", 
                        "details": str(e)}), 500
    

@history.route("/<uid>/history", methods=["GET"])
def get_user_history(uid):
    # decoded_token, error, status_code = verify_token()

    # if error:
    #     return jsonify({"error": error}), status_code
    
    # if decoded_token["user_id"] != uid:
    #     return jsonify({
    #         "error": "You are not authorized to view this user's history"
    #         }), 403
    
    # Fetch User's History
    user_history_ref = firebase_db.collection('attempt_history').document(uid).collection('attempts')
    
    # Fetch all documents in user's attempts subcollection
    attempts = user_history_ref.get()
    
    attempt_history = []
    for attempt in attempts:
        attempt_data = attempt.to_dict()
        attempt_history.append({
            "session_id": attempt.id,
            "matched_user": attempt_data.get("matched_user"),
            "question_id": attempt_data.get("question_id"),
            "timestamp": attempt_data.get("timestamp")
        })
        
    return jsonify(attempt_history), 200
