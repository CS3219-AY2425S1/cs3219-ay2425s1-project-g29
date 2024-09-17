from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin SDK
cred_path = os.getenv('CRED_PATH')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
firebase_app = firebase_admin.initialize_app()

# Initialize Firestore DB
db = firestore.client()

# Create Flask app
app = Flask(__name__)
CORS(app)

REQUIRED_FIELDS = ['title', 'description', 'category', 'difficulty']

def validate_question_data(data):
    missing_fields = [field for field in REQUIRED_FIELDS if field not in data]
    if missing_fields:
        return False, f"Missing fields: {', '.join(missing_fields)}"
    return True, None

@app.route('/questions', methods=['POST'])
def add_question():
    # Get data from request
    question_data = request.json

    # Validate the input data
    is_valid, error_message = validate_question_data(question_data)
    if not is_valid:
        return jsonify({"error": error_message}), 400  # Return bad request

    # Add the question to Firestore
    question_ref = db.collection('questions').add(question_data)

    return jsonify({"id": question_ref[1].id, "message": "Question added"}), 201

@app.route('/questions', methods=['GET'])
def get_questions():
    questions = []
    
    # Retrieve all questions from Firestore
    question_refs = db.collection('questions').stream()
    
    for question in question_refs:
        question_dict = question.to_dict()
        question_dict['id'] = question.id  # Include Firestore document ID
        questions.append(question_dict)
    
    return jsonify(questions), 200

@app.route('/questions/<id>', methods=['DELETE'])
def delete_question(id):
    # Delete a question by its Firestore document ID
    db.collection('questions').document(id).delete()

    return jsonify({"message": "Question deleted"}), 200

@app.route('/questions/<id>', methods=['PUT'])
def update_question(id):
    # Get data from request
    question_data = request.json

    # Validate the input data
    is_valid, error_message = validate_question_data(question_data)
    if not is_valid:
        return jsonify({"error": error_message}), 400  # Return bad request

    # Update the specific question by its Firestore document ID
    question_ref = db.collection('questions').document(id)
    question_ref.update(question_data)

    return jsonify({"message": "Question updated"}), 200


if __name__ == '__main__':
  app.run(debug=True)