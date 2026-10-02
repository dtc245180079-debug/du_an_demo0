import os
import json
import datetime
from database.db import (
    get_phone_products, get_phone_product_by_id, recommend_phones,
    save_customer_preferences, get_customer_preferences,
    create_quotation, get_quotation_by_id, update_quotation_status,
    create_sales_order, get_sales_order_by_id, update_sales_order_status,
    create_warranty, get_warranties, get_warranty_by_id,
    create_ticket, add_ticket_message, save_omnichannel_message,
    get_promotion_by_code, log_audit, get_connection
)

class SalesService:
    @staticmethod
    def consult_and_recommend(customer_id, budget_min, budget_max, primary_usage, preferred_brands, desired_screen_size, key_criteria, agent_notes=None):
        """
        Lưu nhu cầu tư vấn khách hàng và đề xuất các sản phẩm điện thoại phù hợp
        dựa trên thông số, giá và tình trạng hàng thực tế hiện hữu
        """
        # 1. Lưu nhu cầu tư vấn vào hồ sơ khách hàng
        recommendations = recommend_phones(
            budget_min=budget_min,
            budget_max=budget_max,
            usage=primary_usage,
            preferred_brand=preferred_brands,
            screen_size=desired_screen_size
        )
        
        interested_pids = ",".join([str(p["id"]) for p in recommendations[:3]])
        save_customer_preferences(
            customer_id=customer_id,
            budget_min=budget_min,
            budget_max=budget_max,
            primary_usage=primary_usage,
            preferred_brands=preferred_brands,
            desired_screen_size=desired_screen_size,
            key_criteria=key_criteria,
            interested_products=interested_pids,
            agent_notes=agent_notes
        )
        
        return recommendations

    @staticmethod
    def send_product_card_to_chat(channel, conversation_id, product_id, agent_name="Chuyên viên Tư vấn"):
        """
        Gửi thẻ thông tin sản phẩm và báo giá trực tiếp vào cuộc trò chuyện đa kênh
        """
        prod = get_phone_product_by_id(product_id)
        if not prod:
            return None

        # Kiểm tra tồn kho theo nguyên tắc: không tự khẳng định còn hàng nếu dữ liệu không có
        stock_msg = f"Còn hàng ({prod['stock_quantity']} máy tại {prod['warehouse_location']})" if prod['stock_quantity'] > 0 else "Tạm hết hàng tại kho"
        
        price_text = f"{prod['promo_price']:,.0f} ₫" if prod.get('promo_price') else f"{prod['listed_price']:,.0f} ₫"
        listed_text = f" (Niêm yết: {prod['listed_price']:,.0f} ₫)" if prod.get('promo_price') and prod['promo_price'] < prod['listed_price'] else ""

        card_message = (
            f"[GỢI Ý SẢN PHẨM PHÙ HỢP]\n"
            f"Tên máy: {prod['name']} ({prod['brand']})\n"
            f"Giá ưu đãi: {price_text}{listed_text}\n"
            f"Tình trạng: {stock_msg}\n"
            f"Cấu hình: {prod['chip_spec']} | RAM {prod['ram_spec']} | ROM {prod['storage_spec']}\n"
            f"Camera: {prod['camera_spec']}\n"
            f"Pin: {prod['battery_spec']}\n"
            f"Bảo hành: {prod['warranty_months']} tháng chính hãng\n"
            f"Xem chi tiết sản phẩm: /products/{prod['id']}"
        )

        save_omnichannel_message(
            external_msg_id=f"CARD-{int(datetime.datetime.now().timestamp()*1000)}",
            conversation_id=conversation_id,
            channel=channel,
            sender_type="agent",
            sender_id="agent",
            sender_name=agent_name,
            content=card_message,
            direction="outbound"
        )
        return card_message

    @staticmethod
    def create_and_send_quotation(customer_id, customer_name, customer_phone, agent_id, agent_name, items, promo_code=None, notes=None, channel=None, conversation_id=None):
        """
        Tạo báo giá, áp dụng khuyến mãi và gửi vào hộp thư đa kênh nếu được yêu cầu
        """
        discount_amount = 0.0
        if promo_code:
            promo = get_promotion_by_code(promo_code)
            if promo:
                total_check = sum(item.get("promo_price", item.get("listed_price", 0)) * item.get("qty", 1) for item in items)
                if total_check >= float(promo.get("min_order_amount", 0)):
                    if promo["discount_type"] == "fixed":
                        discount_amount = float(promo["discount_value"])
                    elif promo["discount_type"] == "percent":
                        discount_amount = total_check * (float(promo["discount_value"]) / 100.0)

        quote_id, quote_code = create_quotation(
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            agent_id=agent_id,
            agent_name=agent_name,
            items=items,
            discount_amount=discount_amount,
            promotion_code=promo_code,
            notes=notes
        )

        quote = get_quotation_by_id(quote_id)

        # Nếu có hội thoại, gửi thẻ báo giá vào chat
        if channel and conversation_id and quote:
            items_desc = "\n".join([f"• {it['name']} x{it['qty']}: {it['subtotal']:,.0f} ₫" for it in quote['items']])
            quote_msg = (
                f"[BÁO GIÁ ĐIỆN THOẠI CHÍNH THỨC]\n"
                f"Mã báo giá: {quote_code}\n"
                f"Kính gửi: {customer_name} ({customer_phone})\n"
                f"----------------------------------------\n"
                f"{items_desc}\n"
                f"----------------------------------------\n"
                f"Tổng tiền niêm yết: {quote['total_listed_amount']:,.0f} ₫\n"
                f"Khuyến mãi ({quote.get('promotion_code') or 'Không'}): -{quote['discount_amount']:,.0f} ₫\n"
                f"TỔNG THANH TOÁN: {quote['final_amount']:,.0f} ₫\n"
                f"Ghi chú: {notes or 'Báo giá có hiệu lực trong 7 ngày'}\n"
                f"Hạn báo giá: {quote['expiry_date'].strftime('%d/%m/%Y') if quote.get('expiry_date') else '7 ngày'}"
            )
            save_omnichannel_message(
                external_msg_id=f"QUOTE-{quote_code}",
                conversation_id=conversation_id,
                channel=channel,
                sender_type="agent",
                sender_id=str(agent_id),
                sender_name=agent_name,
                content=quote_msg,
                direction="outbound"
            )

        log_audit(agent_id, agent_name, "CREATE_QUOTATION", "QUOTATION", quote_id, f"Báo giá {quote_code}: {quote['final_amount']:,.0f} ₫")
        return quote

    @staticmethod
    def convert_warranty_to_support_ticket(warranty_id, issue_description, agent_id, agent_name):
        """
        Tiếp nhận yêu cầu bảo hành/đổi trả và tạo thành Ticket hỗ trợ
        """
        warr = get_warranty_by_id(warranty_id)
        if not warr:
            return None, "Bảo hành không tồn tại"

        subject = f"Yêu cầu bảo hành: {warr['product_name']} (IMEI: {warr['imei_serial']})"
        ticket_id, ticket_code = create_ticket(
            customer_id=warr["customer_id"],
            customer_name=warr["customer_name"],
            customer_phone=warr["customer_phone"],
            customer_email=None,
            channel="web",
            subject=subject,
            priority="high",
            first_message=f"Gói bảo hành: {warr['warranty_package']}\nHạn bảo hành: {warr['end_date']}\nMô tả sự cố từ khách: {issue_description}"
        )

        log_audit(agent_id, agent_name, "CREATE_WARRANTY_TICKET", "TICKET", ticket_id, f"Mở ticket từ bảo hành {warr['warranty_code']}")
        return ticket_id, ticket_code

sales_service = SalesService()
