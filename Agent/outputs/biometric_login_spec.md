Chào bạn, với tư cách là Senior Business Analyst và System Architect, tôi đã phân tích yêu cầu về việc tích hợp **Đăng nhập sinh trắc học (Biometric Authentication)** và **Xác thực OTP qua Zalo** cho ứng dụng ngân hàng. Dưới đây là bản phân tích chi tiết:

---

### 1. Tóm tắt yêu cầu (Overview)
- **Mục tiêu:** Nâng cao trải nghiệm người dùng (UX) thông qua đăng nhập nhanh (Biometrics) và tối ưu hóa chi phí/tăng tính bảo mật thông qua kênh xác thực OTP thay thế (Zalo thay vì SMS truyền thống).
- **Phạm vi chính:** 
    - Tích hợp Biometric API (Local Authentication) trên iOS/Android.
    - Kết nối Zalo Cloud API (ZCA) để gửi OTP.
    - Xây dựng cơ chế fallback (dự phòng) khi sinh trắc học hoặc Zalo gặp lỗi.

---

### 2. Điểm mờ thấu & Trường hợp biên (Ambiguities & Edge Cases)

* **[Vấn đề 1 - Bảo mật & Tính toàn vẹn của Biometrics]:**
    - *Điểm chưa rõ:* Làm thế nào để đảm bảo tính toàn vẹn khi người dùng thay đổi/thêm vân tay mới vào thiết bị?
    - *Đề xuất xử lý:* Sử dụng **KeyStore (Android) / Keychain (iOS)** để lưu trữ token xác thực. Khi có vân tay mới được thêm vào thiết bị, hệ thống phải tự động hủy (invalidate) token cũ và yêu cầu người dùng nhập lại mật khẩu/PIN để kích hoạt lại sinh trắc học.
* **[Vấn đề 2 - Độ tin cậy của Zalo OTP]:**
    - *Điểm chưa rõ:* Điều gì xảy ra nếu người dùng không có kết nối internet hoặc không cài Zalo?
    - *Đề xuất xử lý:* Thiết lập cơ chế **Fallback tự động**: Nếu Zalo API trả về lỗi hoặc timeout sau X giây, hệ thống phải tự động chuyển sang gửi SMS truyền thống hoặc gọi điện thoại (Voice OTP).
* **[Vấn đề 3 - Xử lý đồng thời & Race Condition]:**
    - *Điểm chưa rõ:* Người dùng có thể yêu cầu gửi lại OTP liên tục (spam).
    - *Đề xuất xử lý:* Áp dụng **Rate Limiting** ở phía Backend (ví dụ: 60s/lần) và hiển thị bộ đếm ngược (countdown) ở phía Frontend để ngăn chặn việc spam request.
* **[Vấn đề 4 - Trải nghiệm người dùng (UX)]:**
    - *Điểm chưa rõ:* Làm sao để xử lý khi thiết bị không hỗ trợ sinh trắc học hoặc người dùng từ chối cấp quyền?
    - *Đề xuất xử lý:* Kiểm tra khả năng hỗ trợ của thiết bị ngay khi khởi tạo app. Nếu không hỗ trợ, ẩn tính năng này và mặc định sử dụng phương thức đăng nhập bằng PIN/Password.

---

### 3. Phân rã công việc (Task Decomposition Tree)

#### **[Backend / Database / API]**
- **Task 1: Thiết kế API Gateway cho Zalo OTP:** Tích hợp Zalo Cloud API, quản lý template tin nhắn và log trạng thái gửi OTP.
- **Task 2: Cơ chế Fallback:** Xây dựng logic chuyển đổi giữa Zalo OTP -> SMS OTP khi có lỗi.
- **Task 3: Quản lý Session & Biometric Token:** API xác thực token sinh trắc học, đảm bảo tính duy nhất cho mỗi thiết bị (Device Binding).
- **Task 4: Rate Limiting & Security:** Cấu hình giới hạn số lần gửi OTP và thời gian hiệu lực của mã.

#### **[Frontend / UI / UX]**
- **Task 5: Tích hợp Biometric SDK:** Triển khai Local Authentication (FaceID/TouchID/Fingerprint) trên React Native/Flutter/Native.
- **Task 6: UI/UX Flow:** Thiết kế màn hình bật/tắt sinh trắc học, màn hình nhập OTP với bộ đếm ngược và nút "Gửi lại mã".
- **Task 7: Xử lý trạng thái lỗi:** Hiển thị thông báo thân thiện khi sinh trắc học thất bại hoặc Zalo OTP không gửi được.

#### **[Third-party Integration / Security]**
- **Task 8: Cấu hình Zalo Business Account:** Đăng ký và cấu hình Zalo Cloud API, phê duyệt template tin nhắn OTP với Zalo.
- **Task 9: Mã hóa dữ liệu:** Đảm bảo các token sinh trắc học được lưu trữ an toàn trong Secure Enclave/Keystore.

#### **[Testing & Quality Assurance]**
- **Task 10: Kiểm thử thiết bị:** Test trên nhiều dòng máy (iOS/Android) với các phiên bản OS khác nhau.
- **Task 11: Kiểm thử luồng ngoại lệ:** Test kịch bản mất mạng, kịch bản người dùng thêm vân tay mới, kịch bản Zalo API bị down.
- **Task 12: Security Audit:** Kiểm tra lỗ hổng bảo mật liên quan đến việc bypass sinh trắc học.

---
*Bạn có muốn tôi đi sâu vào thiết kế Database Schema cho việc quản lý thiết bị (Device Binding) hay cấu trúc API cho Zalo OTP không?*