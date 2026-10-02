import os
import json
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

# =====================================================================
# ABSTRACT BASE PROVIDER
# =====================================================================
class BaseAIProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass

    @abstractmethod
    def analyze_support_question(self, question: str) -> dict:
        pass

# =====================================================================
# GEMINI PROVIDER (GOOGLE GENAI)
# =====================================================================
class GeminiProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.models = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print("[AI INIT] Lỗi nạp Google GenAI Client:", e)

    def generate_text(self, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("Gemini Client chưa được cấu hình hoặc thiếu API Key.")
            
        last_err = None
        for model_name in self.models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_err = e
                continue
        raise RuntimeError(f"Tất cả model Gemini đều không khả dụng: {last_err}")

    def analyze_support_question(self, question: str) -> dict:
        prompt = f"""
        Bạn là hệ thống phân tích yêu cầu CRM hỗ trợ khách hàng của chuỗi bán lẻ thiết bị di động.
        Hãy phân tích câu hỏi và trả về DUY NHẤT một JSON hợp lệ. Không markdown, không giải thích.

        Cấu trúc JSON:
        {{
            "category": null,
            "brand": null,
            "keywords": null
        }}

        Quy tắc:
        1. category: (Kỹ thuật, Bảo hành, Trả góp, Đơn hàng, Giá cả). Nếu không rõ để null.
        2. brand: Thương hiệu (Apple, Samsung, Xiaomi, Oppo...). Nếu chung chung để null.
        3. keywords: 1 cụm từ khóa cốt lõi (ví dụ: 'sọc màn hình', 'trả góp', 'đổi trả', 'tụt pin').

        Câu hỏi: {question}
        """
        raw_text = self.generate_text(prompt)
        text = raw_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())

# =====================================================================
# OPENAI PROVIDER (OPENAI / COMPATIBLE APIS)
# =====================================================================
class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def generate_text(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("Chưa cấu hình OPENAI_API_KEY.")
            
        import requests
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        res = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=20)
        data = res.json()
        if "error" in data:
            raise RuntimeError(f"OpenAI API Error: {data['error'].get('message', '')}")
        return data["choices"][0]["message"]["content"]

    def analyze_support_question(self, question: str) -> dict:
        prompt = f"""
        Phân tích câu hỏi hỗ trợ khách hàng và trả về DUY NHẤT một JSON hợp lệ:
        {{"category": null, "brand": null, "keywords": null}}
        Câu hỏi: {question}
        """
        raw_text = self.generate_text(prompt)
        text = raw_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())

# =====================================================================
# INTELLIGENT MOCK / OFFLINE FALLBACK PROVIDER
# =====================================================================
class MockFallbackProvider(BaseAIProvider):
    """
    Fallback Provider dự phòng khi mạng gặp sự cố hoặc vượt giới hạn API quota.
    Đảm bảo hệ thống CSKH hoạt động 24/7 mà không gián đoạn.
    """
    def generate_text(self, prompt: str) -> str:
        if "DỮ LIỆU TỪ HỆ THỐNG CSKH" in prompt and "CÂU HỎI CỦA KHÁCH HÀNG" in prompt:
            # Rút trích câu hỏi và tài liệu để trả lời thông minh dựa trên rules
            parts = prompt.split("CÂU HỎI CỦA KHÁCH HÀNG")
            q_part = parts[1].split("QUY TẮC BẮT BUỘC")[0].strip() if len(parts) > 1 else ""
            return f"Dạ em chào anh/chị ạ! Về câu hỏi '{q_part}', hệ thống CSKH đã tiếp nhận. Em xin hướng dẫn: Quý khách vui lòng kiểm tra chính sách bảo hành hoặc để lại số điện thoại để chuyên viên gọi điện tư vấn chi tiết nhất ạ!"
        return "Dạ em chào anh/chị! Em đã ghi nhận thông tin và sẽ phản hồi ngay ạ."

    def analyze_support_question(self, question: str) -> dict:
        q_lower = question.lower()
        brand = None
        for b in ["apple", "iphone", "ipad", "macbook", "samsung", "xiaomi", "oppo"]:
            if b in q_lower:
                brand = "Apple" if b in ["apple", "iphone", "ipad", "macbook"] else b.capitalize()
                break
                
        category = "Kỹ thuật"
        if any(w in q_lower for w in ["trả góp", "lãi suất", "thẻ tín dụng", "ngân hàng"]):
            category = "Trả góp"
        elif any(w in q_lower for w in ["bảo hành", "đổi trả", "1 đổi 1", "rơi vỡ"]):
            category = "Bảo hành"
        elif any(w in q_lower for w in ["đơn hàng", "giao hàng", "vận chuyển", "bao lâu"]):
            category = "Đơn hàng"
            
        keywords = None
        for kw in ["sọc màn hình", "trả góp", "tụt pin", "pin ảo", "không lên nguồn", "camera mờ", "bảo hành"]:
            if kw in q_lower:
                keywords = kw
                break
                
        return {"category": category, "brand": brand, "keywords": keywords}

# =====================================================================
# EXTENSIBLE AI SERVICE WITH CHAINED FALLBACK
# =====================================================================
class AIService:
    def __init__(self):
        self.providers = []
        preferred = os.getenv("AI_PROVIDER", "gemini").lower()
        
        # Thứ tự thử nghiệm: Ưu tiên provider cấu hình -> Provider còn lại -> Mock fallback
        if preferred == "mock":
            self.providers.append(("Mock", MockFallbackProvider()))
        elif preferred == "openai":
            self.providers.append(("OpenAI", OpenAIProvider()))
            self.providers.append(("Gemini", GeminiProvider()))
        else:
            self.providers.append(("Gemini", GeminiProvider()))
            self.providers.append(("OpenAI", OpenAIProvider()))
            
        self.fallback_provider = MockFallbackProvider()

    def generate_text(self, prompt: str) -> str:
        for name, provider in self.providers:
            try:
                return provider.generate_text(prompt)
            except Exception as e:
                print(f"[AI SERVICE] Provider {name} thất bại ({e}), chuyển fallback tiếp theo...")
                continue
        # Khi tất cả provider ngoài đều lỗi -> dùng fallback provider
        return self.fallback_provider.generate_text(prompt)

    def analyze_support_question(self, question: str) -> dict:
        for name, provider in self.providers:
            try:
                return provider.analyze_support_question(question)
            except Exception:
                continue
        return self.fallback_provider.analyze_support_question(question)

    def suggest_smart_replies(self, customer_message: str, faqs: list = None) -> list:
        """
        Tự động tạo 3 gợi ý trả lời nhanh cho nhân viên CSKH
        """
        suggestions = [
            "Dạ em chào anh/chị, em đã tiếp nhận yêu cầu và đang kiểm tra thông tin cho mình ngay đây ạ!",
            "Dạ trường hợp này anh/chị vui lòng mang máy qua chi nhánh gần nhất để kỹ thuật viên kiểm tra trực tiếp ạ.",
            "Dạ anh/chị vui lòng cung cấp số điện thoại hoặc mã đơn hàng để em tra cứu nhanh nhất ạ."
        ]
        
        if faqs and len(faqs) > 0:
            faq = faqs[0]
            solution_summary = faq.get("solution", "")[:120]
            suggestions[0] = f"Dạ theo chính sách bên em: {solution_summary}..."
            
        return suggestions

    def classify_ticket(self, subject: str, message: str) -> dict:
        """
        Phân loại tự động độ ưu tiên và chủ đề ticket
        """
        text = f"{subject} {message}".lower()
        priority = "medium"
        category = "Kỹ thuật"
        
        if any(w in text for w in ["cháy", "nổ", "nguy hiểm", "khẩn cấp", "mất tiền", "gian lận"]):
            priority = "urgent"
        elif any(w in text for w in ["sọc màn hình", "mất nguồn", "lỗi nặng", "không dùng được"]):
            priority = "high"
        elif any(w in text for w in ["tư vấn", "hỏi giá", "màu sắc", "thông số"]):
            priority = "low"
            
        if any(w in text for w in ["bảo hành", "đổi máy", "thay pin"]):
            category = "Bảo hành"
        elif any(w in text for w in ["đơn hàng", "vận chuyển", "giao hàng"]):
            category = "Đơn hàng"
        elif any(w in text for w in ["trả góp", "thanh toán", "hóa đơn"]):
            category = "Thanh toán & Trả góp"
            
        return {"priority": priority, "category": category}

# Singleton instance
ai_service = AIService()
