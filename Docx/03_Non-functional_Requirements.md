# TÀI LIỆU 03: NON-FUNCTIONAL REQUIREMENTS (YÊU CẦU PHI CHỨC NĂNG)

Dựa trên cấu trúc mã nguồn, cấu hình database và file cấu hình môi trường, hệ thống CRM đáp ứng các yêu cầu phi chức năng (NFR) sau:

## 1. Yêu cầu về Bảo mật (Security)
- **Mã hóa Mật khẩu:** Toàn bộ mật khẩu của người dùng không lưu dạng plaintext. Mã nguồn sử dụng hàm `generate_password_hash` với thuật toán `pbkdf2:sha256` của thư viện `werkzeug.security` (có thể kiểm chứng tại file `database/init_db.py`).
- **Quản lý Cấu hình (Environment Variables):** Các khóa bảo mật, chuỗi kết nối Database không được hardcode mà được lưu trữ trong file `.env` (qua thư viện `dotenv` trong `app.py`), đảm bảo tính ẩn danh cho thông tin nhạy cảm.
- **Quản lý Phiên bản (Session Management):** Hệ thống duy trì phiên đăng nhập người dùng thông qua `session` của Flask.

## 2. Yêu cầu về Lưu trữ và Toàn vẹn Dữ liệu (Data Integrity)
- **Storage Engine:** Database sử dụng `InnoDB`, hỗ trợ ACID transactions, giúp khóa dòng (row-level locking) và bảo vệ toàn vẹn dữ liệu khi có nhiều người dùng thao tác cùng lúc.
- **Charset & Collation:** Toàn bộ các bảng được cấu hình mặc định là `CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`, đảm bảo hỗ trợ đầy đủ tiếng Việt và các ký tự đặc biệt (emoji trong tin nhắn đa kênh).
- **Ràng buộc dữ liệu (Constraints):** Sử dụng ràng buộc `UNIQUE` cho các trường dữ liệu định danh (Username, Email, Ticket Code, Quote Code, Order Code, SKU...).
- **Tính lũy đẳng (Idempotency):** Có bảng `idempotent_keys` để tránh việc xử lý trùng lặp (ví dụ: tạo 2 đơn hàng giống hệt nhau khi người dùng bấm đúp chuột).

## 3. Yêu cầu về Hiệu năng (Performance & Optimization)
- **Đánh chỉ mục (Indexing):** Các trường thường xuyên được tìm kiếm hoặc lọc (như `phone`, `email`, `status`, `assigned_agent_id`, `customer_id`) đều được tạo `INDEX` (ví dụ: `idx_phone`, `idx_status`...) giúp truy xuất dữ liệu lớn nhanh chóng.
- **Backend Framework:** Sử dụng Flask nhẹ và tối ưu, dễ dàng deploy.

## 4. Yêu cầu về Tương thích và Giao diện (Usability/Compatibility)
- **Giao diện Web:** Ứng dụng chạy trên trình duyệt web, giao diện được render bằng Jinja2, sử dụng chuẩn HTML5. Không yêu cầu người dùng phải cài đặt phần mềm riêng.
- **Console Encoding:** Các cấu hình mã hóa console (`sys.stdout.reconfigure(encoding="utf-8")`) ở backend đảm bảo máy chủ không bị lỗi crash `UnicodeEncodeError` khi in các log có dấu tiếng Việt.
- **Tính khả dụng (Availability):** Cơ chế Catch Exceptions toàn cục (`try...except`) trong các module database hạn chế tối đa việc ứng dụng bị sập khi gặp lỗi kết nối.
