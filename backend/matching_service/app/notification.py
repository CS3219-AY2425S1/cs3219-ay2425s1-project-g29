import asyncio
import websockets
import json
import logging
import requests
from confluent_kafka import Consumer, KafkaError
from redis_client import get_redis_client
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger("notification")


connected_clients = {}

consumer_config = {
    "bootstrap.servers": "kafka:9092",
    "group.id": "websocket-consumer-group",
    "auto.offset.reset": "earliest",
}

redis_client = None


def get_local_redis_client():
    global redis_client
    if redis_client is None:
        redis_client = get_redis_client(logger)
    return redis_client


def set_user_state(redis_client, user_id, state):
    redis_client.hset(f"user:{user_id}", "state", state)
    # logger.info(f"Set user {user_id} to state: {state}")


async def kafka_consumer():
    max_retries = 10
    initial_delay = 1
    backoff_factor = 2
    redis_client = get_local_redis_client()
    for attempt in range(max_retries):
        try:
            logger.info("Attempting to connect to Kafka")
            consumer = Consumer(consumer_config)
            logger.info("Connected to Kafka successfully")
            # consumer.subscribe(["match_requests", "match_results", "question_results"])
            consumer.subscribe(["question_results"])
            break
        except Exception as e:
            delay = initial_delay * (backoff_factor**attempt)
            logger.error(
                f"Error connecting to Kafka broker: {str(e)}. Retrying in {delay:.2f} seconds..."
            )
            await asyncio.sleep(delay)
    else:
        raise Exception("Failed to connect to Kafka after multiple attempts.")

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                await asyncio.sleep(0.1)
                continue

            if msg.error():
                logger.error(f"Kafka error: {msg.error()}")
                continue

            message_value = msg.value().decode("utf-8")
            message = json.loads(message_value)

            logger.info(f"Received message from question_results: {message_value}")
            requests.post("http://user_service:5001/users/history", json=message)
            user1_id = message.get("user1_id")
            user2_id = message.get("user2_id")
            user1_state = redis_client.hget(f"user:{user1_id}", "state").decode("utf-8")
            user2_state = redis_client.hget(f"user:{user2_id}", "state").decode("utf-8")

            if user1_state == "matching" and user2_state == "matching":
                set_user_state(redis_client, user1_id, "completed")
                set_user_state(redis_client, user2_id, "completed")

                redis_client.hset(
                    message.get("uid"),
                    mapping={
                        "user1_id": user1_id,
                        "user2_id": user2_id,
                        "question_id": message.get("question_id"),
                        "question_title": message.get("question_title"),
                        "status": message.get("status"),
                        "category": message.get("category"),
                        "difficulty": message.get("difficulty"),
                    },
                )
                redis_client.expire(message.get("uid"), 60)
                yield message

            elif user1_state == "matching":
                cancelled_message = generate_cancelled_message(redis_client, user1_id)
                yield cancelled_message
            elif user2_state == "matching":
                cancelled_message = generate_cancelled_message(redis_client, user2_id)
                yield cancelled_message

            consumer.commit(msg)
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")


def generate_cancelled_message(redis_client, user_id):
    cancelled_message = {
        "status": "cancelled",
        "user_id": user_id,
    }
    set_user_state(redis_client, user_id, "cancelled")
    return cancelled_message


async def wait_for_ack(websocket, timeout=5):
    try:
        ack_message = await asyncio.wait_for(websocket.recv(), timeout)
        return json.loads(ack_message)
    except asyncio.TimeoutError:
        logger.warning("Timeout waiting for ACK")
        return None


async def send_with_retries(user_id, message, max_retries=4):
    for attempt in range(max_retries):
        try:
            if user_id in connected_clients:
                websocket = connected_clients[user_id]
                await websocket.send(json.dumps(message))
                # logger.info(f"Sent message to user {user_id}: {message}")
                return True
        except Exception as e:
            logger.error(
                f"Error sending message to user {user_id}, attempt {attempt + 1}: {e}"
            )
            await asyncio.sleep(1)
    logger.error(
        f"Failed to send message to user {user_id} after {max_retries} attempts."
    )
    return False


async def match_result_dispatcher():
    async for match_result in kafka_consumer():
        status = match_result.get("status")
        # logger.info(f"Currently connected clients: {list(connected_clients.keys())}")
        if status == "cancelled":
            user_id = match_result.get("user_id")
            await send_with_retries(user_id, match_result)
        elif status == "no_question":
            await send_with_retries(match_result.get("user1_id"), match_result)
            await send_with_retries(match_result.get("user2_id"), match_result)
        else:
            user1_id = match_result.get("user1_id")
            user2_id = match_result.get("user2_id")
            is_sent = await send_with_retries(user1_id, match_result)
            if not is_sent:
                logger.error(f"Failed to send match result to user_1 {user1_id}.")
                cancelled_message = generate_cancelled_message(redis_client, user2_id)
                await send_with_retries(user2_id, cancelled_message)
                logger.error(
                    f"Failed to send match result to user_1 {user1_id}. Cancelling user_2 match."
                )


async def handle_ack(user1_id, status, data):
    uid = data.get("uid")
    user2_id = redis_client.hget(uid, "user2_id").decode("utf-8")
    if status == "success":
        status = redis_client.hget(uid, "status").decode("utf-8")
        hash_values = redis_client.hgetall(uid)
        match_info = {
            k.decode("utf-8"): v.decode("utf-8") for k, v in hash_values.items()
        }
        match_info["uid"] = uid
        await send_with_retries(user2_id, match_info)
    else:
        logger.error(f"Received error ACK from user1 {user1_id}")
        cancelled_message = generate_cancelled_message(redis_client, user2_id)
        await send_with_retries(user2_id, cancelled_message)


async def websocket_handler(websocket, path):
    user_id = path.split("/")[-1]
    connected_clients[user_id] = websocket
    logger.info(f"User {user_id} connected.")

    try:
        async for message in websocket:
            data = json.loads(message)
            status = data.get("status")
            if status == "success" or status == "error":
                # logger.info(f"Received ACK from user1 {user_id}: {message}")
                await handle_ack(user_id, status, data)
            else:
                logger.info(f"Received message from user {user_id}: {message}")
    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"WebSocket connection closed for user {user_id}: {e}")
    finally:
        connected_clients.pop(user_id, None)
        logger.info(f"User {user_id} disconnected.")


async def main():
    asyncio.create_task(match_result_dispatcher())

    async with websockets.serve(websocket_handler, "0.0.0.0", 8001):
        logger.info("WebSocket server started on ws://0.0.0.0:8001")
        await asyncio.Future()  # Keep the server running


if __name__ == "__main__":
    asyncio.run(main())
