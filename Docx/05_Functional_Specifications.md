# TÀI LIỆU 05: FUNCTIONAL SPECIFICATIONS (ĐẶC TẢ CHỨC NĂNG & API)

Tài liệu này đặc tả logic nghiệp vụ và các luồng xử lý (Endpoints/Routes) tương ứng trong mã nguồn Backend (Flask - `app.py`).

## 1. Phân hệ Xác thực & Tài khoản (Auth & RBAC)
- **Đăng nhập (`GET /login`, `POST /login`)**
  - **Input:** `username_or_email`, `password`.
  - **Logic:** Tìm kiếm user bằng username hoặc email trong CSDL. Sử dụng hàm `verify_password()` để so sánh băm `password_hash`. Nếu đúng, lưu `session` và điều hướng: Agent/Admin vào `/dashboard`, Customer vào `/portal`.
  - **Validate:** Báo lỗi nếu sai thông tin hoặc tài khoản bị khóa (`is_active` = 0).
- **Đăng ký (`GET /register`, `POST /register`)**
  - **Input:** `full_name`, `email`, `phone`, `username`, `password`, `role`.
  - **Logic:** Kiểm tra trùng lặp (username, email). Băm mật khẩu. Chỉ Admin mới có quyền tạo role Admin qua UI quản trị, người dùng thường đăng ký mặc định là Role `customer`.
- **Đăng xuất (`/logout`)**: Xóa phiên `session` hiện tại và điều hướng về `/login`.

## 2. Phân hệ Ticket & Hỗ trợ Khách hàng
- **Portal Khách hàng (`/portal`, `/portal/ticket/new`)**
  - **Logic:** Customer tự đăng nhập, xem danh sách Ticket của mình. Nhấn tạo Ticket mới sẽ submit form gồm: `subject`, `priority`, `message`. Hệ thống sinh mã `ticket_code` tự động và lưu `ticket_messages` ban đầu.
- **Xử lý Ticket của Agent (`/tickets`, `/ticket/<id>`)**
  - **Logic:** Agent xem danh sách. Trong màn hình chi tiết, Agent có thể:
    - Gửi tin nhắn phản hồi (`POST /ticket/<id>/reply`).
    - Cập nhật trạng thái (`open` -> `in-progress` -> `resolved`).
    - Khảo sát tự động: Khi trạng thái chuyển sang `resolved`, hệ thống (qua hàm `trigger_ticket_closure_survey`) kích hoạt gửi form đánh giá CSAT/NPS cho khách.
- **RAG AI Chatbot (`POST /api/chat`)**
  - **Logic:** Nhận `question` từ UI, gọi logic `ask_rag(question)`, và trả về JSON chứa `answer` cho người dùng mà không cần reload trang.

## 3. Phân hệ Customer 360 & Sales Pipeline
- **Hồ sơ 360 (`/customer/<id>`)**
  - **Logic:** Truy xuất đồng thời dữ liệu từ bảng `customers`, `tickets`, `sales_orders`, và `customer_preferences` để render lên 1 màn hình duy nhất (Unified View).
- **Cơ hội bán hàng (`/kanban`)**
  - **Logic:** Truy xuất dữ liệu từ bảng `sales_opportunities`. Cho phép Agent kéo thả hoặc cập nhật `stage` (Lead -> Đàm phán -> Chốt). Cập nhật qua AJAX.
- **Tạo Báo giá và Đơn hàng (`/quotation/create`, `/order/create`)**
  - **Logic:** Chọn khách hàng, chọn `phone_products` và `phone_variants`. Tính toán `discount_amount` và `final_amount`. Khi tạo Đơn hàng thành công, tự động cập nhật trừ số lượng `stock_quantity` trong bảng biến thể sản phẩm.

## 4. Phân hệ Omnichannel & Telephony
- **Omnichannel Inbox (`/inbox`)**
  - **Logic:** Gọi webhook hoặc hàm `process_inbound_message()` để nhận tin nhắn từ Zalo/Webchat, lưu vào `omnichannel_messages`. Agent phản hồi qua `POST /inbox/reply` và hệ thống gọi API bên thứ 3 tương ứng qua `send_outbound_reply()`.
- **Tổng đài (`/telephony`)**
  - **Logic:** Tạo token (Twilio token) cho WebRTC, cho phép gọi điện ngay trên trình duyệt. Lưu lịch sử vào bảng `call_logs`.

## 5. Middleware & Bảo vệ (Decorators)
- **`@login_required`**: Chặn truy cập nếu chưa có `session`.
- **`@role_required("agent", "admin")`**: Chặn Customer truy cập vào các màn hình nghiệp vụ nội bộ (Dashboard, Inbox, Kanban).
