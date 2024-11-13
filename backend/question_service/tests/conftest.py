# tests/conftest.py
import pytest
from app import create_app
from unittest.mock import Mock, patch
import firebase_admin
import json

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    with patch('firebase_admin.initialize_app') as mock_firebase_init:
        app = create_app()
        yield app

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def mock_db():
    """Mock Firestore database operations."""
    with patch('app.main.routes.db') as mock_db:
        yield mock_db

@pytest.fixture
def sample_question():
    """Sample valid question data."""
    return {
        'title': 'Test Question',
        'description': 'Test Description',
        'category': ['python', 'testing'],
        'difficulty': 'medium'
    }