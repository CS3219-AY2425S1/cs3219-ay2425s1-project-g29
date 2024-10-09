from confluent_kafka import Consumer, KafkaError, KafkaException
import json
import asyncio
import logging

# Set up the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def kafka_consumer():
    """Asynchronously consume messages from Kafka with exponential backoff on connection failure."""
    consumer_config = {
        "bootstrap.servers": "kafka:9092",
        "group.id": "fastapi-consumer-group",
        "auto.offset.reset": "earliest",
    }

    max_retries = 5
    initial_delay = 1
    backoff_factor = 2

    for attempt in range(max_retries):
        try:
            # Try to create the Kafka consumer and connect to Kafka broker
            logger.info("Attempting to connect to Kafka")
            consumer = Consumer(consumer_config)
            logger.info("Connected to Kafka successfully")
            consumer.subscribe(["question_results"])  # Subscribe to the Kafka category
            logger.info("Subscribe to match_results")
            break  # Exit loop if successful connection
        except KafkaException as e:
            # Calculate the exponential backoff delay
            delay = initial_delay * (backoff_factor**attempt)
            logger.error(
                f"Error connecting to Kafka broker: {str(e)}. Retrying in {delay:.2f} seconds..."
            )
            # Sleep for the calculated backoff delay
            await asyncio.sleep(delay)
    else:
        raise Exception(
            "Failed to connect to Kafka broker after multiple attempts with exponential backoff."
        )

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            await asyncio.sleep(0.1)
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition, continue polling
                continue
            else:
                logger.error(f"Kafka error: {msg.error()}")
        else:
            message_value = msg.value().decode("utf-8")
            logger.info(f"Received message: {message_value}")
            # Convert the message to a JSON object and yield it
            yield json.loads(message_value)
