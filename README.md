# HỆ THỐNG CRM & CHĂM SÓC KHÁCH HÀNG ĐA KÊNH (AI POWERED)

Hệ thống quản lý quan hệ khách hàng (CRM) và chăm sóc khách hàng đa kênh toàn diện, tích hợp Trợ lý Trí tuệ Nhân tạo (Gemini / OpenAI), Hộp thư hợp nhất đa kênh, Customer 360, Tra cứu đơn hàng KiotViet/Sapo/Lazada, Vận chuyển GHN/GHTK, và Tổng đài Softphone Twilio Voice trên trình duyệt.

---

## 🌟 TỔNG QUAN TÍNH NĂNG ĐÃ TRIỂN KHAI

### 1. Tài khoản và Phân quyền (RBAC)
- **Đăng ký, Đăng nhập, Đăng xuất:** Bảo mật phiên làm việc bằng cookie session an toàn.
- **Mật khẩu an toàn:** Băm mật khẩu bằng thuật toán chuẩn `pbkdf2:sha256`.
- **Phân quyền 3 cấp độ:**
  - **Khách hàng (`customer`):** Cổng hỗ trợ khách hàng riêng (`/portal`), gửi yêu cầu hỗ trợ mới, theo dõi trạng thái ticket, xem lịch sử đơn hàng và đánh giá CSAT/NPS sau khi xử lý.
  - **Nhân viên (`agent`):** Không gian làm việc CSKH (`/dashboard`), xử lý và phân công tickets (`/tickets`), hộp thư đa kênh (`/inbox`), tra cứu hồ sơ Customer 360 (`/customers`), quản lý ca trực cá nhân (`/shifts`), cơ hội bán hàng Kanban (`/kanban`) và sử dụng Softphone gọi điện trực tiếp trên trình duyệt.
  - **Quản trị viên (`admin`):** Toàn quyền truy cập tất cả màn hình, quản trị tài khoản & phân quyền (`/users`), xếp ca trực cho nhân viên, cấu hình kịch bản tự động hóa (`/automation`) và theo dõi nhật ký kiểm toán hệ thống (`/audit-logs`).

### 2. Quản lý Khách hàng & Phiếu Hỗ Trợ (Tickets & Customer 360)
- **Luồng Ticket hoàn chỉnh:** Tạo phiếu với mã tự động (VD: `TK-202610-8832`), phân loại mức độ ưu tiên, cập nhật trạng thái (`open`, `in_progress`, `resolved`, `closed`).
- **Trao đổi trực tiếp:** Luồng hội thoại 2 chiều giữa khách hàng và nhân viên, hỗ trợ tin nhắn hệ thống và AI.
- **Trang Customer 360:**
  - Tổng hợp hồ sơ định danh, SĐT, Email, Zalo ID, Facebook ID và Hạng thành viên (Đồng, Bạc, Vàng VIP, Kim Cương).
  - Tra cứu và liên kết tất cả phiếu hỗ trợ của khách hàng.
  - Ghi chú nội bộ cho nhân viên CSKH.
  - Tích hợp nút gọi điện Softphone trực tiếp đến số điện thoại khách hàng.

### 3. Hộp Thư Đa Kênh Hợp Nhất (Omnichannel Inbox)
- **Hợp nhất 5 kênh vào một Inbox duy nhất:** Zalo OA, Facebook Messenger, Instagram Direct, Live Chat Web và Email.
- **Chuẩn hóa thông điệp (`UnifiedMessage`):** Mọi tin nhắn từ các nền tảng khác nhau đều được quy chuẩn cấu trúc, liên kết tự động với hồ sơ Customer 360 theo SĐT hoặc Social ID.
- **Phản hồi qua kênh tương ứng:** Trả lời trực tiếp từ giao diện CRM, hệ thống tự động điều phối gửi ra đúng kênh của khách hàng (Zalo OA API, Email SMTP, Webchat...).
- **Chống trùng lặp sự kiện:** Bảng `idempotent_keys` đảm bảo mỗi sự kiện webhook chỉ được xử lý đúng 1 lần.
- **Widget Webchat nhúng:** Hỗ trợ nhúng ngoài qua URL `/webchat/embed` hoặc iframe, xác thực phiên bảo mật bằng JSON Web Token (JWT) và kiểm tra nguồn gốc tên miền cho phép (`ALLOWED_WEBCHAT_ORIGINS`).
- **Tích hợp Email:** Tiếp nhận thư đến qua SendGrid Inbound Parse Webhook (`/api/webhooks/email/inbound`) hoặc đọc qua giao thức IMAP; gửi thư trả lời qua SMTP.

### 4. AI và Tri thức Hỗ trợ Mở Rộng (Extensible AI & RAG)
- **Kiến trúc AI mở rộng:** Hỗ trợ đa nhà cung cấp thông qua biến môi trường `AI_PROVIDER`:
  - **Google Gemini:** `gemini-3.5-flash`, `gemini-3.8-flash` với bộ lọc tự động trích xuất thương hiệu và từ khóa.
  - **OpenAI:** Tương thích với `gpt-4o-mini`, `gpt-4o` hoặc các endpoint tương thích OpenAI.
  - **Mock / Offline Fallback:** Tự động chuyển mạch dự phòng thông minh khi mất kết nối mạng hoặc hết hạn mức API, đảm bảo chatbot và hệ thống CRM hoạt động liên tục 24/7.
- **Smart Reply cho nhân viên:** Tự động đề xuất 3 câu trả lời nhanh dựa trên nội dung câu hỏi của khách và cơ sở tri thức FAQs.
- **Giữ nguyên 100% chức năng FAQ ban đầu:** Giao diện quản lý FAQs (`/`, `/add`, `/edit/<id>`, `/delete/<id>`) và API chatbot `/api/chat` tiếp tục hoạt động mượt mà.

### 5. Dashboard, Ca Trực, Kanban & Nhật Ký Kiểm Toán
- **Dashboard trực quan:** Biểu đồ xu hướng doanh thu theo thời gian, biểu đồ tỷ lệ kênh hỗ trợ (sử dụng Chart.js), thống kê trạng thái ticket thời gian thực.
- **Quản lý ca trực (Work Shifts):** Lập lịch ca sáng, ca chiều, ca tối, ca đêm; nhân viên thực hiện check-in và check-out ca trực.
- **Bảng Kanban cơ hội bán hàng:** Theo dõi phễu bán hàng qua 6 giai đoạn (`Lead` → `Contacted` → `Proposal` → `Negotiation` → `Won` → `Lost`) kèm xác suất thành công và chuyển cột trực quan.
- **Nhật ký Audit (`audit_logs`):** Ghi vết đầy đủ mọi thao tác đăng nhập, sửa ticket, đổi trạng thái đơn hàng, xếp ca trực kèm địa chỉ IP và dấu thời gian.

### 6. Tự Động Hóa & Khảo Sát Đánh Giá
- **Kịch bản phản hồi tự động:** Cấu hình theo từng kênh hoặc toàn bộ: Lời chào (Greeting), Ngoài giờ làm việc (Out of office - sau 22h và trước 8h), Thông báo bận rộn (Busy).
- **Khảo sát CSAT & NPS:** Khi ticket được chuyển sang trạng thái `resolved` hoặc `closed`, hệ thống tự động gửi tin nhắn mời đánh giá chất lượng (CSAT 1-5 sao, NPS 0-10 điểm và nhận xét).
- **Idempotency bảo vệ:** Đảm bảo mỗi ticket chỉ phát sinh 1 lần gửi khảo sát dù nhân viên thao tác đóng nhiều lần.

### 7. Tích Hợp Đơn Hàng & Giao Vận
- **Tra cứu đơn hàng chỉ đọc (Read-only):** Hỗ trợ tra cứu theo số điện thoại từ KiotViet, Sapo và Lazada.
- **Bảo vệ dữ liệu cá nhân (PII):** Chỉ lưu trữ các trường thông tin cần thiết phục vụ hỗ trợ (Mã đơn, nguồn, tên khách, SĐT, danh sách sản phẩm, giá trị, trạng thái vận chuyển); không lưu địa chỉ chi tiết hoặc thông tin thanh toán nhạy cảm.
- **Làm mới vận đơn GHN & GHTK:** Hỗ trợ kiểm tra và làm mới trạng thái giao hàng tức thời qua nút bấm trên giao diện.
- **Webhook giao vận:** Tiếp nhận cập nhật giao vận từ GHN (`/api/webhooks/logistics/ghn`) và GHTK (`/api/webhooks/logistics/ghtk`), xác thực token/chữ ký HMAC SHA256 và loại bỏ sự kiện trùng lặp.

### 8. Tích Hợp Google OIDC & Twilio Voice Softphone
- **Google OpenID Connect:** Đăng nhập 1-click với Google, tự động xác minh điều kiện `email_verified == True`.
- **Softphone Twilio Voice trên trình duyệt:**
  - Bàn phím số gọi điện nhanh xuất hiện trực tiếp trên thanh điều hướng của nhân viên.
  - API cấp Twilio Voice JWT Access Token (`/api/telephony/token`).
  - Endpoint sinh TwiML XML cho cuộc gọi đi (`/api/telephony/twiml/outbound`) và cuộc gọi đến (`/api/telephony/twiml/inbound`).
  - Nhận webhook callback trạng thái cuộc gọi và lưu bản ghi nhật ký cuộc gọi kèm thời lượng và file ghi âm (`/telephony`).

### 9. Nghiệp Vụ Tư Vấn và Bán Điện Thoại Di Động
- **Danh mục điện thoại & Quản lý tồn kho (`/products`):**
  - Quản lý thương hiệu (Apple, Samsung, Xiaomi, Oppo...), mẫu máy, phiên bản màu sắc, dung lượng lưu trữ.
  - Lưu đầy đủ thông số kỹ thuật: Màn hình, chip (CPU), RAM, bộ nhớ, camera, pin/sạc, hệ điều hành, kết nối 5G/Wi-Fi và số tháng bảo hành.
  - Phân biệt giá niêm yết (listed price), giá khuyến mãi (promo price) và kiểm soát tồn kho thời gian thực theo kho/cửa hàng.
  - Lọc đa tiêu chí: Theo hãng, khoảng giá (< 10 triệu, 10-20 triệu, 20-30 triệu, trên 30 triệu) và lọc máy còn hàng.
  - Nhân viên/quản trị viên cập nhật giá và tồn kho trực tiếp; mọi thay đổi giá đều được ghi vết vào bảng `product_price_history` kèm người thao tác và lý do điều chỉnh.
- **So sánh điện thoại (`/products/compare`):**
  - So sánh trực quan thông số kỹ thuật 2 hoặc 3 mẫu máy cạnh nhau trên một bảng duy nhất (kích thước, chip, camera, pin, giá bán...).
- **Trợ lý tư vấn chọn điện thoại (`/consultation`):**
  - Khảo sát nhanh nhu cầu của khách hàng: Ngân sách tối thiểu - tối đa, mục đích chính (chụp ảnh sang trọng, gaming hiệu năng cao, pin trâu độ bền cao, văn phòng lướt web), hãng yêu thích, kích thước màn hình và tiêu chí đặc biệt.
  - Thuật toán gợi ý thông minh đề xuất top điện thoại phù hợp nhất còn hàng trong kho.
  - Lưu nhu cầu tư vấn vào hồ sơ khách hàng (`customer_preferences`) để tiếp tục chăm sóc trên Customer 360 và Inbox.
- **Báo giá điện thoại (`/quotations`):**
  - Lập báo giá chính thức gửi khách hàng (`/quotations/create`), áp dụng mã khuyến mãi (`promotions`) giảm giá theo số tiền cố định hoặc phần trăm.
  - Theo dõi trạng thái báo giá: `sent` (đã gửi), `accepted` (khách đồng ý), `rejected` (khách từ chối), `expired` (hết hạn).
  - 1-click chuyển đổi từ Báo giá được chấp thuận sang Đơn hàng bán chính thức.
- **Đơn hàng bán trực tiếp (`/sales-orders`):**
  - Quản lý đơn hàng bán điện thoại hoàn chỉnh: Khách hàng, sản phẩm, số lượng, giảm giá, tổng tiền thanh toán, thông tin người nhận, địa chỉ và mã vận đơn GHN.
  - Tự động trừ số lượng tồn kho thực tế (`phone_products.stock_quantity`) ngay khi tạo đơn; đồng bộ vào bảng đơn hàng chung.
  - Theo dõi vòng đời trạng thái đơn: `new` (mới) → `confirmed` (xác nhận) → `processing` (xử lý & đóng gói) → `shipping` (giao hàng) → `completed` (hoàn tất) → `cancelled` (hủy) hoặc `returned` (đổi trả).
  - Ghi vết toàn bộ lịch sử thay đổi trạng thái và người thực hiện vào bảng `order_status_history`.
- **Bảo hành điện tử & Chăm sóc hậu mãi (`/warranties`):**
  - Tra cứu bảo hành điện tử nhanh theo số IMEI/Serial (15 số), số điện thoại hoặc mã sổ bảo hành.
  - Ghi nhận gói bảo hành (tiêu chuẩn 12 tháng, VIP 1 đổi 1, rơi vỡ vào nước) và ngày bắt đầu / hết hạn.
  - Tiếp nhận sự cố máy từ khách và chuyển đổi 1-click thành Phiếu Ticket hỗ trợ kỹ thuật (`/warranties/convert-ticket`).
  - Lịch nhắc chăm sóc sau bán hàng (`followup_reminders`): Nhắc nhân viên liên hệ hỏi thăm trải nghiệm khách hàng sau 3 ngày, 7 ngày hoặc các mốc bảo hành định kỳ.
- **Tích hợp hộp thư đa kênh (Inbox):**
  - Sidebar tư vấn bán hàng trong Omnichannel Inbox hiển thị hồ sơ khách, nhu cầu tư vấn, sản phẩm quan tâm và lịch sử mua gần nhất.
  - Cho phép nhân viên chọn mẫu điện thoại và gửi ngay "Thẻ thông tin sản phẩm & Báo giá" trực tiếp vào cuộc trò chuyện chỉ với 1 click.
- **Dashboard bán hàng chuyên sâu:**
  - Thống kê doanh số bán trực tiếp, số đơn hàng, số báo giá đang mở.
  - Tỷ lệ chốt đơn thành công (Win Rate / Conversion Rate) từ phễu khách hàng tiềm năng.
  - Bảng xếp hạng các mẫu máy nổi bật kèm tồn kho thực tế và phễu khách hàng tiềm năng (`Lead` → `Won`).

---

## 🛠️ CẤU TRÚC DỰ ÁN

```text
quanlykh/
│
├── app.py                      # Entrypoint khởi chạy ứng dụng trực tiếp từ thư mục gốc
├── README.md                   # Tài liệu hướng dẫn sử dụng và triển khai
│
├── backend/                    # TOÀN BỘ LOGIC BACKEND & API SERVER
│   ├── app.py                  # Ứng dụng Flask trung tâm, định tuyến API, Webhooks & View render
│   ├── requirements.txt        # Danh sách thư viện Python cho Backend
│   ├── .env                    # Biến môi trường Backend
│   ├── README.md               # Tài liệu chi tiết Backend
│   │
│   ├── database/               # Tầng cơ sở dữ liệu MySQL
│   │   ├── db.py               # Kết nối DB và toàn bộ hàm CRUD, Customer 360, Bán hàng...
│   │   └── init_db.py          # Script tự động khởi tạo bảng & dữ liệu mẫu ban đầu
│   │
│   ├── services/               # Tầng nghiệp vụ (Services)
│   │   ├── ai_service.py       # Dịch vụ AI mở rộng (Gemini, OpenAI, Mock Fallback, Smart Replies)
│   │   ├── sales_service.py    # Dịch vụ tư vấn, báo giá, thẻ sản phẩm và quy đổi bảo hành
│   │   ├── rag_service.py      # Dịch vụ RAG tìm kiếm FAQs và tổng hợp câu trả lời
│   │   ├── gemini_service.py   # Wrapper tương thích ngược cho Google GenAI
│   │   ├── auth_service.py     # Quản lý phiên, mã hóa mật khẩu, RBAC và Google OIDC
│   │   ├── omnichannel_service.py # Chuẩn hóa tin nhắn đa kênh, Webchat JWT, Email SendGrid/SMTP
│   │   ├── order_service.py    # Connector tra cứu đơn KiotViet, Sapo, Lazada & bảo vệ PII
│   │   ├── logistics_service.py# Vận đơn GHN/GHTK và xác thực webhook HMAC
│   │   ├── telephony_service.py# Tổng đài Softphone Twilio Voice (JWT, TwiML, Call logs)
│   │   └── automation_service.py # Tự động phản hồi & kích hoạt khảo sát CSAT/NPS
│   │
│   └── tests/                  # Bộ kiểm thử tự động
│       └── test_crm.py         # 16 test cases kiểm thử toàn diện các luồng nghiệp vụ
│
└── frontend/                   # TOÀN BỘ GIAO DIỆN NGƯỜI DÙNG (UI/UX)
    ├── README.md               # Tài liệu chi tiết Frontend
    │
    ├── static/                 # Tài nguyên tĩnh CSS, Javascript, Icon, Logo
    │   ├── style.css           # Hệ thống thiết kế CSS hiện đại, responsive
    │   ├── chat.js             # Javascript điều khiển widget chatbot nổi
    │   └── *.png               # Logo thương hiệu & biểu tượng ứng dụng
    │
    └── templates/              # Toàn bộ 34 giao diện HTML Jinja2
        ├── base.html           # Layout khung mẫu dùng chung, Navigation bar & Softphone
        ├── dashboard.html      # Bảng điều khiển kinh doanh & vận hành
        ├── login.html          # Đăng nhập & Google OIDC
        ├── register.html       # Đăng ký tài khoản
        ├── portal.html         # Cổng hỗ trợ khách hàng
        ├── portal_new_ticket.html
        ├── portal_ticket_chat.html
        ├── portal_survey.html  # Đánh giá CSAT & NPS
        ├── tickets.html        # Danh sách quản lý phiếu hỗ trợ
        ├── ticket_create.html
        ├── ticket_detail.html
        ├── customers.html      # Danh bạ khách hàng
        ├── customer_360.html   # Hồ sơ khách hàng 360, đơn hàng, bảo hành
        ├── inbox.html          # Hộp thư đa kênh hợp nhất
        ├── products.html       # Danh mục điện thoại & bộ lọc
        ├── product_detail.html
        ├── product_compare.html
        ├── consultation.html   # Trợ lý AI tư vấn sản phẩm
        ├── quotations.html     # Danh sách báo giá
        ├── quotation_create.html
        ├── sales_orders.html   # Quản lý đơn hàng bán
        ├── sales_order_create.html
        ├── sales_order_detail.html
        ├── warranties.html     # Sổ bảo hành điện tử IMEI
        ├── kanban.html         # Bảng Kanban cơ hội bán hàng
        ├── shifts.html         # Lịch ca trực & chấm công
        ├── automation.html     # Cấu hình kịch bản tự động phản hồi
        ├── users.html          # Quản trị tài khoản & phân quyền
        ├── audit_logs.html     # Nhật ký kiểm toán
        ├── telephony.html      # Nhật ký cuộc gọi softphone
        ├── faqs.html           # Quản lý Knowledge Base / FAQs
        ├── add_faq.html
        ├── edit_faq.html
        └── webchat_embed.html  # Widget webchat nhúng ngoài
```

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT VÀ KHỞI CHẠY

### 1. Cài đặt môi trường
Đảm bảo đã cài đặt Python 3.10+ và máy chủ MySQL (MySQL 8.0 hoặc MariaDB).

```bash
# Cài đặt các gói phụ thuộc
pip install -r backend/requirements.txt
```

### 2. Thiết lập biến môi trường
Tạo file `backend/.env` từ `backend/.env.example` và điền thông số kết nối MySQL của bạn:

```ini
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=customer_support_ai
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Khởi tạo Cơ sở dữ liệu
Chạy lệnh khởi tạo cơ sở dữ liệu (tự động tạo 15+ bảng và nạp sẵn dữ liệu mẫu):

```bash
# Cách 1: Khởi tạo từ thư mục gốc
python -m backend.database.init_db

# Cách 2: Khởi tạo từ thư mục backend
cd backend
python -m database.init_db
```

### 4. Khởi chạy Ứng dụng
Hệ thống hỗ trợ 2 cách khởi chạy vô cùng tiện lợi:

- **Cách 1 (Khuyên dùng - Khởi chạy từ thư mục gốc):**
  ```bash
  python app.py
  ```

- **Cách 2 (Khởi chạy trực tiếp từ thư mục backend):**
  ```bash
  cd backend
  python app.py
  ```

Mở trình duyệt và truy cập: `http://127.0.0.1:5000`

---

## 🔑 TÀI KHOẢN MẪU DÙNG THỬ

| Vai trò | Tên đăng nhập | Mật khẩu | Màn hình truy cập chính |
| :--- | :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin` | `admin123` | Toàn quyền: Dashboard, Tickets, Inbox, Customer 360, Kanban, Ca trực, Users, Audit |
| **Nhân viên (Agent)** | `nhanvien` | `agent123` | Dashboard, Tickets, Hộp thư đa kênh, Customer 360, Kanban, Ca trực của tôi, Softphone |
| **Khách hàng (Customer)** | `khachhang` | `customer123` | Cổng hỗ trợ khách hàng (`/portal`), Trao đổi ticket, Xem đơn hàng, Đánh giá CSAT/NPS |

---

## ⚙️ HƯỚNG DẪN CẤU HÌNH TÍCH HỢP BÊN NGOÀI

### 1. Tích hợp AI (Google Gemini & OpenAI)
- Mặc định hệ thống sử dụng Google Gemini (`GEMINI_API_KEY`).
- Nếu muốn chuyển sang OpenAI, cấu hình trong `.env`:
  ```ini
  AI_PROVIDER=openai
  OPENAI_API_KEY=sk-...
  ```
- Nếu không có mạng hoặc API key hết hạn mức, hệ thống tự động kích hoạt **Mock Fallback Provider** mà không làm sập ứng dụng.

### 2. Tích hợp Zalo Official Account (OA)
- Điền `ZALO_OA_ACCESS_TOKEN`, `ZALO_APP_ID`, `ZALO_SECRET_KEY` trong `.env`.
- Cấu hình Webhook URL trên trang Zalo Developers: `https://your-domain.com/api/webhooks/zalo`.

### 3. Tích hợp Facebook Messenger & Instagram Direct
- Điền `FB_PAGE_ACCESS_TOKEN` và `FB_VERIFY_TOKEN` trong `.env`.
- Webhook URL trên Meta for Developers: `https://your-domain.com/api/webhooks/facebook`.

### 4. Tích hợp Email (SendGrid & SMTP)
- **Gửi thư đi (SMTP):** Điền `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`.
- **Nhận thư đến (SendGrid):** Cấu hình Inbound Parse trỏ về `https://your-domain.com/api/webhooks/email/inbound`.

### 5. Tích hợp Đơn hàng & Vận chuyển (KiotViet, Sapo, Lazada, GHN, GHTK)
- **KiotViet:** Cung cấp `KIOTVIET_CLIENT_ID`, `KIOTVIET_CLIENT_SECRET`, `KIOTVIET_RETAILER`.
- **Sapo:** Cung cấp `SAPO_API_KEY`, `SAPO_STORE_DOMAIN`.
- **GHN Webhook URL:** `https://your-domain.com/api/webhooks/logistics/ghn` kèm `GHN_WEBHOOK_TOKEN`.
- **GHTK Webhook URL:** `https://your-domain.com/api/webhooks/logistics/ghtk` kèm chữ ký HMAC qua `GHTK_SECRET_KEY`.
- *Lưu ý: Khi chưa điền API keys thực tế, hệ thống tự động kích hoạt chế độ Demo Mock Data thực tế theo số điện thoại (ví dụ: `0987654321`) để nhân viên kiểm thử ngay lập tức!*

### 6. Tích hợp Twilio Voice Softphone
- Cấu hình các thông số Twilio trong `.env`:
  `TWILIO_ACCOUNT_SID`, `TWILIO_API_KEY`, `TWILIO_API_SECRET`, `TWILIO_TWIML_APP_SID`, `TWILIO_CALLER_ID`.
- Nhân viên bấm nút **📞 Gọi điện** trên thanh menu để mở bàn phím gọi điện Softphone.

---

## 🧪 CHẠY KIỂM THỬ TỰ ĐỘNG

Dự án đi kèm bộ test suite tự động kiểm tra toàn diện 16 luồng nghiệp vụ:
```bash
# Cách 1: Chạy kiểm thử từ thư mục gốc
python -m unittest backend/tests/test_crm.py

# Cách 2: Chạy kiểm thử từ thư mục backend
cd backend
python -m unittest tests/test_crm.py
```
Kết quả kiểm thử bao gồm:
- ✅ Kiểm tra tương thích 100% chức năng Knowledge Base FAQs hiện có.
- ✅ Kiểm tra xác thực, băm mật khẩu và phân quyền RBAC đa cấp độ.
- ✅ Kiểm tra Cổng hỗ trợ khách hàng và luồng Ticket.
- ✅ Kiểm tra AI Service và cơ chế Fallback tự động.
- ✅ Kiểm tra chuẩn hóa tin nhắn đa kênh và chống trùng lặp sự kiện (Idempotency).
- ✅ Kiểm tra cấp và xác thực bảo mật JWT Token Webchat nhúng.
- ✅ Kiểm tra tra cứu đơn hàng KiotViet/Sapo/Lazada và bảo vệ PII.
- ✅ Kiểm tra làm mới vận đơn GHN/GHTK và xác thực webhook.
- ✅ Kiểm tra cấp Twilio Voice Access Token và sinh TwiML.
