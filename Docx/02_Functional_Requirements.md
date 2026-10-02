# TÀI LIỆU 02: FUNCTIONAL REQUIREMENTS (YÊU CẦU CHỨC NĂNG)

Dựa vào mã nguồn thực tế (các routes Flask và templates), dưới đây là danh sách các yêu cầu chức năng (FR) chi tiết mà hệ thống đang đáp ứng.

## 1. FR01 - Quản lý Định danh & Truy cập (Authentication/Authorization)
- **FR01.1 Đăng nhập/Đăng ký:** Người dùng (Agent/Customer) có thể đăng ký tài khoản mới và đăng nhập thông qua Username/Email & Password (mật khẩu được băm `password_hash`).
- **FR01.2 Phân quyền (Role-based Access):** Hệ thống kiểm tra vai trò (Role: Admin, Agent, Customer) để điều hướng màn hình (Ví dụ: Customer vào `portal.html`, Admin/Agent vào `dashboard.html`).
- **FR01.3 Quản lý Tài khoản (Dành cho Admin):** Admin có thể xem danh sách tài khoản (`users.html`), cập nhật trạng thái hoạt động (`is_active`) và vai trò (`role`).

## 2. FR02 - Quản lý Hồ sơ Khách hàng (Customer 360)
- **FR02.1 Thêm mới/Cập nhật thông tin:** Cho phép lưu trữ Tên, Số điện thoại, Email, Zalo ID, Facebook ID, Instagram ID.
- **FR02.2 Hạng thành viên (Membership Rank):** Theo dõi hạng khách hàng (Mặc định: 'Bạc').
- **FR02.3 Xem Hồ sơ 360 (Customer 360 View):** Màn hình hiển thị toàn bộ vòng đời tương tác của khách hàng: Thông tin cá nhân, Lịch sử mua hàng (Orders), Ticket đã tạo, Khảo sát đã làm, Sở thích và ghi chú.

## 3. FR03 - Hệ thống Hỗ trợ Khách hàng (Ticketing System)
- **FR03.1 Tạo Ticket Hỗ trợ:** Customer (qua Portal) hoặc Agent (qua Dashboard) có thể tạo Ticket với các thông tin: Tiêu đề (Subject), Kênh (Channel - web/zalo/fb), Độ ưu tiên (Priority - medium/high).
- **FR03.2 Xử lý và Phân công (Assign):** Ticket có mã duy nhất (ticket_code). Admin/Quản lý có thể gán (Assign) Ticket cho một Agent cụ thể.
- **FR03.3 Trao đổi trong Ticket:** Agent và Customer có thể chat qua lại bên trong Ticket (dữ liệu lưu vào `ticket_messages`).
- **FR03.4 Đánh giá dịch vụ (CSAT & NPS):** Khi Ticket hoàn tất (`resolved_at`), khách hàng có thể điền Survey đánh giá điểm CSAT (1-5) và NPS (0-10) kèm theo phản hồi.

## 4. FR04 - Quản lý Bán hàng & Cơ hội (Sales Pipeline)
- **FR04.1 Quản lý Cơ hội Kanban (Opportunities):** Hiển thị các cơ hội bán hàng dưới dạng bảng Kanban. Cho phép chuyển trạng thái cơ hội (Lead -> Đang tiếp cận -> Chốt sales).
- **FR04.2 Tạo & Quản lý Báo giá (Quotations):** Agent có thể tạo báo giá (`quotation_create.html`), thêm các sản phẩm, xem tổng tiền, thay đổi trạng thái (draft/sent/accepted/rejected).
- **FR04.3 Tạo & Quản lý Đơn hàng (Sales Orders):** Chuyển đổi báo giá thành Đơn hàng. Quản lý trạng thái đơn (pending, processing, completed, cancelled) và lịch sử thay đổi trạng thái (`order_status_history`).
- **FR04.4 Quản lý Bảo hành (Warranties):** Hệ thống cho phép tạo và tra cứu phiếu bảo hành liên kết với Đơn hàng / IMEI sản phẩm.

## 5. FR05 - Quản lý Sản phẩm (Products)
- **FR05.1 Danh mục sản phẩm:** Hiển thị danh sách điện thoại / sản phẩm. Có lưu thông tin Tên, Slug, Thương hiệu, Cấu hình cơ bản.
- **FR05.2 Quản lý Phiên bản (Variants) & Tồn kho:** Một sản phẩm có nhiều phiên bản (Ví dụ: RAM/ROM/Màu sắc), mỗi phiên bản có Giá và Số lượng tồn kho (Stock). Cập nhật tồn kho tự động.
- **FR05.3 So sánh & Lịch sử giá:** Tính năng so sánh sản phẩm (`product_compare.html`) và biểu đồ/bảng xem biến động lịch sử giá của sản phẩm (`price_history`).

## 6. FR06 - Tương tác Đa kênh & Tổng đài (Omnichannel & Telephony)
- **FR06.1 Hộp thư tập trung (Inbox):** Màn hình (`inbox.html`) gom chung các hội thoại từ nhiều kênh (Zalo, Webchat) để Agent xử lý tập trung.
- **FR06.2 Lưu lịch sử cuộc gọi (Call logs):** Ghi nhận thông tin cuộc gọi (Incoming/Outgoing), thời lượng, trạng thái, ghi âm (nếu có) vào màn hình `telephony.html`.

## 7. FR07 - Tự động hóa & Quản lý nội bộ (Automation & Internal Tools)
- **FR07.1 Trả lời tự động (Auto-replies):** Thiết lập quy tắc (Rules) theo từ khóa để hệ thống tự động phản hồi (`automation.html`).
- **FR07.2 Nhắc nhở theo dõi (Follow-up Reminders):** Hệ thống lưu trữ và hiển thị các nhắc nhở công việc/liên hệ lại khách hàng cho Agent.
- **FR07.3 Quản lý Ca trực (Work Shifts):** Agent phải check-in để bắt đầu ca làm việc (`shifts.html`).
- **FR07.4 Nhật ký hệ thống (Audit Logs):** Ghi lại mọi hành động quan trọng (VD: tạo đơn, thay đổi trạng thái ticket) để Admin kiểm toán (`audit_logs.html`).
- **FR07.5 Bảng điều khiển (Dashboard):** Hiển thị số liệu thống kê (Stats, Analytics) tổng quan cho doanh nghiệp.
