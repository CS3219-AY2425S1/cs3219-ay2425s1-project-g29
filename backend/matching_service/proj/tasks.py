from .celery import (
    app,
)
import time
import redis
import json
from confluent_kafka import Producer

# Initialize Redis client
r = redis.Redis(host="redis", port=6379, db=0)
producer_config = {"bootstrap.servers": "kafka:9092", "debug": "broker, msg"}


def get_kafka_producer():
    """Lazily initialize Kafka producer"""
    if not hasattr(get_kafka_producer, "producer"):
        print("Initializing Kafka producer...")
        get_kafka_producer.producer = Producer(producer_config)
    return get_kafka_producer.producer


@app.task(
    name="process_match",
    queue="matching_queue",
    bind=True,
    max_retries=3,
)
def process_matching_request(self, user_data):
    user_id = user_data["user_id"]
    topic = user_data["topic"]
    difficulty = user_data["difficulty"]
    request_time = user_data["request_time"]
    expiration_time = request_time + 28
    print(
        f"Received matching request: user_id={user_id}, topic={topic}, difficulty={difficulty}"
    )

    key = f"matching:{topic}:{difficulty}"
    topic_key = f"matching:{topic}"
    pipe = None
    # producer_config = {"bootstrap.servers": "kafka:9092", "debug": "broker, msg"}
    # producer = Producer(producer_config)
    producer = get_kafka_producer()
    while True:
        try:
            current_time = time.time()
            min_timestamp = current_time - 28
            r.zremrangebyscore(key, "-inf", min_timestamp)
            r.zremrangebyscore(topic_key, "-inf", min_timestamp)
            r.watch(key, topic_key)
            pipe = r.pipeline()
            pipe.multi()

            complete_matches = r.zrangebyscore(key, min_timestamp, "+inf")
            if complete_matches:
                match = complete_matches[0]
                pipe.zrem(key, match)
                pipe.zrem(topic_key, match)
                pipe.execute()

                print(
                    f"Complete match found: user_id={user_id}, matched_with user_id: {match.decode('utf-8')}"
                )

                push_to_kafka(
                    user_id=user_id,
                    match=match,
                    topic=topic,
                    difficulty=difficulty,
                    producer=producer,
                )
                print(f"Kafka flush complete for complete match result")
                return

            print(
                f"Added user_id={user_id} to matching set for topic={topic} and difficulty={difficulty}"
            )
            topic_matches = r.zrangebyscore(topic_key, min_timestamp, "+inf")
            if topic_matches:
                match = topic_matches[0]
                pipe.zrem(key, match)
                pipe.zrem(topic_key, match)
                pipe.execute()

                print(
                    f"Partial match found: user_id={user_id}, matched with user_id: {match.decode('utf-8')}"
                )
                push_to_kafka(
                    user_id=user_id,
                    match=match,
                    topic=topic,
                    difficulty=difficulty,
                    producer=producer,
                )
                print(f"Kafka flush complete for parital match result")
                return

            pipe.zadd(key, {str(user_id): expiration_time})
            pipe.zadd(topic_key, {str(user_id): expiration_time})
            pipe.execute()
            print(
                f"No partial match found for user_id={user_id}, added to topic matching queue: {topic_key}"
            )
            return
        except redis.WatchError:
            print("Transaction failed due to concurrent modification, retrying...")
            if pipe:
                pipe.reset()


def delivery_report(record_metadata, exception):
    if exception is not None:
        print(f"Message delivery failed: {exception}")
    else:
        print(
            f"Message delivered to {record_metadata.topic} "
            f"partition {record_metadata.partition} "
            f"offset {record_metadata.offset}"
        )


def push_to_kafka(user_id, match, topic, difficulty, producer):
    try:
        match_result = {
            "user1_id": user_id,
            "user2_id": match.decode("utf-8"),
            "topic": topic,
            "difficulty": difficulty,
        }

        print(f"Producing match result to Kafka: {match_result}")
        producer.produce(
            "match_results",
            key=str(user_id),
            value=json.dumps(match_result).encode("utf-8"),
            callback=delivery_report,
        )
        print("before flush")
        producer.flush(timeout=10)
        print("after flush")

    except Exception as e:
        print(f"Error during match result processing: {e}")
