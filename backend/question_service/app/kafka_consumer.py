from confluent_kafka import Consumer, Producer
from firebase_admin import firestore
from app.firebase import initialize_firebase

import json
import time
import uuid

# Kafka configuration
consumer_config = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'question_processor',
    'auto.offset.reset': 'earliest'
}

producer_config = {
    'bootstrap.servers': 'kafka:9092'
}
# Initialize Firestore
initialize_firebase()
db = firestore.client()


def get_kafka_producer():
    """Lazily initialize Kafka producer"""
    if not hasattr(get_kafka_producer, "producer"):
        print("Initializing Kafka producer...")
        get_kafka_producer.producer = Producer(producer_config)
    return get_kafka_producer.producer

def find_matching_question(target_category, difficulty):
    """
    Find a matching question based on category and difficulty.
    Category is now checked against an array of categories.
    Returns the question document if found, None otherwise.
    """
    questions_ref = db.collection('questions')
    
    # Try to find a question matching both category and difficulty
    # We use array_contains instead of == for category matching
    query = questions_ref.where('category', 'array_contains', target_category)\
                         .where('difficulty', '==', difficulty)\
                         .limit(1)
    questions = query.stream()
    for question in questions:
        question_dict = question.to_dict()
        question_dict['id'] = question.id
        return question_dict
    
    # If no exact match, try finding a question matching only category
    category_query = questions_ref.where('category', 'array_contains', target_category).limit(1)
    category_questions = category_query.stream()
    for question in category_questions:
        question_dict = question.to_dict()
        question_dict['id'] = question.id
        return question_dict
    
    # If no matches at all, return None
    return None

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')

def process_match_result(match_result):
    """
    Process the match result and add question data if available.
    """
    category = match_result.get('category')
    difficulty = match_result.get('difficulty')
    
    matching_question = find_matching_question(category, difficulty)
    
    if matching_question is None:
        print(f"No matching question found for category: {category}, difficulty: {difficulty}")
        return None
    print("matching question:", matching_question)
    enhanced_result = match_result.copy()
    enhanced_result.update({
        'timestamp': time.time(),
        'question_id': matching_question['id'],
        'question_title': matching_question['title'],
        'match_difficulty': difficulty,
        'actual_difficulty': matching_question['difficulty']
    })
    
    return enhanced_result

def main():
    consumer = Consumer(consumer_config)
    producer = get_kafka_producer()
    
    try:
        consumer.subscribe(['match_results'])
        
        while True:
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            
            try:
                # Parse the original match result
                match_result = json.loads(msg.value().decode('utf-8'))
                print(f"Received match result: {match_result}")
                
                # Process and enhance the match result
                enhanced_result = process_match_result(match_result)
                
                # Only produce to question_results if we found a matching question
                if enhanced_result:
                    print(f"Enhanced result with question: {enhanced_result}")
                    producer.produce(
                        'question_results',
                        key=str(enhanced_result['user1_id']),
                        value=json.dumps(enhanced_result).encode('utf-8'),
                        callback=delivery_report
                    )
                    producer.flush()
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse message: {e}")
            except Exception as e:
                print(f"Error processing message: {e}")
    
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        consumer.close()

if __name__ == '__main__':
    main()