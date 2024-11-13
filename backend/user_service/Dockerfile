FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and other necessary files
COPY ./app ./app
COPY run.py ./
COPY .env ./
COPY firebase-cred.json ./firebase-cred.json

# Expose port 5001 for Flask
EXPOSE 5001

# Set environment variables
ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

# Command to run the application with conditional logic for development vs production
CMD ["bash", "-c", "if [ \"$FLASK_ENV\" = \"development\" ]; then exec python run.py; else exec waitress-serve --port=5001 run:app; fi"]