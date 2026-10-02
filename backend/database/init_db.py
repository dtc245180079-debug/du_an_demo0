import os
import sys
import platform

# Đảm bảo mã hóa UTF-8 cho console Windows tránh UnicodeEncodeError khi print tiếng Việt
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

if sys.platform == "win32":
    platform.system = lambda: "Windows"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from werkzeug.security import generate_password_hash
from database.db import get_connection

TABLES_SQL = [
    # 1. Users table
    """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(150),
        phone VARCHAR(20),
        role VARCHAR(20) DEFAULT 'customer',
        avatar VARCHAR(255),
        is_active TINYINT DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 2. Customers table (Unified 360)
    """
    CREATE TABLE IF NOT EXISTS customers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NULL,
        full_name VARCHAR(150) NOT NULL,
        phone VARCHAR(20),
        email VARCHAR(255),
        zalo_id VARCHAR(100),
        fb_id VARCHAR(100),
        ig_id VARCHAR(100),
        member_rank VARCHAR(50) DEFAULT 'Bạc',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_phone (phone),
        INDEX idx_email (email)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 3. Tickets table
    """
    CREATE TABLE IF NOT EXISTS tickets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ticket_code VARCHAR(50) UNIQUE NOT NULL,
        customer_id INT NOT NULL,
        customer_name VARCHAR(150),
        customer_phone VARCHAR(20),
        customer_email VARCHAR(255),
        channel VARCHAR(50) DEFAULT 'web',
        subject VARCHAR(255) NOT NULL,
        priority VARCHAR(20) DEFAULT 'medium',
        status VARCHAR(30) DEFAULT 'open',
        assigned_agent_id INT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP NULL,
        INDEX idx_status (status),
        INDEX idx_assigned (assigned_agent_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 4. Ticket Messages
    """
    CREATE TABLE IF NOT EXISTS ticket_messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ticket_id INT NOT NULL,
        sender_type VARCHAR(20) NOT NULL,
        sender_id INT NULL,
        sender_name VARCHAR(150),
        message TEXT NOT NULL,
        channel VARCHAR(50) DEFAULT 'web',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_ticket (ticket_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 5. Ticket Surveys (CSAT & NPS)
    """
    CREATE TABLE IF NOT EXISTS ticket_surveys (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ticket_id INT NOT NULL UNIQUE,
        customer_id INT NULL,
        rating_csat INT,
        score_nps INT,
        feedback TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 6. Omnichannel Messages
    """
    CREATE TABLE IF NOT EXISTS omnichannel_messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        external_msg_id VARCHAR(100),
        conversation_id VARCHAR(100) NOT NULL,
        channel VARCHAR(50) NOT NULL,
        sender_type VARCHAR(20) NOT NULL,
        sender_id VARCHAR(100),
        sender_name VARCHAR(150),
        content TEXT NOT NULL,
        direction VARCHAR(20) NOT NULL,
        raw_payload TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_conv (conversation_id),
        INDEX idx_ext_msg (external_msg_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 7. Orders table (Sapo/KiotViet/Lazada normalized)
    """
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_code VARCHAR(100) UNIQUE NOT NULL,
        source VARCHAR(50) NOT NULL,
        customer_name VARCHAR(150),
        customer_phone VARCHAR(20) NOT NULL,
        total_amount DECIMAL(15, 2) DEFAULT 0,
        status VARCHAR(50) DEFAULT 'completed',
        shipping_code VARCHAR(100),
        shipping_carrier VARCHAR(50),
        shipping_status VARCHAR(100),
        items_summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_ord_phone (customer_phone),
        INDEX idx_ord_ship (shipping_code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 8. Work shifts table
    """
    CREATE TABLE IF NOT EXISTS work_shifts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        agent_id INT NOT NULL,
        shift_name VARCHAR(100) NOT NULL,
        shift_date DATE NOT NULL,
        start_time VARCHAR(20) NOT NULL,
        end_time VARCHAR(20) NOT NULL,
        status VARCHAR(50) DEFAULT 'scheduled',
        check_in_time TIMESTAMP NULL,
        check_out_time TIMESTAMP NULL,
        notes TEXT,
        INDEX idx_shift_agent (agent_id),
        INDEX idx_shift_date (shift_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 9. Sales Opportunities (Kanban)
    """
    CREATE TABLE IF NOT EXISTS sales_opportunities (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NULL,
        customer_name VARCHAR(150),
        customer_phone VARCHAR(20),
        title VARCHAR(255) NOT NULL,
        value DECIMAL(15, 2) DEFAULT 0,
        stage VARCHAR(50) DEFAULT 'lead',
        probability INT DEFAULT 20,
        assigned_agent_id INT NULL,
        expected_close_date DATE NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_opp_stage (stage)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 10. Auto replies table
    """
    CREATE TABLE IF NOT EXISTS auto_replies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        channel VARCHAR(50) NOT NULL,
        trigger_type VARCHAR(50) NOT NULL,
        message TEXT NOT NULL,
        is_active TINYINT DEFAULT 1,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uq_ch_trg (channel, trigger_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 11. Call logs table
    """
    CREATE TABLE IF NOT EXISTS call_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        agent_id INT NULL,
        customer_phone VARCHAR(50) NOT NULL,
        direction VARCHAR(20) DEFAULT 'outbound',
        call_duration INT DEFAULT 0,
        status VARCHAR(50) DEFAULT 'completed',
        recording_url VARCHAR(500),
        call_sid VARCHAR(100),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_call_phone (customer_phone)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 12. Audit logs table
    """
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NULL,
        username VARCHAR(100),
        action VARCHAR(100) NOT NULL,
        target_type VARCHAR(50),
        target_id VARCHAR(50),
        details TEXT,
        ip_address VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_audit_created (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 13. Idempotent keys table
    """
    CREATE TABLE IF NOT EXISTS idempotent_keys (
        id INT AUTO_INCREMENT PRIMARY KEY,
        key_name VARCHAR(255) UNIQUE NOT NULL,
        scope VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_key_scope (scope, key_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # =====================================================================
    # CÁC BẢNG MỚI: NGHIỆP VỤ TƯ VẤN VÀ BÁN ĐIỆN THOẠI DI ĐỘNG
    # =====================================================================

    # 14. Phone Products (Danh mục điện thoại & Thông số kỹ thuật)
    """
    CREATE TABLE IF NOT EXISTS phone_products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        brand VARCHAR(100) NOT NULL,
        model VARCHAR(100),
        slug VARCHAR(255) UNIQUE,
        description TEXT,
        listed_price DECIMAL(15, 2) NOT NULL,
        promo_price DECIMAL(15, 2),
        stock_quantity INT DEFAULT 0,
        stock_status VARCHAR(50) DEFAULT 'in_stock',
        warehouse_location VARCHAR(150) DEFAULT 'Kho Tổng TP.HCM',
        is_active TINYINT DEFAULT 1,
        image_url VARCHAR(500),
        screen_spec VARCHAR(255),
        chip_spec VARCHAR(150),
        ram_spec VARCHAR(50),
        storage_spec VARCHAR(100),
        camera_spec VARCHAR(255),
        battery_spec VARCHAR(100),
        os_spec VARCHAR(100),
        connectivity_spec VARCHAR(150),
        warranty_months INT DEFAULT 12,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_prod_brand (brand),
        INDEX idx_prod_status (stock_status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 15. Phone Variants (Màu sắc, Dung lượng, SKU)
    """
    CREATE TABLE IF NOT EXISTS phone_variants (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        color VARCHAR(50) NOT NULL,
        storage VARCHAR(50) NOT NULL,
        price_modifier DECIMAL(15, 2) DEFAULT 0,
        stock_quantity INT DEFAULT 10,
        sku VARCHAR(100) UNIQUE,
        INDEX idx_var_prod (product_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 16. Customer Consultation Preferences (Nhu cầu tư vấn & sản phẩm quan tâm)
    """
    CREATE TABLE IF NOT EXISTS customer_preferences (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NOT NULL UNIQUE,
        budget_min DECIMAL(15, 2),
        budget_max DECIMAL(15, 2),
        primary_usage VARCHAR(100),
        preferred_brands VARCHAR(255),
        desired_screen_size VARCHAR(100),
        key_criteria TEXT,
        interested_products TEXT,
        agent_notes TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_pref_cust (customer_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 17. Quotations (Báo giá điện thoại)
    """
    CREATE TABLE IF NOT EXISTS quotations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        quote_code VARCHAR(50) UNIQUE NOT NULL,
        customer_id INT NOT NULL,
        customer_name VARCHAR(150),
        customer_phone VARCHAR(20),
        agent_id INT NOT NULL,
        agent_name VARCHAR(150),
        total_listed_amount DECIMAL(15, 2) DEFAULT 0,
        discount_amount DECIMAL(15, 2) DEFAULT 0,
        final_amount DECIMAL(15, 2) DEFAULT 0,
        status VARCHAR(50) DEFAULT 'sent',
        items_json TEXT,
        promotion_code VARCHAR(50),
        notes TEXT,
        expiry_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_quote_cust (customer_id),
        INDEX idx_quote_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 18. Sales Orders (Đơn hàng bán hàng trực tiếp)
    """
    CREATE TABLE IF NOT EXISTS sales_orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_code VARCHAR(50) UNIQUE NOT NULL,
        quote_id INT NULL,
        customer_id INT NOT NULL,
        customer_name VARCHAR(150),
        customer_phone VARCHAR(20) NOT NULL,
        agent_id INT NOT NULL,
        total_amount DECIMAL(15, 2) NOT NULL,
        discount_amount DECIMAL(15, 2) DEFAULT 0,
        final_amount DECIMAL(15, 2) NOT NULL,
        status VARCHAR(50) DEFAULT 'new',
        shipping_address TEXT,
        receiver_name VARCHAR(150),
        receiver_phone VARCHAR(20),
        shipping_code VARCHAR(100),
        shipping_carrier VARCHAR(50) DEFAULT 'GHN',
        payment_method VARCHAR(50) DEFAULT 'cod',
        items_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_so_cust (customer_id),
        INDEX idx_so_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 19. Product Price History (Lịch sử thay đổi giá)
    """
    CREATE TABLE IF NOT EXISTS product_price_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        old_listed_price DECIMAL(15, 2),
        new_listed_price DECIMAL(15, 2),
        old_promo_price DECIMAL(15, 2),
        new_promo_price DECIMAL(15, 2),
        changed_by INT,
        changed_by_name VARCHAR(100),
        reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_hist_prod (product_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 20. Order Status History (Lịch sử thay đổi trạng thái đơn)
    """
    CREATE TABLE IF NOT EXISTS order_status_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT NOT NULL,
        old_status VARCHAR(50),
        new_status VARCHAR(50),
        changed_by INT,
        changed_by_name VARCHAR(100),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_hist_order (order_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 21. Warranties (Quản lý bảo hành & Hậu mãi)
    """
    CREATE TABLE IF NOT EXISTS warranties (
        id INT AUTO_INCREMENT PRIMARY KEY,
        warranty_code VARCHAR(50) UNIQUE NOT NULL,
        order_id INT NULL,
        customer_id INT NOT NULL,
        customer_name VARCHAR(150),
        customer_phone VARCHAR(20),
        product_id INT NOT NULL,
        product_name VARCHAR(255),
        imei_serial VARCHAR(100),
        warranty_package VARCHAR(100) DEFAULT 'Bảo hành chính hãng 12 tháng',
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        status VARCHAR(50) DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_warr_cust (customer_id),
        INDEX idx_warr_imei (imei_serial)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 22. Promotions (Chương trình khuyến mãi)
    """
    CREATE TABLE IF NOT EXISTS promotions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        promo_code VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        discount_type VARCHAR(20) DEFAULT 'fixed',
        discount_value DECIMAL(15, 2) NOT NULL,
        min_order_amount DECIMAL(15, 2) DEFAULT 0,
        start_date DATE,
        end_date DATE,
        is_active TINYINT DEFAULT 1,
        applicable_brands VARCHAR(255) DEFAULT 'all'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 23. Followup Reminders (Nhắc nhở chăm sóc sau mua & mốc bảo hành)
    """
    CREATE TABLE IF NOT EXISTS followup_reminders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NOT NULL,
        order_id INT NULL,
        agent_id INT NOT NULL,
        reminder_type VARCHAR(50) NOT NULL,
        due_date DATE NOT NULL,
        content TEXT NOT NULL,
        status VARCHAR(30) DEFAULT 'pending',
        completed_at TIMESTAMP NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_rem_agent (agent_id),
        INDEX idx_rem_due (due_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 24. Support FAQs (Kho tri thức câu hỏi thường gặp phục vụ RAG AI)
    """
    CREATE TABLE IF NOT EXISTS support_faqs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        issue_name VARCHAR(255) NOT NULL,
        category VARCHAR(100) NOT NULL,
        brand VARCHAR(100) NOT NULL,
        symptom TEXT NOT NULL,
        solution TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_faq_cat_brand (category, brand)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
]

def init_database():
    print("[DB INIT] Đang khởi tạo các bảng CRM & Bán hàng điện thoại...")
    conn = get_connection()
    cursor = conn.cursor()

    for sql in TABLES_SQL:
        try:
            cursor.execute(sql)
        except Exception as e:
            print(f"[DB INIT ERROR] Lỗi khi tạo bảng: {e}")

    conn.commit()

    # Seed Default Users if none exist
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    if user_count == 0:
        print("[DB INIT] Tạo người dùng mặc định (Mật khẩu: 12345678)...")
        default_users = [
            ("admin", "admin@cskh.vn", generate_password_hash("12345678", method="pbkdf2:sha256"), "Quản Trị Viên Hệ Thống", "0901234567", "admin"),
            ("nhanvien", "agent1@cskh.vn", generate_password_hash("12345678", method="pbkdf2:sha256"), "Nguyễn Văn Hỗ Trợ", "0912345678", "agent"),
            ("agent2", "agent2@cskh.vn", generate_password_hash("12345678", method="pbkdf2:sha256"), "Trần Thị Chăm Sóc", "0923456789", "agent"),
            ("khachhang", "customer@gmail.com", generate_password_hash("12345678", method="pbkdf2:sha256"), "Lê Khách Hàng VIP", "0987654321", "customer")
        ]
        insert_user_sql = """
            INSERT INTO users (username, email, password_hash, full_name, phone, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_user_sql, default_users)
        conn.commit()

    # Seed Phone Products if none exist
    cursor.execute("SELECT COUNT(*) FROM phone_products")
    prod_count = cursor.fetchone()[0]
    if prod_count == 0:
        print("[DB INIT] Khởi tạo danh mục điện thoại di động...")
        products = [
            (
                "iPhone 15 Pro Max", "Apple", "A3106", "iphone-15-pro-max",
                "Flagship cao cấp nhất của Apple với khung viền Titan siêu nhẹ, camera tiềm vọng 5x và chip A17 Pro mạnh mẽ vượt trội.",
                34990000.0, 29990000.0, 15, "in_stock", "Kho Quận 1 (TP.HCM)",
                "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500&auto=format&fit=crop",
                "6.7 inch OLED Super Retina XDR 120Hz ProMotion", "Apple A17 Pro (3nm)", "8GB", "256GB / 512GB / 1TB",
                "Chính 48MP (F/1.78) + Siêu rộng 12MP + Tele 5x 12MP (OIS)", "4422 mAh, Sạc nhanh 25W, MagSafe 15W",
                "iOS 17", "5G, Wi-Fi 6E, Bluetooth 5.3, USB-C 3.0", 12
            ),
            (
                "iPhone 15", "Apple", "A3090", "iphone-15",
                "Thiết kế mặt lưng nhám thời thượng, màn hình Dynamic Island thông minh và camera 48MP sắc nét.",
                22990000.0, 19490000.0, 25, "in_stock", "Kho Quận 1 (TP.HCM)",
                "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500&auto=format&fit=crop",
                "6.1 inch OLED Super Retina XDR 60Hz Dynamic Island", "Apple A16 Bionic (4nm)", "6GB", "128GB / 256GB",
                "Chính 48MP + Siêu rộng 12MP (zoom 2x chất lượng quang học)", "3349 mAh, Sạc nhanh 20W, MagSafe",
                "iOS 17", "5G, Wi-Fi 6, USB-C", 12
            ),
            (
                "Samsung Galaxy S24 Ultra", "Samsung", "SM-S928B", "samsung-galaxy-s24-ultra",
                "Siêu phẩm AI toàn năng với khung viền Titan, màn hình chống chói Dynamic AMOLED 2X và quyền năng Galaxy AI.",
                33990000.0, 27990000.0, 12, "in_stock", "Kho Quận 3 (TP.HCM)",
                "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500&auto=format&fit=crop",
                "6.8 inch Dynamic AMOLED 2X 120Hz QHD+ Phẳng (Kính Gorilla Armor chống chói)", "Snapdragon 8 Gen 3 for Galaxy (4nm)", "12GB", "256GB / 512GB / 1TB",
                "Chính 200MP + Tele 50MP (5x) + Tele 10MP (3x) + Siêu rộng 12MP", "5000 mAh, Sạc nhanh 45W, Bút S-Pen",
                "Android 14 (One UI 6.1, Galaxy AI)", "5G, Wi-Fi 7, Bluetooth 5.3, UWB", 12
            ),
            (
                "Samsung Galaxy A55 5G", "Samsung", "SM-A556B", "samsung-galaxy-a55-5g",
                "Điện thoại tầm trung xuất sắc với khung viền kim loại, chống nước IP67 và camera chụp đêm chuyên nghiệp.",
                9990000.0, 8490000.0, 30, "in_stock", "Kho Quận 3 (TP.HCM)",
                "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500&auto=format&fit=crop",
                "6.6 inch Super AMOLED 120Hz FHD+ Vision Booster", "Exynos 1480 (4nm)", "8GB", "128GB / 256GB",
                "Chính 50MP (OIS) + Siêu rộng 12MP + Macro 5MP", "5000 mAh, Sạc nhanh 25W",
                "Android 14 (One UI 6.1)", "5G, Wi-Fi 6, IP67", 12
            ),
            (
                "Xiaomi 14", "Xiaomi", "23127PN0CC", "xiaomi-14",
                "Flagship nhỏ gọn hoàn hảo với ống kính quang học Leica Summilux đỉnh cao và hiệu năng bùng nổ.",
                22990000.0, 18990000.0, 8, "in_stock", "Kho Tân Bình (TP.HCM)",
                "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&auto=format&fit=crop",
                "6.36 inch OLED 1.5K 120Hz LTPO viền siêu mỏng", "Snapdragon 8 Gen 3 (4nm)", "12GB", "256GB / 512GB",
                "Bộ 3 camera Leica 50MP (Chính + Tele 75mm + Siêu rộng)", "4610 mAh, Sạc siêu tốc 90W + Không dây 50W",
                "Xiaomi HyperOS (Android 14)", "5G, Wi-Fi 7, Hồng ngoại IR, IP68", 24
            ),
            (
                "Oppo Find N3 5G", "Oppo", "CPH2499", "oppo-find-n3",
                "Tuyệt tác màn hình gập cao cấp không nếp gấp, camera Hasselblad đẳng cấp doanh nhân.",
                44990000.0, 41990000.0, 5, "in_stock", "Kho Quận 1 (TP.HCM)",
                "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=500&auto=format&fit=crop",
                "Màn trong 7.82 inch 120Hz + Màn ngoài 6.31 inch 120Hz", "Snapdragon 8 Gen 2 (4nm)", "16GB", "512GB",
                "Hasselblad: 48MP (Sony LYT-T808) + 64MP tiềm vọng + 48MP siêu rộng", "4805 mAh, Sạc SuperVOOC 67W",
                "ColorOS 13.2 (Android 13)", "5G, Wi-Fi 7, Loa kép không gian", 12
            )
        ]

        cursor.executemany("""
            INSERT INTO phone_products (
                name, brand, model, slug, description, listed_price, promo_price, stock_quantity, stock_status, warehouse_location,
                image_url, screen_spec, chip_spec, ram_spec, storage_spec, camera_spec, battery_spec, os_spec, connectivity_spec, warranty_months
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, products)
        conn.commit()

        # Seed Phone Variants
        variants = [
            (1, "Titan Tự Nhiên", "256GB", 0, 8, "IP15PM-256-NAT"),
            (1, "Titan Đen", "256GB", 0, 5, "IP15PM-256-BLK"),
            (1, "Titan Xanh", "512GB", 5000000.0, 2, "IP15PM-512-BLU"),
            (2, "Xanh Pastel", "128GB", 0, 15, "IP15-128-BLU"),
            (2, "Hồng Pastel", "128GB", 0, 10, "IP15-128-PNK"),
            (3, "Xám Titan", "256GB", 0, 7, "S24U-256-GRY"),
            (3, "Đen Titan", "512GB", 4000000.0, 5, "S24U-512-BLK"),
            (4, "Xanh Iceblue", "128GB", 0, 20, "A55-128-ICE"),
            (5, "Đen Nhám", "256GB", 0, 8, "MI14-256-BLK"),
            (6, "Vàng Cổ Điển", "512GB", 0, 5, "N3-512-GLD")
        ]
        cursor.executemany("""
            INSERT INTO phone_variants (product_id, color, storage, price_modifier, stock_quantity, sku)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, variants)
        conn.commit()

        # Seed Promotions
        promos = [
            ("TET2026", "Lì Xì Tết - Giảm 1.000.000đ cho đơn từ 20 triệu", "fixed", 1000000.0, 20000000.0, "2026-01-01", "2026-12-31", 1, "all"),
            ("APPLE500", "Ưu đãi khách hàng thân thiết mua Apple", "fixed", 500000.0, 15000000.0, "2026-01-01", "2026-12-31", 1, "Apple"),
            ("SAM5PERCENT", "Giảm 5% cho dòng Galaxy S24 Ultra", "percent", 5.0, 25000000.0, "2026-01-01", "2026-12-31", 1, "Samsung")
        ]
        cursor.executemany("""
            INSERT INTO promotions (promo_code, name, discount_type, discount_value, min_order_amount, start_date, end_date, is_active, applicable_brands)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, promos)
        conn.commit()

        # Seed Customer Preferences for customer ID 1
        cursor.execute("""
            INSERT INTO customer_preferences (customer_id, budget_min, budget_max, primary_usage, preferred_brands, desired_screen_size, key_criteria, interested_products, agent_notes)
            VALUES (1, 25000000.0, 35000000.0, 'Chụp ảnh quay phim & Sang trọng', 'Apple, Samsung', 'Màn hình lớn > 6.7 inch', 'Camera zoom quang học tốt, Pin trâu, Hỗ trợ trả góp 0%', '1,3', 'Khách VIP thích sản phẩm màu Titan Tự Nhiên hoặc Titan Xám')
            ON DUPLICATE KEY UPDATE budget_max=VALUES(budget_max)
        """)
        conn.commit()

        # Seed Sample Quotation
        import json
        quote_items = [
            {"product_id": 1, "name": "iPhone 15 Pro Max 256GB (Titan Tự Nhiên)", "qty": 1, "listed_price": 34990000.0, "promo_price": 29990000.0, "subtotal": 29990000.0}
        ]
        cursor.execute("""
            INSERT INTO quotations (quote_code, customer_id, customer_name, customer_phone, agent_id, agent_name, total_listed_amount, discount_amount, final_amount, status, items_json, promotion_code, notes, expiry_date)
            VALUES ('BG-2026-1001', 1, 'Lê Khách Hàng VIP', '0987654321', 2, 'Nguyễn Văn Hỗ Trợ', 34990000.0, 5000000.0, 29990000.0, 'sent', %s, 'APPLE500', 'Báo giá ưu đãi kèm gói dán màn hình cao cấp và ốp lưng chính hãng', '2026-12-31')
        """, (json.dumps(quote_items, ensure_ascii=False),))
        conn.commit()

        # Seed Sample Warranty
        cursor.execute("""
            INSERT INTO warranties (warranty_code, order_id, customer_id, customer_name, customer_phone, product_id, product_name, imei_serial, warranty_package, start_date, end_date, status)
            VALUES ('BH-2026-9011', 1, 1, 'Lê Khách Hàng VIP', '0987654321', 1, 'iPhone 15 Pro Max 256GB', '356789012345678', 'Bảo hành chính hãng 12 tháng Apple Care+', '2026-01-15', '2027-01-15', 'active')
        """)
        conn.commit()

        # Seed Sample Followup Reminder
        cursor.execute("""
            INSERT INTO followup_reminders (customer_id, order_id, agent_id, reminder_type, due_date, content, status)
            VALUES (1, 1, 2, '7_day_satisfaction', CURDATE(), 'Gọi điện hỏi thăm khách hàng sau 7 ngày nhận máy iPhone 15 Pro Max, kiểm tra tình trạng sử dụng và hướng dẫn kích hoạt iCloud', 'pending')
        """)
        conn.commit()

    # Seed Support FAQs if none exist
    cursor.execute("SELECT COUNT(*) FROM support_faqs")
    faq_count = cursor.fetchone()[0]
    if faq_count == 0:
        print("[DB INIT] Khởi tạo kho tri thức hỏi đáp CSKH (support_faqs)...")
        default_faqs = [
            ("Màn hình iPhone bị sọc xanh", "Kỹ thuật", "Apple", "Màn hình xuất hiện sọc xanh lá cây sau khi cập nhật hoặc tự nhiên bị.", "Nếu máy còn bảo hành và không có dấu hiệu rơi cấn, vào nước, trung tâm sẽ gửi hãng thay màn hình miễn phí. Nếu hết bảo hành, cửa hàng hỗ trợ giảm 20% chi phí thay linh kiện chính hãng."),
            ("Thủ tục mua trả góp 0%", "Trả góp", "Tất cả", "Khách hàng hỏi cần giấy tờ gì để mua trả góp và trả trước bao nhiêu.", "Chỉ cần mang theo CCCD gắn chip. Hỗ trợ 2 hình thức: Trả góp 0% qua thẻ tín dụng (không cần trả trước) hoặc qua công ty tài chính (Home Credit/HD Saison, trả trước từ 10% giá trị máy)."),
            ("Chính sách 1 đổi 1 trong 30 ngày", "Bảo hành", "Tất cả", "Máy mới mua bị lỗi phần cứng có được đổi mới không?", "Trong vòng 30 ngày đầu tính từ ngày mua, nếu máy gặp lỗi phần cứng do nhà sản xuất (được kỹ thuật viên thẩm định), khách hàng được đổi ngay 1 máy mới nguyên seal cùng model hoàn toàn miễn phí."),
            ("Điện thoại tụt pin nhanh và nóng máy", "Kỹ thuật", "Samsung", "Máy tụt pin nhanh bất thường, máy nóng khi dùng 4G hoặc lướt web.", "Khách hàng thử tắt ứng dụng chạy ngầm và giảm độ sáng màn hình. Nếu máy tụt quá 20% pin/giờ khi không sử dụng, mời khách mang máy ra cửa hàng để kỹ thuật đo dòng và kiểm tra độ chai pin."),
            ("Quên mật khẩu Apple ID / iCloud", "Kỹ thuật", "Apple", "Khách quên mật khẩu iCloud, không tải được ứng dụng hoặc bị khóa máy.", "Cửa hàng không thể tự mở khóa iCloud. Hướng dẫn khách truy cập iforgot.apple.com để đặt lại mật khẩu bằng SĐT đăng ký, hoặc mang hóa đơn mua hàng gốc đến để nhờ Apple hỗ trợ.")
        ]
        cursor.executemany("""
            INSERT INTO support_faqs (issue_name, category, brand, symptom, solution)
            VALUES (%s, %s, %s, %s, %s)
        """, default_faqs)
        conn.commit()

    # Seed Sample Customers if none exist
    cursor.execute("SELECT COUNT(*) FROM customers")
    cust_count = cursor.fetchone()[0]
    if cust_count == 0:
        print("[DB INIT] Khởi tạo hồ sơ khách hàng mẫu...")
        sample_customers = [
            (4, "Lê Văn Hùng", "0987654321", "hung.le@gmail.com", "zalo_hung99", "fb_hungvip", "VIP", "Khách VIP thường mua flagship Apple."),
            (None, "Trần Thị Mai", "0912345678", "mai.tran@gmail.com", "zalo_mai", None, "Vàng", "Quan tâm chính sách trả góp 0% qua thẻ tín dụng."),
            (None, "Nguyễn Tuấn Anh", "0933221100", "anh.nguyen@gmail.com", None, None, "Bạc", "Khách hàng mới tiếp cận qua Webchat.")
        ]
        cursor.executemany("""
            INSERT INTO customers (user_id, full_name, phone, email, zalo_id, fb_id, member_rank, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, sample_customers)
        conn.commit()

    # Seed Sample Tickets if none exist
    cursor.execute("SELECT COUNT(*) FROM tickets")
    ticket_count = cursor.fetchone()[0]
    if ticket_count == 0:
        print("[DB INIT] Khởi tạo phiếu hỗ trợ (tickets) mẫu...")
        sample_tickets = [
            ("TK-202610-001", 1, "Lê Văn Hùng", "0987654321", "hung.le@gmail.com", "web", "Màn hình iPhone 15 Pro Max xuất hiện sọc xanh mép phải", "high", "in_progress", 2),
            ("TK-202610-002", 2, "Trần Thị Mai", "0912345678", "mai.tran@gmail.com", "zalo", "Tư vấn hồ sơ trả góp 0% Galaxy S24 Ultra qua thẻ Sacombank", "medium", "open", 2),
            ("TK-202610-003", 3, "Nguyễn Tuấn Anh", "0933221100", "anh.nguyen@gmail.com", "facebook", "Hỏi chính sách bảo hành 1 đổi 1 và quà tặng Xiaomi 14", "low", "resolved", 3)
        ]
        cursor.executemany("""
            INSERT INTO tickets (ticket_code, customer_id, customer_name, customer_phone, customer_email, channel, subject, priority, status, assigned_agent_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, sample_tickets)
        conn.commit()

        # Seed Sample Ticket Messages
        sample_msgs = [
            (1, "customer", "Lê Văn Hùng", "Em ơi máy iPhone 15 Pro Max mới mua được 2 tháng tự dưng mép phải màn hình có sọc xanh lá, bên em có nhận bảo hành không?"),
            (1, "agent", "Nguyễn Văn Hỗ Trợ", "Dạ chào anh Hùng! Máy còn trong thời gian bảo hành và không bị rơi vỡ hay vào nước bên em sẽ gửi hãng thay màn hình miễn phí cho anh ạ. Anh có thể mang qua chi nhánh gần nhất nhé!"),
            (2, "customer", "Trần Thị Mai", "Mình muốn mua Galaxy S24 Ultra trả góp qua thẻ Sacombank thì có mất phí chuyển đổi không shop?"),
            (2, "agent", "Nguyễn Văn Hỗ Trợ", "Dạ chào chị Mai, bên em đang có chương trình liên kết Sacombank trả góp 0% lãi suất và miễn 100% phí chuyển đổi kỳ hạn 6-12 tháng ạ.")
        ]
        cursor.executemany("""
            INSERT INTO ticket_messages (ticket_id, sender_type, sender_name, message)
            VALUES (%s, %s, %s, %s)
        """, sample_msgs)
        conn.commit()

    conn.close()
    print("[DB INIT] Khởi tạo cơ sở dữ liệu CRM & Bán hàng hoàn tất thành công!")

if __name__ == "__main__":
    init_database()
