FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY run.py .

EXPOSE 8000
EXPOSE 8001

# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
# Set environment variables for Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=development  
ENV PYTHONUNBUFFERED=1



# CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

