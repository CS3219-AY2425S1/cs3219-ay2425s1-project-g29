from app import create_app
import os

if __name__ == "__main__":
    is_debug_mode = os.getenv("FLASK_ENV") == "development"
    app = create_app()
    app.run(debug=is_debug_mode, host="0.0.0.0", port=8000)
