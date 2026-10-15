import sys
import os

# Đảm bảo mã hóa UTF-8 cho console Windows tránh UnicodeEncodeError khi print tiếng Việt
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")

from flask import Flask, render_template, request, redirect, jsonify, session, url_for, flash, Response
from dotenv import load_dotenv

load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))
load_dotenv()

# Database imports
from database.db import (
    get_connection, get_faqs, get_faq, add_faq, update_faq, delete_faq, search_faqs,
    get_user_by_username, get_user_by_email, get_user_by_id, create_user, get_all_agents, get_all_users, update_user_role_status, update_user_profile,
    get_or_create_customer, get_customer_by_id, get_customer_by_phone, get_customer_by_user_id, search_customers, get_all_customers, update_customer_notes, update_customer_full,
    create_ticket, get_ticket_by_id, get_ticket_by_code, get_tickets, update_ticket_status, assign_ticket, add_ticket_message, get_ticket_messages, delete_ticket,
    create_ticket_survey, get_ticket_survey, get_customer_surveys, get_all_surveys,
    get_omnichannel_conversations, get_conversation_messages, save_omnichannel_message,
    get_orders_by_phone, get_all_orders,
    get_work_shifts, create_work_shift, checkin_shift,
    get_sales_opportunities, create_sales_opportunity, update_opportunity_stage, delete_opportunity,
    get_auto_replies, save_auto_reply,
    create_call_log, get_call_logs,
    log_audit, get_audit_logs,
    get_dashboard_stats,
    get_phone_products, get_phone_product_by_id, get_phone_product_by_slug, get_phone_variants,
    add_phone_product, update_phone_product, update_phone_stock, get_price_history, get_phone_comparison,
    get_customer_preferences, save_customer_preferences, recommend_phones,
    create_quotation, get_quotations, get_quotation_by_id, update_quotation_status,
    create_sales_order, get_sales_orders, get_sales_order_by_id, update_sales_order_status, get_order_status_history,
    create_warranty, get_warranties, get_warranty_by_id, get_followup_reminders, complete_followup_reminder,
    get_promotions, get_promotion_by_code, get_sales_analytics,
    get_all_vouchers, get_customer_vouchers, grant_customer_voucher,
    get_all_notifications, create_notification,
    get_agent_performance_report
)
from database.init_db import init_database

# Service imports
from services.rag_service import ask_rag
from services.ai_service import ai_service
from services.sales_service import sales_service
from services.auth_service import (
    hash_password, verify_password, login_user, logout_user, login_required, role_required,
    get_google_auth_url, verify_google_oauth_code
)
from services.omnichannel_service import (
    process_inbound_message, send_outbound_reply, generate_webchat_token, verify_webchat_token,
    parse_sendgrid_inbound, poll_imap_inbox
)
from services.order_service import lookup_and_sync_customer_orders
from services.logistics_service import refresh_tracking_status, handle_ghn_webhook, handle_ghtk_webhook
from services.telephony_service import (
    generate_twilio_voice_token, generate_outbound_twiml, generate_inbound_twiml, handle_call_status_callback
)
from services.automation_service import trigger_ticket_closure_survey

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)
app.secret_key = os.getenv("SECRET_KEY", "super-crm-flask-secret-2026")

# Tự động khởi tạo DB schema nếu chưa có
try:
    init_database()
except Exception as e:
    print("[APP INIT] Database check:", e)

# =====================================================================
# 1. TRANG CHỦ / KNOWLEDGE BASE (GIỮ NGUYÊN 100% TƯƠNG THÍCH CỦA DỰ ÁN)
# =====================================================================
@app.route("/")
@app.route("/faqs")
def index():
    keyword = request.args.get("keyword", "").strip()
    if keyword:
        faqs = search_faqs(keyword=keyword)
    else:
        faqs = get_faqs()
    return render_template("faqs.html", faqs=faqs, keyword=keyword)

@app.route("/add", methods=["GET", "POST"])
@app.route("/add-faq", methods=["GET", "POST"])
@login_required
@role_required("agent", "admin")
def add():
    if request.method == "POST":
        add_faq(
            request.form["issue_name"],
            request.form["category"],
            request.form["brand"],
            request.form["symptom"],
            request.form["solution"]
        )
        log_audit(session.get("user_id"), session.get("username"), "CREATE_FAQ", "FAQ", None, request.form["issue_name"])
        flash("Đã thêm dữ liệu hỗ trợ mới thành công!", "success")
        return redirect("/faqs")
    return render_template("add_faq.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@app.route("/edit-faq/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("agent", "admin")
def edit(id):
    if request.method == "POST":
        update_faq(
            id,
            request.form["issue_name"],
            request.form["category"],
            request.form["brand"],
            request.form["symptom"],
            request.form["solution"]
        )
        log_audit(session.get("user_id"), session.get("username"), "UPDATE_FAQ", "FAQ", id, request.form["issue_name"])
        flash(f"Đã cập nhật dữ liệu hỗ trợ #{id} thành công!", "success")
        return redirect("/faqs")
    faq = get_faq(id)
    return render_template("edit_faq.html", faq=faq)

@app.route("/delete/<int:id>")
@app.route("/delete-faq/<int:id>")
@login_required
@role_required("admin")
def delete(id):
    delete_faq(id)
    log_audit(session.get("user_id"), session.get("username"), "DELETE_FAQ", "FAQ", id)
    flash(f"Đã xóa dữ liệu hỗ trợ #{id}!", "info")
    return redirect("/faqs")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    try:
        data = request.get_json()
        question = data.get("question", "").strip()
        if not question:
            return jsonify({"success": False, "message": "Vui lòng nhập câu hỏi."}), 400
            
        # 1. Quản lý trạng thái phiên chat (Human Handoff)
        chat_mode = session.get("chat_mode", "bot")
        
        # NẾU ĐÃ CHUYỂN CHO NHÂN VIÊN: Không gọi AI, lưu tin nhắn vào Inbox
        if chat_mode == "human":
            ticket_id = session.get("chat_ticket_id")
            if ticket_id:
                from database.db import add_ticket_message
                user_id = session.get("user_id", 0)
                user_name = session.get("full_name", "Khách hàng trực tuyến")
                add_ticket_message(ticket_id, "customer", user_id, user_name, question)
            return jsonify({
                "success": True,
                "answer": "" # Không hiện tin nhắn tự động nữa vì đã vào chế độ chat với người
            })
            
        # NẾU VẪN LÀ BOT XỬ LÝ: Lọc rác
        import re
        if len(question) < 2 or not re.search(r'[a-zA-Z0-9a-zA-ZÀ-ỹ]', question):
            return jsonify({
                "success": True,
                "answer": "Dạ, em chưa nhận được thông tin rõ ràng. Anh/chị có thể mô tả chi tiết hơn vấn đề mình đang gặp phải không ạ?"
            })
            
        # 2. Điểm kích hoạt chuyển giao (Handoff Trigger)
        handoff_keywords = ['gặp nhân viên', 'tư vấn viên', 'người thật', 'tổng đài', 'hỗ trợ trực tiếp']
        q_lower = question.lower()
        if any(kw in q_lower for kw in handoff_keywords):
            session["chat_mode"] = "human"
            from database.db import create_ticket
            
            user_id = session.get("user_id", 0)
            user_name = session.get("full_name", "Khách hàng trực tuyến")
            phone = session.get("phone", "")
            email = session.get("email", "")
            
            # Lấy customer_id thực tế từ bảng customers (không dùng user_id của bảng users)
            actual_customer_id = session.get("customer_id")
            if not actual_customer_id and user_id:
                cust_for_ticket = get_or_create_customer(full_name=user_name, phone=phone, email=email, user_id=user_id)
                actual_customer_id = cust_for_ticket["id"] if cust_for_ticket else user_id
            
            # Tạo thẻ Ticket mới ra màn hình Kanban
            ticket_id, ticket_code = create_ticket(
                customer_id=actual_customer_id or user_id,
                customer_name=user_name,
                customer_phone=phone,
                customer_email=email,
                channel="web",
                subject="Khách hàng yêu cầu hỗ trợ trực tiếp",
                priority="high",
                first_message=question
            )
            session["chat_ticket_id"] = ticket_id
            
            return jsonify({
                "success": True,
                "answer": "Dạ, em đã ghi nhận yêu cầu. Hệ thống đang kết nối anh/chị với nhân viên CSKH. Anh/chị vui lòng giữ máy trong giây lát nhé!"
            })
            
        # 3. Tiếp tục chạy logic RAG nếu không chuyển giao
        result = ask_rag(question)
        return jsonify({
            "success": True,
            "answer": result["answer"]
        })
    except Exception as e:
        print("LỖI CHATBOT:", e)
        return jsonify({"success": False, "message": "Không thể xử lý câu hỏi.", "error": str(e)}), 500

@app.route("/api/chat/poll", methods=["GET"])
def api_chat_poll():
    chat_mode = session.get("chat_mode", "bot")
    ticket_id = session.get("chat_ticket_id")
    last_msg_id = request.args.get("last_msg_id", type=int, default=0)
    
    if chat_mode != "human" or not ticket_id:
        return jsonify({"messages": []})
        
    from database.db import get_ticket_messages
    messages = get_ticket_messages(ticket_id)
    new_messages = []
    
    for msg in messages:
        if msg["id"] > last_msg_id and msg["sender_type"] == "agent":
            new_messages.append({
                "id": msg["id"],
                "text": msg["message"],
                "sender_name": msg["sender_name"]
            })
            
    return jsonify({"messages": new_messages})

# =====================================================================
# 2. XÁC THỰC VÀ TÀI KHOẢN (AUTH & RBAC)
# =====================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ident = request.form.get("username_or_email", "").strip()
        password = request.form.get("password", "")
        next_url = request.form.get("next") or request.args.get("next")
        
        user = get_user_by_username(ident) or get_user_by_email(ident)
        if user and verify_password(user["password_hash"], password):
            if not user.get("is_active", 1):
                flash("Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên.", "danger")
                return render_template("login.html")
                
            login_user(user)
            flash(f"Chào mừng trở lại, {user['full_name']}!", "success")
            
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            if user["role"] in ["agent", "admin"]:
                return redirect(url_for("dashboard"))
            return redirect(url_for("portal"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không chính xác.", "danger")
            
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "customer")
        
        # Chỉ admin mới có quyền tạo admin khác qua giao diện quản trị
        if role not in ["customer", "agent"]:
            role = "customer"
            
        if get_user_by_username(username):
            flash("Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác.", "warning")
            return render_template("register.html")
        if get_user_by_email(email):
            flash("Email đã được đăng ký. Vui lòng đăng nhập.", "warning")
            return render_template("register.html")
            
        pass_hash = hash_password(password)
        user_id = create_user(username, email, pass_hash, full_name, phone, role)
        
        # Tạo liên kết Customer 360
        get_or_create_customer(full_name=full_name, phone=phone, email=email, user_id=user_id)
        
        user = get_user_by_id(user_id)
        login_user(user)
        flash("Đăng ký tài khoản thành công!", "success")
        
        if role in ["agent", "admin"]:
            return redirect(url_for("dashboard"))
        return redirect(url_for("portal"))
        
    return render_template("register.html")

@app.route("/logout")
def logout():
    logout_user()
    flash("Đã đăng xuất an toàn.", "info")
    return redirect(url_for("login"))

# =====================================================================
# HỒ SƠ CÁ NHÂN (USER / CUSTOMER PROFILE)
# =====================================================================
@app.route("/profile", methods=["GET", "POST"])
@login_required
def user_profile():
    user = get_user_by_id(session["user_id"])
    if not user:
        flash("Không tìm thấy thông tin tài khoản.", "danger")
        return redirect(url_for("login"))
        
    customer = get_customer_by_user_id(user["id"])
    if not customer:
        customer = get_or_create_customer(
            full_name=user.get("full_name") or user["username"],
            phone=user.get("phone"),
            email=user.get("email"),
            user_id=user["id"]
        )

    if request.method == "POST":
        new_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        zalo_id = request.form.get("zalo_id", "").strip()
        fb_id = request.form.get("fb_id", "").strip()
        member_rank = request.form.get("member_rank", customer.get("member_rank", "Đồng (Mới)"))
        notes = request.form.get("notes", customer.get("notes", "")).strip()

        if not new_name:
            flash("Họ và tên không được để trống.", "danger")
            return redirect(url_for("user_profile"))

        # 1. Cập nhật bảng users
        update_user_profile(user["id"], full_name=new_name, phone=phone, email=email)

        # 2. Cập nhật bảng customers
        if customer:
            update_customer_full(
                customer["id"],
                full_name=new_name,
                phone=phone,
                email=email,
                zalo_id=zalo_id,
                fb_id=fb_id,
                member_rank=member_rank,
                notes=notes
            )

        # 3. Cập nhật session ngay lập tức
        session["full_name"] = new_name

        log_audit(user["id"], user["username"], "UPDATE_PROFILE", "USER", user["id"], f"Đổi tên hồ sơ: {new_name}")
        flash("Đã cập nhật thông tin hồ sơ và đổi tên thành công!", "success")
        return redirect(url_for("user_profile"))

    # Lấy lại customer mới nhất để hiển thị
    customer = get_customer_by_id(customer["id"]) if customer else {}
    tickets = get_tickets(customer_id=customer["id"]) if customer else []
    warranties = get_warranties(customer_id=customer["id"]) if customer else []

    return render_template("profile.html", user=user, customer=customer, tickets=tickets, warranties=warranties)

# Google OpenID Connect (OIDC)
@app.route("/auth/google/login")
def google_login():
    redirect_uri = url_for("google_callback", _external=True)
    auth_url = get_google_auth_url(redirect_uri)
    if not auth_url:
        flash("Google OIDC chưa được cấu hình (thiếu GOOGLE_CLIENT_ID trong .env).", "warning")
        return redirect(url_for("login"))
    return redirect(auth_url)

@app.route("/auth/google/callback")
def google_callback():
    code = request.args.get("code")
    if not code:
        flash("Đăng nhập Google thất bại hoặc bị hủy.", "danger")
        return redirect(url_for("login"))
        
    redirect_uri = url_for("google_callback", _external=True)
    result = verify_google_oauth_code(code, redirect_uri)
    if result.get("success"):
        user = result["user"]
        login_user(user)
        flash(f"Đăng nhập Google thành công! Chào mừng {user['full_name']}.", "success")
        if user["role"] in ["agent", "admin"]:
            return redirect(url_for("dashboard"))
        return redirect(url_for("portal"))
    else:
        flash(result.get("message", "Xác thực Google không thành công."), "danger")
        return redirect(url_for("login"))

# =====================================================================
# 3. DASHBOARD & VẬN HÀNH (AGENT & ADMIN)
# =====================================================================

@app.route("/api/agent/tickets/count")
@login_required
@role_required("agent", "admin")
def api_agent_tickets_count():
    from database.db import get_dashboard_stats
    stats = get_dashboard_stats()
    open_count = stats.get('ticket_status', {}).get('open', 0)
    return jsonify({"open_tickets": open_count})

@app.route("/dashboard")
@login_required
@role_required("agent", "admin")
def dashboard():
    stats = get_dashboard_stats()
    sales_analytics = get_sales_analytics()
    import datetime
    today = datetime.date.today()
    shifts = get_work_shifts(shift_date=today)
    return render_template("dashboard.html", stats=stats, sales_analytics=sales_analytics, shifts=shifts)

# =====================================================================
# 4. CỔNG HỖ TRỢ KHÁCH HÀNG (CUSTOMER PORTAL)
# =====================================================================
@app.route("/portal")
@login_required
def portal():
    user = get_user_by_id(session["user_id"])
    customer = get_or_create_customer(full_name=user["full_name"], phone=user["phone"], email=user["email"], user_id=user["id"])
    tickets = get_tickets(customer_id=customer["id"])
    orders = get_orders_by_phone(user["phone"]) if user.get("phone") else []
    return render_template("portal.html", tickets=tickets, orders=orders, customer=customer)

@app.route("/portal/new-ticket", methods=["GET", "POST"])
@login_required
def portal_new_ticket():
    user = get_user_by_id(session["user_id"])
    customer = get_or_create_customer(full_name=user["full_name"], phone=user["phone"], email=user["email"], user_id=user["id"])
    
    if request.method == "POST":
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()
        phone = request.form.get("customer_phone", "").strip() or user.get("phone")
        priority = request.form.get("priority", "medium")
        
        ticket_id, ticket_code = create_ticket(
            customer_id=customer["id"],
            customer_name=customer["full_name"],
            customer_phone=phone,
            customer_email=customer["email"],
            channel="web",
            subject=subject,
            priority=priority,
            first_message=message
        )
        log_audit(user["id"], user["username"], "CREATE_TICKET", "TICKET", ticket_id, f"Khách hàng tạo ticket {ticket_code}")
        flash(f"Phiếu hỗ trợ [{ticket_code}] đã được gửi tới chuyên viên CSKH!", "success")
        return redirect(f"/portal/ticket/{ticket_id}")
        
    return render_template("portal_new_ticket.html", user=user, customer=customer)

@app.route("/portal/ticket/<int:id>", methods=["GET", "POST"])
@login_required
def portal_ticket_chat(id):
    ticket = get_ticket_by_id(id)
    if not ticket:
        flash("Phiếu hỗ trợ không tồn tại.", "danger")
        return redirect(url_for("portal"))
        
    user = get_user_by_id(session["user_id"])
    # Quyền: Chỉ khách hàng sở hữu hoặc Agent/Admin
    if user["role"] == "customer":
        cust = get_customer_by_user_id(user["id"])
        # Kiểm tra theo customer_id hoặc email
        customer_match = (
            (cust and ticket["customer_id"] == cust["id"]) or
            (ticket.get("customer_email") and ticket["customer_email"] == user.get("email"))
        )
        if not customer_match:
            flash("Bạn không có quyền truy cập ticket này.", "danger")
            return redirect(url_for("portal"))

    if request.method == "POST":
        message = request.form.get("message", "").strip()
        if message:
            add_ticket_message(
                ticket_id=id,
                sender_type="customer",
                sender_id=user["id"],
                sender_name=user["full_name"],
                message=message,
                channel=ticket.get("channel", "web")
            )
            flash("Đã gửi phản hồi!", "success")
            return redirect(f"/portal/ticket/{id}")

    messages = get_ticket_messages(id)
    survey = get_ticket_survey(id)
    return render_template("portal_ticket_chat.html",
                           ticket=ticket, messages=messages, customer=None, orders=[], agents=[], smart_replies=[], survey=survey)




@app.route("/portal/survey/<int:ticket_id>", methods=["GET", "POST"])
def portal_survey(ticket_id):
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        flash("Ticket không tồn tại.", "danger")
        return redirect("/")
        
    if request.method == "POST":
        rating_csat = int(request.form.get("rating_csat", 5))
        score_nps = int(request.form.get("score_nps", 10))
        feedback = request.form.get("feedback", "").strip()
        
        create_ticket_survey(ticket_id, ticket.get("customer_id"), rating_csat, score_nps, feedback)
        log_audit(None, ticket.get("customer_name"), "SUBMIT_SURVEY", "TICKET", ticket_id, f"CSAT: {rating_csat}, NPS: {score_nps}")
        flash("Chân thành cảm ơn quý khách đã gửi đánh giá dịch vụ!", "success")
        if session.get("user_id"):
            return redirect(url_for("portal"))
        return redirect("/")
        
    return render_template("portal_survey.html", ticket=ticket)

# =====================================================================
# 5. QUẢN LÝ TICKETS (AGENT & ADMIN)
# =====================================================================
@app.route("/tickets")
@login_required
@role_required("agent", "admin")
def tickets_list():
    status = request.args.get("status", "all")
    channel = request.args.get("channel", "all")
    keyword = request.args.get("keyword", "").strip()
    
    tickets = get_tickets(status=status, channel=channel, keyword=keyword)
    return render_template("tickets.html", tickets=tickets, current_status=status, current_channel=channel, keyword=keyword)

@app.route("/tickets/create", methods=["GET", "POST"])
@login_required
@role_required("agent", "admin")
def ticket_create_agent():
    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        customer_phone = request.form.get("customer_phone", "").strip()
        channel = request.form.get("channel", "web")
        priority = request.form.get("priority", "medium")
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()
        assigned_agent_id = request.form.get("assigned_agent_id") or session.get("user_id")
        
        customer = get_or_create_customer(full_name=customer_name, phone=customer_phone)
        ticket_id, ticket_code = create_ticket(
            customer_id=customer["id"],
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer.get("email"),
            channel=channel,
            subject=subject,
            priority=priority,
            first_message=message
        )
        if assigned_agent_id:
            assign_ticket(ticket_id, assigned_agent_id)
            
        log_audit(session.get("user_id"), session.get("username"), "CREATE_TICKET", "TICKET", ticket_id, f"Tiếp nhận ticket {ticket_code}")
        flash(f"Đã mở phiếu hỗ trợ [{ticket_code}] thành công!", "success")
        return redirect(f"/tickets/{ticket_id}")
        
    agents = get_all_agents()
    cust_id = request.args.get("customer_id")
    selected_customer = get_customer_by_id(cust_id) if cust_id else None
    return render_template("ticket_create.html", agents=agents, selected_customer=selected_customer)

@app.route("/tickets/<int:id>")
@login_required
def ticket_detail(id):
    if session.get("role") == "customer":
        return redirect(f"/portal/ticket/{id}")
    if session.get("role") not in ["agent", "admin"]:
        flash("Bạn không có quyền truy cập khu vực này.", "danger")
        return redirect(url_for("portal"))
    ticket = get_ticket_by_id(id)
    if not ticket:
        flash("Phiếu hỗ trợ không tồn tại.", "danger")
        return redirect(url_for("tickets_list"))
        
    messages = get_ticket_messages(id)
    customer = get_customer_by_id(ticket["customer_id"]) if ticket.get("customer_id") else None
    orders = get_orders_by_phone(ticket["customer_phone"]) if ticket.get("customer_phone") else []
    agents = get_all_agents()
    survey = get_ticket_survey(id)
    warranties = get_warranties(customer_id=ticket.get("customer_id")) if ticket.get("customer_id") else []
    past_tickets = get_tickets(customer_id=ticket.get("customer_id"), limit=10) if ticket.get("customer_id") else []
    primary_device = warranties[0] if warranties else None
    
    # AI Smart Reply Suggestion
    last_customer_msg = ""
    for m in reversed(messages):
        if m["sender_type"] == "customer":
            last_customer_msg = m["message"]
            break
            
    related_faqs = search_faqs(keyword=ticket["subject"])
    smart_replies = ai_service.suggest_smart_replies(last_customer_msg or ticket["subject"], related_faqs)
    
    # 6-Stage Workflow: AI tự đề xuất bước tiếp theo
    ai_next_action = ai_service.suggest_next_ticket_action(
        current_status=ticket.get("status", "open"),
        messages=[{"content": m.get("message", "")} for m in messages],
        subject=ticket.get("subject", ""),
        description=ticket.get("description", "")
    )

    # Chấm điểm AI: Sentiment, Mức độ khẩn cấp, Rủi ro khiếu nại (%), Khuyến nghị, Voucher
    ai_risk_score = ai_service.assess_ticket_risk_and_scoring(
        ticket_data=ticket,
        messages=[{"content": m.get("message", "")} for m in messages]
    )

    return render_template("ticket_detail.html",
                           ticket=ticket, messages=messages, customer=customer,
                           orders=orders, agents=agents, survey=survey, smart_replies=smart_replies,
                           warranties=warranties, past_tickets=past_tickets, primary_device=primary_device,
                           ai_next_action=ai_next_action, ai_risk_score=ai_risk_score)

@app.route("/api/tickets/<int:id>/next-action")
@login_required
@role_required("agent", "admin")
def api_ticket_next_action(id):
    ticket = get_ticket_by_id(id)
    if not ticket:
        return jsonify({"success": False, "message": "Ticket không tồn tại."}), 404
    messages = get_ticket_messages(id)
    res = ai_service.suggest_next_ticket_action(
        current_status=ticket.get("status", "open"),
        messages=[{"content": m.get("message", "")} for m in messages],
        subject=ticket.get("subject", ""),
        description=ticket.get("description", "")
    )
    return jsonify({"success": True, "data": res})

@app.route("/api/tickets/<int:id>/risk-score")
@login_required
@role_required("agent", "admin")
def api_ticket_risk_score(id):
    ticket = get_ticket_by_id(id)
    if not ticket:
        return jsonify({"success": False, "message": "Ticket không tồn tại."}), 404
    messages = get_ticket_messages(id)
    res = ai_service.assess_ticket_risk_and_scoring(
        ticket_data=ticket,
        messages=[{"content": m.get("message", "")} for m in messages]
    )
    return jsonify({"success": True, "data": res})

@app.route("/tickets/<int:id>/status", methods=["POST"])
@login_required
@role_required("agent", "admin")
def ticket_update_status(id):
    new_status = request.form.get("status")
    if new_status:
        update_ticket_status(id, new_status)
        log_audit(session.get("user_id"), session.get("username"), "UPDATE_TICKET_STATUS", "TICKET", id, f"Trạng thái mới: {new_status}")
        
        # Tự động hóa: Nếu chuyển sang resolved hoặc closed -> Gửi khảo sát CSAT/NPS
        if new_status in ["resolved", "closed"]:
            trigger_ticket_closure_survey(id)
            flash(f"Đã cập nhật trạng thái ticket và tự động gửi khảo sát CSAT/NPS cho khách hàng!", "success")
        else:
            flash(f"Đã cập nhật trạng thái ticket sang '{new_status}' thành công!", "success")
            
    return redirect(f"/tickets/{id}")

@app.route("/tickets/<int:id>/assign", methods=["POST"])
@login_required
@role_required("agent", "admin")
def ticket_assign_agent(id):
    agent_id = request.form.get("agent_id")
    if agent_id:
        assign_ticket(id, int(agent_id))
        log_audit(session.get("user_id"), session.get("username"), "ASSIGN_TICKET", "TICKET", id, f"Phân công cho nhân viên #{agent_id}")
        flash("Đã phân công chuyên viên xử lý ticket!", "success")
    return redirect(f"/tickets/{id}")

@app.route("/tickets/<int:id>/message", methods=["POST"])
@login_required
@role_required("agent", "admin")
def ticket_post_message(id):
    ticket = get_ticket_by_id(id)
    if not ticket:
        flash("Ticket không tồn tại.", "danger")
        return redirect(url_for("tickets_list"))
        
    message = request.form.get("message", "").strip()
    if message:
        add_ticket_message(
            ticket_id=id,
            sender_type="agent",
            sender_id=session.get("user_id"),
            sender_name=session.get("full_name") or session.get("username"),
            message=message,
            channel=ticket.get("channel", "web")
        )
        # Gửi phản hồi ra kênh tương ứng nếu là Zalo/Email/FB
        if ticket.get("channel") in ["zalo", "email", "facebook"]:
            recipient = ticket.get("customer_phone") if ticket.get("channel") == "zalo" else ticket.get("customer_email")
            send_outbound_reply(
                channel=ticket.get("channel"),
                conversation_id=f"CONV-TICKET-{id}",
                recipient_id=recipient or "user",
                content=message,
                agent_id=session.get("user_id"),
                agent_name=session.get("full_name")
            )
            
        flash("Đã gửi tin nhắn phản hồi tới khách hàng!", "success")
    return redirect(f"/tickets/{id}")

# =====================================================================
# 6. CUSTOMER 360 (AGENT & ADMIN)
# =====================================================================
@app.route("/customers")
@login_required
@role_required("agent", "admin")
def customers_list():
    keyword = request.args.get("keyword", "").strip()
    if keyword:
        customers = search_customers(keyword)
    else:
        customers = get_all_customers()
    return render_template("customers.html", customers=customers, keyword=keyword)

@app.route("/customers/<int:id>")
@login_required
@role_required("agent", "admin")
def customer_360_detail(id):
    customer = get_customer_by_id(id)
    if not customer:
        flash("Hồ sơ khách hàng không tồn tại.", "danger")
        return redirect(url_for("customers_list"))
        
    tickets = get_tickets(customer_id=id)
    orders = get_orders_by_phone(customer["phone"]) if customer.get("phone") else []
    surveys = get_customer_surveys(id)
    preference = get_customer_preferences(id)
    warranties = get_warranties(customer_id=id)
    quotations = get_quotations(customer_id=id)
    sales_orders = get_sales_orders(customer_id=id)
    return render_template("customer_360.html",
                           customer=customer,
                           tickets=tickets,
                           orders=orders,
                           surveys=surveys,
                           preference=preference,
                           warranties=warranties,
                           quotations=quotations,
                           sales_orders=sales_orders)

@app.route("/api/customers/<int:id>/notes", methods=["POST"])
@app.route("/api/customers/<int:id>/update", methods=["POST"])
@login_required
@role_required("agent", "admin")
def customer_update_notes(id):
    customer = get_customer_by_id(id)
    if not customer:
        flash("Khách hàng không tồn tại.", "danger")
        return redirect(url_for("customers_list"))
        
    full_name = request.form.get("full_name", customer["full_name"]).strip() or customer["full_name"]
    phone = request.form.get("phone", customer.get("phone") or "").strip()
    email = request.form.get("email", customer.get("email") or "").strip()
    zalo_id = request.form.get("zalo_id", customer.get("zalo_id") or "").strip()
    fb_id = request.form.get("fb_id", customer.get("fb_id") or "").strip()
    member_rank = request.form.get("member_rank", customer.get("member_rank", "Đồng (Mới)"))
    notes = request.form.get("notes", customer.get("notes") or "")

    update_customer_full(id, full_name, phone=phone, email=email, zalo_id=zalo_id, fb_id=fb_id, member_rank=member_rank, notes=notes)
    
    if customer.get("user_id"):
        update_user_profile(customer["user_id"], full_name, phone=phone, email=email)
        if session.get("user_id") == customer["user_id"]:
            session["full_name"] = full_name

    log_audit(session.get("user_id"), session.get("username"), "UPDATE_CUSTOMER", "CUSTOMER", id, f"Cập nhật hồ sơ/đổi tên: {full_name}")
    flash("Đã cập nhật thông tin và đổi tên khách hàng thành công!", "success")
    return redirect(f"/customers/{id}")

@app.route("/api/customers/lookup-orders", methods=["POST"])
@login_required
@role_required("agent", "admin")
def api_lookup_orders():
    # Lấy phone từ JSON body hoặc form data
    if request.is_json:
        phone = (request.get_json() or {}).get("phone")
    else:
        phone = request.form.get("phone")
    
    if not phone:
        return jsonify({"success": False, "message": "Thiếu số điện thoại."}), 400
        
    orders = lookup_and_sync_customer_orders(phone)
    log_audit(session.get("user_id"), session.get("username"), "SYNC_ORDERS", "ORDER", phone, f"Đồng bộ {len(orders)} đơn hàng")
    if request.is_json:
        return jsonify({"success": True, "orders": orders})
    flash(f"Đã đồng bộ {len(orders)} đơn hàng từ KiotViet, Sapo, Lazada cho SĐT {phone}!", "success")
    return redirect(request.referrer or "/customers")

# =====================================================================
# 7. HỘP THƯ ĐA KÊNH HỢP NHẤT (OMNICHANNEL INBOX)
# =====================================================================
@app.route("/inbox")
@login_required
@role_required("agent", "admin")
def omnichannel_inbox():
    channel = request.args.get("channel", "all")
    conv_id = request.args.get("conv_id")
    
    conversations = get_omnichannel_conversations(channel=channel)
    active_conv = None
    messages = []
    
    if conv_id:
        messages = get_conversation_messages(conv_id)
        for c in conversations:
            if c["conversation_id"] == conv_id:
                active_conv = c
                break
    elif conversations:
        conv_id = conversations[0]["conversation_id"]
        active_conv = conversations[0]
        messages = get_conversation_messages(conv_id)
        
    # Liên kết thông tin khách hàng nếu tìm thấy theo sender_id hoặc phone
    linked_customer = None
    customer_pref = None
    recent_orders = []
    if active_conv:
        sender = active_conv.get("sender_name") or ""
        cust = get_customer_by_phone(sender)
        if not cust and sender:
            matched = search_customers(sender)
            if matched:
                cust = matched[0]
        if cust:
            linked_customer = cust
            customer_pref = get_customer_preferences(linked_customer["id"])
            recent_orders = get_sales_orders(customer_id=linked_customer["id"], limit=5)
            if not recent_orders and linked_customer.get("phone"):
                recent_orders = get_orders_by_phone(linked_customer["phone"])
                
    phone_catalog = get_phone_products(in_stock_only=False)
    return render_template("inbox.html",
                           conversations=conversations,
                           active_conv_id=conv_id,
                           active_conv=active_conv,
                           messages=messages,
                           current_channel=channel,
                           linked_customer=linked_customer,
                           customer_pref=customer_pref,
                           recent_orders=recent_orders,
                           phone_catalog=phone_catalog)

@app.route("/api/inbox/send-product-card", methods=["POST"])
@login_required
@role_required("agent", "admin")
def api_inbox_send_product_card():
    data = request.get_json() or {}
    conv_id = data.get("conversation_id")
    channel = data.get("channel", "webchat")
    product_id = data.get("product_id")
    
    if not conv_id or not product_id:
        return jsonify({"success": False, "message": "Thiếu thông tin hội thoại hoặc sản phẩm."}), 400
        
    card_msg = sales_service.send_product_card_to_chat(
        channel=channel,
        conversation_id=conv_id,
        product_id=product_id,
        agent_name=session.get("full_name") or session.get("username")
    )
    if not card_msg:
        return jsonify({"success": False, "message": "Không tìm thấy sản phẩm."}), 404
        
    log_audit(session.get("user_id"), session.get("username"), "SEND_PRODUCT_CARD", "INBOX", product_id, f"Gửi thẻ máy #{product_id} vào {conv_id}")
    return jsonify({"success": True, "card_message": card_msg})

@app.route("/api/inbox/reply", methods=["POST"])
@login_required
@role_required("agent", "admin")
def api_inbox_reply():
    data = request.get_json()
    conv_id = data.get("conversation_id")
    channel = data.get("channel", "webchat")
    content = data.get("content", "").strip()
    
    if not conv_id or not content:
        return jsonify({"success": False, "message": "Thiếu thông tin tin nhắn."}), 400
        
    recipient_id = conv_id.split("-")[-1] if "-" in conv_id else "user"
    res = send_outbound_reply(
        channel=channel,
        conversation_id=conv_id,
        recipient_id=recipient_id,
        content=content,
        agent_id=session.get("user_id"),
        agent_name=session.get("full_name") or session.get("username")
    )
    return jsonify(res)

# =====================================================================
# 8. WEBCHAT EMBED WIDGET (TOKEN SESSION & ALLOWED ORIGINS)
# =====================================================================
@app.route("/webchat/embed")
def webchat_embed_view():
    token = request.args.get("token")
    origin = request.headers.get("Origin") or request.headers.get("Referer") or ""
    
    if not token:
        # Tự động cấp token phiên cho khách ẩn danh hoặc đã đăng nhập
        user_name = session.get("full_name") or "Khách Livechat"
        user_phone = session.get("phone")
        token = generate_webchat_token(user_name, user_phone, origin)
        
    valid, payload = verify_webchat_token(token, origin)
    if not valid:
        return f"<h3>Lỗi truy cập Webchat: {payload}</h3>", 403
        
    conv_id = f"CONV-WEBCHAT-{payload.get('customer_name')}"
    return render_template("webchat_embed.html", conversation_id=conv_id, token=token)

@app.route("/api/webchat/token", methods=["POST"])
def api_webchat_token():
    origin = request.headers.get("Origin") or request.headers.get("Referer") or ""
    data = request.get_json() or {}
    name = data.get("name", "Khách Webchat")
    phone = data.get("phone")
    token = generate_webchat_token(name, phone, origin)
    return jsonify({"success": True, "token": token})

@app.route("/api/webchat/messages", methods=["POST"])
def api_webchat_post_message():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else request.args.get("token")
    origin = request.headers.get("Origin") or ""
    
    valid, payload = verify_webchat_token(token, origin)
    if not valid:
        return jsonify({"success": False, "message": payload}), 403
        
    data = request.get_json()
    message = data.get("message", "").strip()
    conv_id = data.get("conversation_id")
    
    if not message:
        return jsonify({"success": False, "message": "Nội dung trống."}), 400
        
    import time as _time
    result = process_inbound_message(
        channel="webchat",
        external_msg_id=f"WEB-{int(_time.time() * 1000)}",
        sender_id=payload.get("customer_name"),
        sender_name=payload.get("customer_name"),
        content=message,
        conversation_id=conv_id
    )
    return jsonify(result)

# =====================================================================
# 9. VẬN HÀNH: CA TRỰC, KANBAN, TỰ ĐỘNG HÓA & AUDIT
# =====================================================================
@app.route("/kanban")
@login_required
@role_required("agent", "admin", "sales")
def kanban_view():
    tickets = get_tickets(limit=200)
    agents = get_all_agents()
    return render_template("kanban.html", tickets=tickets, agents=agents)

@app.route("/api/kanban/ticket-create", methods=["POST"])
@login_required
@role_required("agent", "admin")
def api_kanban_ticket_create():
    subject = request.form.get("subject", "").strip()
    cust_name = request.form.get("customer_name", "").strip()
    cust_phone = request.form.get("customer_phone", "").strip()
    channel = request.form.get("channel", "web")
    priority = request.form.get("priority", "medium")
    
    cust = get_or_create_customer(full_name=cust_name, phone=cust_phone)
    ticket_id, ticket_code = create_ticket(
        customer_id=cust["id"],
        customer_name=cust_name,
        customer_phone=cust_phone,
        customer_email=None,
        channel=channel,
        subject=subject,
        priority=priority,
        first_message=f"Tiếp nhận yêu cầu từ Bảng Kanban: {subject}"
    )
    assign_ticket(ticket_id, session.get("user_id"))
    log_audit(session.get("user_id"), session.get("username"), "CREATE_TICKET", "KANBAN", ticket_id, f"Ticket #{ticket_code}: {subject}")
    flash(f"Đã tiếp nhận Ticket hỗ trợ #{ticket_code} vào bảng Kanban thành công!", "success")
    return redirect(url_for("kanban_view"))

@app.route("/api/kanban/<int:id>/stage", methods=["POST"])
@login_required
@role_required("agent", "admin")
def api_kanban_stage(id):
    data = request.get_json() or {}
    new_stage = data.get("stage")
    update_ticket_status(id, new_stage)
    log_audit(session.get("user_id"), session.get("username"), "UPDATE_TICKET_STAGE", "KANBAN", id, f"Giai đoạn: {new_stage}")
    return jsonify({"success": True})

@app.route("/api/kanban/<int:id>/delete", methods=["POST"])
@login_required
@role_required("agent", "admin")
def api_kanban_delete(id):
    delete_ticket(id)
    log_audit(session.get("user_id"), session.get("username"), "DELETE_TICKET", "KANBAN", id, f"Xoá ticket ID: {id}")
    return jsonify({"success": True})

@app.route("/devices")
@login_required
def devices_view():
    keyword = request.args.get("keyword", "").strip()
    warranties = get_warranties(keyword=keyword)
    return render_template("devices.html", warranties=warranties, keyword=keyword)

@app.route("/care-schedule")
@login_required
def care_schedule_alias():
    return redirect(url_for("shifts_view"))

@app.route("/reports")
@login_required
@role_required("agent", "admin")
def reports_view():
    stats = get_dashboard_stats()
    surveys = get_all_surveys(limit=50)
    agent_report = get_agent_performance_report()
    return render_template("reports.html", stats=stats, surveys=surveys, agent_report=agent_report)

# =====================================================================
# 9.5. VOUCHER & RETENTION MANAGEMENT (QUẢN LÝ VOUCHER & GIỮ CHÂN KHÁCH)
# =====================================================================
@app.route("/vouchers")
@login_required
@role_required("agent", "admin")
def vouchers_view():
    catalog = get_all_vouchers()
    customer_vouchers = get_customer_vouchers()
    customers = get_all_customers()
    return render_template("vouchers.html", catalog=catalog, customer_vouchers=customer_vouchers, customers=customers)

@app.route("/api/vouchers/grant", methods=["POST"])
@login_required
@role_required("agent", "admin")
def api_voucher_grant():
    data = request.get_json() if request.is_json else request.form
    customer_id = int(data.get("customer_id", 0))
    voucher_code = data.get("voucher_code", "").strip()
    title = data.get("title", "").strip()
    discount_type = data.get("discount_type", "fixed")
    discount_value = float(data.get("discount_value", 0))
    min_order_amount = float(data.get("min_order_amount", 0))
    valid_days = int(data.get("valid_days", 30))
    reason = data.get("reason", "").strip()
    ticket_id = int(data.get("ticket_id", 0)) if data.get("ticket_id") else None

    if not customer_id or not voucher_code:
        return jsonify({"success": False, "message": "Thiếu mã voucher hoặc thông tin khách hàng."}), 400

    import datetime
    valid_until = (datetime.datetime.now() + datetime.timedelta(days=valid_days)).strftime("%Y-%m-%d %H:%M:%S")

    cv_id = grant_customer_voucher(
        customer_id=customer_id,
        voucher_code=voucher_code,
        title=title or f"Voucher ưu đãi {voucher_code}",
        discount_type=discount_type,
        discount_value=discount_value,
        min_order_amount=min_order_amount,
        valid_until=valid_until,
        reason=reason,
        ticket_id=ticket_id
    )

    # Tự động ghi nhận thông báo gửi tới khách hàng
    cust = get_customer_by_id(customer_id)
    if cust and cust.get("phone"):
        create_notification(
            customer_id=customer_id,
            recipient=cust["phone"],
            channel="zalo",
            event_type="voucher_gift",
            title=f"Quà tặng ưu đãi dịch vụ {voucher_code}",
            content=f"CSKH Mobile xin gửi tặng Quý khách {cust.get('full_name')} mã voucher {voucher_code} giảm {discount_value:,.0f}đ. Hạn dùng đến {valid_until[:10]}."
        )

    log_audit(session.get("user_id"), session.get("username"), "GRANT_VOUCHER", "VOUCHER", cv_id, f"Cấp mã {voucher_code} cho khách #{customer_id}")

    if request.is_json:
        return jsonify({"success": True, "message": f"Đã cấp voucher {voucher_code} thành công!", "customer_voucher_id": cv_id})
    flash(f"Đã cấp voucher {voucher_code} thành công cho khách hàng!", "success")
    return redirect(url_for("vouchers_view"))

@app.route("/api/vouchers/ai-suggest", methods=["POST"])
@login_required
@role_required("agent", "admin")
def api_voucher_ai_suggest():
    data = request.get_json() or {}
    cust_name = data.get("customer_name", "Quý khách")
    incident_desc = data.get("incident_description", "")
    sentiment = data.get("sentiment", "negative")
    res = ai_service.suggest_ai_vouchers(cust_name, incident_desc, sentiment)
    return jsonify({"success": True, "suggestion": res})

# =====================================================================
# 9.6. TRUNG TÂM THÔNG BÁO ĐA KÊNH (NOTIFICATIONS: ZALO, SMS, EMAIL, PUSH)
# =====================================================================
@app.route("/notifications")
@login_required
@role_required("agent", "admin")
def notifications_view():
    notifications = get_all_notifications()
    customers = get_all_customers()
    return render_template("notifications.html", notifications=notifications, customers=customers)

@app.route("/api/notifications/send", methods=["POST"])
@login_required
@role_required("agent", "admin")
def api_notification_send():
    data = request.get_json() if request.is_json else request.form
    customer_id = int(data.get("customer_id", 0)) if data.get("customer_id") else None
    recipient = data.get("recipient", "").strip()
    channel = data.get("channel", "zalo")
    event_type = data.get("event_type", "ticket_created")
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    if not recipient or not content:
        return jsonify({"success": False, "message": "Thiếu người nhận hoặc nội dung thông báo."}), 400

    notif_id = create_notification(
        customer_id=customer_id,
        recipient=recipient,
        channel=channel,
        event_type=event_type,
        title=title or "Thông báo từ CSKH Mobile",
        content=content
    )
    log_audit(session.get("user_id"), session.get("username"), "SEND_NOTIFICATION", "NOTIFICATION", notif_id, f"Gửi {channel} tới {recipient}")

    if request.is_json:
        return jsonify({"success": True, "message": f"Đã gửi thông báo thành công qua kênh {channel.upper()}!", "id": notif_id})
    flash(f"Đã gửi thông báo thành công qua kênh {channel.upper()}!", "success")
    return redirect(url_for("notifications_view"))


@app.route("/shifts")
@login_required
@role_required("agent", "admin")
def shifts_view():
    shifts = get_work_shifts()
    agents = get_all_agents()
    return render_template("shifts.html", shifts=shifts, agents=agents)

@app.route("/api/shifts/create", methods=["POST"])
@login_required
@role_required("admin")
def api_shifts_create():
    agent_id = request.form.get("agent_id")
    shift_name = request.form.get("shift_name")
    shift_date = request.form.get("shift_date")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    
    create_work_shift(agent_id, shift_name, shift_date, start_time, end_time)
    log_audit(session.get("user_id"), session.get("username"), "CREATE_SHIFT", "SHIFT", None, f"Ca: {shift_name}, Ngày: {shift_date}")
    flash("Đã xếp ca trực mới thành công!", "success")
    return redirect(url_for("shifts_view"))

@app.route("/api/shifts/<int:id>/checkin", methods=["POST"])
@login_required
@role_required("agent", "admin")
def api_shifts_checkin(id):
    ctype = request.form.get("type", "checkin")
    checkin_shift(id, is_checkin=(ctype == "checkin"))
    log_audit(session.get("user_id"), session.get("username"), f"SHIFT_{ctype.upper()}", "SHIFT", id)
    flash("Chấm công thành công!", "success")
    return redirect(url_for("shifts_view"))

@app.route("/automation")
@login_required
@role_required("admin")
def automation_view():
    replies = get_auto_replies()
    return render_template("automation.html", auto_replies=replies)

@app.route("/api/automation/save", methods=["POST"])
@login_required
@role_required("admin")
def api_automation_save():
    channel = request.form.get("channel", "all")
    trigger_type = request.form.get("trigger_type")
    message = request.form.get("message", "").strip()
    is_active = 1 if request.form.get("is_active") else 0
    
    save_auto_reply(channel, trigger_type, message, is_active)
    log_audit(session.get("user_id"), session.get("username"), "UPDATE_AUTOMATION", "AUTO_REPLY", f"{channel}_{trigger_type}")
    flash("Đã lưu cấu hình phản hồi tự động!", "success")
    return redirect(url_for("automation_view"))

@app.route("/users")
@login_required
@role_required("admin")
def users_view():
    users = get_all_users()
    return render_template("users.html", users=users)

@app.route("/api/users/<int:id>/role", methods=["POST"])
@login_required
@role_required("admin")
def api_user_role(id):
    role = request.form.get("role")
    is_active = int(request.form.get("is_active", 1))
    update_user_role_status(id, role, is_active)
    log_audit(session.get("user_id"), session.get("username"), "UPDATE_USER_ROLE", "USER", id, f"Role: {role}, Active: {is_active}")
    flash("Đã cập nhật quyền hạn người dùng!", "success")
    return redirect(url_for("users_view"))

@app.route("/audit-logs")
@login_required
@role_required("admin")
def audit_logs_view():
    logs = get_audit_logs()
    return render_template("audit_logs.html", logs=logs)

# =====================================================================
# 10. SOFTPHONE TWILIO VOICE TRÊN TRÌNH DUYỆT
# =====================================================================
@app.route("/telephony")
@login_required
@role_required("agent", "admin")
def telephony_view():
    call_logs = get_call_logs()
    return render_template("telephony.html", call_logs=call_logs)

@app.route("/api/telephony/token")
@login_required
@role_required("agent", "admin")
def api_telephony_token():
    token_data = generate_twilio_voice_token(session.get("user_id"), session.get("username"))
    return jsonify(token_data)

@app.route("/api/telephony/call", methods=["POST"])
@login_required
@role_required("agent", "admin")
def api_telephony_call():
    data = request.get_json() or {}
    to_phone = data.get("to_phone", "").strip()
    if not to_phone:
        return jsonify({"success": False, "message": "Thiếu số điện thoại."}), 400
        
    import uuid
    call_sid = f"CA{uuid.uuid4().hex[:30]}"
    create_call_log(agent_id=session.get("user_id"), customer_phone=to_phone, direction="outbound", call_sid=call_sid)
    log_audit(session.get("user_id"), session.get("username"), "OUTBOUND_CALL", "TELEPHONY", call_sid, f"Gọi tới {to_phone}")
    return jsonify({"success": True, "call_sid": call_sid, "phone": to_phone})

@app.route("/api/telephony/status_callback", methods=["POST"])
def api_telephony_callback():
    handle_call_status_callback(request.form)
    return Response("<Response/>", mimetype="text/xml")

@app.route("/api/telephony/twiml/outbound", methods=["POST"])
def api_twiml_outbound():
    to = request.form.get("To", "")
    xml_str = generate_outbound_twiml(to)
    return Response(xml_str, mimetype="text/xml")

@app.route("/api/telephony/twiml/inbound", methods=["POST"])
def api_twiml_inbound():
    xml_str = generate_inbound_twiml()
    return Response(xml_str, mimetype="text/xml")

@app.route("/api/logistics/refresh")
@login_required
@role_required("agent", "admin")
def api_logistics_refresh():
    code = request.args.get("code")
    carrier = request.args.get("carrier", "GHN")
    res = refresh_tracking_status(code, carrier)
    return jsonify(res)

# =====================================================================
# 10.5. NGHIỆP VỤ TƯ VẤN VÀ BÁN ĐIỆN THOẠI DI ĐỘNG
# =====================================================================
@app.route("/products")
def phone_products_list():
    keyword = request.args.get("keyword", "").strip()
    brand = request.args.get("brand", "all")
    price_range = request.args.get("price_range", "")
    in_stock_only = bool(request.args.get("in_stock"))
    
    price_min = None
    price_max = None
    if price_range == "under_10m":
        price_max = 10000000
    elif price_range == "10m_20m":
        price_min = 10000000
        price_max = 20000000
    elif price_range == "20m_30m":
        price_min = 20000000
        price_max = 30000000
    elif price_range == "over_30m":
        price_min = 30000000

    products = get_phone_products(
        keyword=keyword,
        brand=brand,
        price_min=price_min,
        price_max=price_max,
        in_stock_only=in_stock_only
    )
    return render_template("products.html",
                           products=products,
                           keyword=keyword,
                           current_brand=brand,
                           current_price=price_range,
                           in_stock_only=in_stock_only)

@app.route("/products/create", methods=["POST"])
@login_required
@role_required("agent", "admin")
def phone_product_create():
    name = request.form.get("name", "").strip()
    brand = request.form.get("brand", "Khác")
    model = request.form.get("model") or name
    description = request.form.get("description", "")
    listed_price = float(request.form.get("listed_price", 0))
    promo_price = float(request.form.get("promo_price")) if request.form.get("promo_price") else None
    stock_quantity = int(request.form.get("stock_quantity", 0))
    warehouse_location = request.form.get("warehouse_location", "Kho Tổng")
    screen_spec = request.form.get("screen_spec")
    chip_spec = request.form.get("chip_spec")
    ram_spec = request.form.get("ram_spec")
    storage_spec = request.form.get("storage_spec")
    camera_spec = request.form.get("camera_spec")
    battery_spec = request.form.get("battery_spec")
    os_spec = request.form.get("os_spec")
    connectivity_spec = request.form.get("connectivity_spec", "5G, Wi-Fi 6, Bluetooth 5.3")
    warranty_months = int(request.form.get("warranty_months", 12))

    prod_id = add_phone_product(
        name=name, brand=brand, model=model, description=description,
        listed_price=listed_price, promo_price=promo_price,
        stock_quantity=stock_quantity, warehouse_location=warehouse_location,
        screen_spec=screen_spec, chip_spec=chip_spec, ram_spec=ram_spec,
        storage_spec=storage_spec, camera_spec=camera_spec, battery_spec=battery_spec,
        os_spec=os_spec, connectivity_spec=connectivity_spec, warranty_months=warranty_months
    )
    log_audit(session.get("user_id"), session.get("username"), "CREATE_PHONE_PRODUCT", "PRODUCT", prod_id, f"Thêm dòng máy: {name}")
    flash(f"Đã thêm mẫu điện thoại '{name}' vào danh mục thành công!", "success")
    return redirect(url_for("phone_products_list"))

@app.route("/products/<int:id>")
def phone_product_detail(id):
    product = get_phone_product_by_id(id)
    if not product:
        flash("Sản phẩm điện thoại không tồn tại.", "danger")
        return redirect(url_for("phone_products_list"))
        
    variants = get_phone_variants(id)
    price_history = get_price_history(id)
    return render_template("product_detail.html", product=product, variants=variants, price_history=price_history)

@app.route("/products/<int:id>/update-price", methods=["POST"])
@login_required
@role_required("agent", "admin")
def phone_product_update_price(id):
    product = get_phone_product_by_id(id)
    if not product:
        flash("Sản phẩm không tồn tại.", "danger")
        return redirect(url_for("phone_products_list"))
        
    listed_price = float(request.form.get("listed_price", 0))
    promo_price = float(request.form.get("promo_price")) if request.form.get("promo_price") else None
    stock_quantity = int(request.form.get("stock_quantity", 0))
    warehouse_location = request.form.get("warehouse_location") or product.get("warehouse_location")
    change_reason = request.form.get("change_reason", "Cập nhật bảng giá")

    update_phone_product(
        product_id=id,
        name=product["name"],
        brand=product["brand"],
        model=product.get("model", ""),
        description=product.get("description", ""),
        listed_price=listed_price,
        promo_price=promo_price,
        stock_quantity=stock_quantity,
        warehouse_location=warehouse_location,
        screen_spec=product.get("screen_spec"),
        chip_spec=product.get("chip_spec"),
        ram_spec=product.get("ram_spec"),
        storage_spec=product.get("storage_spec"),
        camera_spec=product.get("camera_spec"),
        battery_spec=product.get("battery_spec"),
        os_spec=product.get("os_spec"),
        connectivity_spec=product.get("connectivity_spec"),
        warranty_months=product.get("warranty_months", 12),
        image_url=product.get("image_url"),
        user_id=session.get("user_id"),
        user_name=session.get("full_name") or session.get("username"),
        change_reason=change_reason
    )
    log_audit(session.get("user_id"), session.get("username"), "UPDATE_PRICE_STOCK", "PRODUCT", id, f"Giá mới: {listed_price:,.0f} ₫, Tồn: {stock_quantity}")
    flash("Đã cập nhật bảng giá và lượng tồn kho thành công!", "success")
    return redirect(f"/products/{id}")

@app.route("/products/compare")
def phone_products_compare():
    p1 = request.args.get("p1")
    p2 = request.args.get("p2")
    p3 = request.args.get("p3")
    
    selected_ids = [int(p) for p in [p1, p2, p3] if p and p.isdigit()]
    compare_list = get_phone_comparison(selected_ids)
    all_products = get_phone_products()
    
    sel_p1 = get_phone_product_by_id(int(p1)) if p1 and p1.isdigit() else None
    sel_p2 = get_phone_product_by_id(int(p2)) if p2 and p2.isdigit() else None
    sel_p3 = get_phone_product_by_id(int(p3)) if p3 and p3.isdigit() else None

    return render_template("product_compare.html",
                           all_products=all_products,
                           compare_list=compare_list,
                           sel_p1=sel_p1,
                           sel_p2=sel_p2,
                           sel_p3=sel_p3)

@app.route("/consultation", methods=["GET", "POST"])
@login_required
@role_required("agent", "admin")
def phone_consultation():
    customers = get_all_customers()
    if request.method == "POST":
        customer_id = int(request.form.get("customer_id"))
        budget_min = float(request.form.get("budget_min") or 0)
        budget_max = float(request.form.get("budget_max") or 100000000)
        primary_usage = request.form.get("primary_usage")
        preferred_brands = request.form.get("preferred_brands")
        desired_screen_size = request.form.get("desired_screen_size")
        key_criteria = request.form.get("key_criteria")
        agent_notes = request.form.get("agent_notes")

        recommendations = sales_service.consult_and_recommend(
            customer_id=customer_id,
            budget_min=budget_min,
            budget_max=budget_max,
            primary_usage=primary_usage,
            preferred_brands=preferred_brands,
            desired_screen_size=desired_screen_size,
            key_criteria=key_criteria,
            agent_notes=agent_notes
        )
        selected_cust = get_customer_by_id(customer_id)
        pref = get_customer_preferences(customer_id)
        log_audit(session.get("user_id"), session.get("username"), "CONSULT_PHONE", "CUSTOMER", customer_id, f"Gợi ý {len(recommendations)} máy")
        flash(f"Đã lưu nhu cầu tư vấn và thuật toán đề xuất {len(recommendations)} sản phẩm tối ưu!", "success")
        return render_template("consultation.html",
                               customers=customers,
                               selected_cust=selected_cust,
                               pref=pref,
                               recommendations=recommendations)

    cust_id = request.args.get("customer_id")
    selected_cust = get_customer_by_id(int(cust_id)) if cust_id and cust_id.isdigit() else (customers[0] if customers else None)
    pref = get_customer_preferences(selected_cust["id"]) if selected_cust else None
    recommendations = []
    if pref:
        recommendations = recommend_phones(
            budget_min=pref.get("budget_min"),
            budget_max=pref.get("budget_max"),
            usage=pref.get("primary_usage"),
            preferred_brand=pref.get("preferred_brands"),
            screen_size=pref.get("desired_screen_size")
        )
    elif selected_cust:
        recommendations = recommend_phones()

    return render_template("consultation.html",
                           customers=customers,
                           selected_cust=selected_cust,
                           pref=pref,
                           recommendations=recommendations)

@app.route("/quotations")
@login_required
@role_required("agent", "admin")
def quotations_list():
    quotations = get_quotations()
    return render_template("quotations.html", quotations=quotations)

@app.route("/quotations/create", methods=["GET", "POST"])
@login_required
@role_required("agent", "admin")
def quotation_create():
    customers = get_all_customers()
    products = get_phone_products()
    promotions = get_promotions()

    if request.method == "POST":
        customer_id = int(request.form.get("customer_id"))
        cust = get_customer_by_id(customer_id)
        customer_name = cust["full_name"] if cust else "Khách hàng"
        customer_phone = request.form.get("customer_phone") or (cust["phone"] if cust else "")
        
        product_id = int(request.form.get("product_id"))
        prod = get_phone_product_by_id(product_id)
        qty = int(request.form.get("quantity", 1))
        promo_code = request.form.get("promotion_code")
        notes = request.form.get("notes")

        if not prod:
            flash("Sản phẩm không hợp lệ.", "danger")
            return redirect(url_for("quotations_list"))

        price = float(prod.get("promo_price") or prod["listed_price"])
        items = [{
            "product_id": prod["id"],
            "name": prod["name"],
            "listed_price": float(prod["listed_price"]),
            "promo_price": float(prod.get("promo_price") or prod["listed_price"]),
            "qty": qty,
            "subtotal": price * qty
        }]

        quote = sales_service.create_and_send_quotation(
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            agent_id=session.get("user_id"),
            agent_name=session.get("full_name") or session.get("username"),
            items=items,
            promo_code=promo_code,
            notes=notes
        )
        flash(f"Đã lập bản báo giá {quote['quote_code']} thành công!", "success")
        return redirect(url_for("quotations_list"))

    sel_cust_id = int(request.args.get("customer_id", 0))
    sel_prod_id = int(request.args.get("product_id", 0))
    sel_cust = get_customer_by_id(sel_cust_id) if sel_cust_id else None

    return render_template("quotation_create.html",
                           customers=customers,
                           products=products,
                           promotions=promotions,
                           sel_cust_id=sel_cust_id,
                           sel_prod_id=sel_prod_id,
                           sel_cust=sel_cust)

@app.route("/quotations/<int:id>/status", methods=["POST"])
@login_required
@role_required("agent", "admin")
def quotation_update_status(id):
    new_status = request.form.get("status")
    update_quotation_status(id, new_status)
    log_audit(session.get("user_id"), session.get("username"), "UPDATE_QUOTE_STATUS", "QUOTATION", id, f"Trạng thái mới: {new_status}")
    flash(f"Đã chuyển trạng thái báo giá sang '{new_status}'!", "success")
    return redirect(url_for("quotations_list"))

@app.route("/sales-orders")
@login_required
@role_required("agent", "admin")
def sales_orders_list():
    orders = get_sales_orders()
    return render_template("sales_orders.html", orders=orders)

@app.route("/sales-orders/create", methods=["GET", "POST"])
@login_required
@role_required("agent", "admin")
def sales_order_create_view():
    customers = get_all_customers()
    products = get_phone_products()

    if request.method == "POST":
        customer_id = int(request.form.get("customer_id", 0)) or None
        cust = get_customer_by_id(customer_id) if customer_id else None
        customer_name = cust["full_name"] if cust else "Khách vãng lai"
        customer_phone = request.form.get("customer_phone", "")
        
        product_id = int(request.form.get("product_id"))
        prod = get_phone_product_by_id(product_id)
        qty = int(request.form.get("quantity", 1))
        discount_amount = float(request.form.get("discount_amount", 0) or 0)
        shipping_address = request.form.get("shipping_address")
        payment_method = request.form.get("payment_method", "cod")
        quote_id = int(request.form.get("quote_id", 0)) or None

        if not prod:
            flash("Sản phẩm không hợp lệ.", "danger")
            return redirect(url_for("sales_orders_list"))

        if prod["stock_quantity"] < qty:
            flash(f"Tồn kho không đủ! Hiện tại kho chỉ còn {prod['stock_quantity']} máy.", "warning")
            return redirect(url_for("sales_order_create_view"))

        unit_price = float(prod.get("promo_price") or prod["listed_price"])
        items = [{
            "product_id": prod["id"],
            "name": prod["name"],
            "unit_price": unit_price,
            "qty": qty,
            "subtotal": unit_price * qty
        }]

        order_id, order_code = create_sales_order(
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            agent_id=session.get("user_id"),
            items=items,
            discount_amount=discount_amount,
            shipping_address=shipping_address,
            payment_method=payment_method,
            quote_id=quote_id
        )

        if quote_id:
            update_quotation_status(quote_id, "accepted")

        log_audit(session.get("user_id"), session.get("username"), "CREATE_SALES_ORDER", "ORDER", order_id, f"Tạo đơn {order_code}")
        flash(f"Đã tạo đơn hàng bán điện thoại {order_code} và trừ tồn kho tự động!", "success")
        return redirect(f"/sales-orders/{order_id}")

    quote_id = request.args.get("quote_id")
    quote = get_quotation_by_id(int(quote_id)) if quote_id and quote_id.isdigit() else None
    sel_cust = get_customer_by_id(quote["customer_id"]) if quote and quote.get("customer_id") else None

    return render_template("sales_order_create.html",
                           customers=customers,
                           products=products,
                           quote=quote,
                           sel_cust=sel_cust)

@app.route("/sales-orders/<int:id>")
@login_required
@role_required("agent", "admin")
def sales_order_detail_view(id):
    order = get_sales_order_by_id(id)
    if not order:
        flash("Đơn hàng không tồn tại.", "danger")
        return redirect(url_for("sales_orders_list"))
        
    history = get_order_status_history(id)
    return render_template("sales_order_detail.html", order=order, history=history)

@app.route("/sales-orders/<int:id>/status", methods=["POST"])
@login_required
@role_required("agent", "admin")
def sales_order_update_status(id):
    new_status = request.form.get("status")
    notes = request.form.get("notes")
    update_sales_order_status(
        order_id=id,
        new_status=new_status,
        user_id=session.get("user_id"),
        user_name=session.get("full_name") or session.get("username"),
        notes=notes
    )
    log_audit(session.get("user_id"), session.get("username"), "UPDATE_ORDER_STATUS", "ORDER", id, f"Trạng thái: {new_status}")
    flash(f"Đã chuyển trạng thái đơn hàng sang '{new_status}'!", "success")
    return redirect(f"/sales-orders/{id}")

@app.route("/warranties")
@login_required
def warranties_list():
    keyword = request.args.get("keyword", "").strip()
    if session.get("role") == "customer":
        cust = get_customer_by_user_id(session.get("user_id"))
        cust_id = cust["id"] if cust else None
        warranties = get_warranties(customer_id=cust_id, keyword=keyword)
        reminders = []
    else:
        warranties = get_warranties(keyword=keyword)
        reminders = get_followup_reminders()

    return render_template("warranties.html", warranties=warranties, reminders=reminders, keyword=keyword)

@app.route("/warranties/create", methods=["POST"])
@login_required
@role_required("agent", "admin")
def warranty_create():
    order_id = int(request.form.get("order_id", 0)) or None
    customer_id = int(request.form.get("customer_id", 0)) or None
    customer_name = request.form.get("customer_name")
    customer_phone = request.form.get("customer_phone")
    product_id = int(request.form.get("product_id", 0))
    imei_serial = request.form.get("imei_serial", "").strip()
    warranty_package = request.form.get("warranty_package", "Bảo hành tiêu chuẩn chính hãng 12 tháng")
    months = int(request.form.get("months", 12))

    prod = get_phone_product_by_id(product_id)
    product_name = prod["name"] if prod else "Điện thoại chính hãng"

    warr_id, code = create_warranty(
        order_id=order_id,
        customer_id=customer_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        product_id=product_id,
        product_name=product_name,
        imei_serial=imei_serial,
        warranty_package=warranty_package,
        months=months
    )
    log_audit(session.get("user_id"), session.get("username"), "ACTIVATE_WARRANTY", "WARRANTY", warr_id, f"Mã sổ {code}, IMEI: {imei_serial}")
    flash(f"Đã kích hoạt sổ bảo hành điện tử {code} (IMEI: {imei_serial}) thành công!", "success")
    return redirect(url_for("warranties_list"))

@app.route("/warranties/convert-ticket", methods=["POST"])
@login_required
@role_required("agent", "admin")
def warranty_convert_ticket():
    warranty_id = int(request.form.get("warranty_id"))
    issue_description = request.form.get("issue_description", "").strip()
    ticket_id, ticket_code = sales_service.convert_warranty_to_support_ticket(
        warranty_id=warranty_id,
        issue_description=issue_description,
        agent_id=session.get("user_id"),
        agent_name=session.get("full_name") or session.get("username")
    )
    flash(f"Đã mở phiếu Ticket hỗ trợ & tiếp nhận sửa chữa #{ticket_code}!", "success")
    return redirect(f"/tickets/{ticket_id}")

@app.route("/warranties/reminders/<int:id>/complete", methods=["POST"])
@login_required
@role_required("agent", "admin")
def warranty_complete_reminder(id):
    complete_followup_reminder(id)
    log_audit(session.get("user_id"), session.get("username"), "COMPLETE_REMINDER", "REMINDER", id, "Hoàn tất chăm sóc sau bán")
    flash("Đã đánh dấu hoàn tất nhắc nhở chăm sóc sau bán hàng!", "success")
    return redirect(url_for("warranties_list"))

# =====================================================================
# 11. WEBHOOKS BÊN THỨ BA (ZALO, FACEBOOK, EMAIL, GHN, GHTK)
# =====================================================================
@app.route("/api/webhooks/zalo", methods=["POST"])
def webhook_zalo():
    payload = request.get_json() or {}
    event_name = payload.get("event_name")
    sender_id = payload.get("sender", {}).get("id")
    msg_id = payload.get("message", {}).get("msg_id", f"ZALO-{payload.get('timestamp')}")
    text = payload.get("message", {}).get("text", "")
    
    if text:
        process_inbound_message(
            channel="zalo",
            external_msg_id=msg_id,
            sender_id=sender_id,
            sender_name=f"Khách Zalo ({sender_id})",
            content=text,
            raw_payload=payload
        )
    return jsonify({"error": 0, "message": "Success"})

@app.route("/api/webhooks/facebook", methods=["GET", "POST"])
def webhook_facebook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        verify_token = os.getenv("FB_VERIFY_TOKEN", "crm_facebook_token_2026")
        if mode == "subscribe" and token == verify_token:
            return challenge
        return "Forbidden", 403

    payload = request.get_json() or {}
    for entry in payload.get("entry", []):
        for messaging_event in entry.get("messaging", []):
            if "message" in messaging_event:
                sender_id = messaging_event["sender"]["id"]
                msg_id = messaging_event["message"].get("mid")
                text = messaging_event["message"].get("text", "")
                if text:
                    process_inbound_message(
                        channel="facebook",
                        external_msg_id=msg_id,
                        sender_id=sender_id,
                        sender_name=f"Khách Facebook ({sender_id})",
                        content=text,
                        raw_payload=messaging_event
                    )
    return "EVENT_RECEIVED", 200

@app.route("/api/webhooks/email/inbound", methods=["POST"])
def webhook_email_inbound():
    res = parse_sendgrid_inbound(request.form)
    return jsonify(res)

@app.route("/api/webhooks/logistics/ghn", methods=["POST"])
def webhook_ghn():
    payload = request.get_json() or {}
    data, code = handle_ghn_webhook(request.headers, payload)
    return jsonify(data), code

@app.route("/api/webhooks/logistics/ghtk", methods=["POST"])
def webhook_ghtk():
    raw_body = request.get_data()
    payload = request.get_json() or {}
    data, code = handle_ghtk_webhook(request.headers, raw_body, payload)
    return jsonify(data), code

# =====================================================================
# 12. AI REQUIREMENT AGENT (PHÂN TÍCH YÊU CẦU BA TỪ THƯ MỤC AGENT)
# =====================================================================
@app.route("/agent", methods=["GET", "POST"])
@login_required
@role_required("agent", "admin")
def requirement_agent():
    result = None
    user_requirement = ""
    error = None
    saved_filename = None
    
    if request.method == "POST":
        user_requirement = request.form.get("requirement", "").strip()
        if user_requirement:
            try:
                from services.requirement_agent_service import analyze_requirement
                analysis_res = analyze_requirement(user_requirement)
                result = analysis_res["content"]
                saved_filename = analysis_res.get("saved_filename")
                log_audit(session.get("user_id"), session.get("username"), "RUN_AGENT", "REQUIREMENT", None, "Phân tích yêu cầu bằng AI Agent")
            except Exception as e:
                error = str(e)
        else:
            error = "Vui lòng nhập nội dung yêu cầu."
            
    from services.requirement_agent_service import get_recent_specs
    recent_specs = get_recent_specs()
    return render_template("requirement_agent.html", result=result, user_requirement=user_requirement, error=error, saved_filename=saved_filename, recent_specs=recent_specs)

@app.route("/agent/outputs/<filename>")
@login_required
@role_required("agent", "admin")
def agent_download_output(filename):
    from pathlib import Path
    from flask import send_from_directory
    outputs_dir = Path(__file__).resolve().parent.parent / "Agent" / "outputs"
    return send_from_directory(outputs_dir, filename, as_attachment=True)

# =====================================================================
# 13. AI ASSISTANT HUB (SMART REPLY, RAG KNOWLEDGE SEARCH, SENTIMENT)
# =====================================================================
@app.route("/ai-assistant")
@login_required
@role_required("agent", "admin")
def ai_assistant_view():
    return render_template("ai_assistant.html")

@app.route("/api/ai/smart-reply", methods=["POST"])
@login_required
@role_required("agent", "admin")
def api_ai_smart_reply():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    cust_name = data.get("customer_name", "Quý khách")
    device_model = data.get("device_model")
    
    if not message:
        return jsonify({"success": False, "message": "Nội dung trống."}), 400
        
    replies = ai_service.generate_contextual_replies(message, customer_name=cust_name, device_model=device_model)
    return jsonify({"success": True, "replies": replies})

@app.route("/api/ai/rag-search", methods=["POST"])
@login_required
@role_required("agent", "admin")
def api_ai_rag_search():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    
    if not query:
        return jsonify({"success": False, "message": "Câu truy vấn trống."}), 400
        
    import json
    from services.rag_service import retrieve_faqs
    faqs, _ = retrieve_faqs(query)
    faqs = faqs[:4]
    
    prompt = f"""
    Bạn là chuyên viên kỹ thuật cao cấp hỗ trợ sau bán hàng của chuỗi điện thoại CSKH Mobile.
    Hãy tổng hợp câu trả lời hướng dẫn kỹ thuật chi tiết, ân cần và từng bước cho khách hàng dựa trên câu hỏi và các tài liệu sau.
    
    CÂU HỎI: {query}
    TÀI LIỆU CẨM NANG:
    {json.dumps([{'issue': f.get('issue_name'), 'solution': f.get('solution')} for f in faqs], ensure_ascii=False)}
    
    Yêu cầu: Viết theo cấu trúc:
    1. Chẩn đoán nguyên nhân
    2. Hướng dẫn khách tự kiểm tra / xử lý tại chỗ
    3. Chính sách bảo hành áp dụng và khuyến nghị
    """
    try:
        ai_answer = ai_service.generate_text(prompt)
    except Exception:
        if faqs:
            ai_answer = f"Theo quy định kỹ thuật: {faqs[0].get('solution')}"
        else:
            ai_answer = "Dạ với sự cố này, trung tâm CSKH Mobile sẵn sàng tiếp nhận kiểm tra thẩm định miễn phí cho máy của mình ạ."
            
    return jsonify({"success": True, "faqs": faqs, "ai_answer": ai_answer})

@app.route("/api/ai/sentiment-analysis", methods=["POST"])
@login_required
@role_required("agent", "admin")
def api_ai_sentiment():
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    
    if not text:
        return jsonify({"success": False, "message": "Nội dung trống."}), 400
        
    res = ai_service.analyze_sentiment(text)
    return jsonify({"success": True, "result": res})

# =====================================================================
# 14. SETTINGS
# =====================================================================
CRM_SETTINGS = {
    "brand_name": "CSKH/MOBILE Service Center",
    "hotline": "0868643044",
    "support_email": "support@cskhmobile.vn",
    "address": "Số 123 Đường Ba Tháng Hai, Phường 11, Quận 10, TP. Hồ Chí Minh",
    "working_hours": "08:00 - 21:30 (Thứ 2 đến Chủ nhật, kể cả ngày lễ)",
    "sla_first_response": 15,
    "sla_resolution_hours": 24,
    "auto_assign_method": "least_busy",
    "auto_survey_enabled": 1,
    "ai_provider": "gemini",
    "ai_tone": "empathetic"
}

@app.route("/settings", methods=["GET", "POST"])
@login_required
@role_required("admin", "agent")
def settings_view():
    global CRM_SETTINGS
    if request.method == "POST":
        CRM_SETTINGS["brand_name"] = request.form.get("brand_name", CRM_SETTINGS["brand_name"])
        CRM_SETTINGS["hotline"] = request.form.get("hotline", CRM_SETTINGS["hotline"])
        CRM_SETTINGS["support_email"] = request.form.get("support_email", CRM_SETTINGS["support_email"])
        CRM_SETTINGS["address"] = request.form.get("address", CRM_SETTINGS["address"])
        CRM_SETTINGS["working_hours"] = request.form.get("working_hours", CRM_SETTINGS["working_hours"])
        try:
            CRM_SETTINGS["sla_first_response"] = int(request.form.get("sla_first_response", 15))
            CRM_SETTINGS["sla_resolution_hours"] = int(request.form.get("sla_resolution_hours", 24))
        except Exception:
            pass
        CRM_SETTINGS["auto_assign_method"] = request.form.get("auto_assign_method", "least_busy")
        CRM_SETTINGS["auto_survey_enabled"] = 1 if request.form.get("auto_survey_enabled") else 0
        CRM_SETTINGS["ai_provider"] = request.form.get("ai_provider", "gemini")
        CRM_SETTINGS["ai_tone"] = request.form.get("ai_tone", "empathetic")
        log_audit(session.get("user_id"), session.get("username"), "UPDATE_SETTINGS", "SYSTEM", None, "Cập nhật cấu hình hệ thống")
        flash("Đã lưu cài đặt hệ thống thành công!", "success")
        return redirect(url_for("settings_view"))
        
    return render_template("settings.html", settings=CRM_SETTINGS)

# =====================================================================
# KHỞI CHẠY ỨNG DỤNG
# =====================================================================
if __name__ == "__main__":
    app.run(debug=True, port=5000)