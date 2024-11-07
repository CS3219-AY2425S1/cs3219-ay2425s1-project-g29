import datetime

from firebase import initialize_firebase

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from firebase_admin import credentials, firestore
from flask_socketio import SocketIO

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                "https://peerprep.store",
                "http://peerprep.store",
            ]
        },
    },
)

socketio = SocketIO(app, cors_allowed_origins="*")

# init Firebase
initialize_firebase()
db = firestore.client()
# cache to store conversation data
conversations_data = ["conversation1", "conversation2", "conversation3", "conversation"]


chat_cache = {}


@app.route("/api/sessions", methods=["POST"])
# adds a new session to the sessionlist collection
# returns session data
def create_session():
    data = request.json
    session_name = data.get("sessionname")
    username = data.get("username")
    if not session_name or not username:
        return jsonify({"error": "sessionname and username are required"}), 400
    session = {
        "sessionName": session_name,
        "username": username,
        "flag": "active",  # flag users as active
        "timestamp": datetime.datetime.now().isoformat(),
    }
    db.collection("sessionlist").add(session)
    return jsonify({"message": "Session created successfully", "session": session}), 201


@app.route("/api/conversations/<username>", methods=["GET"])
# return convonersations associated with different usernames
def get_conversations(username):
    print(username)
    # query Firestore get this username's conversations
    sessions_ref = (
        db.collection("sessionlist").where("username", "==", username).stream()
    )
    conversations = []
    for session in sessions_ref:
        conversations.append(session.to_dict())
    print(conversations)
    return jsonify({"conversations": conversations}), 200


@app.route("/api/history/<conversation>", methods=["GET"])
# query specific chats records from firebase
def get_history(conversation):
    print(f"Requested conversation: {conversation}")

    # Query Firestore for messages in the specified conversation
    messages_ref = (
        db.collection("messages").where("conversation", "==", conversation).stream()
    )

    messages = []
    for msg in messages_ref:
        messages.append(msg.to_dict())

    print(f"Messages found: {messages}")
    return jsonify({"messages": messages})



# DB ver
@socketio.on("chat message")
# handle incoming msg from client, add to firestore
# broadcast to all clients
def handle_message(data):
    conversation = data["conversation"]
    message = data["message"]
    username = data["username"]
    print(conversation)
    print(message)
    message_data = {
        "conversation": conversation,
        "message": message,
        "username": username,
        "avatar": "https://pic2.zhimg.com/v2-8cc7729677b65f6ec620f067365e6181_b.jpg",
        "timestamp": datetime.datetime.now().isoformat(),
    }

    # Save the message to Firestore
    db.collection("messages").add(message_data)

    if "user has exited collaboration" in message.lower():  # lower() to make sure stop in all cases
        # update convo as stop
        session_ref = (
            db.collection("sessionlist").where("sessionName", "==", conversation).get()
        )

        if not session_ref:
            return jsonify({"error": "Session not found"}), 404

        # update Firebase collection's flag
        for session in session_ref:
            session.reference.update({"flag": "stop"})  # flag now stopped here!
            updated_session = session.to_dict()
            updated_session["flag"] = "stop"

    # Broadcast the message to all connected clients
    emit(
        "chat message",
        {"conversation": conversation, "message": message_data},
        broadcast=True,
    )


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5002, allow_unsafe_werkzeug=True)
