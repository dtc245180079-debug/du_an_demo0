import os
import time
import jwt
from database.db import create_call_log, update_call_log, log_audit

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "ACmockaccount00000000000000000000")
TWILIO_API_KEY = os.getenv("TWILIO_API_KEY", "SKmockapikey000000000000000000000")
TWILIO_API_SECRET = os.getenv("TWILIO_API_SECRET", "mockapisecret0000000000000000000")
TWILIO_TWIML_APP_SID = os.getenv("TWILIO_TWIML_APP_SID", "APmocktwiml00000000000000000000")
TWILIO_CALLER_ID = os.getenv("TWILIO_CALLER_ID", "+84901234567")

def generate_twilio_voice_token(agent_id, username):
    """
    Sinh Twilio Voice Access Token (JWT) cho Softphone trên trình duyệt web của nhân viên
    """
    identity = f"agent_{agent_id}_{username}"
    now = int(time.time())
    
    payload = {
        "jti": f"{TWILIO_API_KEY}-{now}",
        "iss": TWILIO_API_KEY,
        "sub": TWILIO_ACCOUNT_SID,
        "iat": now,
        "exp": now + 3600 * 8, # 8 giờ làm việc
        "grants": {
            "identity": identity,
            "voice": {
                "outgoing": {
                    "application_sid": TWILIO_TWIML_APP_SID
                },
                "incoming": {
                    "allow": True
                }
            }
        }
    }
    
    token = jwt.encode(payload, TWILIO_API_SECRET, algorithm="HS256")
    return {
        "identity": identity,
        "token": token,
        "caller_id": TWILIO_CALLER_ID,
        "expires_in": 3600 * 8
    }

def generate_outbound_twiml(to_number):
    """
    Tạo TwiML XML cho cuộc gọi đi tới khách hàng
    """
    cleaned_number = to_number.strip().replace(" ", "")
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Dial callerId="{TWILIO_CALLER_ID}" record="record-from-answer-dual" statusCallback="/api/telephony/status_callback" statusCallbackEvent="initiated ringing answered completed">
        <Number>{cleaned_number}</Number>
    </Dial>
</Response>"""
    return twiml

def generate_inbound_twiml(agent_identity="agent_all"):
    """
    Tạo TwiML XML cho cuộc gọi đến đổ chuông vào Softphone nhân viên
    """
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Dial record="record-from-answer-dual" statusCallback="/api/telephony/status_callback" statusCallbackEvent="initiated ringing answered completed">
        <Client>{agent_identity}</Client>
    </Dial>
</Response>"""
    return twiml

def handle_call_status_callback(form_data):
    """
    Nhận callback trạng thái cuộc gọi từ Twilio và ghi nhận bản ghi cuộc gọi
    """
    call_sid = form_data.get("CallSid")
    duration = int(form_data.get("CallDuration", 0) or 0)
    status = form_data.get("CallStatus", "completed")
    recording_url = form_data.get("RecordingUrl")
    from_number = form_data.get("From", "")
    to_number = form_data.get("To", "")

    if call_sid:
        update_call_log(
            call_sid=call_sid,
            duration=duration,
            status=status,
            recording_url=recording_url,
            notes=f"Từ: {from_number} Đến: {to_number}"
        )
        
        log_audit(
            user_id=None,
            username="TWILIO_VOICE",
            action="CALL_COMPLETED",
            target_type="TELEPHONY",
            target_id=call_sid,
            details=f"Cuộc gọi {call_sid} kết thúc: {duration}s, trạng thái: {status}"
        )

    return {"status": "ok"}
