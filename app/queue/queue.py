from redis import Redis
from rq import Queue

# custom imports
from app.config import redis_host, redis_pass

redis_client = Redis(
    host=redis_host,
    port=18112,
    decode_responses=True,
    username="default",
    password=redis_pass,
)

queue = Queue(connection=redis_client)