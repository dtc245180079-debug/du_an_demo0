# TÀI LIỆU 04: OBJECT / DATA MODEL (MÔ HÌNH DỮ LIỆU)

Dựa trên cấu trúc thực tế của script `init_db.py`, Cơ sở dữ liệu của CRM được chia thành 24 bảng chính, phân cụm theo 6 nhóm nghiệp vụ (Domains) như sau:

## 1. Domain User & Authentication (Phân quyền & Định danh)
- **`users`**: Bảng quản lý người dùng (Admin, Agent, Customer).
  + Khóa chính: `id`
  + Trường nổi bật: `username`, `email`, `password_hash`, `role` (Admin/Agent/Customer).
- **`work_shifts`**: Quản lý ca trực nhân viên.
  + Khóa phụ: `agent_id` (Nối tới `users.id`).
- **`audit_logs`**: Nhật ký hoạt động của user trên hệ thống.

## 2. Domain Customer (Hồ sơ Khách hàng)
- **`customers`**: Hồ sơ khách hàng (Customer 360).
  + Trường nổi bật: `full_name`, `phone`, `email`, `zalo_id`, `fb_id`, `member_rank`.
- **`customer_preferences`**: Lưu nhu cầu, sở thích của khách hàng để phục vụ tư vấn bán hàng.
  + Khóa phụ: `customer_id` (Unique).

## 3. Domain Ticketing & Support (Hệ thống Hỗ trợ)
- **`tickets`**: Vé yêu cầu hỗ trợ.
  + Trạng thái (`status`): open, in-progress, resolved...
  + Khóa phụ: `customer_id`, `assigned_agent_id`.
- **`ticket_messages`**: Lịch sử trao đổi nội dung giữa Agent và Customer trong Ticket.
- **`ticket_surveys`**: Kết quả đánh giá dịch vụ CSAT (rating_csat) & NPS (score_nps).
- **`support_faqs`**: Kho dữ liệu FAQ giúp trả lời nhanh các lỗi thường gặp của khách hàng.

## 4. Domain Omnichannel (Giao tiếp Đa kênh)
- **`omnichannel_messages`**: Lưu trữ tin nhắn tập trung từ nhiều kênh (Zalo, Webchat...).
- **`auto_replies`**: Cấu hình quy tắc trả lời tự động.
- **`call_logs`**: Lịch sử các cuộc gọi điện thoại (Có URL file ghi âm).

## 5. Domain Product Catalog (Danh mục Sản phẩm)
- **`phone_products`**: Thông tin chung của sản phẩm (Tên, hãng, cấu hình, giá niêm yết, tồn kho).
- **`phone_variants`**: Các biến thể sản phẩm (Màu sắc, Dung lượng, SKU, giá chênh lệch).
  + Khóa phụ: `product_id`.
- **`product_price_history`**: Lưu vết lịch sử mỗi lần cập nhật giá của admin.
- **`promotions`**: Các chương trình khuyến mãi/Mã giảm giá đang áp dụng.

## 6. Domain Sales Pipeline (Cơ hội, Báo giá, Đơn hàng & Bảo hành)
- **`sales_opportunities`**: Cơ hội bán hàng Kanban. Các stage (Lead, đàm phán, chốt...).
- **`quotations`**: Báo giá gửi khách hàng (Có `total_listed_amount`, `discount_amount`, `final_amount`).
- **`sales_orders`**: Đơn hàng chốt sales. 
  + Trạng thái: new, processing, completed...
  + Lịch sử giao hàng: `shipping_carrier`, `shipping_code`.
- **`order_status_history`**: Lưu vết chi tiết lịch sử chuyển đổi trạng thái của Đơn hàng.
- **`warranties`**: Phiếu bảo hành (Liên kết `order_id` và `imei_serial`).
- **`followup_reminders`**: Lịch nhắc nhở chăm sóc sau mua hàng.

## Các Mối Quan Hệ Chính (Relationships)
- **1 - N:** Một `users` (Role: Agent) có thể được assign nhiều `tickets` và nhiều `sales_opportunities`.
- **1 - N:** Một `customers` có thể tạo ra nhiều `tickets`, nhiều `quotations`, và nhiều `sales_orders`.
- **1 - N:** Một `phone_products` có thể có nhiều `phone_variants` (Cùng mẫu điện thoại nhưng khác màu sắc, dung lượng).
- **1 - 1:** Mỗi `tickets` chỉ có tối đa một đánh giá `ticket_surveys`. Mỗi `customers` chỉ có một `customer_preferences`.
