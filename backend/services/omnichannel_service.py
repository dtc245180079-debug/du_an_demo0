import os
import json
import time
import hmac
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jwt
import requests
from dotenv import load_dotenv
from database.db import (
    save_omnichannel_message, 
    check_and_set_idempotent_key, 
    get_or_create_customer, 
    get_conversation_messages
)

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "super-crm-omnichannel-jwt-secret-key-32bytes-secure-2026")
ALLOWED_WEBCHAT_ORIGINS = os.getenv("ALLOWED_WEBCHAT_ORIGINS", "*").split(",")

# =====================================================================
# 1. WEBCHAT TOKEN & ORIGIN VALIDATION
# =====================================================================
def generate_webchat_token(customer_name, customer_phone=None, origin=None):
    payload = {
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "origin": origin,
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400 * 7 # 7 ngày
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_webchat_token(token, request_origin=None):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        # Kiểm tra origin nếu có cấu hình giới hạn
        if "*" not in ALLOWED_WEBCHAT_ORIGINS and request_origin:
            allowed = any(request_origin.strip().rstrip("/") == o.strip().rstrip("/") for o in ALLOWED_WEBCHAT_ORIGINS)
            if not allowed:
                return False, "Origin không được phép truy cập Webchat widget."
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, "Token Webchat đã hết hạn."
    except Exception as e:
        return False, f"Token không hợp lệ: {str(e)}"

# =====================================================================
# 2. CHUẨN HÓA TIN NHẮN (MESSAGE NORMALIZER)
# =====================================================================
def process_inbound_message(channel, external_msg_id, sender_id, sender_name, content, conversation_id=None, raw_payload=None):
    """
    Xử lý tin nhắn đến từ tất cả các kênh:
    - Chống xử lý trùng sự kiện (Idempotency)
    - Chuẩn hóa thông tin khách hàng vào Customer 360
    - Lưu vào hộp thư hợp nhất
    """
    # 1. Chống trùng lặp sự kiện
    idempotent_key = f"omni_{channel}_{external_msg_id}"
    if not check_and_set_idempotent_key(idempotent_key, scope="omnichannel"):
        print(f"[OMNICHANNEL DEDUP] Bỏ qua tin nhắn trùng lặp: {idempotent_key}")
        return {"status": "duplicate", "message": "Tin nhắn đã được xử lý trước đó."}

    # 2. Tạo hoặc chuẩn hóa conversation_id
    if not conversation_id:
        conversation_id = f"CONV-{channel.upper()}-{sender_id}"

    # 3. Chuẩn hóa & liên kết khách hàng trong Customer 360
    phone = None
    email = None
    zalo_id = sender_id if channel == "zalo" else None
    fb_id = sender_id if channel == "facebook" else None
    ig_id = sender_id if channel == "instagram" else None
    
    if channel == "email" and "@" in sender_id:
        email = sender_id
    elif sender_id and sender_id.isdigit() and len(sender_id) >= 10:
        phone = sender_id

    customer = get_or_create_customer(
        full_name=sender_name or f"Khách hàng {channel.capitalize()}",
        phone=phone,
        email=email,
        zalo_id=zalo_id,
        fb_id=fb_id,
        ig_id=ig_id
    )

    # 4. Lưu tin nhắn vào cơ sở dữ liệu
    msg_id = save_omnichannel_message(
        external_msg_id=external_msg_id,
        conversation_id=conversation_id,
        channel=channel,
        sender_type="customer",
        sender_id=sender_id,
        sender_name=sender_name or customer["full_name"],
        content=content,
        direction="inbound",
        raw_payload=json.dumps(raw_payload, ensure_ascii=False) if raw_payload else None
    )

    # 5. Kích hoạt phản hồi tự động nếu có
    from services.automation_service import check_and_send_auto_reply
    auto_reply = check_and_send_auto_reply(channel, conversation_id, sender_id, sender_name)

    return {
        "status": "success",
        "msg_id": msg_id,
        "conversation_id": conversation_id,
        "customer": customer,
        "auto_reply": auto_reply
    }

# =====================================================================
# 3. TRẢ LỜI TIN NHẮN THEO KÊNH TƯƠNG ỨNG (OUTBOUND DISPATCHER)
# =====================================================================
def send_outbound_reply(channel, conversation_id, recipient_id, content, agent_id=None, agent_name="Chuyên viên CSKH"):
    """
    Gửi tin nhắn trả lời từ nhân viên tới khách hàng qua kênh tương ứng
    """
    external_msg_id = f"OUT-{int(time.time()*1000)}"
    dispatch_success = True
    dispatch_error = None

    # Gửi qua kênh Zalo OA
    if channel == "zalo":
        zalo_token = os.getenv("ZALO_OA_ACCESS_TOKEN")
        if zalo_token:
            try:
                url = "https://openapi.zalo.me/v3.0/oa/message/cs"
                headers = {"access_token": zalo_token, "Content-Type": "application/json"}
                data = {
                    "recipient": {"user_id": recipient_id},
                    "message": {"text": content}
                }
                res = requests.post(url, headers=headers, json=data, timeout=10)
                res_data = res.json()
                if res_data.get("error") != 0:
                    dispatch_error = f"Zalo OA Error: {res_data.get('message')}"
            except Exception as e:
                dispatch_error = str(e)
        else:
            print(f"[MOCK ZALO OA] Gửi tin nhắn tới Zalo ID {recipient_id}: {content}")

    # Gửi qua Email (SMTP)
    elif channel == "email":
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASSWORD")
        smtp_from = os.getenv("SMTP_FROM", smtp_user)
        
        if smtp_host and smtp_user and smtp_pass:
            try:
                msg = MIMEMultipart()
                msg["From"] = smtp_from
                msg["To"] = recipient_id
                msg["Subject"] = f"[CSKH] Phản hồi yêu cầu hỗ trợ"
                msg.attach(MIMEText(content, "plain", "utf-8"))
                
                with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            except Exception as e:
                dispatch_error = str(e)
        else:
            print(f"[MOCK EMAIL SMTP] Gửi email tới {recipient_id}: {content}")

    # Gửi qua Facebook Messenger / Instagram
    elif channel in ["facebook", "instagram"]:
        fb_token = os.getenv("FB_PAGE_ACCESS_TOKEN")
        if fb_token:
            try:
                url = "https://graph.facebook.com/v19.0/me/messages"
                params = {"access_token": fb_token}
                data = {
                    "recipient": {"id": recipient_id},
                    "message": {"text": content}
                }
                res = requests.post(url, params=params, json=data, timeout=10)
                res_data = res.json()
                if "error" in res_data:
                    dispatch_error = res_data["error"].get("message")
            except Exception as e:
                dispatch_error = str(e)
        else:
            print(f"[MOCK {channel.upper()}] Gửi tin tới {recipient_id}: {content}")

    # Kênh Webchat: Chỉ cần lưu vào cơ sở dữ liệu để client polling nhận về
    elif channel == "webchat":
        pass

    # Lưu bản ghi tin nhắn gửi đi
    msg_id = save_omnichannel_message(
        external_msg_id=external_msg_id,
        conversation_id=conversation_id,
        channel=channel,
        sender_type="agent",
        sender_id=str(agent_id or "agent"),
        sender_name=agent_name,
        content=content,
        direction="outbound",
        raw_payload=json.dumps({"error": dispatch_error} if dispatch_error else {"status": "sent"})
    )

    return {
        "success": True if not dispatch_error else False,
        "msg_id": msg_id,
        "error": dispatch_error
    }

# =====================================================================
# 4. SENDGRID & IMAP EMAIL INBOUND HANDLERS
# =====================================================================
def parse_sendgrid_inbound(form_data):
    """
    Phân tích payload từ SendGrid Inbound Parse Webhook
    """
    sender = form_data.get("from", "")
    to = form_data.get("to", "")
    subject = form_data.get("subject", "Hỗ trợ khách hàng")
    text = form_data.get("text", "") or form_data.get("html", "")
    
    # Rút trích email thuần túy
    email_addr = sender
    if "<" in sender and ">" in sender:
        email_addr = sender.split("<")[1].split(">")[0].strip()
        
    sender_name = sender.split("<")[0].strip().strip('"') if "<" in sender else email_addr
    external_msg_id = form_data.get("headers", {}).get("Message-ID") or f"SG-{int(time.time()*1000)}"
    
    return process_inbound_message(
        channel="email",
        external_msg_id=external_msg_id,
        sender_id=email_addr,
        sender_name=sender_name,
        content=f"Tiêu đề: {subject}\n\n{text}",
        conversation_id=f"CONV-EMAIL-{email_addr}",
        raw_payload=form_data
    )

def poll_imap_inbox():
    """
    Đọc hộp thư đến qua giao thức IMAP nếu cấu hình biến môi trường
    """
    imap_host = os.getenv("IMAP_HOST")
    imap_user = os.getenv("IMAP_USER")
    imap_pass = os.getenv("IMAP_PASSWORD")
    if not (imap_host and imap_user and imap_pass):
        return {"status": "skipped", "message": "Chưa cấu hình IMAP trong .env"}

    import imaplib
    import email
    from email.header import decode_header
    
    processed_count = 0
    try:
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(imap_user, imap_pass)
        mail.select("inbox")
        
        status, messages = mail.search(None, "UNSEEN")
        if status == "OK":
            for num in messages[0].split():
                status, data = mail.fetch(num, "(RFC822)")
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8", errors="ignore")
                
                sender = msg.get("From")
                msg_id = msg.get("Message-ID", f"IMAP-{num.decode()}")
                
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore")
                    
                process_inbound_message(
                    channel="email",
                    external_msg_id=msg_id,
                    sender_id=sender,
                    sender_name=sender,
                    content=f"Tiêu đề: {subject}\n\n{body}",
                    conversation_id=f"CONV-EMAIL-{sender}"
                )
                processed_count += 1
                
        mail.close()
        mail.logout()
        return {"status": "success", "processed_emails": processed_count}
    except Exception as e:
        return {"status": "error", "error": str(e)}
