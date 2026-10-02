import sys
import platform

# Khắc phục lỗi Python 3.13 trên Windows bị nghẽn truy vấn WMI khi kết nối MySQL
if sys.platform == "win32":
    platform.system = lambda: "Windows"

# Đảm bảo mã hóa UTF-8 cho console Windows tránh UnicodeEncodeError
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import os
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))
load_dotenv(os.path.join(BASE_DIR, "..", "..", ".env"))
load_dotenv()

def get_connection():
    db_name = os.getenv("DB_NAME", "customer_support_ai")
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD"),
            database=db_name,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci"
        )
    except mysql.connector.errors.ProgrammingError as err:
        if err.errno == 1049:  # Unknown database
            init_conn = mysql.connector.connect(
                host=os.getenv("DB_HOST", "127.0.0.1"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD"),
                charset="utf8mb4",
                collation="utf8mb4_unicode_ci"
            )
            init_cursor = init_conn.cursor()
            init_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            init_conn.commit()
            init_cursor.close()
            init_conn.close()
            return mysql.connector.connect(
                host=os.getenv("DB_HOST", "127.0.0.1"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD"),
                database=db_name,
                charset="utf8mb4",
                collation="utf8mb4_unicode_ci"
            )
        raise err

# =====================================================================
# MODULE: SUPPORT FAQS (GIỮ NGUYÊN 100% CÁC HÀM HIỆN CÓ CỦA DỰ ÁN)
# =====================================================================
def get_faqs():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM support_faqs ORDER BY id DESC")
    data = cursor.fetchall()
    conn.close()
    return data

def add_faq(issue_name, category, brand, symptom, solution):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
    INSERT INTO support_faqs (issue_name, category, brand, symptom, solution)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (issue_name, category, brand, symptom, solution))
    conn.commit()
    conn.close()

def get_faq(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM support_faqs WHERE id=%s", (id,))
    faq = cursor.fetchone()
    conn.close()
    return faq

def update_faq(id, issue_name, category, brand, symptom, solution):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
    UPDATE support_faqs
    SET issue_name=%s, category=%s, brand=%s, symptom=%s, solution=%s
    WHERE id=%s
    """
    cursor.execute(sql, (issue_name, category, brand, symptom, solution, id))
    conn.commit()
    conn.close()

def delete_faq(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM support_faqs WHERE id=%s", (id,))
    conn.commit()
    conn.close()

def search_faqs(keyword=None, category=None, brand=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM support_faqs WHERE 1=1"
    params = []

    if keyword:
        words = [w.strip() for w in keyword.strip().split() if len(w.strip()) > 1]
        if words:
            clauses = []
            for w in words:
                clauses.append("(issue_name LIKE %s OR symptom LIKE %s OR solution LIKE %s)")
                val = f"%{w}%"
                params.extend([val, val, val])
            sql += f" AND ({' OR '.join(clauses)})"
        else:
            sql += " AND (issue_name LIKE %s OR symptom LIKE %s OR solution LIKE %s)"
            value = f"%{keyword}%"
            params.extend([value, value, value])
    
    if category:
        sql += " AND category LIKE %s"
        params.append(f"%{category}%")
        
    if brand:
        sql += " AND (brand LIKE %s OR brand LIKE '%Tất cả%')"
        params.append(f"%{brand}%")

    sql += " ORDER BY id DESC"
    cursor.execute(sql, params)
    data = cursor.fetchall()
    conn.close()
    return data

# =====================================================================
# MODULE: USERS & AUTHENTICATION
# =====================================================================
def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, email, password_hash, full_name, phone=None, role="customer"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, full_name, phone, role)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (username, email, password_hash, full_name, phone, role))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_all_agents():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, full_name, email, phone, role FROM users WHERE role IN ('agent', 'admin') AND is_active=1")
    agents = cursor.fetchall()
    conn.close()
    return agents

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, full_name, phone, role, is_active, created_at FROM users ORDER BY id DESC")
    users = cursor.fetchall()
    conn.close()
    return users

def update_user_role_status(user_id, role, is_active):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role=%s, is_active=%s WHERE id=%s", (role, is_active, user_id))
    conn.commit()
    conn.close()

# =====================================================================
# MODULE: CUSTOMER 360
# =====================================================================
def get_or_create_customer(full_name, phone=None, email=None, user_id=None, zalo_id=None, fb_id=None, ig_id=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Tìm theo phone hoặc email
    customer = None
    if phone:
        cursor.execute("SELECT * FROM customers WHERE phone=%s LIMIT 1", (phone,))
        customer = cursor.fetchone()
    if not customer and email:
        cursor.execute("SELECT * FROM customers WHERE email=%s LIMIT 1", (email,))
        customer = cursor.fetchone()
    if not customer and user_id:
        cursor.execute("SELECT * FROM customers WHERE user_id=%s LIMIT 1", (user_id,))
        customer = cursor.fetchone()
        
    if customer:
        # Cập nhật thông tin bổ sung nếu có
        updates = []
        params = []
        if user_id and not customer.get("user_id"):
            updates.append("user_id=%s")
            params.append(user_id)
        if zalo_id and not customer.get("zalo_id"):
            updates.append("zalo_id=%s")
            params.append(zalo_id)
        if fb_id and not customer.get("fb_id"):
            updates.append("fb_id=%s")
            params.append(fb_id)
        if updates:
            params.append(customer["id"])
            cursor.execute(f"UPDATE customers SET {', '.join(updates)} WHERE id=%s", params)
            conn.commit()
        conn.close()
        return customer
        
    # Tạo mới khách hàng
    cursor.execute("""
        INSERT INTO customers (user_id, full_name, phone, email, zalo_id, fb_id, ig_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, full_name, phone, email, zalo_id, fb_id, ig_id))
    cust_id = cursor.lastrowid
    conn.commit()
    cursor.execute("SELECT * FROM customers WHERE id=%s", (cust_id,))
    new_customer = cursor.fetchone()
    conn.close()
    return new_customer

def get_customer_by_id(customer_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE id=%s", (customer_id,))
    customer = cursor.fetchone()
    conn.close()
    return customer

def get_customer_by_phone(phone):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE phone=%s", (phone,))
    customer = cursor.fetchone()
    conn.close()
    return customer

def get_customer_by_user_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE user_id=%s", (user_id,))
    customer = cursor.fetchone()
    conn.close()
    return customer

def search_customers(keyword):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    kw = f"%{keyword}%"
    cursor.execute("""
        SELECT * FROM customers 
        WHERE full_name LIKE %s OR phone LIKE %s OR email LIKE %s OR zalo_id LIKE %s OR fb_id LIKE %s
        ORDER BY id DESC LIMIT 50
    """, (kw, kw, kw, kw, kw))
    customers = cursor.fetchall()
    conn.close()
    return customers

def get_all_customers(limit=100):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers ORDER BY id DESC LIMIT %s", (limit,))
    customers = cursor.fetchall()
    conn.close()
    return customers

def update_customer_notes(customer_id, notes, member_rank=None):
    conn = get_connection()
    cursor = conn.cursor()
    if member_rank:
        cursor.execute("UPDATE customers SET notes=%s, member_rank=%s WHERE id=%s", (notes, member_rank, customer_id))
    else:
        cursor.execute("UPDATE customers SET notes=%s WHERE id=%s", (notes, customer_id))
    conn.commit()
    conn.close()

# =====================================================================
# MODULE: TICKETS & TICKET MESSAGES
# =====================================================================
def generate_ticket_code():
    import random
    import datetime
    now = datetime.datetime.now()
    rand = random.randint(1000, 9999)
    return f"TK-{now.strftime('%Y%m')}-{rand}"

def create_ticket(customer_id, customer_name, customer_phone, customer_email, channel, subject, priority="medium", first_message=None):
    conn = get_connection()
    cursor = conn.cursor()
    ticket_code = generate_ticket_code()
    cursor.execute("""
        INSERT INTO tickets (ticket_code, customer_id, customer_name, customer_phone, customer_email, channel, subject, priority, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'open')
    """, (ticket_code, customer_id, customer_name, customer_phone, customer_email, channel, subject, priority))
    ticket_id = cursor.lastrowid
    
    if first_message:
        cursor.execute("""
            INSERT INTO ticket_messages (ticket_id, sender_type, sender_id, sender_name, message, channel)
            VALUES (%s, 'customer', %s, %s, %s, %s)
        """, (ticket_id, customer_id, customer_name, first_message, channel))
        
    conn.commit()
    conn.close()
    return ticket_id, ticket_code

def get_ticket_by_id(ticket_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.*, u.full_name as assigned_agent_name 
        FROM tickets t
        LEFT JOIN users u ON t.assigned_agent_id = u.id
        WHERE t.id=%s
    """, (ticket_id,))
    ticket = cursor.fetchone()
    conn.close()
    return ticket

def get_ticket_by_code(ticket_code):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.*, u.full_name as assigned_agent_name 
        FROM tickets t
        LEFT JOIN users u ON t.assigned_agent_id = u.id
        WHERE t.ticket_code=%s
    """, (ticket_code,))
    ticket = cursor.fetchone()
    conn.close()
    return ticket

def get_tickets(status=None, assigned_agent_id=None, customer_id=None, channel=None, keyword=None, limit=100):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT t.*, u.full_name as assigned_agent_name 
        FROM tickets t
        LEFT JOIN users u ON t.assigned_agent_id = u.id
        WHERE 1=1
    """
    params = []
    if status and status != 'all':
        sql += " AND t.status=%s"
        params.append(status)
    if assigned_agent_id:
        sql += " AND t.assigned_agent_id=%s"
        params.append(assigned_agent_id)
    if customer_id:
        sql += " AND t.customer_id=%s"
        params.append(customer_id)
    if channel and channel != 'all':
        sql += " AND t.channel=%s"
        params.append(channel)
    if keyword:
        kw = f"%{keyword}%"
        sql += " AND (t.ticket_code LIKE %s OR t.subject LIKE %s OR t.customer_name LIKE %s OR t.customer_phone LIKE %s)"
        params.extend([kw, kw, kw, kw])
        
    sql += " ORDER BY t.id DESC LIMIT %s"
    params.append(limit)
    cursor.execute(sql, params)
    tickets = cursor.fetchall()
    conn.close()
    return tickets

def update_ticket_status(ticket_id, status):
    import datetime
    conn = get_connection()
    cursor = conn.cursor()
    if status in ['resolved', 'closed']:
        cursor.execute("UPDATE tickets SET status=%s, resolved_at=%s WHERE id=%s", (status, datetime.datetime.now(), ticket_id))
    else:
        cursor.execute("UPDATE tickets SET status=%s WHERE id=%s", (status, ticket_id))
    conn.commit()
    conn.close()

def assign_ticket(ticket_id, agent_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tickets SET assigned_agent_id=%s, status=IF(status='open', 'in_progress', status) WHERE id=%s", (agent_id, ticket_id))
    conn.commit()
    conn.close()

def add_ticket_message(ticket_id, sender_type, sender_id, sender_name, message, channel='web'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ticket_messages (ticket_id, sender_type, sender_id, sender_name, message, channel)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (ticket_id, sender_type, sender_id, sender_name, message, channel))
    msg_id = cursor.lastrowid
    cursor.execute("UPDATE tickets SET updated_at=CURRENT_TIMESTAMP WHERE id=%s", (ticket_id,))
    conn.commit()
    conn.close()
    return msg_id

def get_ticket_messages(ticket_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ticket_messages WHERE ticket_id=%s ORDER BY id ASC", (ticket_id,))
    messages = cursor.fetchall()
    conn.close()
    return messages

# =====================================================================
# MODULE: SURVEYS (CSAT / NPS)
# =====================================================================
def create_ticket_survey(ticket_id, customer_id, rating_csat, score_nps, feedback):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ticket_surveys (ticket_id, customer_id, rating_csat, score_nps, feedback)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE rating_csat=VALUES(rating_csat), score_nps=VALUES(score_nps), feedback=VALUES(feedback)
    """, (ticket_id, customer_id, rating_csat, score_nps, feedback))
    conn.commit()
    conn.close()

def get_ticket_survey(ticket_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ticket_surveys WHERE ticket_id=%s", (ticket_id,))
    survey = cursor.fetchone()
    conn.close()
    return survey

def get_customer_surveys(customer_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ticket_surveys WHERE customer_id=%s ORDER BY id DESC", (customer_id,))
    surveys = cursor.fetchall()
    conn.close()
    return surveys

# =====================================================================
# MODULE: OMNICHANNEL INBOX
# =====================================================================
def save_omnichannel_message(external_msg_id, conversation_id, channel, sender_type, sender_id, sender_name, content, direction, raw_payload=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO omnichannel_messages (external_msg_id, conversation_id, channel, sender_type, sender_id, sender_name, content, direction, raw_payload)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (external_msg_id, conversation_id, channel, sender_type, sender_id, sender_name, content, direction, raw_payload))
    msg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return msg_id

def get_omnichannel_conversations(channel=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT conversation_id, channel, sender_name, content as last_message, direction, created_at,
               (SELECT COUNT(*) FROM omnichannel_messages m2 WHERE m2.conversation_id = m1.conversation_id) as msg_count
        FROM omnichannel_messages m1
        WHERE id IN (
            SELECT MAX(id) FROM omnichannel_messages GROUP BY conversation_id
        )
    """
    params = []
    if channel and channel != 'all':
        sql += " AND channel=%s"
        params.append(channel)
    sql += " ORDER BY created_at DESC LIMIT 50"
    cursor.execute(sql, params)
    convs = cursor.fetchall()
    conn.close()
    return convs

def get_conversation_messages(conversation_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM omnichannel_messages WHERE conversation_id=%s ORDER BY id ASC", (conversation_id,))
    msgs = cursor.fetchall()
    conn.close()
    return msgs

# =====================================================================
# MODULE: ORDERS & LOGISTICS
# =====================================================================
def get_orders_by_phone(phone):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders WHERE customer_phone=%s ORDER BY id DESC", (phone,))
    orders = cursor.fetchall()
    conn.close()
    return orders

def save_order(order_code, source, customer_name, customer_phone, total_amount, status, shipping_code=None, shipping_carrier=None, shipping_status=None, items_summary=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (order_code, source, customer_name, customer_phone, total_amount, status, shipping_code, shipping_carrier, shipping_status, items_summary)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            total_amount=VALUES(total_amount),
            status=VALUES(status),
            shipping_code=VALUES(shipping_code),
            shipping_carrier=VALUES(shipping_carrier),
            shipping_status=VALUES(shipping_status),
            items_summary=VALUES(items_summary)
    """, (order_code, source, customer_name, customer_phone, total_amount, status, shipping_code, shipping_carrier, shipping_status, items_summary))
    conn.commit()
    conn.close()

def update_shipping_status(shipping_code, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET shipping_status=%s WHERE shipping_code=%s", (new_status, shipping_code))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected

def get_all_orders(limit=100):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders ORDER BY id DESC LIMIT %s", (limit,))
    orders = cursor.fetchall()
    conn.close()
    return orders

# =====================================================================
# MODULE: WORK SHIFTS
# =====================================================================
def get_work_shifts(agent_id=None, shift_date=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT ws.*, u.full_name as agent_name, u.username
        FROM work_shifts ws
        JOIN users u ON ws.agent_id = u.id
        WHERE 1=1
    """
    params = []
    if agent_id:
        sql += " AND ws.agent_id=%s"
        params.append(agent_id)
    if shift_date:
        sql += " AND ws.shift_date=%s"
        params.append(shift_date)
    sql += " ORDER BY ws.shift_date DESC, ws.start_time ASC LIMIT 100"
    cursor.execute(sql, params)
    shifts = cursor.fetchall()
    conn.close()
    return shifts

def create_work_shift(agent_id, shift_name, shift_date, start_time, end_time, notes=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO work_shifts (agent_id, shift_name, shift_date, start_time, end_time, status, notes)
        VALUES (%s, %s, %s, %s, %s, 'scheduled', %s)
    """, (agent_id, shift_name, shift_date, start_time, end_time, notes))
    shift_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return shift_id

def checkin_shift(shift_id, is_checkin=True):
    import datetime
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    if is_checkin:
        cursor.execute("UPDATE work_shifts SET check_in_time=%s, status='present' WHERE id=%s", (now, shift_id))
    else:
        cursor.execute("UPDATE work_shifts SET check_out_time=%s, status='completed' WHERE id=%s", (now, shift_id))
    conn.commit()
    conn.close()

# =====================================================================
# MODULE: SALES OPPORTUNITIES (KANBAN PIPELINE)
# =====================================================================
def get_sales_opportunities(agent_id=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT so.*, u.full_name as agent_name 
        FROM sales_opportunities so
        LEFT JOIN users u ON so.assigned_agent_id = u.id
        WHERE 1=1
    """
    params = []
    if agent_id:
        sql += " AND so.assigned_agent_id=%s"
        params.append(agent_id)
    sql += " ORDER BY so.id DESC"
    cursor.execute(sql, params)
    opps = cursor.fetchall()
    conn.close()
    return opps

def create_sales_opportunity(customer_name, customer_phone, title, value, stage="lead", probability=20, assigned_agent_id=None, expected_close_date=None, customer_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sales_opportunities (customer_id, customer_name, customer_phone, title, value, stage, probability, assigned_agent_id, expected_close_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (customer_id, customer_name, customer_phone, title, value, stage, probability, assigned_agent_id, expected_close_date))
    opp_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return opp_id

def update_opportunity_stage(opp_id, new_stage):
    prob_map = {"lead": 20, "contacted": 40, "proposal": 60, "negotiation": 80, "won": 100, "lost": 0}
    prob = prob_map.get(new_stage, 50)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sales_opportunities SET stage=%s, probability=%s WHERE id=%s", (new_stage, prob, opp_id))
    conn.commit()
    conn.close()

# =====================================================================
# MODULE: AUTO-REPLIES & AUTOMATION
# =====================================================================
def get_auto_replies():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM auto_replies ORDER BY id ASC")
    replies = cursor.fetchall()
    conn.close()
    return replies

def get_auto_reply(channel, trigger_type):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM auto_replies WHERE (channel=%s OR channel='all') AND trigger_type=%s AND is_active=1 ORDER BY channel DESC LIMIT 1", (channel, trigger_type))
    reply = cursor.fetchone()
    conn.close()
    return reply

def save_auto_reply(channel, trigger_type, message, is_active=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO auto_replies (channel, trigger_type, message, is_active)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE message=VALUES(message), is_active=VALUES(is_active)
    """, (channel, trigger_type, message, is_active))
    conn.commit()
    conn.close()

# =====================================================================
# MODULE: CALL LOGS (TWILIO SOFTPHONE)
# =====================================================================
def create_call_log(agent_id, customer_phone, direction="outbound", call_sid=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO call_logs (agent_id, customer_phone, direction, call_sid, status)
        VALUES (%s, %s, %s, %s, 'in-progress')
    """, (agent_id, customer_phone, direction, call_sid))
    call_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return call_id

def update_call_log(call_sid, duration, status, recording_url=None, notes=None):
    conn = get_connection()
    cursor = conn.cursor()
    updates = ["call_duration=%s", "status=%s"]
    params = [duration, status]
    if recording_url:
        updates.append("recording_url=%s")
        params.append(recording_url)
    if notes:
        updates.append("notes=%s")
        params.append(notes)
    params.append(call_sid)
    cursor.execute(f"UPDATE call_logs SET {', '.join(updates)} WHERE call_sid=%s", params)
    conn.commit()
    conn.close()

def get_call_logs(limit=50):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT cl.*, u.full_name as agent_name 
        FROM call_logs cl
        LEFT JOIN users u ON cl.agent_id = u.id
        ORDER BY cl.id DESC LIMIT %s
    """, (limit,))
    logs = cursor.fetchall()
    conn.close()
    return logs

# =====================================================================
# MODULE: AUDIT LOGS
# =====================================================================
def log_audit(user_id, username, action, target_type, target_id, details=None, ip_address=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (user_id, username, action, target_type, target_id, details, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, username, action, target_type, str(target_id) if target_id else None, details, ip_address))
        conn.commit()
        conn.close()
    except Exception as e:
        print("[AUDIT ERROR] Không thể ghi audit log:", e)

def get_audit_logs(limit=100):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT %s", (limit,))
    logs = cursor.fetchall()
    conn.close()
    return logs

# =====================================================================
# MODULE: IDEMPOTENCY HANDLER (CHỐNG LẶP SỰ KIỆN WEBHOOK / KHẢO SÁT)
# =====================================================================
def check_and_set_idempotent_key(key_name, scope="general"):
    """
    Trả về True nếu key chưa tồn tại (cho phép xử lý và ghi nhận key).
    Trả về False nếu key đã tồn tại (phát hiện trùng lặp, bỏ qua).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO idempotent_keys (key_name, scope) VALUES (%s, %s)", (key_name, scope))
        conn.commit()
        conn.close()
        return True
    except mysql.connector.IntegrityError:
        conn.close()
        return False
    except Exception:
        conn.close()
        return False

# =====================================================================
# MODULE: DASHBOARD & ANALYTICS STATS
# =====================================================================
def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Thống kê Ticket theo trạng thái
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM tickets 
        GROUP BY status
    """)
    ticket_status_rows = cursor.fetchall()
    ticket_status = {r['status']: r['count'] for r in ticket_status_rows}
    
    # 2. Tổng số khách hàng
    cursor.execute("SELECT COUNT(*) as total_customers FROM customers")
    total_customers = cursor.fetchone()['total_customers']
    
    # 3. Tổng số tickets
    cursor.execute("SELECT COUNT(*) as total_tickets FROM tickets")
    total_tickets = cursor.fetchone()['total_tickets']
    
    # 4. Thống kê doanh thu theo thời gian (theo ngày trong 7 ngày gần nhất)
    cursor.execute("""
        SELECT DATE(created_at) as order_date, SUM(total_amount) as daily_revenue, COUNT(*) as order_count
        FROM orders
        GROUP BY DATE(created_at)
        ORDER BY order_date DESC
        LIMIT 7
    """)
    revenue_rows = cursor.fetchall()
    
    # 5. Phân bổ Ticket theo kênh tiếp nhận
    cursor.execute("""
        SELECT channel, COUNT(*) as count
        FROM tickets
        GROUP BY channel
    """)
    channel_rows = cursor.fetchall()
    
    # 6. CSAT trung bình
    cursor.execute("SELECT AVG(rating_csat) as avg_csat, AVG(score_nps) as avg_nps, COUNT(*) as survey_count FROM ticket_surveys")
    survey_stat = cursor.fetchone()
    
    conn.close()
    return {
        "ticket_status": ticket_status,
        "total_customers": total_customers,
        "total_tickets": total_tickets,
        "revenue_trend": revenue_rows,
        "channel_distribution": channel_rows,
        "csat_avg": round(float(survey_stat['avg_csat'] or 5.0), 1),
        "nps_avg": round(float(survey_stat['avg_nps'] or 10.0), 1),
        "survey_count": survey_stat['survey_count']
    }

# =====================================================================
# MODULE: PHONE PRODUCTS CATALOG & INVENTORY
# =====================================================================
def get_phone_products(keyword=None, brand=None, price_min=None, price_max=None, in_stock_only=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM phone_products WHERE is_active=1"
    params = []
    
    if keyword:
        kw = f"%{keyword}%"
        sql += " AND (name LIKE %s OR model LIKE %s OR chip_spec LIKE %s OR camera_spec LIKE %s)"
        params.extend([kw, kw, kw, kw])
    if brand and brand != 'all':
        sql += " AND brand=%s"
        params.append(brand)
    if price_min:
        sql += " AND COALESCE(promo_price, listed_price) >= %s"
        params.append(float(price_min))
    if price_max:
        sql += " AND COALESCE(promo_price, listed_price) <= %s"
        params.append(float(price_max))
    if in_stock_only:
        sql += " AND stock_quantity > 0 AND stock_status='in_stock'"
        
    sql += " ORDER BY COALESCE(promo_price, listed_price) DESC"
    cursor.execute(sql, params)
    products = cursor.fetchall()
    conn.close()
    return products

def get_phone_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM phone_products WHERE id=%s", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def get_phone_product_by_slug(slug):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM phone_products WHERE slug=%s", (slug,))
    product = cursor.fetchone()
    conn.close()
    return product

def get_phone_variants(product_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM phone_variants WHERE product_id=%s ORDER BY id ASC", (product_id,))
    variants = cursor.fetchall()
    conn.close()
    return variants

def add_phone_product(name, brand, model, description, listed_price, promo_price, stock_quantity, warehouse_location, screen_spec, chip_spec, ram_spec, storage_spec, camera_spec, battery_spec, os_spec, connectivity_spec, warranty_months=12, image_url=None):
    import re
    conn = get_connection()
    cursor = conn.cursor()
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
    stock_status = 'in_stock' if int(stock_quantity) > 5 else ('low_stock' if int(stock_quantity) > 0 else 'out_of_stock')
    
    cursor.execute("""
        INSERT INTO phone_products (
            name, brand, model, slug, description, listed_price, promo_price, stock_quantity, stock_status, warehouse_location,
            image_url, screen_spec, chip_spec, ram_spec, storage_spec, camera_spec, battery_spec, os_spec, connectivity_spec, warranty_months
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (name, brand, model, slug, description, listed_price, promo_price, stock_quantity, stock_status, warehouse_location,
          image_url, screen_spec, chip_spec, ram_spec, storage_spec, camera_spec, battery_spec, os_spec, connectivity_spec, warranty_months))
    prod_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return prod_id

def update_phone_product(product_id, name, brand, model, description, listed_price, promo_price, stock_quantity, warehouse_location, screen_spec, chip_spec, ram_spec, storage_spec, camera_spec, battery_spec, os_spec, connectivity_spec, warranty_months=12, image_url=None, user_id=None, user_name=None, change_reason=None):
    old_prod = get_phone_product_by_id(product_id)
    conn = get_connection()
    cursor = conn.cursor()
    stock_status = 'in_stock' if int(stock_quantity) > 5 else ('low_stock' if int(stock_quantity) > 0 else 'out_of_stock')
    
    cursor.execute("""
        UPDATE phone_products
        SET name=%s, brand=%s, model=%s, description=%s, listed_price=%s, promo_price=%s,
            stock_quantity=%s, stock_status=%s, warehouse_location=%s, image_url=%s,
            screen_spec=%s, chip_spec=%s, ram_spec=%s, storage_spec=%s, camera_spec=%s,
            battery_spec=%s, os_spec=%s, connectivity_spec=%s, warranty_months=%s
        WHERE id=%s
    """, (name, brand, model, description, listed_price, promo_price, stock_quantity, stock_status, warehouse_location,
          image_url, screen_spec, chip_spec, ram_spec, storage_spec, camera_spec, battery_spec, os_spec, connectivity_spec, warranty_months, product_id))
    
    # Ghi lại lịch sử thay đổi giá nếu có chênh lệch
    if old_prod and (float(old_prod["listed_price"]) != float(listed_price) or float(old_prod.get("promo_price") or 0) != float(promo_price or 0)):
        cursor.execute("""
            INSERT INTO product_price_history (product_id, old_listed_price, new_listed_price, old_promo_price, new_promo_price, changed_by, changed_by_name, reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (product_id, old_prod["listed_price"], listed_price, old_prod.get("promo_price"), promo_price, user_id, user_name, change_reason or "Cập nhật giá bán"))
        
    conn.commit()
    conn.close()

def update_phone_stock(product_id, new_quantity, warehouse=None):
    conn = get_connection()
    cursor = conn.cursor()
    stock_status = 'in_stock' if int(new_quantity) > 5 else ('low_stock' if int(new_quantity) > 0 else 'out_of_stock')
    if warehouse:
        cursor.execute("UPDATE phone_products SET stock_quantity=%s, stock_status=%s, warehouse_location=%s WHERE id=%s", (new_quantity, stock_status, warehouse, product_id))
    else:
        cursor.execute("UPDATE phone_products SET stock_quantity=%s, stock_status=%s WHERE id=%s", (new_quantity, stock_status, product_id))
    conn.commit()
    conn.close()

def get_price_history(product_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product_price_history WHERE product_id=%s ORDER BY id DESC", (product_id,))
    history = cursor.fetchall()
    conn.close()
    return history

def get_phone_comparison(product_ids):
    if not product_ids:
        return []
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    format_strings = ','.join(['%s'] * len(product_ids))
    cursor.execute(f"SELECT * FROM phone_products WHERE id IN ({format_strings})", tuple(product_ids))
    prods = cursor.fetchall()
    conn.close()
    return prods

# =====================================================================
# MODULE: CUSTOMER CONSULTATION PREFERENCES & RECOMMENDATIONS
# =====================================================================
def get_customer_preferences(customer_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customer_preferences WHERE customer_id=%s", (customer_id,))
    pref = cursor.fetchone()
    conn.close()
    return pref

def save_customer_preferences(customer_id, budget_min, budget_max, primary_usage, preferred_brands, desired_screen_size, key_criteria, interested_products, agent_notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customer_preferences (customer_id, budget_min, budget_max, primary_usage, preferred_brands, desired_screen_size, key_criteria, interested_products, agent_notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            budget_min=VALUES(budget_min),
            budget_max=VALUES(budget_max),
            primary_usage=VALUES(primary_usage),
            preferred_brands=VALUES(preferred_brands),
            desired_screen_size=VALUES(desired_screen_size),
            key_criteria=VALUES(key_criteria),
            interested_products=VALUES(interested_products),
            agent_notes=VALUES(agent_notes)
    """, (customer_id, budget_min, budget_max, primary_usage, preferred_brands, desired_screen_size, key_criteria, interested_products, agent_notes))
    conn.commit()
    conn.close()

def recommend_phones(budget_min=None, budget_max=None, usage=None, preferred_brand=None, screen_size=None):
    """
    Thuật toán tư vấn đề xuất điện thoại dựa trên ngân sách, nhu cầu và tồn kho thực tế
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM phone_products WHERE is_active=1 AND stock_quantity > 0"
    params = []

    if budget_min:
        sql += " AND COALESCE(promo_price, listed_price) >= %s"
        params.append(float(budget_min))
    if budget_max:
        sql += " AND COALESCE(promo_price, listed_price) <= %s"
        params.append(float(budget_max))
    if preferred_brand and preferred_brand != 'all':
        brands = [b.strip() for b in preferred_brand.split(',') if b.strip()]
        if brands:
            clauses = ["brand LIKE %s" for _ in brands]
            sql += f" AND ({' OR '.join(clauses)})"
            params.extend([f"%{b}%" for b in brands])

    sql += " ORDER BY stock_quantity DESC, COALESCE(promo_price, listed_price) DESC LIMIT 6"
    cursor.execute(sql, params)
    recs = cursor.fetchall()
    conn.close()
    return recs

# =====================================================================
# MODULE: QUOTATIONS (BÁO GIÁ ĐIỆN THOẠI)
# =====================================================================
def create_quotation(customer_id, customer_name, customer_phone, agent_id, agent_name, items, discount_amount=0, promotion_code=None, notes=None, expiry_days=7):
    import json
    import datetime
    import random
    conn = get_connection()
    cursor = conn.cursor()
    
    quote_code = f"BG-{datetime.date.today().strftime('%Y%m')}-{random.randint(1000, 9999)}"
    expiry_date = datetime.date.today() + datetime.timedelta(days=expiry_days)
    
    total_listed = sum(item.get("listed_price", 0) * item.get("qty", 1) for item in items)
    subtotal = sum(item.get("promo_price", item.get("listed_price", 0)) * item.get("qty", 1) for item in items)
    final_amount = max(0, subtotal - float(discount_amount or 0))
    
    cursor.execute("""
        INSERT INTO quotations (quote_code, customer_id, customer_name, customer_phone, agent_id, agent_name, total_listed_amount, discount_amount, final_amount, status, items_json, promotion_code, notes, expiry_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'sent', %s, %s, %s, %s)
    """, (quote_code, customer_id, customer_name, customer_phone, agent_id, agent_name, total_listed, discount_amount, final_amount, json.dumps(items, ensure_ascii=False), promotion_code, notes, expiry_date))
    quote_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return quote_id, quote_code

def get_quotations(customer_id=None, agent_id=None, status=None):
    import json
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM quotations WHERE 1=1"
    params = []
    if customer_id:
        sql += " AND customer_id=%s"
        params.append(customer_id)
    if agent_id:
        sql += " AND agent_id=%s"
        params.append(agent_id)
    if status and status != 'all':
        sql += " AND status=%s"
        params.append(status)
    sql += " ORDER BY id DESC LIMIT 50"
    cursor.execute(sql, params)
    quotes = cursor.fetchall()
    for q in quotes:
        try:
            q["items"] = json.loads(q["items_json"]) if q.get("items_json") else []
        except Exception:
            q["items"] = []
    conn.close()
    return quotes

def get_quotation_by_id(quote_id):
    import json
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM quotations WHERE id=%s", (quote_id,))
    quote = cursor.fetchone()
    if quote:
        try:
            quote["items"] = json.loads(quote["items_json"]) if quote.get("items_json") else []
        except Exception:
            quote["items"] = []
    conn.close()
    return quote

def update_quotation_status(quote_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE quotations SET status=%s WHERE id=%s", (new_status, quote_id))
    conn.commit()
    conn.close()

# =====================================================================
# MODULE: SALES ORDERS (ĐƠN HÀNG BÁN HÀNG TRỰC TIẾP)
# =====================================================================
def create_sales_order(customer_id, customer_name, customer_phone, agent_id, items, discount_amount=0, shipping_address=None, payment_method="cod", quote_id=None):
    import json
    import datetime
    import random
    conn = get_connection()
    cursor = conn.cursor()
    
    order_code = f"SO-{datetime.date.today().strftime('%Y%m')}-{random.randint(1000, 9999)}"
    total_amount = sum(item.get("unit_price", 0) * item.get("qty", 1) for item in items)
    final_amount = max(0, total_amount - float(discount_amount or 0))
    shipping_code = f"GHN{random.randint(10000000, 99999999)}"
    
    cursor.execute("""
        INSERT INTO sales_orders (order_code, quote_id, customer_id, customer_name, customer_phone, agent_id, total_amount, discount_amount, final_amount, status, shipping_address, receiver_name, receiver_phone, shipping_code, shipping_carrier, payment_method, items_json)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'new', %s, %s, %s, %s, 'GHN', %s, %s)
    """, (order_code, quote_id, customer_id, customer_name, customer_phone, agent_id, total_amount, discount_amount, final_amount, shipping_address, customer_name, customer_phone, shipping_code, payment_method, json.dumps(items, ensure_ascii=False)))
    order_id = cursor.lastrowid
    
    # Cập nhật số lượng tồn kho sản phẩm
    for item in items:
        pid = item.get("product_id")
        qty = item.get("qty", 1)
        if pid:
            cursor.execute("UPDATE phone_products SET stock_quantity = GREATEST(0, stock_quantity - %s) WHERE id=%s", (qty, pid))
            
    # Ghi nhận vào bảng order_status_history
    cursor.execute("""
        INSERT INTO order_status_history (order_id, old_status, new_status, changed_by, notes)
        VALUES (%s, NULL, 'new', %s, 'Đơn hàng mới tạo')
    """, (order_id, agent_id))
    
    # Đồng bộ vào bảng orders dùng chung
    items_summary = ", ".join([f"{item.get('name')} (x{item.get('qty')})" for item in items])
    cursor.execute("""
        INSERT INTO orders (order_code, source, customer_name, customer_phone, total_amount, status, shipping_code, shipping_carrier, shipping_status, items_summary)
        VALUES (%s, 'crm_store', %s, %s, %s, 'new', %s, 'GHN', 'Chờ bàn giao vận chuyển', %s)
        ON DUPLICATE KEY UPDATE total_amount=VALUES(total_amount), items_summary=VALUES(items_summary)
    """, (order_code, customer_name, customer_phone, final_amount, shipping_code, items_summary))

    conn.commit()
    conn.close()
    return order_id, order_code

def get_sales_orders(customer_id=None, status=None, limit=100):
    import json
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT so.*, u.full_name as agent_name FROM sales_orders so LEFT JOIN users u ON so.agent_id = u.id WHERE 1=1"
    params = []
    if customer_id:
        sql += " AND so.customer_id=%s"
        params.append(customer_id)
    if status and status != 'all':
        sql += " AND so.status=%s"
        params.append(status)
    sql += " ORDER BY so.id DESC LIMIT %s"
    params.append(limit)
    cursor.execute(sql, params)
    orders = cursor.fetchall()
    for o in orders:
        try:
            o["items"] = json.loads(o["items_json"]) if o.get("items_json") else []
        except Exception:
            o["items"] = []
    conn.close()
    return orders

def get_sales_order_by_id(order_id):
    import json
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT so.*, u.full_name as agent_name FROM sales_orders so LEFT JOIN users u ON so.agent_id = u.id WHERE so.id=%s", (order_id,))
    order = cursor.fetchone()
    if order:
        try:
            order["items"] = json.loads(order["items_json"]) if order.get("items_json") else []
        except Exception:
            order["items"] = []
    conn.close()
    return order

def update_sales_order_status(order_id, new_status, user_id, user_name, notes=None):
    old_ord = get_sales_order_by_id(order_id)
    old_status = old_ord["status"] if old_ord else "new"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sales_orders SET status=%s WHERE id=%s", (new_status, order_id))
    
    # Ghi log lịch sử trạng thái
    cursor.execute("""
        INSERT INTO order_status_history (order_id, old_status, new_status, changed_by, changed_by_name, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (order_id, old_status, new_status, user_id, user_name, notes or f"Chuyển trạng thái sang {new_status}"))
    
    # Đồng bộ trạng thái vào bảng orders dùng chung
    if old_ord and old_ord.get("order_code"):
        cursor.execute("UPDATE orders SET status=%s WHERE order_code=%s", (new_status, old_ord["order_code"]))
        
    conn.commit()
    conn.close()

def get_order_status_history(order_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM order_status_history WHERE order_id=%s ORDER BY id ASC", (order_id,))
    history = cursor.fetchall()
    conn.close()
    return history

# =====================================================================
# MODULE: WARRANTIES & POST-SALE REMINDERS
# =====================================================================
def create_warranty(order_id, customer_id, customer_name, customer_phone, product_id, product_name, imei_serial, warranty_package="Bảo hành chính hãng 12 tháng", months=12):
    import datetime
    import random
    conn = get_connection()
    cursor = conn.cursor()
    code = f"BH-{datetime.date.today().strftime('%Y%m')}-{random.randint(1000, 9999)}"
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=months * 30)
    
    cursor.execute("""
        INSERT INTO warranties (warranty_code, order_id, customer_id, customer_name, customer_phone, product_id, product_name, imei_serial, warranty_package, start_date, end_date, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
    """, (code, order_id, customer_id, customer_name, customer_phone, product_id, product_name, imei_serial, warranty_package, start_date, end_date))
    warr_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return warr_id, code

def get_warranties(customer_id=None, keyword=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM warranties WHERE 1=1"
    params = []
    if customer_id:
        sql += " AND customer_id=%s"
        params.append(customer_id)
    if keyword:
        kw = f"%{keyword}%"
        sql += " AND (warranty_code LIKE %s OR imei_serial LIKE %s OR product_name LIKE %s OR customer_phone LIKE %s)"
        params.extend([kw, kw, kw, kw])
    sql += " ORDER BY id DESC LIMIT 50"
    cursor.execute(sql, params)
    warranties = cursor.fetchall()
    conn.close()
    return warranties

def get_warranty_by_id(warranty_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM warranties WHERE id=%s", (warranty_id,))
    warr = cursor.fetchone()
    conn.close()
    return warr

def get_followup_reminders(agent_id=None, status='pending'):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT fr.*, c.full_name as customer_name, c.phone as customer_phone
        FROM followup_reminders fr
        JOIN customers c ON fr.customer_id = c.id
        WHERE 1=1
    """
    params = []
    if agent_id:
        sql += " AND fr.agent_id=%s"
        params.append(agent_id)
    if status and status != 'all':
        sql += " AND fr.status=%s"
        params.append(status)
    sql += " ORDER BY fr.due_date ASC LIMIT 50"
    cursor.execute(sql, params)
    reminders = cursor.fetchall()
    conn.close()
    return reminders

def complete_followup_reminder(reminder_id):
    import datetime
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE followup_reminders SET status='completed', completed_at=%s WHERE id=%s", (datetime.datetime.now(), reminder_id))
    conn.commit()
    conn.close()

# =====================================================================
# MODULE: PROMOTIONS
# =====================================================================
def get_promotions(active_only=True):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM promotions"
    if active_only:
        sql += " WHERE is_active=1 AND (end_date IS NULL OR end_date >= CURDATE())"
    sql += " ORDER BY id DESC"
    cursor.execute(sql)
    promos = cursor.fetchall()
    conn.close()
    return promos

def get_promotion_by_code(code):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM promotions WHERE promo_code=%s AND is_active=1", (code,))
    promo = cursor.fetchone()
    conn.close()
    return promo

# =====================================================================
# MODULE: SALES ANALYTICS DASHBOARD STATS
# =====================================================================
def get_sales_analytics():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Tổng doanh số bán trực tiếp
    cursor.execute("SELECT COALESCE(SUM(final_amount), 0) as total_sales, COUNT(*) as order_count FROM sales_orders WHERE status != 'cancelled'")
    sales_data = cursor.fetchone()
    
    # 2. Sản phẩm bán chạy (Top Products)
    cursor.execute("SELECT id, name, brand, listed_price, promo_price, stock_quantity, stock_status FROM phone_products WHERE is_active=1 ORDER BY stock_quantity ASC LIMIT 5")
    top_products = cursor.fetchall()
    
    # 3. Phễu chuyển đổi Kanban (Conversion Rate)
    cursor.execute("SELECT stage, COUNT(*) as count FROM sales_opportunities GROUP BY stage")
    opp_stages = {r["stage"]: r["count"] for r in cursor.fetchall()}
    total_opps = sum(opp_stages.values()) or 1
    won_opps = opp_stages.get("won", 0)
    conversion_rate = round((won_opps / total_opps) * 100, 1)
    
    # 4. Số lượng báo giá đang mở
    cursor.execute("SELECT COUNT(*) as active_quotes FROM quotations WHERE status='sent'")
    active_quotes = cursor.fetchone()["active_quotes"]
    
    conn.close()
    return {
        "total_sales": float(sales_data["total_sales"]),
        "order_count": sales_data["order_count"],
        "top_products": top_products,
        "opp_stages": opp_stages,
        "conversion_rate": conversion_rate,
        "active_quotes": active_quotes
    }