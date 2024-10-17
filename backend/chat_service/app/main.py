# backend/your_service/chat_service.py
import uuid
from .firebase import db

def create_chat_session(user1_id, user2_id, session_id):
    chat_data = {
        'participants': [user1_id, user2_id],
        'created_at': firestore.SERVER_TIMESTAMP
    }
    try:
        db.collection('chats').document(session_id).set(chat_data)
        print(f"Chat session {session_id} created successfully.")
        return session_id
    except Exception as e:
        print(f"Error creating chat session: {e}")
        return None

    

def add_message(session_id, sender_id, message_text):
    message_data = {
        'text': message_text,
        'sender': sender_id,
        'timestamp': firestore.SERVER_TIMESTAMP
    }
    try:
        db.collection('chats').document(session_id).collection('messages').add(message_data)
        print("Message added successfully.")
        return True
    except Exception as e:
        print(f"Error adding message: {e}")
        return False


'''
# example usage
from .chat_service import add_message

# When a user sends a message
session_id = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
sender_id = "user1_id"
message_text = "Hello, how are you?"

add_message(session_id, sender_id, message_text)

'''