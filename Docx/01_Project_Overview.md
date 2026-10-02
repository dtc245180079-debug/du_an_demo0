# TÀI LIỆU 01: PROJECT OVERVIEW (TỔNG QUAN DỰ ÁN)

## 1. Tên Dự Án
Hệ thống Quản lý Khách hàng Toàn diện (Omnichannel CRM System)

## 2. Mục tiêu Dự án
Dựa trên mã nguồn thực tế, dự án nhằm mục đích xây dựng một nền tảng Web-based CRM hỗ trợ doanh nghiệp trong việc:
- **Quản lý thông tin khách hàng tập trung (Customer 360):** Lưu trữ hồ sơ, lịch sử tương tác đa kênh (Web, Zalo, Facebook, Instagram).
- **Hỗ trợ bán hàng (Sales):** Quản lý quy trình từ Lead/Cơ hội bán hàng (Opportunity Kanban) -> Báo giá (Quotation) -> Đơn hàng (Sales Order) -> Bảo hành (Warranty).
- **Chăm sóc khách hàng (Ticketing & Helpdesk):** Hệ thống Ticket hỗ trợ đa kênh, có phân công xử lý (Assign), trao đổi nội bộ và đo lường mức độ hài lòng (CSAT/NPS).
- **Quản lý sản phẩm & Tồn kho:** Danh mục sản phẩm, theo dõi biến động giá và tồn kho.
- **Vận hành nội bộ:** Quản lý ca trực (Shifts) của nhân viên (Agent), ghi nhận lịch sử hệ thống (Audit Logs).

## 3. Kiến trúc Công nghệ (Tech Stack)
Theo phân tích cấu trúc mã nguồn tại thư mục `backend/` và `frontend/`:
- **Ngôn ngữ lập trình Backend:** Python.
- **Web Framework:** Flask (Server-side rendering).
- **Frontend:** Jinja2 Templates (Render HTML/CSS/JS tĩnh), thư viện giao diện chuẩn (Bootstrap/Tailwind).
- **Cơ sở dữ liệu (Database):** Cơ sở dữ liệu quan hệ (Relational Database) sử dụng chuẩn MySQL/MariaDB (Engine InnoDB, charset utf8mb4) được khởi tạo thông qua script `init_db.py`.
- **Luồng xử lý (Architecture Pattern):** Monolithic Architecture. Client gửi HTTP Requests đến Flask Backend, Backend tương tác trực tiếp với Database layer (file `database/db.py`) và trả về (render) các template HTML tại thư mục `frontend/templates`.

## 4. Các Đối tượng / Tác nhân hệ thống (Actors)
Hệ thống phân chia quyền truy cập thành 3 nhóm tác nhân chính (dựa vào trường `role` trong bảng `users`):
1. **Admin:** Quản trị viên hệ thống, có toàn quyền truy cập Dashboard, cấu hình hệ thống, quản lý tài khoản User/Agent, xem mọi Audit logs, cấu hình Automation.
2. **Agent:** Nhân viên bán hàng / chăm sóc khách hàng. Có thể tạo mới khách hàng, xử lý Ticket được giao, tạo Báo giá/Đơn hàng, chấm công ca trực (Check-in).
3. **Customer:** Khách hàng (End-user). Có thể đăng nhập (Portal), tạo Ticket hỗ trợ, xem trạng thái Ticket, thực hiện đánh giá khảo sát (Survey).

## 5. Danh sách Phân hệ Chính (Key Modules)
Dựa vào kiến trúc thư mục template và routes:
1. **Module Authentication:** Đăng nhập, đăng ký, phân quyền (`login.html`, `register.html`).
2. **Module Dashboard & Analytics:** Báo cáo tổng quan, số liệu thống kê (`dashboard.html`).
3. **Module Customer 360:** Hồ sơ khách hàng, sở thích, lịch sử tương tác (`customer_360.html`, `customers.html`).
4. **Module Ticketing & Support:** Quản lý vé hỗ trợ, trao đổi trên vé, đánh giá CSAT/NPS (`tickets.html`, `ticket_detail.html`, `ticket_create.html`).
5. **Module Sales Pipeline & Orders:** Quản lý cơ hội, báo giá, đơn hàng, bảo hành (`kanban.html`, `quotations.html`, `sales_orders.html`, `warranties.html`).
6. **Module Products:** Danh sách, chi tiết, so sánh sản phẩm (`products.html`, `product_detail.html`, `product_compare.html`).
7. **Module Omnichannel & Telephony:** Trò chuyện đa kênh, lịch sử cuộc gọi (`inbox.html`, `telephony.html`).
8. **Module Automation & Internal Tools:** Auto-reply, quản lý ca làm việc, quản lý người dùng, nhật ký hoạt động (`automation.html`, `shifts.html`, `audit_logs.html`, `users.html`).
