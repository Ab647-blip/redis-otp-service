import random
from redis_client import r

OTP_EXPIRY = 10 # 5 minutes, in seconds
MAX_SENDS_PER_HOUR = 3
RATE_WINDOW = 3600
MAX_ATTEMPTS = 5


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