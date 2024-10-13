from fastapi import FastAPI, WebSocket
from .kafka_consumer import kafka_consumer
import asyncio
import logging
import json
import time

# Set up the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

connected_clients = {}


async def send_with_retries(user_id, message, max_retries=4, delay=0.5, timeout=30):
    """Attempts to send the message with retry logic within the 30-second window."""
    retries = 0
    start_time = time.time()

    while retries < max_retries and (time.time() - start_time) < timeout:
        if user_id in connected_clients:
            try:
                await connected_clients[user_id].send_text(json.dumps(message))
                logger.info(f"Sent match result to user {user_id}: {message}")
                return
            except Exception as e:
                logger.error(f"Error sending match result to user {user_id}: {str(e)}")

        await asyncio.sleep(delay * (2**retries))
        retries += 1

    logger.warning(
        f"Failed to send match result to user {user_id} after {max_retries} retries or {timeout} seconds"
    )


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    connected_clients[user_id] = websocket
    logger.info(f"User {user_id} connected.")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message from user {user_id}: {data}")
    except Exception as e:
        logger.error(f"Error with WebSocket connection: {e}")
    finally:
        connected_clients.pop(user_id, None)
        logger.info(f"User {user_id} disconnected.")


async def match_result_dispatcher():
    async for match_result in kafka_consumer():
        logger.info("Fetched from Kafka topic", match_result)
        logger.info(f"curent connected clients: {connected_clients}")
        user1_id = match_result.get("user1_id")
        user2_id = match_result.get("user2_id")
        if user1_id in connected_clients:
            await send_with_retries(user1_id, match_result, max_retries=4)
        else:
            logger.info(f"User {user1_id} is not connected. Cannot send match result.")

        if user2_id in connected_clients:
            await send_with_retries(user2_id, match_result, max_retries=4)
        else:
            logger.info(f"User {user2_id} is not connected. Cannot send match result.")


@app.on_event("startup")
async def startup_event():
    logger.info("Starting match result dispatcher")
    asyncio.create_task(match_result_dispatcher())
    logger.info("Match result dispatcher started successfully")
