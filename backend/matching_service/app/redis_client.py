import redis
import os
from datetime import datetime, timezone, timedelta


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)
REDIS_MAX_RETRIES = 5
COMPLETE_MATCHING_PATTERN = "c_matching:*:*"
PARTIAL_MATCHING_PATTERN = "p_matching:*"


def get_available_matching_requests(
    is_before,
    redis_client,
    logger,
    is_complete=True,
    req_user_id=None,
    req_user_category=None,
    req_user_difficulty=None,
    req_user_request_time=None,
):
    if is_before:
        logger.info("Queue before matching:")
    else:
        logger.info("Queue after matching:")
    if is_complete:
        pattern = COMPLETE_MATCHING_PATTERN
        part_count = 3
    else:
        pattern = PARTIAL_MATCHING_PATTERN
        part_count = 2

    matching_keys = redis_client.keys(pattern)

    all_requests = []

    for key in matching_keys:
        key_str = key.decode("utf-8")
        key_parts = key_str.split(":")

        if len(key_parts) != part_count:
            continue

        if is_complete:
            _, category, difficulty = key_parts
        else:
            _, category = key_parts
            difficulty = "any"

        entries = redis_client.zrange(key_str, 0, -1, withscores=True)

        for user_id, req_time in entries:
            readable_time = datetime.fromtimestamp(
                req_time, tz=timezone(timedelta(hours=8))
            ).strftime("%Y-%m-%d %H:%M:%S")
            all_requests.append(
                {
                    "category": category,
                    "difficulty": difficulty,
                    "user_id": user_id.decode("utf-8"),
                    "req_time": readable_time,
                }
            )
    if is_before:
        readable_time = datetime.fromtimestamp(
            req_user_request_time, tz=timezone(timedelta(hours=8))
        ).strftime("%Y-%m-%d %H:%M:%S")
        all_requests.append(
            {
                "user_id": req_user_id,
                "category": req_user_category,
                "difficulty": req_user_difficulty,
                "req_time": readable_time,
            }
        )

    sorted_requests = sorted(all_requests, key=lambda x: x["req_time"])

    logger.info(sorted_requests)


def get_redis_client(logger):
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        redis_client.ping()
        logger.info("Connected to Redis successfully")
        return redis_client
    except redis.RedisError as e:
        logger.error(f"Error connecting to Redis: {e}")


def can_add_to_queue(redis_client, user_id, request_time, logger):
    previous_request_time = redis_client.hget(f"user:{user_id}", "request_time")
    state = redis_client.hget(f"user:{user_id}", "state")

    if not state or not previous_request_time:
        return True

    state = state.decode("utf-8")
    logger.info(f"State for user {user_id}: {state}")

    try:
        diff = float(request_time) - float(previous_request_time.decode("utf-8"))
    except (ValueError, AttributeError) as e:
        logger.error(f"Error decoding previous request time for user {user_id}: {e}")
        return True

    if diff >= 30 or state in ["completed", "cancelled"]:
        return True

    if state == "matching":
        return False

    logger.warning(f"Unexpected state {state} for user {user_id}. Allowing queue.")
    return True


def can_proceed(redis_client, user1_id, user2_id, logger=None):
    if user1_id == user2_id:
        return {"can_proceed": False, "cancelled_users": []}

    user1_state = redis_client.hget(f"user:{user1_id}", "state")
    user2_state = redis_client.hget(f"user:{user2_id}", "state")
    if user1_state != b"cancelled" and user2_state != b"cancelled":
        return {"can_proceed": True, "cancelled_users": []}

    cancelled_users = []
    if user1_state == b"cancelled":
        cancelled_users.append(user1_id)
    if user2_state == b"cancelled":
        cancelled_users.append(user2_id)

    return {"can_proceed": False, "cancelled_users": cancelled_users}
