FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and important files to container
COPY ./app ./app
COPY run.py ./
COPY .env ./
COPY firebase-cred.json ./firebase-cred.json

COPY ./app/kafka_consumer.py ./
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose port 5000 for Flask
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

# Command to run your Flask app
# ENTRYPOINT ["python"]
# CMD ["run.py"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]