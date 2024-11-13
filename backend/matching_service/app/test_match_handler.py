import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

import pytest
from unittest import mock
from unittest.mock import MagicMock, call
from app.match_handler import (
    process_message,
    find_and_handle_match,
    push_to_kafka,
)
import redis


@pytest.fixture
def mock_redis_client(mocker):
    mock_redis = mocker.Mock()
    mocker.patch("app.match_handler.redis_client", mock_redis)
    return mock_redis


@pytest.fixture
def mock_kafka_producer(mocker):
    mock_producer = mocker.Mock()
    mocker.patch("app.match_handler.get_kafka_producer", return_value=mock_producer)
    return mock_producer


@pytest.fixture
def mock_time(mocker):
    mock_time = mocker.patch("time.time")
    mock_time.return_value = 1000
    return mock_time


def test_process_message(mock_redis_client, mock_kafka_producer, mocker, mock_time):
    message = {
        "user_id": "user124",
        "category": "science",
        "difficulty": "hard",
        "request_time": 1000,
    }

    mocker.patch("app.match_handler.remove_expired_entries")
    mocker.patch("app.match_handler.get_available_matching_requests")

    mock_find_and_handle_match = mocker.patch("app.match_handler.find_and_handle_match")
    mock_find_and_handle_match.side_effect = [None, True]

    process_message(message, mock_kafka_producer)

    assert mock_find_and_handle_match.call_count == 2
    mock_find_and_handle_match.assert_has_calls(
        [
            call(
                mock_redis_client,
                mock.ANY,
                "user124",
                "c_matching:science:hard",
                "p_matching:science",
                mock_time.return_value,
                "complete",
                mock_kafka_producer,
                "science",
                "hard",
                1000,
            ),
            call(
                mock_redis_client,
                mock.ANY,
                "user124",
                "c_matching:science:hard",
                "p_matching:science",
                mock_time.return_value,
                "partial",
                mock_kafka_producer,
                "science",
                "hard",
                1000,
            ),
        ]
    )
    mock_redis_client.pipeline.return_value.zadd.assert_not_called()
    mock_redis_client.pipeline.return_value.execute.assert_not_called()


def test_process_message_no_match_add_to_queue(
    mock_redis_client, mock_kafka_producer, mocker, mock_time
):
    message = {
        "user_id": "user125",
        "category": "history",
        "difficulty": "medium",
        "request_time": 1000,
    }

    mocker.patch("app.match_handler.remove_expired_entries")
    mocker.patch("app.match_handler.get_available_matching_requests")

    mock_find_and_handle_match = mocker.patch("app.match_handler.find_and_handle_match")
    mock_find_and_handle_match.side_effect = [None, None]

    mock_pipeline = mocker.Mock()
    mock_redis_client.pipeline.return_value = mock_pipeline

    process_message(message, mock_kafka_producer)

    assert mock_find_and_handle_match.call_count == 2
    mock_pipeline.zadd.assert_has_calls(
        [
            call(
                f'c_matching:{message["category"]}:{message["difficulty"]}',
                {message["user_id"]: 1030},
            ),
            call(
                f'p_matching:{message["category"]}',
                {f'{message["user_id"]}:{message["difficulty"]}': 1030},
            ),
        ]
    )
    mock_pipeline.execute.assert_called_once()


def test_find_and_handle_match_complete_success(
    mock_redis_client, mock_kafka_producer, mocker, mock_time
):
    user_id = "user123"
    key = "c_matching:math:easy"
    category_key = "p_matching:math"
    current_time = 1000
    match_type = "complete"
    category = "math"
    difficulty = "easy"
    request_time = 1000

    mock_redis_client.zrangebyscore.return_value = [b"user456"]

    mock_can_proceed = mocker.patch("app.match_handler.can_proceed")
    mock_can_proceed.return_value = {"can_proceed": True, "cancelled_users": []}

    mock_pipeline = mocker.Mock()
    mock_redis_client.pipeline.return_value = mock_pipeline

    mock_push_to_kafka = mocker.patch("app.match_handler.push_to_kafka")

    result = find_and_handle_match(
        mock_redis_client,
        mock_pipeline,
        user_id,
        key,
        category_key,
        current_time,
        match_type,
        mock_kafka_producer,
        category,
        difficulty,
        request_time,
    )

    assert result is True

    mock_push_to_kafka.assert_called_once_with(
        match_type, user_id, "user456", category, difficulty, mock_kafka_producer
    )

    mock_pipeline.zrem.assert_has_calls(
        [
            call(key, "user456"),
            call(category_key, "user456:easy"),
        ]
    )

    mock_pipeline.execute.assert_called_once()


def test_find_and_handle_partial_match(mock_redis_client, mock_kafka_producer, mocker):
    user_id = "user123"
    match_user_id = "user456"
    key = "c_matching:math:easy"
    category_key = "p_matching:math"
    current_time = 1000
    category = "math"
    difficulty = "easy"
    request_time = 1000

    match_type = "partial"
    match_difficulty = "medium"

    mock_pipeline = mocker.Mock()
    mock_redis_client.pipeline.return_value = mock_pipeline
    mock_redis_client.zrangebyscore.return_value = [
        f"{match_user_id}:{match_difficulty}".encode()
    ]
    mock_redis_client.pipeline.return_value = mock_pipeline

    mock_can_proceed = mocker.patch("app.match_handler.can_proceed")
    mock_can_proceed.return_value = {"can_proceed": True, "cancelled_users": []}

    mock_push_to_kafka = mocker.patch("app.match_handler.push_to_kafka")

    result = find_and_handle_match(
        mock_redis_client,
        mock_pipeline,
        user_id,
        key,
        category_key,
        current_time,
        match_type,
        mock_kafka_producer,
        category,
        difficulty,
        request_time,
    )

    assert result is True
    mock_push_to_kafka.assert_called_once_with(
        match_type, user_id, match_user_id, category, difficulty, mock_kafka_producer
    )

    mock_pipeline.zrem.assert_any_call(
        f"c_matching:{category}:{match_difficulty}", match_user_id
    )
    mock_pipeline.zrem.assert_any_call(
        category_key, f"{match_user_id}:{match_difficulty}"
    )
    mock_pipeline.execute.assert_called_once()


def test_process_message_watch_error(
    mock_redis_client, mock_kafka_producer, mocker, mock_time
):
    message = {
        "user_id": "user126",
        "category": "art",
        "difficulty": "easy",
        "request_time": 1000,
    }

    mocker.patch("app.match_handler.remove_expired_entries")
    mocker.patch("app.match_handler.get_available_matching_requests")

    mock_redis_client.watch.side_effect = redis.WatchError

    mock_pipeline = mocker.Mock()
    mock_redis_client.pipeline.return_value = mock_pipeline

    process_message(message, mock_kafka_producer)

    assert mock_redis_client.watch.called
    mock_pipeline.execute.assert_not_called()
