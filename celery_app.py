import time
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


@celery_app.task
def send_otp_sms(phone, code):
    """Pretend to send an SMS. Real providers take 2-3 seconds."""
    print(f"[WORKER] Sending OTP to {phone}...")

    time.sleep(3)   # fake SMS provider delay

    print(f"[WORKER] Sent {code} to {phone}")
    return {"phone": phone, "status": "sent"}