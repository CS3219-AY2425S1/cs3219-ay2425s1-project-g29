import os
import firebase_admin

def initialize_firebase():
    cred_path = "./firebase-cred.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
    firebase_admin.initialize_app()