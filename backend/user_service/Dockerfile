FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and important files to container
COPY ./app ./app
COPY run.py ./
COPY .env ./
COPY firebase-cred.json ./firebase-cred.json

# Expose port 5001 for Flask
EXPOSE 5001

# Set environment variables
ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

# Command to run your Flask app
# ENTRYPOINT ["python"]
# CMD ["run.py"]
CMD ["waitress-serve", "--port=5001", "run:app"]