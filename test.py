import time
import otp_service

phone = "0300"
code = otp_service.generate_otp()
otp_service.save_otp(phone, code)

print("Now:", otp_service.get_otp(phone))
print("Waiting 7 seconds...")
time.sleep(7)
print("After:", otp_service.get_otp(phone))