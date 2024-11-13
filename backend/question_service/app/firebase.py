import os
import firebase_admin

def initialize_firebase():
    cred_path = os.getenv('CRED_PATH')
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
    firebase_admin.initialize_app()