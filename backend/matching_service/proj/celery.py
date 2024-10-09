from celery import Celery
import os

broker_url = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
backend_url = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

app = Celery(
    "matching_service", broker=broker_url, backend=backend_url, include=["proj.tasks"]
)
app.conf.broker_connection_retry_on_startup = True
if __name__ == "__main__":
    app.start()
