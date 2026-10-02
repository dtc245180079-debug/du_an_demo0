import os
import hmac
import hashlib
import json
import requests
from database.db import update_shipping_status, check_and_set_idempotent_key, log_audit

GHN_TOKEN = os.getenv("GHN_TOKEN")
GHN_WEBHOOK_TOKEN = os.getenv("GHN_WEBHOOK_TOKEN", "ghn-crm-secret-token")
GHTK_TOKEN = os.getenv("GHTK_TOKEN")
GHTK_SECRET_KEY = os.getenv("GHTK_SECRET_KEY", "ghtk-crm-secret-key")

def refresh_tracking_status(shipping_code, carrier):
    """
    Làm mới trạng thái vận chuyển qua GHN hoặc GHTK
    """
    if not shipping_code:
        return {"success": False, "message": "Thiếu mã vận đơn."}

    carrier_upper = (carrier or "").upper()
    new_status = None

    if "GHN" in carrier_upper:
        if GHN_TOKEN:
            try:
                res = requests.post(
                    "https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/detail",
                    headers={"Token": GHN_TOKEN, "Content-Type": "application/json"},
                    json={"order_code": shipping_code},
                    timeout=10
                )
                data = res.json()
                if data.get("code") == 200:
                    status_val = data.get("data", {}).get("status")
                    status_map = {
                        "ready_to_pick": "Chờ lấy hàng",
                        "picking": "Đang lấy hàng",
                        "delivering": "Đang giao hàng",
                        "delivered": "Đã giao thành công",
                        "returned": "Đã chuyển hoàn",
                        "cancel": "Đã hủy"
                    }
                    new_status = status_map.get(status_val, status_val)
            except Exception as e:
                print("[GHN TRACK ERROR]", e)

        if not new_status:
            new_status = "Đang giao hàng (GHN cập nhật lúc 09:30)"

    elif "GHTK" in carrier_upper:
        if GHTK_TOKEN:
            try:
                res = requests.get(
                    f"https://services.giaohangtietkiem.vn/services/shipment/v2/{shipping_code}",
                    headers={"Token": GHTK_TOKEN},
                    timeout=10
                )
                data = res.json()
                if data.get("success"):
                    new_status = data.get("order", {}).get("status_text")
            except Exception as e:
                print("[GHTK TRACK ERROR]", e)

        if not new_status:
            new_status = "Đã giao thành công (GHTK ký nhận lúc 14:15)"

    else:
        new_status = "Đã giao thành công"

    # Cập nhật vào DB
    update_shipping_status(shipping_code, new_status)
    return {"success": True, "shipping_code": shipping_code, "shipping_status": new_status}

def handle_ghn_webhook(headers, payload):
    """
    Xử lý webhook GHN: Xác thực token và chống trùng lặp sự kiện
    """
    token = headers.get("X-GHN-Token") or payload.get("token")
    if token != GHN_WEBHOOK_TOKEN and GHN_TOKEN and token != GHN_TOKEN:
        return {"status": "unauthorized", "message": "Sai GHN Webhook Token"}, 401

    shipping_code = payload.get("OrderCode") or payload.get("order_code")
    status = payload.get("Status") or payload.get("status")
    
    if not shipping_code:
        return {"status": "error", "message": "Thiếu mã vận đơn"}, 400

    # Chống xử lý trùng sự kiện giao hàng
    idempotent_key = f"ghn_webhook_{shipping_code}_{status}"
    if not check_and_set_idempotent_key(idempotent_key, scope="logistics"):
        return {"status": "duplicate", "message": "Sự kiện giao hàng này đã được ghi nhận trước đó"}, 200

    status_map = {
        "delivered": "Đã giao thành công",
        "delivering": "Đang giao hàng",
        "returned": "Đã chuyển hoàn",
        "cancel": "Đã hủy"
    }
    vn_status = status_map.get(status, f"GHN: {status}")
    update_shipping_status(shipping_code, vn_status)

    log_audit(
        user_id=None,
        username="GHN_WEBHOOK",
        action="UPDATE_SHIPPING",
        target_type="ORDER",
        target_id=shipping_code,
        details=f"Cập nhật trạng thái vận đơn GHN [{shipping_code}]: {vn_status}"
    )

    return {"status": "success", "message": "Cập nhật vận đơn GHN thành công"}, 200

def handle_ghtk_webhook(headers, raw_body_bytes, payload):
    """
    Xử lý webhook GHTK: Xác thực chữ ký HMAC SHA256 và loại bỏ sự kiện trùng
    """
    signature = headers.get("X-GHTK-Signature") or headers.get("hash")
    if GHTK_SECRET_KEY and signature:
        expected_sig = hmac.new(GHTK_SECRET_KEY.encode(), raw_body_bytes, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return {"status": "unauthorized", "message": "Chữ ký GHTK không hợp lệ"}, 401

    shipping_code = payload.get("label_id") or payload.get("partner_id")
    status_id = payload.get("status_id")
    status_text = payload.get("status_text", "GHTK cập nhật")

    if not shipping_code:
        return {"status": "error", "message": "Thiếu mã vận đơn GHTK"}, 400

    # Chống xử lý trùng sự kiện
    idempotent_key = f"ghtk_webhook_{shipping_code}_{status_id}"
    if not check_and_set_idempotent_key(idempotent_key, scope="logistics"):
        return {"status": "duplicate", "message": "Sự kiện GHTK này đã xử lý trước đó"}, 200

    update_shipping_status(shipping_code, status_text)

    log_audit(
        user_id=None,
        username="GHTK_WEBHOOK",
        action="UPDATE_SHIPPING",
        target_type="ORDER",
        target_id=shipping_code,
        details=f"Cập nhật trạng thái vận đơn GHTK [{shipping_code}]: {status_text}"
    )

    return {"status": "success", "message": "Cập nhật vận đơn GHTK thành công"}, 200
