import time
import random
from celery import Celery

celery_app = Celery(
    "otp_service",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2"
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def send_otp_sms(self, phone, code):
    attempt = self.request.retries + 1

    print("")
    print(f"=== ATTEMPT {attempt} for {phone} ===")
    print(f"    Code: {code}")

    time.sleep(2)

    # Fail on attempts 1 and 2. Succeed on attempt 3.
    if attempt < 3:
        print(f"    RESULT: failed. Retrying in 5 seconds...")
        raise self.retry(exc=Exception("SMS provider down"))

    print(f"    RESULT: sent successfully!")
    return {"phone": phone, "status": "sent", "attempts": attempt}