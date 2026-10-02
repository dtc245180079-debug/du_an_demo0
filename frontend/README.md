# FRONTEND - HỆ THỐNG CRM & BÁN HÀNG

Thư mục chứa toàn bộ mã nguồn giao diện người dùng (UI/UX) của ứng dụng CRM.

---

## 📁 Cấu trúc thư mục

```text
frontend/
├── static/                   # Tài nguyên tĩnh (CSS, JS, hình ảnh, icon)
│   ├── style.css             # Hệ thống CSS chính cho toàn bộ 34 màn hình
│   ├── chat.js               # Logic điều khiển khung chat AI & tư vấn
│   ├── chatbot_*.png         # Các biến thể logo & icon Chatbot AI
│   └── cskh_*.png            # Logo thương hiệu & biểu tượng ứng dụng
│
└── templates/                # Toàn bộ 34 giao diện HTML Jinja2
    ├── base.html             # Layout chuẩn (Navbar, Sidebar, Softphone modal, thông báo)
    ├── dashboard.html        # Tổng quan số liệu thống kê & biểu đồ Chart.js
    ├── login.html            # Đăng nhập hệ thống (hỗ trợ Google OIDC)
    ├── register.html         # Đăng ký tài khoản mới
    ├── customers.html        # Danh sách khách hàng
    ├── customer_360.html     # Hồ sơ khách hàng 360 độ (đơn hàng, bảo hành, ticket)
    ├── tickets.html          # Danh sách phiếu hỗ trợ
    ├── ticket_detail.html    # Chi tiết ticket & luồng trao đổi
    ├── ticket_create.html    # Biểu mẫu tạo ticket mới
    ├── inbox.html            # Hộp thư hợp nhất đa kênh (Omnichannel Inbox)
    ├── products.html         # Danh mục sản phẩm & điện thoại thông minh
    ├── product_detail.html   # Chi tiết sản phẩm & thông số kỹ thuật
    ├── product_compare.html  # So sánh cấu hình và giá điện thoại
    ├── quotations.html       # Quản lý báo giá bán hàng
    ├── quotation_create.html # Lập báo giá mới cho khách hàng
    ├── sales_orders.html     # Quản lý đơn hàng bán
    ├── sales_order_detail.html # Chi tiết đơn hàng, lịch sử trạng thái
    ├── sales_order_create.html # Tạo đơn hàng mới
    ├── warranties.html       # Quản lý hồ sơ bảo hành thiết bị
    ├── kanban.html           # Phễu bán hàng dạng thẻ Kanban kéo thả
    ├── shifts.html           # Quản lý & check-in ca trực nhân viên
    ├── consultation.html     # Trợ lý AI tư vấn và so sánh sản phẩm
    ├── telephony.html        # Lịch sử cuộc gọi tổng đài
    ├── automation.html       # Kịch bản tự động phản hồi khách hàng
    ├── audit_logs.html       # Nhật ký thao tác hệ thống (Audit Logs)
    ├── faqs.html             # Danh sách câu hỏi thường gặp (Knowledge Base)
    ├── add_faq.html          # Thêm mới câu hỏi FAQ
    ├── edit_faq.html         # Chỉnh sửa FAQ
    ├── users.html            # Quản trị tài khoản & phân quyền (RBAC)
    ├── portal.html           # Cổng thông tin dành cho Khách hàng
    ├── portal_new_ticket.html # Khách hàng gửi ticket hỗ trợ mới
    ├── portal_ticket_chat.html# Khách hàng trao đổi trực tiếp trên ticket
    ├── portal_survey.html    # Đánh giá khảo sát CSAT / NPS
    └── webchat_embed.html    # Giao diện widget chat nhúng website ngoài
```

---

## 🎨 Tùy biến giao diện

1. **CSS & Giao diện:** Chỉnh sửa file [style.css](file:///e:/quanlykh/frontend/static/style.css) để thay đổi màu sắc chủ đạo, font chữ hoặc các hiệu ứng chuyển động.
2. **Kịch bản Chat:** Chỉnh sửa [chat.js](file:///e:/quanlykh/frontend/static/chat.js) để cập nhật logic gửi/nhận tin nhắn trợ lý AI.
3. **Thêm trang mới:**
   - Tạo file HTML mới trong `frontend/templates/` kế thừa `{% extends "base.html" %}`.
   - Thêm route tương ứng trong [backend/app.py](file:///e:/quanlykh/backend/app.py) gọi `render_template("ten_trang.html")`.
