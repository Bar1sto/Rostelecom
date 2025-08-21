import os
from dotenv import load_dotenv


load_dotenv()

AMQP_URL = os.getenv(
    "AMQP_URL",
    "amqp://guest:guest@localhost:5672/"
)
RABBITMQ_EXCHANGE = os.getenv(
    "RABBITMQ_EXCHANGE",
    "tasks",
)
QUEUE_TASK_CREATE = os.getenv(
    "QUEUE_TASK_CREATE",
    "task.create",
)
QUEUE_TASK_RESULT = os.getenv(
    "QUEUE_TASK_RESULT",
    "task.result",
)

SSL_CERT_PATH = os.getenv(
    "SSL_CERT_PATH",
    "certs/cert.pem",
)
SSL_KEY_PATH = os.getenv(
    "SSL_KEY_PATH",
    "certs/key.pem",
)
SERVICE_A_URL = os.getenv(
    "SERVICE_A_URL",
    "https://localhost:8444",
)
A_VERIFY_TLS = os.getenv(
    "A_VERIFY_TLS",
    "false"
).lower() == "true"
WORKER_CONCURRENCY = int(os.getenv(
    "WORKER_CONCURRENCY",
    "5"
))
MAX_RETRIES = int(os.getenv(
    "MAX_RETRIES",
    "3",
))
REQUEST_TIMEOUT_BUFFER = int(os.getenv(
    "REQUEST_TIMEOUT_BUFFER",
    "5",
))
BACKOFF_BASE = int(os.getenv("BACKOFF_BASE", "1"))