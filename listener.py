import json
from redis_client import r
from events import CHANNEL

pubsub = r.pubsub()
pubsub.subscribe(CHANNEL)

print(f"Listening on '{CHANNEL}'... (Ctrl+C to stop)")
print("")

for message in pubsub.listen():
    if message["type"] != "message":
        continue

    payload = json.loads(message["data"])
    event = payload["event"]
    data = payload["data"]

    print(f"[EVENT] {event} — {data}")