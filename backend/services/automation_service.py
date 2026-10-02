import os
import datetime
from database.db import (
    get_auto_reply, 
    save_omnichannel_message, 
    check_and_set_idempotent_key, 
    get_ticket_by_id, 
    add_ticket_message,
    log_audit
)

def is_within_working_hours():
    """
    Kiểm tra xem thời điểm hiện tại có trong khung giờ làm việc không (08:00 - 22:00)
    """
    now = datetime.datetime.now().time()
    start = datetime.time(8, 0)
    end = datetime.time(22, 0)
    return start <= now <= end

def check_and_send_auto_reply(channel, conversation_id, sender_id, sender_name):
    """
    Tự động kích hoạt phản hồi dựa trên kênh và ngữ cảnh
    """
    # 1. Kiểm tra ngoài giờ làm việc
    if not is_within_working_hours():
        reply = get_auto_reply(channel, "out_of_office")
        if reply and reply.get("is_active"):
            save_omnichannel_message(
                external_msg_id=f"AUTO-OOF-{datetime.datetime.now().timestamp()}",
                conversation_id=conversation_id,
                channel=channel,
                sender_type="bot",
                sender_id="bot_auto",
                sender_name="Trợ lý tự động",
                content=reply["message"],
                direction="outbound"
            )
            return {"type": "out_of_office", "message": reply["message"]}

    # 2. Kiểm tra phản hồi lời chào (Greeting)
    reply = get_auto_reply(channel, "greeting")
    if reply and reply.get("is_active"):
        save_omnichannel_message(
            external_msg_id=f"AUTO-GREET-{datetime.datetime.now().timestamp()}",
            conversation_id=conversation_id,
            channel=channel,
            sender_type="bot",
            sender_id="bot_auto",
            sender_name="Trợ lý tự động",
            content=reply["message"],
            direction="outbound"
        )
        return {"type": "greeting", "message": reply["message"]}

    return None

def trigger_ticket_closure_survey(ticket_id):
    """
    Khi đóng ticket, tự động tạo khảo sát CSAT/NPS và gửi qua kênh phù hợp.
    Theo dõi tính Idempotent để tuyệt đối KHÔNG gửi trùng lặp khảo sát!
    """
    idempotent_key = f"survey_ticket_{ticket_id}"
    if not check_and_set_idempotent_key(idempotent_key, scope="survey"):
        print(f"[SURVEY IDEMPOTENT] Khảo sát cho ticket {ticket_id} đã được gửi trước đó. Bỏ qua.")
        return {"status": "already_sent", "message": "Khảo sát đã được gửi trước đó."}

    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        return {"status": "error", "message": "Ticket không tồn tại."}

    survey_message = (
        f"[ĐÁNH GIÁ DỊCH VỤ CSKH]\n"
        f"Kính gửi {ticket.get('customer_name', 'Quý khách')},\n"
        f"Yêu cầu hỗ trợ mã [{ticket.get('ticket_code')}] đã được chuyên viên hoàn tất xử lý.\n"
        f"Quý khách vui lòng dành 30 giây đánh giá chất lượng phục vụ để chúng tôi cải thiện tốt hơn:\n"
        f"Link đánh giá CSAT & NPS: /portal/survey/{ticket_id}\n\n"
        f"1. Mức độ hài lòng chung (CSAT: 1 - 5 sao)\n"
        f"2. Bạn có sẵn lòng giới thiệu dịch vụ tới bạn bè? (NPS: 0 - 10 điểm)\n"
        f"Chân thành cảm ơn quý khách!"
    )

    # Gửi tin nhắn khảo sát vào luồng ticket
    add_ticket_message(
        ticket_id=ticket_id,
        sender_type="system",
        sender_id=0,
        sender_name="Hệ thống Khảo sát CSKH",
        message=survey_message,
        channel=ticket.get("channel", "web")
    )

    # Ghi audit log
    log_audit(
        user_id=None,
        username="SYSTEM_AUTOMATION",
        action="DISPATCH_SURVEY",
        target_type="TICKET",
        target_id=ticket_id,
        details=f"Gửi khảo sát CSAT/NPS cho ticket {ticket.get('ticket_code')} thành công"
    )

    return {"status": "success", "message": "Đã gửi lời mời khảo sát thành công."}
