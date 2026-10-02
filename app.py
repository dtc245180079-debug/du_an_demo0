import sys
import os
import importlib.util

# Đảm bảo mã hóa UTF-8 cho console Windows tránh UnicodeEncodeError khi print tiếng Việt
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Thêm thư mục backend vào sys.path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Nạp module backend/app.py chính xác mà không bị xung đột tên với app.py ở root
backend_app_path = os.path.join(BACKEND_DIR, "app.py")
spec = importlib.util.spec_from_file_location("backend_app", backend_app_path)
backend_app_module = importlib.util.module_from_spec(spec)
sys.modules["backend_app"] = backend_app_module
spec.loader.exec_module(backend_app_module)

app = backend_app_module.app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Đang khởi chạy CRM Server tại: http://127.0.0.1:{port}")
    print("[*] Backend: ./backend | Frontend: ./frontend")
    app.run(debug=True, host="0.0.0.0", port=port)
