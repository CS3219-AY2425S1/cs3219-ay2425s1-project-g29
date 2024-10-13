import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = "matching_queue"
TIMEOUT_DURATION = 30
