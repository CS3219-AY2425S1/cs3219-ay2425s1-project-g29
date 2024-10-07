
from .chat_service import add_message

def send_user_message(session_id, sender_id, message_text):
    success = add_message(session_id, sender_id, message_text)
    if success:
        print("Message sent.")
    else:
        print("Failed to send message.")
