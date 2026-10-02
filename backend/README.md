# BACKEND - HỆ THỐNG CRM & BÁN HÀNG

Thư mục chứa toàn bộ mã nguồn xử lý logic máy chủ (Server-side logic), API endpoints, kết nối cơ sở dữ liệu và tích hợp dịch vụ bên ngoài.

---

## 📁 Cấu trúc thư mục

```text
backend/
├── app.py                    # Điểm khởi chạy chính của Flask Web & API Server
├── requirements.txt          # Danh sách thư viện Python cần cài đặt
├── .env                      # Cấu hình biến môi trường (Database, API Keys, v.v.)
├── .env.example              # Mẫu cấu hình biến môi trường chuẩn
│
├── database/                 # Tầng tương tác cơ sở dữ liệu (MySQL)
│   ├── __init__.py
│   ├── db.py                 # Hàm kết nối & truy vấn dữ liệu (CRUD, tổng hợp 360, thống kê)
│   └── init_db.py            # Script tự động tạo bảng & dữ liệu mẫu (15+ bảng chuẩn hóa)
│
├── services/                 # Tầng dịch vụ nghiệp vụ chuyên biệt
│   ├── __init__.py
│   ├── ai_service.py         # Bộ điều phối AI (Gemini, OpenAI, Mock Fallback)
│   ├── gemini_service.py     # Tích hợp Google Gemini API
│   ├── rag_service.py        # Truy xuất tri thức thông minh (Retrieval-Augmented Generation)
│   ├── omnichannel_service.py# Hợp nhất tin nhắn 5 kênh (Zalo, FB, IG, Webchat, Email)
│   ├── sales_service.py      # Báo giá, đơn hàng, gợi ý cấu hình & bảo hành
│   ├── order_service.py      # Tra cứu & đồng bộ đơn hàng KiotViet, Sapo, Lazada
│   ├── logistics_service.py  # Vận đơn GHN, GHTK & xử lý Webhook vận chuyển
│   ├── telephony_service.py  # Twilio Voice Softphone & sinh TwiML gọi điện
│   ├── auth_service.py       # Xác thực, băm mật khẩu, phân quyền RBAC & Google OIDC
│   └── automation_service.py # Kịch bản phản hồi tự động & kích hoạt CSAT/NPS
│
└── tests/                    # Bộ kiểm thử tự động
    ├── __init__.py
    └── test_crm.py           # 16 test case kiểm tra toàn diện mọi tính năng
```

---

## 🚀 Cách khởi chạy Backend

### 1. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 2. Khởi tạo cơ sở dữ liệu (nếu cần)
```bash
python -m database.init_db
```

### 3. Khởi chạy máy chủ Backend
```bash
python app.py
```
Máy chủ sẽ lắng nghe tại: `http://127.0.0.1:5000`

---

## 🧪 Chạy kiểm thử tự động
```bash
python -m unittest tests/test_crm.py
```
Toàn bộ 16 kịch bản kiểm thử sẽ được thực thi tự động.
