from fastapi import FastAPI
from pydantic import BaseModel

import otp_service
from celery_app import send_otp_sms

app = FastAPI(title="OTP Service")


class SendRequest(BaseModel):
    phone: str


class VerifyRequest(BaseModel):
    phone: str
    code: str


@app.post("/send-otp")
def send_otp(data: SendRequest):
    if not otp_service.check_rate_limit(data.phone):
        return {
            "success": False,
            "message": "Too many requests. Try again later."
        }

    code = otp_service.generate_otp()
    otp_service.save_otp(data.phone, code)
    otp_service.clear_attempts(data.phone)

    print(f"[SMS] Sending {code} to {data.phone}")

    task = send_otp_sms.delay(data.phone, code)

    return {
        "success": True,
        "message": "OTP sent",
        "task_id": task.id,
        "expires_in": otp_service.OTP_EXPIRY
    }


@app.post("/verify-otp")
def verify_otp(data: VerifyRequest):
    stored = otp_service.get_otp(data.phone)

    if stored is None:
        return {"success": False, "message": "OTP expired or not found"}

    if stored != data.code:
        attempts = otp_service.record_attempt(data.phone)

        if attempts >= otp_service.MAX_ATTEMPTS:
            otp_service.delete_otp(data.phone)
            otp_service.clear_attempts(data.phone)
            return {
                "success": False,
                "message": "Too many wrong attempts. Request a new OTP."
            }

        remaining = otp_service.MAX_ATTEMPTS - attempts
        return {
            "success": False,
            "message": f"Incorrect OTP. {remaining} attempts left."
        }

    otp_service.delete_otp(data.phone)
    otp_service.clear_attempts(data.phone)
    return {"success": True, "message": "Verified"}