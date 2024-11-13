# app/kafka_producer.py
from confluent_kafka import Producer, KafkaError
import os
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s-%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_FLUSH_TIMEOUT = 10


def get_kafka_producer(logger):
    """Create and return a Kafka producer instance"""
    producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})
    return producer


def produce_message(producer, topic, key, value, logger):
    try:
        producer.produce(
            topic=topic,
            key=str(key),
            value=json.dumps(value).encode("utf-8"),
            callback=delivery_report,
        )
        producer.poll(0)
        producer.flush(KAFKA_FLUSH_TIMEOUT)
    except KafkaError as e:
        logger.error(f"Error producing message to Kafka: {e}")


def delivery_report(err, msg):
    """Callback for message delivery confirmation or failure"""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(
            f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
        )
