from flask import json
from .config import RABBITMQ_HOST, RABBITMQ_QUEUE
import pika
import uuid


def publish_to_matching_queue(message):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        channel = connection.channel()

        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        celery_message_body = {
            "args": [message],
            "kwargs": {},
        }
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(celery_message_body),
            properties=pika.BasicProperties(
                delivery_mode=2,
                headers={
                    "id": str(uuid.uuid4()),
                    "task": "process_match",
                },
                content_type="application/json",
                expiration="28000",
            ),
        )
        connection.close()
    except pika.exceptions.AMQPConnectionError:
        return {"error": "Failed to connect to RabbitMQ. Please try again later."}, 500

    except pika.exceptions.ChannelError:
        return {"error": "RabbitMQ channel error. Please try again later."}, 500

    except Exception as e:
        print("exception", e)
        return {"error": f"An unexpected error occurred with RabbitMQ."}, 500
