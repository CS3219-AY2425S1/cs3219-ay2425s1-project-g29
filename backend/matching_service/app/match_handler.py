from confluent_kafka import Consumer, Producer
import json
import redis
import time
import uuid
import logging
import os
from redis_client import (
    can_proceed,
    get_redis_client,
    get_available_matching_requests,
    PARTIAL_MATCHING_PATTERN,
    COMPLETE_MATCHING_PATTERN,
)
from kafka_producer import get_kafka_producer, produce_message

CONSUMER_CONFIG = {
    "bootstrap.servers": "kafka:9092",
    "group.id": "match-handler-group",
    "auto.offset.reset": "earliest",
    "group.instance.id": "match-handler-instance",
}

PRODUCER_CONFIG = {
    "bootstrap.servers": "kafka:9092",
    "client.id": "match-handler",
}
RETRY_ATTEMPTS = 4
EXPIRATION_TIME = 30  # 29


logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger("match_handler")

redis_client = None


def get_local_redis_client():
    global redis_client
    if redis_client is None:
        redis_client = get_redis_client(logger)
    return redis_client


def main():
    consumer = Consumer(CONSUMER_CONFIG)
    producer = get_kafka_producer(logger)
    get_local_redis_client()

    try:
        consumer.subscribe(["match_requests"])
        logger.info("Successfully subscribed to match_requests topic")

        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue

            try:
                message = json.loads(msg.value().decode("utf-8"))
                process_message(message, producer)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON: {e}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
    finally:
        consumer.close()


def process_message(message, producer):
    user_id = message.get("user_id")
    category = message.get("category")
    difficulty = message.get("difficulty")
    request_time = message.get("request_time")
    expiration_time = request_time + EXPIRATION_TIME

    key = f"c_matching:{category}:{difficulty}"
    category_key = f"p_matching:{category}"
    logger.info(
        f"Received matching request: user_id={user_id}, category={category}, difficulty={difficulty}"
    )

    retry_attempts = RETRY_ATTEMPTS

    while retry_attempts > 0:
        try:
            current_time = time.time()

            remove_expired_entries(redis_client, current_time)

            redis_client.watch(key, category_key)
            pipe = redis_client.pipeline()
            pipe.multi()
            get_available_matching_requests(
                is_before=True,
                redis_client=redis_client,
                logger=logger,
                is_complete=True,
                req_user_id=user_id,
                req_user_difficulty=difficulty,
                req_user_category=category,
                req_user_request_time=request_time,
            )
            for match_type in ["complete", "partial"]:
                res = find_and_handle_match(
                    redis_client,
                    pipe,
                    user_id,
                    key,
                    category_key,
                    current_time,
                    match_type,
                    producer,
                    category,
                    difficulty,
                    request_time,
                )
                if res is False:
                    return
                if res:
                    get_available_matching_requests(
                        is_before=False, redis_client=redis_client, logger=logger
                    )
                    return

            add_user_to_matching_queue(
                pipe, user_id, key, category_key, expiration_time
            )

            get_available_matching_requests(
                is_before=False, redis_client=redis_client, logger=logger
            )
            return

        except redis.WatchError:
            logger.warning(
                "Transaction failed due to concurrent modification, retrying..."
            )
            pipe.reset()
            retry_attempts -= 1

    logger.error("Exceeded maximum retries. Exiting without processing the match.")


def find_and_handle_match(
    redis_client,
    pipe,
    user_id,
    key,
    category_key,
    current_time,
    match_type,
    producer,
    category,
    difficulty,
    request_time,
):
    matches = redis_client.zrangebyscore(
        key if match_type == "complete" else category_key, current_time, "+inf"
    )

    for match in matches:
        match = match.decode("utf-8")
        can_continue, cancelled_users = can_proceed(
            redis_client, user_id, match, logger
        )

        if can_continue:
            remove_and_execute(pipe, key, category_key, match)
            push_to_kafka(match_type, user_id, match, category, difficulty, producer)

            return True

        if user_id in cancelled_users:
            logger.info(
                f"User {user_id} has cancelled its match request. Stop matching"
            )
            return False
        remove_and_execute(pipe, key, category_key, match)

    logger.info(f"No {match_type} matches found for user_id={user_id}.")
    return None


def remove_expired_entries(redis_client, min_timestamp):

    for pattern in [COMPLETE_MATCHING_PATTERN, PARTIAL_MATCHING_PATTERN]:
        cursor = 0
        while True:
            cursor, keys = redis_client.scan(cursor=cursor, match=pattern)
            if not keys:
                break

            pipeline = redis_client.pipeline()

            for key in keys:
                pipeline.zremrangebyscore(key, "-inf", min_timestamp)

            try:
                pipeline.execute()
            except redis.exceptions.RedisError as e:
                logger.error(f"Error executing Redis pipeline: {e}")

            if cursor == 0:
                break


def remove_and_execute(pipe, key, category_key, match):
    pipe.zrem(key, match)
    pipe.zrem(category_key, match)
    pipe.execute()


def add_user_to_matching_queue(pipe, user_id, key, category_key, expiration_time):
    pipe.zadd(key, {str(user_id): expiration_time})
    pipe.zadd(category_key, {str(user_id): expiration_time})
    pipe.execute()


def log_redis_state(redis_client, key, category_key, user_id):
    logger.info(
        f"Redis set '{key}' after adding user {user_id}: {redis_client.zrange(key, 0, -1, withscores=True)}"
    )
    logger.info(
        f"Redis set '{category_key}' after adding user {user_id}: {redis_client.zrange(category_key, 0, -1, withscores=True)}"
    )


def push_to_kafka(match_type, user_id, match, category, difficulty, producer):
    match_result = {
        "user1_id": match,
        "user2_id": user_id,
        "category": category,
        "difficulty": difficulty,
        "uid": str(uuid.uuid4()),
        "status": match_type + " match",
    }

    logger.info(f"Producing {match_type} match result to Kafka: {match_result}")
    produce_message(producer, "match_results", user_id, match_result, logger)


if __name__ == "__main__":
    main()
