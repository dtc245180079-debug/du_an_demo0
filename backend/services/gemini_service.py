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
        for model_name in AVAILABLE_MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception:
                continue
    except Exception as e:
        print("[GEMINI] Lỗi khởi tạo client:", e)

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
        "keywords": null
    }}

    Quy tắc:
    1. category: Phân loại câu hỏi vào nhóm (Kỹ thuật, Bảo hành, Trả góp, Đơn hàng). Nếu không rõ để null.
    2. brand: Thương hiệu khách nhắc đến (Apple, Samsung, Xiaomi, Oppo...). Nếu hỏi chung chung để null.
    3. keywords: 1 cụm từ khóa ngắn gọn cốt lõi nhất của vấn đề (ví dụ: 'sọc màn hình', 'trả góp', 'đổi trả', 'tụt pin', 'iCloud').

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