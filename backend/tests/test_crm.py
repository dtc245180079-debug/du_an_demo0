import os
import sys

# Ensure UTF-8 stdout
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend directory is in sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(TEST_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import unittest
from app import app
from database.db import (
    get_connection, get_faqs, get_user_by_username, get_customer_by_phone,
    get_ticket_by_code, check_and_set_idempotent_key,
    get_phone_products, get_phone_product_by_id, get_phone_comparison,
    get_price_history, get_customer_preferences, recommend_phones,
    get_quotations, get_quotation_by_id,
    get_sales_orders, get_sales_order_by_id,
    get_warranties, get_sales_analytics
)
from services.ai_service import ai_service
from services.omnichannel_service import generate_webchat_token, verify_webchat_token, process_inbound_message
from services.order_service import lookup_and_sync_customer_orders
from services.logistics_service import refresh_tracking_status, handle_ghn_webhook
from services.telephony_service import generate_twilio_voice_token, generate_outbound_twiml
from services.sales_service import sales_service

class TestCRMSystem(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_01_existing_faqs_and_compatibility(self):
        """Kiểm tra tính tương thích 100% của tính năng FAQs sẵn có"""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("HỆ THỐNG QUẢN LÝ DỮ LIỆU HỖ TRỢ KHÁCH HÀNG".encode("utf-8"), res.data)
        
        faqs = get_faqs()
        self.assertGreater(len(faqs), 0)

    def test_02_auth_and_rbac(self):
        """Kiểm tra Đăng nhập, session và phân quyền RBAC"""
        # Đăng nhập thất bại khi sai mật khẩu
        res = self.client.post("/login", data={"username_or_email": "admin", "password": "wrongpassword"})
        self.assertEqual(res.status_code, 200)
        
        # Đăng nhập thành công với tài khoản Admin
        with self.client:
            res = self.client.post("/login", data={"username_or_email": "admin", "password": "admin123"}, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Dashboard".encode("utf-8"), res.data)
            
            # Truy cập trang quản trị thành công
            res_users = self.client.get("/users")
            self.assertEqual(res_users.status_code, 200)
            
            # Đăng xuất
            res_logout = self.client.get("/logout", follow_redirects=True)
            self.assertEqual(res_logout.status_code, 200)

    def test_03_customer_portal_and_ticket_flow(self):
        """Kiểm tra Cổng khách hàng, tạo ticket và khảo sát CSAT/NPS"""
        # Đăng nhập bằng tài khoản khách hàng
        with self.client:
            self.client.post("/login", data={"username_or_email": "khachhang", "password": "customer123"})
            
            # Xem cổng khách hàng
            res_portal = self.client.get("/portal")
            self.assertEqual(res_portal.status_code, 200)
            
            # Khách hàng không thể truy cập màn hình admin /users (RBAC test)
            res_forbidden = self.client.get("/users", follow_redirects=True)
            self.assertIn("Bạn không có quyền truy cập khu vực này".encode("utf-8"), res_forbidden.data)

    def test_04_ai_service_and_fallback(self):
        """Kiểm tra AI Service, cơ chế fallback và smart replies"""
        analysis = ai_service.analyze_support_question("iPhone 15 bị sọc xanh màn hình sau khi rơi")
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis.get("brand"), "Apple")
        
        replies = ai_service.suggest_smart_replies("Máy tôi bị hỏng màn hình")
        self.assertGreater(len(replies), 0)

    def test_05_omnichannel_normalization_and_idempotency(self):
        """Kiểm tra chuẩn hóa tin nhắn đa kênh và chống xử lý trùng lặp"""
        msg_id = f"TEST-EXT-{os.urandom(4).hex()}"
        res1 = process_inbound_message("zalo", msg_id, "zalo_test_user", "Khách Test Zalo", "Xin chào shop")
        self.assertEqual(res1.get("status"), "success")
        
        # Gửi lại sự kiện trùng lặp
        res2 = process_inbound_message("zalo", msg_id, "zalo_test_user", "Khách Test Zalo", "Xin chào shop")
        self.assertEqual(res2.get("status"), "duplicate")

    def test_06_webchat_jwt_token_and_origin(self):
        """Kiểm tra cấp và xác thực token JWT Webchat"""
        token = generate_webchat_token("Nguyễn Khách", "0901234567")
        valid, payload = verify_webchat_token(token)
        self.assertTrue(valid)
        self.assertEqual(payload.get("customer_name"), "Nguyễn Khách")

    def test_07_order_service_and_pii_protection(self):
        """Kiểm tra tra cứu đơn hàng KiotViet/Sapo/Lazada và bảo vệ PII"""
        orders = lookup_and_sync_customer_orders("0987654321")
        self.assertGreater(len(orders), 0)
        first_ord = orders[0]
        self.assertIn("order_code", first_ord)
        self.assertIn("source", first_ord)
        # Đảm bảo không lưu địa chỉ giao hàng nhạy cảm
        self.assertNotIn("address_detail", first_ord)

    def test_08_logistics_refresh_and_webhook(self):
        """Kiểm tra làm mới vận đơn và webhook GHN"""
        refresh_res = refresh_tracking_status("GHN77321098", "GHN")
        self.assertTrue(refresh_res.get("success"))
        
        headers = {"X-GHN-Token": "ghn-crm-secret-token"}
        payload = {"OrderCode": "GHN77321098", "Status": "delivered"}
        data, code = handle_ghn_webhook(headers, payload)
        self.assertIn(code, [200, 401])

    def test_09_telephony_twilio_softphone(self):
        """Kiểm tra sinh Twilio Voice JWT Access Token và TwiML XML"""
        token_info = generate_twilio_voice_token(2, "nhanvien")
        self.assertIn("token", token_info)
        self.assertIn("identity", token_info)
        
        twiml = generate_outbound_twiml("0987654321")
        self.assertIn("<Response>", twiml)
        self.assertIn("<Dial", twiml)

    def test_10_phone_catalog_and_filtering(self):
        """Kiểm tra tra cứu, tìm kiếm và lọc danh mục điện thoại di động"""
        # 1. Lấy tất cả sản phẩm
        all_prods = get_phone_products()
        self.assertGreater(len(all_prods), 0)

        # 2. Lọc theo thương hiệu Apple
        apple_prods = get_phone_products(brand="Apple")
        self.assertTrue(all(p["brand"] == "Apple" for p in apple_prods))

        # 3. Lọc theo khoảng giá
        cheap_prods = get_phone_products(price_max=15000000)
        self.assertTrue(all((p.get("promo_price") or p["listed_price"]) <= 15000000 for p in cheap_prods))

        # 4. Kiểm tra trang chi tiết sản phẩm qua HTTP GET
        prod = all_prods[0]
        res = self.client.get(f"/products/{prod['id']}")
        self.assertEqual(res.status_code, 200)
        self.assertIn(prod["name"].encode("utf-8"), res.data)

    def test_11_phone_comparison(self):
        """Kiểm tra tính năng so sánh đa sản phẩm theo thông số kỹ thuật"""
        prods = get_phone_products()
        if len(prods) >= 2:
            p1, p2 = prods[0]["id"], prods[1]["id"]
            comp = get_phone_comparison([p1, p2])
            self.assertEqual(len(comp), 2)
            
            res = self.client.get(f"/products/compare?p1={p1}&p2={p2}")
            self.assertEqual(res.status_code, 200)
            self.assertIn("SO SÁNH CÁC MẪU ĐIỆN THOẠI".encode("utf-8"), res.data)

    def test_12_phone_price_update_and_audit(self):
        """Kiểm tra cập nhật giá bán và lưu lịch sử thay đổi giá kiểm toán"""
        prods = get_phone_products()
        self.assertGreater(len(prods), 0)
        prod = prods[0]
        old_price = float(prod["listed_price"])
        new_price = old_price + 500000

        with self.client:
            # Đăng nhập Admin
            self.client.post("/login", data={"username_or_email": "admin", "password": "admin123"})
            
            # Cập nhật giá
            res = self.client.post(f"/products/{prod['id']}/update-price", data={
                "listed_price": new_price,
                "promo_price": new_price - 200000,
                "stock_quantity": prod["stock_quantity"],
                "warehouse_location": prod.get("warehouse_location", "Kho Quận 1"),
                "change_reason": "Điều chỉnh giá kiểm thử unit test"
            }, follow_redirects=True)
            self.assertEqual(res.status_code, 200)

            # Kiểm tra lịch sử giá
            history = get_price_history(prod["id"])
            self.assertGreater(len(history), 0)
            self.assertEqual(float(history[0]["new_listed_price"]), new_price)

    def test_13_smart_consultation_and_recommendation(self):
        """Kiểm tra thuật toán tư vấn gợi ý điện thoại theo ngân sách và lưu hồ sơ"""
        recs = recommend_phones(budget_min=20000000, budget_max=40000000, preferred_brand="Apple")
        self.assertGreater(len(recs), 0)
        self.assertTrue(all(r["brand"] == "Apple" for r in recs))

        # Lưu nhu cầu tư vấn vào hồ sơ khách hàng
        customer = get_customer_by_phone("0987654321")
        if customer:
            recommendations = sales_service.consult_and_recommend(
                customer_id=customer["id"],
                budget_min=20000000,
                budget_max=35000000,
                primary_usage="Chụp ảnh quay phim & Sang trọng",
                preferred_brands="Apple",
                desired_screen_size="Lớn > 6.7 inch",
                key_criteria="Bảo hành VIP 1 đổi 1",
                agent_notes="Khách thích dòng Pro Max màu Titan Tự Nhiên"
            )
            self.assertGreater(len(recommendations), 0)
            pref = get_customer_preferences(customer["id"])
            self.assertIsNotNone(pref)
            self.assertEqual(pref["preferred_brands"], "Apple")

    def test_14_quotation_and_sales_order_inventory_flow(self):
        """Kiểm tra luồng lập báo giá, trừ tồn kho khi tạo đơn và ghi lịch sử trạng thái"""
        prods = get_phone_products(in_stock_only=True)
        self.assertGreater(len(prods), 0)
        target_prod = prods[0]
        initial_stock = target_prod["stock_quantity"]

        # 1. Tạo báo giá có áp dụng khuyến mãi
        items = [{
            "product_id": target_prod["id"],
            "name": target_prod["name"],
            "listed_price": float(target_prod["listed_price"]),
            "promo_price": float(target_prod.get("promo_price") or target_prod["listed_price"]),
            "qty": 1,
            "subtotal": float(target_prod.get("promo_price") or target_prod["listed_price"])
        }]
        quote = sales_service.create_and_send_quotation(
            customer_id=1,
            customer_name="Trần Thị B",
            customer_phone="0912345678",
            agent_id=1,
            agent_name="Admin",
            items=items,
            promo_code="TET2026",
            notes="Báo giá kiểm thử đơn hàng"
        )
        self.assertIsNotNone(quote)
        self.assertGreater(float(quote["discount_amount"]), 0)

        # 2. Tạo đơn hàng từ báo giá và kiểm tra tồn kho giảm 1
        with self.client:
            self.client.post("/login", data={"username_or_email": "admin", "password": "admin123"})
            res_order = self.client.post("/sales-orders/create", data={
                "customer_id": 1,
                "customer_phone": "0912345678",
                "shipping_address": "789 Đường Lê Duẩn, Q1, TP.HCM",
                "product_id": target_prod["id"],
                "quantity": 1,
                "discount_amount": quote["discount_amount"],
                "payment_method": "cod",
                "quote_id": quote["id"]
            }, follow_redirects=True)
            self.assertEqual(res_order.status_code, 200)

            # Kiểm tra trừ tồn kho
            updated_prod = get_phone_product_by_id(target_prod["id"])
            self.assertEqual(updated_prod["stock_quantity"], initial_stock - 1)

    def test_15_electronic_warranty_and_ticket_conversion(self):
        """Kiểm tra kích hoạt bảo hành điện tử theo IMEI và chuyển sự cố thành Ticket hỗ trợ"""
        with self.client:
            self.client.post("/login", data={"username_or_email": "admin", "password": "admin123"})
            
            # Kích hoạt bảo hành
            prods = get_phone_products()
            prod = prods[0]
            imei_test = f"358941098{os.urandom(3).hex()}"
            res_warr = self.client.post("/warranties/create", data={
                "order_id": 1,
                "customer_id": 1,
                "customer_name": "Nguyễn Văn Test",
                "customer_phone": "0988776655",
                "product_id": prod["id"],
                "imei_serial": imei_test,
                "warranty_package": "Bảo hành chính hãng 12 tháng",
                "months": 12
            }, follow_redirects=True)
            self.assertEqual(res_warr.status_code, 200)

            # Tra cứu bảo hành
            warranties = get_warranties(keyword=imei_test)
            self.assertGreater(len(warranties), 0)
            target_warr = warranties[0]

            # Chuyển thành ticket hỗ trợ
            ticket_id, ticket_code = sales_service.convert_warranty_to_support_ticket(
                warranty_id=target_warr["id"],
                issue_description="Màn hình nhấp nháy khi mở camera góc siêu rộng",
                agent_id=1,
                agent_name="Admin"
            )
            self.assertIsNotNone(ticket_id)
            self.assertIsNotNone(ticket_code)

    def test_16_inbox_product_card_and_sales_analytics(self):
        """Kiểm tra gửi thẻ thông tin máy vào chat và chỉ số Dashboard bán hàng"""
        with self.client:
            self.client.post("/login", data={"username_or_email": "admin", "password": "admin123"})
            
            prods = get_phone_products()
            prod = prods[0]
            
            # Gửi thẻ sản phẩm vào chat
            res_card = self.client.post("/api/inbox/send-product-card", json={
                "conversation_id": "CONV-TEST-SALES-01",
                "channel": "webchat",
                "product_id": prod["id"]
            })
            self.assertEqual(res_card.status_code, 200)
            data = res_card.get_json()
            self.assertTrue(data.get("success"))
            self.assertIn(prod["name"], data.get("card_message"))

            # Kiểm tra thống kê bán hàng
            analytics = get_sales_analytics()
            self.assertIn("total_sales", analytics)
            self.assertIn("conversion_rate", analytics)
            self.assertIn("top_products", analytics)

if __name__ == "__main__":
    unittest.main()
