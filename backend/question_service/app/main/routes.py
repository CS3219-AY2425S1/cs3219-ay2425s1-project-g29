from . import main
from flask import jsonify, request, Response
from firebase_admin import firestore

db = firestore.client()

REQUIRED_FIELDS = ['title', 'description', 'category', 'difficulty']

def validate_question_data(data):
    # Check for missing fields
    missing_fields = [field for field in REQUIRED_FIELDS if field not in data]
    if missing_fields:
        return False, f"Missing fields: {', '.join(missing_fields)}"
    
    # Validate title
    if not isinstance(data['title'], str):
        return False, "Title must be a string."

    # Validate description
    if not isinstance(data['description'], str):
        return False, "Description must be a string."

    # Validate category
    if not isinstance(data['category'], list) or not all(isinstance(cat, str) for cat in data['category']):
        return False, "Category must be an array of strings."

    # Remove duplicates in the category
    data['category'] = list(set(data['category']))

    # Validate difficulty
    valid_difficulties = ['easy', 'medium', 'hard']
    if not isinstance(data['difficulty'], str) or data['difficulty'].lower() not in valid_difficulties:
        return False, "Difficulty must be one of 'easy', 'medium', or 'hard'."

    return True, None

def is_title_unique(title, exclude_id=None):
    """
    Check if the question title is unique.
    If `exclude_id` is provided, the question with that ID will be excluded from the uniqueness check (useful for updates).
    """
    questions_ref = db.collection('questions')
    normalized_title = title.strip().lower()

    query = questions_ref.stream()

    for doc in query:
        doc_data = doc.to_dict()
        existing_title = doc_data['title'].strip().lower()
        if existing_title == normalized_title and (exclude_id is None or doc.id != exclude_id):
            return False 
    return True

@main.route("/categories", methods=["GET"])
def get_categories():
    try:
        # Retrieve all questions from Firestore
        questions_ref = db.collection('questions').stream()
        
        # Set to store unique categories
        unique_categories = set()
        
        # Iterate through all questions and add categories to the set
        for question in questions_ref:
            question_data = question.to_dict()
            categories = question_data.get('category', [])
            
            # Add each category from the array to our set
            unique_categories.update(categories)
        
        # Convert set to sorted list for consistent output
        categories_list = sorted(list(unique_categories))
        
        return jsonify({"categories": categories_list}), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve categories: {str(e)}"}), 500

@main.route("/", methods=["POST"], strict_slashes=False)
def add_question():
    # Get data from request
    question_data = request.json

    # Validate the input data
    is_valid, error_message = validate_question_data(question_data)
    if not is_valid:
        return jsonify({"error": error_message}), 400  # Return bad request

    # Check if the title is unique
    if not is_title_unique(question_data['title']):
        return jsonify({"error": "A question with the same title already exists."}), 400

    # Add the question to Firestore
    question_ref = db.collection('questions').add(question_data)

    return jsonify({"id": question_ref[1].id, "message": "Question added"}), 201

@main.route("/", methods=["GET"])
def get_questions():
    questions = []
    
    # Retrieve all questions from Firestore
    question_refs = db.collection('questions').stream()
    
    for question in question_refs:
        question_dict = question.to_dict()
        question_dict['id'] = question.id  # Include Firestore document ID
        questions.append(question_dict)
    
    return jsonify(questions), 200

@main.route("/<id>", methods=["GET"])
def get_question(id):
    try:
        questions = []
        
        # Retrieve all questions from Firestore
        question_ref = db.collection('questions').document(id)

        question = question_ref.get()
        if question.exists:
            return jsonify(question.to_dict()), 200
        else:
            return jsonify({"error": "Question not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/<id>", methods=["DELETE"])
def delete_question(id):
    # Delete a question by its Firestore document ID
    db.collection('questions').document(id).delete()

    return jsonify({"message": "Question deleted"}), 200

@main.route("/<id>", methods=["PUT"])
def update_question(id):
    # Get data from request
    question_data = request.json

    # Validate the input data
    is_valid, error_message = validate_question_data(question_data)
    if not is_valid:
        return jsonify({"error": error_message}), 400  # Return bad request

    # Check if the title is unique (excluding the current question's ID)
    if not is_title_unique(question_data['title'], exclude_id=id):
        return jsonify({"error": "A question with the same title already exists."}), 400


    # Update the specific question by its Firestore document ID
    question_ref = db.collection('questions').document(id)
    question_ref.update(question_data)

    return jsonify({"message": "Question updated"}), 200

# @main.before_request
def before_request():
    headers = { 'Access-Control-Allow-Origin': '*', 
               'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS', 
               'Access-Control-Allow-Headers': 'Content-Type' } 
    if request.method == 'OPTIONS' or request.method == 'options': return jsonify(headers), 200