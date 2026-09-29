import json
import os
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAME = "security_events"

_client = None

def get_redis():
    global _client
    if _client is None:
        _client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    return _client

def publish_event(event):
    get_redis().rpush(QUEUE_NAME, json.dumps(event))

def pop_event(timeout=2):
    item = get_redis().blpop(QUEUE_NAME, timeout=timeout)
    if not item:
        return None
    return json.loads(item[1])
