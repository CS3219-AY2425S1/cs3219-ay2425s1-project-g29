# test_matching_service.py

import pytest
from unittest.mock import MagicMock
from flask import Flask
from app.routes import matching_bp
from confluent_kafka import KafkaException
import json


@pytest.fixture
def client(mocker):
    app = Flask(__name__)
    app.register_blueprint(matching_bp)

    mock_redis_client = mocker.patch("app.routes.get_local_redis_client")
    mock_redis = mocker.Mock()
    mock_redis_client.return_value = mock_redis

    mock_redis.hget.return_value = None  # This ensures hget returns None by default

    mock_kafka_producer = mocker.patch("app.routes.get_kafka_producer")
    mock_producer = mocker.Mock()
    mock_kafka_producer.return_value = mock_producer

    mock_validate_user = mocker.patch("app.routes.validate_user")
    mock_validate_user.return_value = True

    mocker.patch("app.routes.delivery_report")

    with app.test_client() as test_client:
        test_client.mock_redis = mock_redis
        yield test_client


def test_match_request_success(client, mocker):
    data = {"user_id": "user123", "category": "math", "difficulty": "easy"}
    headers = {"Authorization": "Bearer valid_token"}

    mock_redis = client.mock_redis
    mock_kafka_producer = mocker.patch("app.routes.get_kafka_producer")
    kafka_mock = mocker.Mock()
    mock_kafka_producer.return_value = kafka_mock

    response = client.post(
        "/matching",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.get_json() == {"message": "User is queued for matching"}

    mock_redis.hset.assert_called_once_with(
        "user:user123",
        mapping={
            "state": "matching",
            "category": "math",
            "difficulty": "easy",
            "request_time": mocker.ANY,
        },
    )
    mock_redis.expire.assert_called_once_with("user:user123", 45)

    kafka_mock.produce.assert_called_once_with(
        "match_requests",
        key="user123",
        value=mocker.ANY,
        callback=mocker.ANY,
    )


def test_match_request_missing_user_id(client):
    data = {"category": "math", "difficulty": "easy"}
    headers = {"Authorization": "Bearer valid_token"}

    response = client.post(
        "/matching",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "user_id is required"}


def test_match_request_invalid_difficulty(client):
    data = {
        "user_id": "user123",
        "category": "math",
        "difficulty": "invalid_difficulty",
    }
    headers = {"Authorization": "Bearer valid_token"}

    response = client.post(
        "/matching",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "difficulty must be one of 'easy', 'medium', or 'hard'"
    }


def test_match_request_invalid_token(client, mocker):
    mock_validate_user = mocker.patch("app.routes.validate_user")
    mock_validate_user.return_value = False

    data = {"user_id": "user123", "category": "math", "difficulty": "easy"}
    headers = {"Authorization": "Bearer invalid_token"}

    response = client.post(
        "/matching",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )

    assert response.status_code == 401
    assert response.get_json() == {"error": "Invalid token"}


def test_cancel_request_success(client):
    user_id = "user123"
    headers = {"Authorization": "Bearer valid_token"}

    mock_redis = client.mock_redis
    mock_redis.hget.side_effect = [
        b"matching",
        b"math",
        b"easy",
    ]

    response = client.post(f"/cancel/{user_id}", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == {"message": "Matching request cancelled"}


def test_cancel_request_no_matching_request(client):
    user_id = "user123"
    headers = {"Authorization": "Bearer valid_token"}

    mock_redis = client.mock_redis
    mock_redis.hget.return_value = None

    response = client.post(f"/cancel/{user_id}", headers=headers)

    assert response.status_code == 404
    assert response.get_json() == {"error": "No matching request found for user"}


def test_cancel_request_already_cancelled(client):
    user_id = "user123"
    headers = {"Authorization": "Bearer valid_token"}

    mock_redis = client.mock_redis
    mock_redis.hget.side_effect = [
        b"cancelled",
    ]

    response = client.post(f"/cancel/{user_id}", headers=headers)

    assert response.status_code == 400
    assert response.get_json() == {"error": "Matching request already cancelled"}


def test_cancel_request_match_completed(client):
    user_id = "user123"
    headers = {"Authorization": "Bearer valid_token"}

    mock_redis = client.mock_redis
    mock_redis.hget.side_effect = [
        b"completed",
    ]

    response = client.post(f"/cancel/{user_id}", headers=headers)

    assert response.status_code == 400
    assert response.get_json() == {"error": "Match completed"}


def test_match_request_user_already_in_queue(client, mocker):
    mock_can_add_to_queue = mocker.patch("app.routes.can_add_to_queue")
    mock_can_add_to_queue.return_value = False

    data = {"user_id": "user123", "category": "math", "difficulty": "easy"}
    headers = {"Authorization": "Bearer valid_token"}

    response = client.post(
        "/matching",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "User is already in the queue"}


def test_match_request_kafka_exception(client, mocker):
    mock_kafka_producer = mocker.patch("app.routes.get_kafka_producer")
    mock_producer = mocker.Mock()
    mock_producer.produce.side_effect = KafkaException("Kafka error")
    mock_kafka_producer.return_value = mock_producer

    data = {"user_id": "user123", "category": "math", "difficulty": "easy"}
    headers = {"Authorization": "Bearer valid_token"}

    response = client.post(
        "/matching",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )

    assert response.status_code == 500
    assert response.get_json() == {
        "error": "Failed to send message to Kafka",
        "details": "Kafka error",
    }
