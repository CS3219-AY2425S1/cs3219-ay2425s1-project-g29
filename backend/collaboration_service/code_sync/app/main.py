from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin SDK
cred_path = os.getenv('CRED_PATH')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
firebase_admin.initialize_app()

# Firestore reference for syncing code changes
db = firestore.client()

# Create Flask app
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Function to update the code in Firestore
def update_code_in_firestore(session_id, code_content):
    try:
        db.collection('collaborations').document(session_id).set({
            'code': code_content
        }, merge=True)
        return True
    except Exception as e:
        print(f"Error updating Firestore: {e}")
        return False

# API to get the current code for a session
@app.route('/collaboration/<session_id>', methods=['GET'])
def get_code(session_id):
    try:
        doc_ref = db.collection('collaborations').document(session_id)
        doc = doc_ref.get()
        if doc.exists:
            return jsonify(doc.to_dict()), 200
        else:
            return jsonify({"error": "Session not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to save initial code for a session
@app.route('/collaboration/<session_id>', methods=['POST'])
def create_session(session_id):
    try:
        data = request.json
        code_content = data.get('code', '')
        db.collection('collaborations').document(session_id).set({
            'code': code_content
        })
        return jsonify({"message": "Session created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# WebSocket to handle real-time code sync
@socketio.on('sync_code')
def sync_code(data):
    session_id = data['session_id']
    code_content = data['code']
    
    # Broadcast code to other connected clients
    emit('code_update', {'code': code_content}, broadcast=True, include_self=False)
    
    # Update Firestore with the new code content
    update_code_in_firestore(session_id, code_content)

# WebSocket to join a session
@socketio.on('join_session')
def join_session(data):
    session_id = data['session_id']
    emit('joined', {'message': f'Joined session {session_id}'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
