# TÀI LIỆU 06: SCREEN SPECIFICATIONS (ĐẶC TẢ MÀN HÌNH VÀ LUỒNG GIAO DIỆN)

Hệ thống được thiết kế theo mô hình Server-side Rendering với Jinja2 (`frontend/templates/`). Cấu trúc giao diện được kế thừa từ Layout chuẩn.

## 1. Cấu trúc Layout Chung
- **`base.html`**: Layout gốc của hệ thống (chứa thẻ `<head>`, thanh Navbar/Sidebar dùng chung, thư viện CSS/JS cốt lõi, cơ chế hiển thị tin nhắn thông báo `flash` của Flask).
- **Navigation Flow:** 
  - Khách chưa đăng nhập: Xem được trang `faqs.html`, `login.html`, `register.html`.
  - Customer đăng nhập: Điều hướng tới `portal.html`.
  - Agent/Admin đăng nhập: Điều hướng tới `dashboard.html`.

## 2. Nhóm Màn hình Đăng nhập & Portal Khách hàng
- **`login.html` & `register.html`**: Form nhập liệu đăng nhập / đăng ký. Có nút chuyển đổi qua lại giữa 2 form.
- **`portal.html`**: Màn hình tổng quan dành riêng cho Khách hàng. Hiển thị danh sách Ticket họ đã gửi và trạng thái mua hàng.
- **`portal_new_ticket.html`**: Form để Customer tạo Ticket mới.
- **`portal_ticket_chat.html`**: Khách hàng xem chi tiết Ticket và chat trực tiếp với Agent hỗ trợ.
- **`portal_survey.html`**: Form khảo sát đánh giá độ hài lòng (CSAT & NPS) hiển thị khi Ticket được đóng (`resolved`).

## 3. Nhóm Màn hình Dành cho Agent/Admin (Nghiệp vụ nội bộ)
- **`dashboard.html`**: Bảng điều khiển chính, chứa các biểu đồ thống kê (Tickets, Doanh thu, Đơn hàng) dành cho Admin/Agent.
- **`customers.html` & `customer_360.html`**: 
  - *customers*: Danh sách khách hàng (Dạng bảng, có công cụ lọc/tìm kiếm).
  - *customer_360*: Màn hình chi tiết của 1 khách hàng. Bố cục chia nhiều tab: Thông tin chung, Lịch sử mua hàng, Ticket liên quan, Nhắc nhở chăm sóc (Follow-up).
- **`tickets.html` & `ticket_detail.html`**:
  - *tickets*: Bảng danh sách Ticket toàn hệ thống (Dành cho Agent/Admin xử lý).
  - *ticket_detail*: Hiển thị chi tiết nội dung khiếu nại/hỗ trợ, form chat nội bộ, và nút chuyển trạng thái Ticket (Đóng/Mở). Cửa sổ chat chiếm phần lớn không gian.
- **`kanban.html`**: Màn hình dạng bảng kéo thả (Trello-like) các cột tương ứng với các trạng thái của Sales Opportunity.
- **`inbox.html`**: Màn hình chat tổng hợp (Omnichannel). Có danh sách hội thoại bên trái, khung chat bên phải.
- **`telephony.html`**: Giao diện tổng đài Softphone giả lập. Gồm bàn phím số (Numpad) để gọi điện thoại và danh sách lịch sử Call logs bên dưới.

## 4. Nhóm Màn hình Sản phẩm & Bán hàng (Sales & Product)
- **`products.html` & `product_detail.html`**: Màn hình lưới (Grid) hiển thị thẻ sản phẩm (Điện thoại). Trang chi tiết cho phép xem các biến thể (RAM/ROM) và tồn kho.
- **`product_compare.html`**: Giao diện chia cột hiển thị song song thông số kỹ thuật (Màn hình, Chip, RAM, Camera) giữa 2-3 sản phẩm.
- **`quotations.html` & `quotation_create.html`**: Bảng danh sách báo giá. Form tạo báo giá gồm bảng động để thêm/bớt sản phẩm, tự động tính tổng tiền.
- **`sales_orders.html` & `sales_order_detail.html`**: Bảng quản lý đơn hàng. Chi tiết đơn hàng cho phép cập nhật trạng thái Giao hàng và Thanh toán.
- **`warranties.html`**: Quản lý phiếu bảo hành, tra cứu qua IMEI hoặc mã đơn hàng.

## 5. Nhóm Màn hình Quản trị & Công cụ (Chỉ Admin / Agent)
- **`automation.html`**: Form cấu hình các luồng tự động (Auto-reply từ khóa).
- **`shifts.html`**: Giao diện quản lý ca trực, nút Check-in/Check-out lớn dành cho Agent.
- **`audit_logs.html`**: Bảng lịch sử các hành động hệ thống (Chỉ Admin xem được), có phân trang và lọc theo ngày.
- **`users.html`**: Quản lý danh sách nhân sự/Tài khoản trên hệ thống (Phân quyền).
