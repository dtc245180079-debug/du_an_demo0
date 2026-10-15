Chào bạn, với tư cách là Senior Business Analyst & System Architect, tôi đã phân tích yêu cầu về tính năng **"Ví Voucher & Tự động áp dụng mã giảm giá"** cho ứng dụng ngân hàng của bạn. Dưới đây là bản phân tích chi tiết:

---

### 1. Tóm tắt yêu cầu (Overview)
- **Mục tiêu:** Xây dựng hệ thống quản lý Voucher tập trung (Ví Voucher) và thuật toán gợi ý/áp dụng mã giảm giá thông minh (Best-fit algorithm) cho các dịch vụ thanh toán hóa đơn (Điện, Nước, Internet).
- **Phạm vi chính:** 
    - Quản lý vòng đời Voucher (Lưu, Xem, Hết hạn).
    - Thuật toán tối ưu hóa (Auto-apply).
    - Tích hợp luồng thanh toán (Payment Gateway integration).

---

### 2. Điểm mờ thấu & Trường hợp biên (Ambiguities & Edge Cases)

* **[Vấn đề 1 - Thuật toán tối ưu (Best-fit Logic)]:**
    - *Điểm chưa rõ:* Thế nào là "tối ưu nhất"? Là giảm số tiền tuyệt đối lớn nhất, hay giảm theo tỷ lệ %, hay ưu tiên voucher sắp hết hạn?
    - *Đề xuất xử lý:* Định nghĩa ưu tiên: (1) Giảm số tiền lớn nhất -> (2) Nếu bằng nhau, chọn voucher có hạn sử dụng gần nhất. Cần có cơ chế "Override" để người dùng chọn thủ công nếu muốn.
* **[Vấn đề 2 - Xử lý đồng thời (Race Condition)]:**
    - *Điểm chưa rõ:* Điều gì xảy ra nếu 2 người dùng cùng thanh toán và chỉ còn 1 voucher giới hạn số lượng (Limited quantity)?
    - *Đề xuất xử lý:* Sử dụng cơ chế **Optimistic Locking** hoặc **Redis Atomic Counter** để trừ số lượng voucher ngay khi người dùng nhấn "Thanh toán" (trước khi trừ tiền thực tế) và hoàn trả nếu giao dịch thất bại.
* **[Vấn đề 3 - Trạng thái giao dịch lỗi (Transaction Failures)]:**
    - *Điểm chưa rõ:* Nếu thanh toán hóa đơn thất bại (do lỗi hệ thống nhà cung cấp điện/nước), voucher đã áp dụng có được hoàn lại không?
    - *Đề xuất xử lý:* Xây dựng cơ chế **Saga Pattern** hoặc **Transaction Rollback**. Nếu giao dịch thanh toán trả về trạng thái `FAILED`, hệ thống tự động hoàn lại trạng thái `ACTIVE` cho voucher.
* **[Vấn đề 4 - Bảo mật & Gian lận (Fraud Prevention)]:**
    - *Điểm chưa rõ:* Làm sao ngăn chặn việc lạm dụng voucher bằng cách tạo nhiều tài khoản hoặc can thiệp API?
    - *Đề xuất xử lý:* Áp dụng giới hạn theo `Device ID` hoặc `User ID`. Validate điều kiện voucher tại phía Server (Backend) ngay trước khi thực hiện lệnh trừ tiền.

---

### 3. Phân rã công việc (Task Decomposition Tree)

#### [Backend / Database / API]
- **Database Schema Design:** Thiết kế bảng `Vouchers` (Master data), `User_Vouchers` (Mapping user-voucher), và `Transaction_Voucher_Log`.
- **Voucher Engine API:** Xây dựng API `GET /vouchers/eligible` (lấy danh sách voucher hợp lệ cho hóa đơn) và `POST /vouchers/apply` (validate và lock voucher).
- **Optimization Algorithm:** Phát triển logic tính toán số tiền giảm giá tối ưu dựa trên danh sách voucher khả dụng.
- **Rollback Service:** Xây dựng cơ chế hoàn trả voucher khi giao dịch thanh toán thất bại.

#### [Frontend / UI / UX]
- **Voucher Wallet Screen:** Màn hình hiển thị danh sách voucher (Đang dùng, Đã dùng, Hết hạn).
- **Payment Checkout Integration:** 
    - Hiển thị "Voucher tốt nhất" mặc định tại màn hình thanh toán.
    - Cho phép người dùng nhấn "Thay đổi" để chọn voucher khác.
- **Feedback UI:** Thông báo rõ ràng số tiền được giảm sau khi áp dụng voucher.

#### [Third-party Integration / Security]
- **Payment Gateway Hook:** Tích hợp logic áp dụng voucher vào luồng thanh toán hiện tại (trước bước xác thực OTP).
- **Audit Logging:** Ghi log chi tiết mỗi lần áp dụng voucher để phục vụ đối soát (Reconciliation) với nhà cung cấp dịch vụ.

#### [Testing & Quality Assurance]
- **Unit Test:** Kiểm tra logic tính toán giảm giá (đặc biệt là các trường hợp biên: hóa đơn nhỏ hơn giá trị voucher).
- **Load Test:** Giả lập hàng ngàn người dùng cùng áp dụng voucher trong các chiến dịch Flash Sale.
- **Integration Test:** Kiểm tra luồng hoàn trả voucher khi thanh toán thất bại.

---
*Bạn có muốn tôi đi sâu vào thiết kế Database Schema hoặc luồng Sequence Diagram cho tính năng này không?*