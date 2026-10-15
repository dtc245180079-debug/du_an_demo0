import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BASE_DIR / "promts" / "reqirement_agent.md"


def load_system_prompt(filepath: Path = PROMPT_PATH) -> str:
    """Read the system prompt as UTF-8 text."""
    try:
        return filepath.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Không tìm thấy file system prompt: {filepath}") from exc


def run_requirements_agent(user_requirement: str, output_file: str | None = None) -> str:
    """Analyze a requirement with Gemini's OpenAI-compatible API."""
    if not user_requirement or not user_requirement.strip():
        raise ValueError("Yêu cầu đầu vào không được để trống.")

    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Thiếu GEMINI_API_KEY. Hãy cấu hình khóa API trong file .env.")

    model = os.getenv("GEMINI_MODEL")
    if not model:
        raise RuntimeError("Thiếu GEMINI_MODEL. Hãy cấu hình tên model trong file .env.")

    system_prompt = load_system_prompt()
    client = OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    print("[Agent] Đang phân tích yêu cầu...\n")
    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Phân tích yêu cầu sau:\n{user_requirement}"},
        ],
    )

    result = response.choices[0].message.content
    if not result:
        raise RuntimeError("Model trả về nội dung rỗng.")

    print(result)

    if output_file:
        output_path = Path(output_file)
        if not output_path.is_absolute():
            output_path = BASE_DIR / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result, encoding="utf-8")
        print(f"\n[OK] Đã lưu kết quả phân tích vào: {output_path}")

    return result


if __name__ == "__main__":
    raw_requirement1 = """
    Thêm tính năng đăng nhập bằng sinh trắc học (Fingerprint/FaceID)
    và gửi mã OTP xác thực qua Zalo cho ứng dụng di động ngân hàng.
    """

    run_requirements_agent(
        user_requirement=raw_requirement1,
        output_file="outputs/biometric_login_spec.md",
    )
    raw_requirement2 = """
    Thêm tính năng Ví Voucher và áp dụng mã giảm giá tự động khi thanh toán 
    hóa đơn điện, nước, internet trên ứng dụng di động ngân hàng.
    Bệnh nhân/Khách hàng có thể lưu voucher, xem thời hạn sử dụng và hệ thống 
    tự động gợi ý voucher tối ưu nhất tại màn hình thanh toán.
    """

    run_requirements_agent(
        user_requirement=raw_requirement2,
        output_file="outputs/run_requirements2.md",
    )