import requests
import json
import time
import sys

# Đảm bảo mã hóa UTF-8 cho console Windows tránh UnicodeEncodeError khi print tiếng Việt
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

URL = "http://127.0.0.1:5000/api/chat"

TEST_CASES = [
    # 1. Câu hỏi rác, quá ngắn
    "a",
    "test",
    "alo",
    "dfdsf",
    
    # 2. Yêu cầu gặp nhân viên (Handoff trigger)
    "cho tôi gặp nhân viên",
    "cần hỗ trợ trực tiếp từ tổng đài",
    
    # 3. Ngoài phạm vi hỗ trợ
    "thời tiết hôm nay thế nào?",
    "cách nấu ăn ngon",
    
    # 4. Kỹ thuật (Tech)
    "iphone bị sọc màn hình thì làm sao?",
    "samsung bị tụt pin rất nhanh",
    
    # 5. Chính sách / Bảo hành (Policy)
    "chính sách trả góp như thế nào?",
    "có hỗ trợ 1 đổi 1 không?",
    
    # 6. Không có trong hệ thống (Sẽ vào Fallback)
    "bên bạn có bán tivi tủ lạnh không?",
    "thông tin về màn hình iPhone 15 Pro Max"
]

def run_tests():
    print("Bắt đầu kiểm thử Chatbot AI CSKH...")
    print("===================================\n")
    
    for i, question in enumerate(TEST_CASES, 1):
        print(f"Test case {i}: {question}")
        try:
            # Dùng requests.post độc lập để không lưu session/cookies
            # Tránh việc Test 5 (handoff) làm các test sau bị rơi vào chế độ chat_mode="human"
            response = requests.post(
                URL, 
                json={"question": question},
                headers={"Content-Type": "application/json"}
            )
            data = response.json()
            if data.get("success"):
                print(">> Trả lời:", data.get("answer"))
            else:
                print(">> Lỗi:", data.get("message"))
                
        except Exception as e:
            print(">> Gọi API thất bại:", e)
            
        print("-" * 50)
        time.sleep(1) # Tránh spam rate limit (nếu có)
        
if __name__ == "__main__":
    run_tests()
