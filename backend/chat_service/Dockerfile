# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install Supervisor and any required system packages
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files into the container
COPY firebase.py .
COPY run.py .
COPY .env ./
COPY firebase-cred.json ./firebase-cred.json

# Copy Supervisor configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose the application's port
EXPOSE 5002

# Set environment variables for Flask
ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

# Run the application with supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
