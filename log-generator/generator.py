from time import sleep
from faker import Faker
from kafka import KafkaProducer
from kafka.errors import KafkaError, NoBrokersAvailable
import time
import random
import logging
import sys
import signal

# Configuration
KAFKA_BROKER = 'redpanda:9092'
TOPIC_NAME = 'raw-logs'
RETRY_INTERVAL = 5  # Seconds between connection retries
LOG_INTERVAL = 0.5  # Seconds between log messages

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

fake = Faker()
producer = None

def create_kafka_producer():
    """Create Kafka producer with retry mechanism"""
    retries = 5
    while retries > 0:
        try:
            return KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: v.encode('utf-8'),
                max_block_ms=30000,  # 30 sec timeout
                retries=3
            )
        except NoBrokersAvailable:
            logging.warning(f"Broker not available, retrying in {RETRY_INTERVAL} seconds...")
            time.sleep(RETRY_INTERVAL)
            retries -= 1
    logging.error("Failed to connect to Kafka broker")
    sys.exit(1)


def generate_apache_log():
    """Generate Apache combined log format entry"""
    return (
        f'{fake.ipv4()} '  # Client IP
        f'{fake.user_name()} '  # User
        f'- '  # Auth
        f'[{fake.date_time_this_year().strftime("%d/%b/%Y:%H:%M:%S %z")}] '  # Timestamp
        f'"{" ".join([  # Request
            random.choice(["GET", "POST", "PUT", "DELETE"]),
            f"/{fake.uri_path()}",
            "HTTP/1.1"
        ])}" '
        f'{random.choice([200, 301, 404, 500])} '  # Status code
        f'{random.randint(100, 10000)} '  # Response size
        f'"{fake.url()}" '  # Referer
        f'"{fake.user_agent()}"'  # User agent
    )


def graceful_shutdown(signum, frame):
    """Handle shutdown signal"""
    logging.info("Shutting down producer...")
    if producer:
        producer.flush()
        producer.close()
    sys.exit(0)


if __name__ == "__main__":
    # Handle termination signals
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    # Initialize Kafka producer
    producer = create_kafka_producer()

    # Start generating logs
    while True:
        log_entry = generate_apache_log()
        logging.info(f"Generated log: {log_entry}")
        try:
            producer.send(TOPIC_NAME, value=log_entry)
        except KafkaError as e:
            logging.error(f"Failed to send message to Kafka: {e}")
        time.sleep(LOG_INTERVAL)