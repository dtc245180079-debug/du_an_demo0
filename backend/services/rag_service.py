from database.db import search_faqs, get_faqs
from services.gemini_service import analyze_support_question, generate_answer

def retrieve_faqs(question):
    faqs = []
    seen_ids = set()
    q_clean = question.strip()

    # 1. Tìm kiếm nhanh trực tiếp từ câu hỏi trước (giúp phản hồi siêu tốc, không cần đợi AI trích xuất nếu đã khớp)
    if len(q_clean) >= 2:
        quick_matches = search_faqs(keyword=q_clean)
        for f in quick_matches:
            if f["id"] not in seen_ids:
                faqs.append(f)
                seen_ids.add(f["id"])

    # 2. Nếu tìm trực tiếp chưa ra, mới nhờ AI phân tích trích xuất category / brand / keywords
    if not faqs:
        filters = analyze_support_question(question)
        print("\n[AI FILTER]", filters)
        
        category = filters.get("category")
        brand = filters.get("brand")
        keywords = filters.get("keywords")

        if category or brand:
            cb_faqs = search_faqs(category=category, brand=brand)
            for f in cb_faqs:
                if f["id"] not in seen_ids:
                    faqs.append(f)
                    seen_ids.add(f["id"])

        if keywords:
            kw_faqs = search_faqs(keyword=keywords)
            for f in kw_faqs:
                if f["id"] not in seen_ids:
                    faqs.append(f)
                    seen_ids.add(f["id"])

    # 3. Fallback: Nếu vẫn chưa thấy, lấy toàn bộ FAQs (nếu <= 20) để AI tự tổng hợp
    if not faqs:
        all_faqs = get_faqs()
        if len(all_faqs) <= 20:
            faqs = all_faqs
        else:
            faqs = search_faqs(keyword=question)

    return faqs

def build_context(faqs):
    if not faqs:
        return "Hệ thống chưa có thông tin hỗ trợ cho sự cố này."
    
    context = ""
    for i, faq in enumerate(faqs, start=1):
        context += f"""
--- TÀI LIỆU HỖ TRỢ {i} ---
Sự cố: {faq.get('issue_name', '')}
Danh mục: {faq.get('category', '')} - Hãng: {faq.get('brand', '')}
Biểu hiện: {faq.get('symptom', '')}
Cách xử lý: {faq.get('solution', '')}
"""
    return context

def build_prompt(context, question):
    prompt = f"""
    Bạn là Chuyên viên Chăm sóc Khách hàng (CSKH) của một hệ thống bán lẻ điện thoại di động uy tín.
    NHIỆM VỤ: Giải đáp thắc mắc, hỗ trợ lỗi kỹ thuật và tư vấn chính sách cho khách hàng dựa HOÀN TOÀN vào tài liệu bên dưới.

    ===============================
    DỮ LIỆU TỪ HỆ THỐNG CSKH
    ===============================
    {context}

    ===============================
    CÂU HỎI CỦA KHÁCH HÀNG
    ===============================
    {question}

    ===============================
    QUY TẮC BẮT BUỘC (TUÂN THỦ 100%)
    ===============================
    1. THÁI ĐỘ: Luôn lịch sự, thấu hiểu sự bất tiện của khách.
    2. CHÍNH XÁC: Tuyệt đối không tự bịa ra chính sách, giá tiền hay số tháng bảo hành nếu dữ liệu không có.
    3. TRÌNH BÀY: Hướng dẫn kỹ thuật phải dùng gạch đầu dòng ngắn gọn.
    4. KHI KHÔNG CÓ DỮ LIỆU: Nói rõ: "Dạ, hiện tại hệ thống chưa có thông tin cụ thể về trường hợp này. Anh/chị vui lòng để lại số điện thoại hoặc mang máy ra cửa hàng gần nhất để kỹ thuật viên kiểm tra ạ."
    5. XƯNG HÔ: Luôn xưng "em" và gọi khách là "anh/chị".
    """
    return prompt

def ask_rag(question):
    faqs = retrieve_faqs(question)
    context = build_context(faqs)
    prompt = build_prompt(context, question)
    answer = generate_answer(prompt)
    return {
        "answer": answer,
        "faqs": faqs
    }