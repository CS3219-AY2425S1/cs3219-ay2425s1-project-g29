from flask import Flask
from .routes import matching_bp
from flask_cors import CORS
import json


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)  # Enable CORS for cross-origin requests

    @app.route("/")
    def hello_world():
        return "<p>Hello, World from Flask!</p>"

    app.register_blueprint(matching_bp)
    return app
