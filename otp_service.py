import random
from redis_client import r
import json

STATS_CACHE_KEY = "cache:stats"
STATS_CACHE_TTL = 30 

OTP_EXPIRY = 300 # 5 minutes, in seconds
MAX_SENDS_PER_HOUR = 3
RATE_WINDOW = 3600
MAX_ATTEMPTS = 5

def compute_stats():
   
    import time
    time.sleep(2)   # simulates an expensive query

    active_otps = len(r.keys("otp:*"))
    rate_limited = len(r.keys("rate:*"))
    with_attempts = len(r.keys("attempts:*"))

    return {
        "active_otps": active_otps,
        "phones_with_rate_counters": rate_limited,
        "phones_with_failed_attempts": with_attempts
    }

def get_stats():
    """Cache-aside: check cache, compute on miss, store, return."""
    cached = r.get(STATS_CACHE_KEY)

    if cached is not None:
        data = json.loads(cached)
        data["cached"] = True
        return data

    data = compute_stats()
    r.set(STATS_CACHE_KEY, json.dumps(data), ex=STATS_CACHE_TTL)
    data["cached"] = False
    return data


def generate_otp():
    return str(random.randint(100000, 999999))


def save_otp(phone, code):
    key = f"otp:{phone}"
    r.set(key, code, ex=OTP_EXPIRY)


def get_otp(phone):
    key = f"otp:{phone}"
    return r.get(key)


def delete_otp(phone):
    key = f"otp:{phone}"
    r.delete(key)


#time left of otp
def get_ttl(phone): 
    key = f"otp:{phone}"
    return r.ttl(key)

def check_rate_limit(phone):
    
    key = f"rate:{phone}"
    count = r.incr(key)

    if count == 1:
        r.expire(key, RATE_WINDOW) # start the  1 hour timer of count

    return count <= MAX_SENDS_PER_HOUR


def record_attempt(phone):
    key = f"attempts:{phone}"
    count = r.incr(key)

    if count == 1:
        r.expire(key, OTP_EXPIRY)

    return count

#reset the number for attempts
def clear_attempts(phone):
    r.delete(f"attempts:{phone}")