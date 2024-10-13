FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
# Set environment variables for Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=development  

# Command to run Flask's development server
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]

