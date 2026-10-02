# TÀI LIỆU 07: USER GUIDE & USER STORIES (KỊCH BẢN SỬ DỤNG)

Tài liệu này mô tả các Kịch bản sử dụng (User Stories) từ góc độ của 3 nhóm người dùng chính trên hệ thống: Khách hàng (Customer), Nhân viên hỗ trợ/Bán hàng (Agent), và Quản trị viên (Admin).

---

## 1. Dành cho Khách hàng (Customer)

### US-C01: Tra cứu FAQ (Trang chủ)
- **Kịch bản:** Khi tôi truy cập trang chủ, tôi muốn tìm kiếm nhanh các câu hỏi thường gặp (FAQ) và cách khắc phục lỗi điện thoại bằng thanh tìm kiếm, để tự xử lý vấn đề mà không cần chờ Agent. Hoặc tôi có thể dùng Chatbot AI RAG để hỏi trực tiếp.

### US-C02: Đăng ký và Đăng nhập
- **Kịch bản:** Là một khách hàng mới, tôi muốn đăng ký tài khoản qua số điện thoại/email. Đăng nhập thành công, tôi được chuyển hướng vào khu vực Khách hàng (`Portal`).

### US-C03: Yêu cầu Hỗ trợ (Tạo Ticket)
- **Kịch bản:** Khi điện thoại bị hỏng hoặc cần tư vấn, tôi đăng nhập vào Portal và tạo một Ticket hỗ trợ. Tôi điền Tiêu đề, Mức độ ưu tiên và Nội dung cần hỏi. Sau khi gửi, hệ thống cung cấp cho tôi một Mã Ticket.

### US-C04: Theo dõi và Tương tác Ticket
- **Kịch bản:** Tôi muốn xem danh sách các Ticket tôi đã gửi. Khi click vào một Ticket cụ thể, tôi xem được Agent nào đang xử lý, và tôi có thể chat trực tiếp với Agent ngay tại màn hình này.

### US-C05: Đánh giá Chất lượng dịch vụ (Survey)
- **Kịch bản:** Khi Agent báo đã giải quyết xong vấn đề (Ticket chuyển sang trạng thái Resolved), hệ thống hiển thị form CSAT/NPS. Tôi điền số điểm (1-5 sao hoặc 0-10) kèm lời nhắn để phản hồi về chất lượng dịch vụ.

---

## 2. Dành cho Nhân viên (Agent)

### US-A01: Check-in Ca làm việc
- **Kịch bản:** Vào đầu ngày làm việc, sau khi đăng nhập, tôi mở màn hình `Quản lý Ca trực (Shifts)` và bấm "Check-in" để hệ thống ghi nhận tôi bắt đầu làm việc và sẵn sàng nhận Ticket.

### US-A02: Xử lý Ticket Hỗ trợ
- **Kịch bản:** Tại màn hình `Danh sách Ticket`, tôi có thể lọc ra các Ticket trạng thái "Open" và tự phân công cho mình (Assign to me). Mở Ticket ra, tôi chat hướng dẫn cho Khách hàng. Khi xong việc, tôi bấm nút chuyển trạng thái thành "Resolved".

### US-A03: Quản lý Hồ sơ Khách hàng (Customer 360)
- **Kịch bản:** Khi đang chat với một Khách, tôi có thể bấm vào tên Khách hàng để mở `Customer 360`. Tại đây tôi thấy toàn bộ Lịch sử mua hàng, Sở thích, Ticket cũ... từ đó tôi đưa ra cách tư vấn hoặc báo giá phù hợp nhất.

### US-A04: Xử lý Kênh giao tiếp đa chiều (Omnichannel Inbox)
- **Kịch bản:** Tại màn hình `Inbox`, tôi nhận được tin nhắn từ cả Zalo và Webchat cùng một lúc. Tôi chỉ việc gõ phản hồi tại khung chat trên CRM, hệ thống tự động gửi tin nhắn về đúng nền tảng (Zalo/Web) của khách.

### US-A05: Quy trình Bán hàng (Sales & Orders)
- **Kịch bản:** Khi thuyết phục được khách mua một dòng điện thoại mới:
  1. Tôi tạo một Cơ hội (Opportunity Kanban).
  2. Kéo thả cơ hội sang cột "Đàm phán".
  3. Tạo "Báo giá" (Quotation) chứa thông số RAM/ROM, giá gốc và mã giảm giá.
  4. Nếu khách chốt, tôi chuyển Báo giá thành "Đơn hàng" (Sales Order).

---

## 3. Dành cho Quản trị viên (Admin)

### US-AD01: Báo cáo Tổng quan (Dashboard)
- **Kịch bản:** Đăng nhập vào hệ thống, tôi xem ngay trang `Dashboard` để theo dõi biểu đồ thống kê: Có bao nhiêu Ticket đang tồn đọng, Tổng doanh thu hôm nay là bao nhiêu, và SLA của các Agent.

### US-AD02: Quản lý Danh mục Sản phẩm & Giá
- **Kịch bản:** Mở trang `Sản phẩm`, tôi có quyền thêm mới một điện thoại. Khi thay đổi giá bán (ví dụ: iPhone 15 giảm giá), tôi cập nhật giá và hệ thống lưu vết sự thay đổi đó vào `Lịch sử giá (Price History)`.

### US-AD03: Thiết lập Automation (Trả lời tự động)
- **Kịch bản:** Mở trang `Automation`, tôi tạo một quy tắc: Nếu khách nhắn từ khóa "bảo hành", hệ thống tự động gửi lại tin nhắn "Thời gian bảo hành máy là 12 tháng".

### US-AD04: Kiểm toán Hệ thống (Audit Logs)
- **Kịch bản:** Khi có sự cố dữ liệu (ví dụ: một Đơn hàng tự nhiên bị Hủy), tôi mở trang `Audit Logs`, tìm theo ID Đơn hàng để truy vết chính xác Agent nào đã thao tác Hủy đơn vào thời gian nào.
