import pytest
from unittest.mock import patch, Mock
from app.kafka_consumer import process_match_result, find_matching_question
from confluent_kafka import KafkaError

@pytest.fixture
def mock_firestore():
    with patch('app.kafka_consumer.db') as mock_db:
        yield mock_db

def test_find_matching_question(mock_firestore):
    """Test finding a matching question."""
    # Mock question document
    question_doc = Mock()
    question_doc.to_dict.return_value = {
        'title': 'Test Question',
        'difficulty': 'medium',
        'category': ['python']
    }
    question_doc.id = 'test_id'
    
    # Mock query results
    mock_query = Mock()
    mock_query.stream.return_value = [question_doc]
    mock_firestore.collection().where().where().limit.return_value = mock_query

    result = find_matching_question('python', 'medium')
    
    assert result['id'] == 'test_id'
    assert result['title'] == 'Test Question'
    assert result['difficulty'] == 'medium'

def test_process_match_result_with_match(mock_firestore):
    """Test processing match result with a matching question."""
    # Mock finding a matching question
    with patch('app.kafka_consumer.find_matching_question') as mock_find:
        mock_find.return_value = {
            'id': 'test_id',
            'title': 'Test Question',
            'difficulty': 'medium'
        }
        
        match_result = {
            'category': 'python',
            'difficulty': 'medium',
            'user1_id': 'user1'
        }
        
        result = process_match_result(match_result)
        
        assert result['question_id'] == 'test_id'
        assert result['question_title'] == 'Test Question'
        assert result['match_difficulty'] == 'medium'
        assert result['actual_difficulty'] == 'medium'

def test_process_match_result_no_match(mock_firestore):
    """Test processing match result with no matching question."""
    with patch('app.kafka_consumer.find_matching_question') as mock_find:
        mock_find.return_value = None
        
        match_result = {
            'category': 'nonexistent',
            'difficulty': 'medium',
            'user1_id': 'user1'
        }
        
        result = process_match_result(match_result)
        
        assert result['question_id'] == 'unknown'
        assert result['status'] == 'no_question'