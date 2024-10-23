from flask import Blueprint, request, jsonify
import time
from confluent_kafka import Producer, KafkaException
import json
import requests
import os
import uuid
from .redis_client import can_add_to_queue, get_redis_client
from .kafka_producer import get_kafka_producer
import logging

logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

matching_bp = Blueprint(
    "matching",
    __name__,
)


producer_config = {
    "bootstrap.servers": "kafka:9092",
    "client.id": "matching-request",
}
redis_client = None


def get_local_redis_client():
    global redis_client
    if redis_client is None:
        redis_client = get_redis_client(logger)
    return redis_client


@matching_bp.route("/cancel/<user_id>", methods=["POST"])
def cancel_request(user_id):
    logger.info(f"Cancel request for user {user_id}")
    redis_client = get_local_redis_client()
    state = redis_client.hget(f"user:{user_id}", "state")
    token = request.headers.get("Authorization")
    if not validate_user(token):
        return jsonify({"error": "Invalid token"}), 401
    if not state:
        logger.error(f"No matching request found for user {user_id}")
        return jsonify({"error": "No matching request found for user"}), 404
    current_state = state.decode("utf-8")
    logger.info(f"Current state for user {user_id}: {current_state}")
    if current_state == "cancelled":
        return jsonify({"error": "Matching request already cancelled"}), 400
    if current_state == "completed":
        return jsonify({"error": "Match completed"}), 400
    category = redis_client.hget(f"user:{user_id}", "category").decode("utf-8")
    difficulty = redis_client.hget(f"user:{user_id}", "difficulty").decode("utf-8")
    complete_key = f"c_matching:{category}:{difficulty}"
    category_key = f"p_matching:{category}"
    for key in [complete_key, category_key]:
        redis_client.zrem(key, user_id)
    redis_client.hset(f"user:{user_id}", "state", "cancelled")
    logger.info(f"Matching request for user {user_id} cancelled")
    return jsonify({"message": "Matching request cancelled"}), 200


@matching_bp.route("/matching", methods=["POST"])
def match_request():
    data = request.get_json()
    user_id = data.get("user_id")
    category = data.get("category")
    difficulty = data.get("difficulty")
    redis_client = get_local_redis_client()
    token = request.headers.get("Authorization")
    if not validate_user(token):
        return jsonify({"error": "Invalid token"}), 401
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    if not category:
        return jsonify({"error": "category is required"}), 400

    if not difficulty or difficulty not in ["easy", "medium", "hard"]:
        return (
            jsonify({"error": "difficulty must be one of 'easy', 'medium', or 'hard'"}),
            400,
        )
    req_time = time.time()
    if not can_add_to_queue(redis_client, user_id, req_time, logger):
        return (
            jsonify({"error": "User is already in the queue"}),
            400,
        )
    message = {
        "user_id": user_id,
        "category": category,
        "difficulty": difficulty,
        "request_time": req_time,
    }
    redis_client.hset(
        f"user:{user_id}",
        mapping={
            "state": "matching",
            "request_time": req_time,
            "category": category,
            "difficulty": difficulty,
        },
    )

    redis_client.expire(f"user:{user_id}", 45)

    logger.info(f"User {user_id} state set to matching")
    kafka_producer = get_kafka_producer(logger)
    try:
        kafka_producer.produce(
            "match_requests",
            key=str(user_id),
            value=json.dumps(message).encode("utf-8"),
            callback=delivery_report,
        )

        kafka_producer.flush()

    except KafkaException as e:
        logger.error(f"Error while sending message to Kafka: {str(e)}")
        return (
            jsonify({"error": "Failed to send message to Kafka", "details": str(e)}),
            500,
        )

    return jsonify({"message": "User is queued for matching"}), 200


def delivery_report(err, msg):
    if err is not None:
        logger.error("Message delivery failed: {}".format(err))
    else:
        logger.info("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))


import requests


def validate_user(token):
    try:
        res = requests.post(
            "http://user_service:5001/auth/verify_token",
            headers={"Authorization": f"{token}"},
        )

        if res.status_code != 200:
            logger.error(f"User service returned {res.status_code}: {res.text}")
            return False

        try:
            output = res.json()
        except requests.exceptions.JSONDecodeError:
            logger.error("Failed to parse JSON response")
            return False

        return output.get("isValid") == True

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to auth service failed: {e}")
        return False
