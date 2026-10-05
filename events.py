import json
from redis_client import r

CHANNEL = "otp_events"


def publish_event(event_type, data):
 
    message = json.dumps({
        "event": event_type,
        "data": data
    })
    return r.publish(CHANNEL, message)