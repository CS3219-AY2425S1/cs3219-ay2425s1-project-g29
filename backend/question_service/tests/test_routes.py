import pytest
from app import create_app
from unittest.mock import Mock, patch
import firebase_admin
import json

def test_add_question_success(client, mock_db, sample_question):
    """Test successfully adding a question."""
    # Mock the title uniqueness check
    mock_db.collection().stream.return_value = []
    
    # Mock the document reference
    doc_ref = Mock()
    doc_ref.id = 'test_id'
    mock_db.collection().add.return_value = (None, doc_ref)

    response = client.post('/questions/', 
                         json=sample_question,
                         content_type='application/json')
    
    assert response.status_code == 201
    assert 'test_id' in response.json['id']
    
    # Get the actual argument passed to add
    add_call_args = mock_db.collection().add.call_args[0][0]
    
    # Check individual fields instead of the entire dictionary
    assert add_call_args['title'] == sample_question['title']
    assert add_call_args['description'] == sample_question['description']
    assert set(add_call_args['category']) == set(sample_question['category'])  # Compare as sets
    assert add_call_args['difficulty'] == sample_question['difficulty']
    
    # Verify add was called exactly once
    assert mock_db.collection().add.call_count == 1
    
def test_add_question_duplicate_title(client, mock_db, sample_question):
    """Test adding a question with duplicate title."""
    # Mock existing question with same title
    existing_doc = Mock()
    existing_doc.to_dict.return_value = {'title': sample_question['title']}
    mock_db.collection().stream.return_value = [existing_doc]

    response = client.post('/questions/', 
                         json=sample_question,
                         content_type='application/json')
    
    assert response.status_code == 400
    assert 'already exists' in response.json['error']

def test_get_questions(client, mock_db):
    """Test retrieving all questions."""
    # Mock questions in database
    doc1 = Mock()
    doc1.to_dict.return_value = {'title': 'Question 1'}
    doc1.id = 'id1'
    doc2 = Mock()
    doc2.to_dict.return_value = {'title': 'Question 2'}
    doc2.id = 'id2'
    
    mock_db.collection().stream.return_value = [doc1, doc2]

    response = client.get('/questions/')
    
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]['title'] == 'Question 1'
    assert response.json[1]['title'] == 'Question 2'

def test_get_categories(client, mock_db):
    """Test retrieving all categories."""
    # Mock questions with categories
    doc1 = Mock()
    doc1.to_dict.return_value = {'category': ['python', 'beginner']}
    doc2 = Mock()
    doc2.to_dict.return_value = {'category': ['python', 'advanced']}
    
    mock_db.collection().stream.return_value = [doc1, doc2]

    response = client.get('/questions/categories')
    
    assert response.status_code == 200
    assert set(response.json['categories']) == {'python', 'beginner', 'advanced'}

def test_update_question_success(client, mock_db, sample_question):
    """Test successfully updating a question."""
    # Mock the document exists
    doc_ref = mock_db.collection().document.return_value
    
    # Mock the title uniqueness check (excluding current question)
    existing_doc = Mock()
    existing_doc.to_dict.return_value = {'title': 'Different Title'}
    existing_doc.id = 'different_id'
    mock_db.collection().stream.return_value = [existing_doc]
    
    # Updated question data
    updated_question = sample_question.copy()
    updated_question['title'] = 'Updated Test Question'
    
    response = client.put('/questions/test_id', 
                         json=updated_question,
                         content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['message'] == 'Question updated'
    
    # Get the actual argument passed to update
    update_call_args = doc_ref.update.call_args[0][0]
    
    # Check individual fields instead of the entire dictionary
    assert update_call_args['title'] == updated_question['title']
    assert update_call_args['description'] == updated_question['description']
    assert set(update_call_args['category']) == set(updated_question['category'])  # Compare as sets
    assert update_call_args['difficulty'] == updated_question['difficulty']
    
    # Verify update was called exactly once
    assert doc_ref.update.call_count == 1

def test_update_question_duplicate_title(client, mock_db, sample_question):
    """Test updating a question with a duplicate title."""
    # Mock existing question with same title (different ID)
    existing_doc = Mock()
    existing_doc.to_dict.return_value = {'title': 'Updated Test Question'}
    existing_doc.id = 'different_id'
    mock_db.collection().stream.return_value = [existing_doc]
    
    updated_question = sample_question.copy()
    updated_question['title'] = 'Updated Test Question'
    
    response = client.put('/questions/test_id', 
                         json=updated_question,
                         content_type='application/json')
    
    assert response.status_code == 400
    assert 'already exists' in response.json['error']

def test_update_question_invalid_data(client, mock_db):
    """Test updating a question with invalid data."""
    invalid_question = {
        'title': 'Valid Title',
        'description': 'Valid Description',
        'category': 'invalid_category',  # Should be a list
        'difficulty': 'invalid_difficulty'  # Should be easy/medium/hard
    }
    
    response = client.put('/questions/test_id', 
                         json=invalid_question,
                         content_type='application/json')
    
    assert response.status_code == 400
    assert 'error' in response.json

def test_delete_question_success(client, mock_db):
    """Test successfully deleting a question."""
    response = client.delete('/questions/test_id')
    
    assert response.status_code == 200
    assert response.json['message'] == 'Question deleted'
    mock_db.collection().document.assert_called_once_with('test_id')
    mock_db.collection().document().delete.assert_called_once()

def test_get_single_question_success(client, mock_db):
    """Test successfully retrieving a single question."""
    # Mock the document exists
    doc_ref = mock_db.collection().document.return_value
    doc = Mock()
    doc.exists = True
    doc.to_dict.return_value = {
        'title': 'Test Question',
        'description': 'Test Description',
        'category': ['python'],
        'difficulty': 'medium'
    }
    doc_ref.get.return_value = doc
    
    response = client.get('/questions/test_id')
    
    assert response.status_code == 200
    assert response.json['title'] == 'Test Question'
    assert response.json['category'] == ['python']

def test_get_single_question_not_found(client, mock_db):
    """Test retrieving a non-existent question."""
    # Mock the document doesn't exist
    doc_ref = mock_db.collection().document.return_value
    doc = Mock()
    doc.exists = False
    doc_ref.get.return_value = doc
    
    response = client.get('/questions/nonexistent_id')
    
    assert response.status_code == 404
    assert 'not found' in response.json['error']

def test_update_question_missing_fields(client, mock_db):
    """Test updating a question with missing required fields."""
    incomplete_question = {
        'title': 'Test Question',
        # missing description, category, and difficulty
    }
    
    response = client.put('/questions/test_id', 
                         json=incomplete_question,
                         content_type='application/json')
    
    assert response.status_code == 400
    assert 'Missing fields' in response.json['error']