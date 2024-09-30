from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Initialize Firebase
    from app.firebase import initialize_firebase
    initialize_firebase()
    
    # Register Blueprints
    from app.main import main as main_bp
    app.register_blueprint(main_bp, url_prefix='/users')
    
    from app.admin import admin as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app