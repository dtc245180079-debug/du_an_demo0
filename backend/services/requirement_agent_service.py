import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent
AGENT_DIR = ROOT_DIR / "Agent"
PROMPT_PATH = AGENT_DIR / "promts" / "reqirement_agent.md"
BACKUP_PROMPT_PATH = BASE_DIR / "reqirement_agent_prompt.md"
OUTPUTS_DIR = AGENT_DIR / "outputs"

def load_system_prompt() -> str:
    """Đọc system prompt từ Agent/promts/reqirement_agent.md hoặc file backup."""
    if PROMPT_PATH.exists():
        try:
            return PROMPT_PATH.read_text(encoding="utf-8")
        except Exception:
            pass
    if BACKUP_PROMPT_PATH.exists():
        try:
            return BACKUP_PROMPT_PATH.read_text(encoding="utf-8")
        except Exception:
            pass
    return "Bạn là một Senior Business Analyst và System Architect phân tích yêu cầu phần mềm."

def analyze_requirement(user_requirement: str, save_to_file: bool = True) -> dict:
    """
    Phân tích yêu cầu thô bằng AI Agent (kết hợp logic của Agent/agent_runner.py và gemini_service).
    Trả về dict: {"content": result_text, "saved_filename": filename_or_none}
    """
    if not user_requirement or not user_requirement.strip():
        raise ValueError("Yêu cầu đầu vào không được để trống.")

    system_prompt = load_system_prompt()
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    result = None

    # 1. Thử dùng OpenAI client kết nối Gemini endpoint (giống Agent/agent_runner.py)
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        response = client.chat.completions.create(
            model=model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Phân tích yêu cầu sau:\n{user_requirement}"},
            ],
        )
        if response and response.choices and response.choices[0].message:
            result = response.choices[0].message.content
    except Exception as e:
        print("[AGENT RUNNER] OpenAI client không khả dụng, chuyển sang fallback:", e)

    # 2. Fallback sang Gemini SDK nội bộ của dự án
    if not result:
        from services.gemini_service import call_gemini
        full_prompt = f"{system_prompt}\n\n--- YÊU CẦU TỪ NGƯỜI DÙNG ---\n{user_requirement}"
        result = call_gemini(full_prompt)

    if not result:
        raise RuntimeError("AI không phản hồi nội dung. Vui lòng kiểm tra GEMINI_API_KEY trong file .env.")

    # 3. Đồng bộ lưu file kết quả vào Agent/outputs/
    saved_filename = None
    if save_to_file:
        try:
            OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_filename = f"spec_{timestamp}.md"
            filepath = OUTPUTS_DIR / saved_filename
            filepath.write_text(result, encoding="utf-8")
        except Exception as e:
            print("[AGENT OUTPUT] Không thể lưu file output:", e)

    return {
        "content": result,
        "saved_filename": saved_filename
    }

def get_recent_specs() -> list:
    """Lấy danh sách các tài liệu đặc tả yêu cầu đã được lưu trong Agent/outputs/"""
    specs = []
    if OUTPUTS_DIR.exists():
        for file in sorted(OUTPUTS_DIR.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True):
            try:
                content = file.read_text(encoding="utf-8")
                # Lấy 1-2 dòng đầu làm tóm tắt
                lines = [line.strip().replace('#', '').strip() for line in content.splitlines() if line.strip() and not line.startswith("---")]
                title = lines[0] if lines else file.stem
                if len(title) > 80:
                    title = title[:77] + "..."
                specs.append({
                    "filename": file.name,
                    "title": title,
                    "size_kb": round(file.stat().st_size / 1024, 1),
                    "modified_time": datetime.fromtimestamp(file.stat().st_mtime).strftime("%d/%m/%Y %H:%M"),
                    "content": content
                })
            except Exception:
                continue
    return specs
