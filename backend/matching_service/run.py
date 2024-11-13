from app import create_app
import os
from waitress import serve

if __name__ == "__main__":
    app = create_app()
    # is_dev = os.getenv("FLASK_ENV") == "development"
    # if is_dev:
    #     app.run(debug=is_dev, host="0.0.0.0", port=8000)
    # else:
    serve(app, host="0.0.0.0", port=8000)
