import os
import json
from dotenv import load_dotenv

load_dotenv()

AVAILABLE_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.8-flash"
]

def clean_json_response(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def call_gemini(prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        from services.ai_service import ai_service
        return ai_service.generate_text(prompt)

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        if response and response.text:
            return response.text
    except Exception as e:
        print(f"[GEMINI] Lỗi gọi model {os.getenv('GEMINI_MODEL')}:", e)

    # Cơ chế fallback mở rộng
    from services.ai_service import ai_service
    return ai_service.generate_text(prompt)

def analyze_support_question(question):
    prompt = f"""
    Bạn là hệ thống phân tích yêu cầu CRM hỗ trợ khách hàng của chuỗi bán lẻ điện thoại.
    Hãy phân tích câu hỏi và trả về DUY NHẤT một JSON hợp lệ. Không giải thích thêm.

    Cấu trúc JSON:
    {{
        "category": null,
        "brand": null,
        "keywords": null,
        "budget_min": null,
        "budget_max": null
    }}

    Quy tắc:
    1. category: Phân loại câu hỏi vào nhóm (Kỹ thuật, Bảo hành, Trả góp, Đơn hàng, Tư vấn mua hàng). Nếu không rõ để null.
    2. brand: Thương hiệu khách nhắc đến (Apple, Samsung, Xiaomi, Oppo...). Nếu hỏi chung chung để null.
    3. keywords: 1 cụm từ khóa ngắn gọn cốt lõi nhất của vấn đề (ví dụ: 'sọc màn hình', 'trả góp', 'đổi trả', 'tụt pin', 'iCloud').
    4. budget_min: Số tiền tối thiểu khách muốn mua (kiểu số nguyên). Ví dụ: "trên 5 triệu" -> 5000000. Nếu không có để null.
    5. budget_max: Số tiền tối đa khách muốn mua (kiểu số nguyên). Ví dụ: "dưới 10 triệu" -> 10000000. Nếu không có để null.

    Câu hỏi của khách: {question}
    """
    try:
        raw_text = call_gemini(prompt)
        text = clean_json_response(raw_text)
        return json.loads(text)
    except Exception:
        from services.ai_service import ai_service
        return ai_service.analyze_support_question(question)

def generate_answer(prompt):
    return call_gemini(prompt)