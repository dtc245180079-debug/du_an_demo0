from database.db import search_faqs, get_faqs, recommend_phones
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


    # 2. Luôn nhờ AI phân tích trích xuất category / brand / keywords / budget
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

    return faqs, filters if 'filters' in locals() else {}

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
    1. THÁI ĐỘ: Luôn lịch sự, thấu hiểu sự bất tiện của khách. Luôn xưng "em" và gọi khách là "anh/chị".
    2. CHÍNH XÁC: Tuyệt đối không tự bịa ra chính sách, giá tiền hay số tháng bảo hành nếu dữ liệu không có. Hướng dẫn kỹ thuật phải dùng gạch đầu dòng ngắn gọn.
    3. PHẠM VI HỖ TRỢ: Bạn chỉ giải đáp các vấn đề liên quan đến điện thoại di động, tư vấn sản phẩm, bảo hành, chính sách mua hàng và lỗi kỹ thuật.
    4. XỬ LÝ TIN NHẮN RÁC/LẠC ĐỀ: Nếu người dùng nhập những từ vô nghĩa, quá ngắn (ví dụ: 'a', 'test', 'alo'), các ký tự rác, hoặc câu hỏi không liên quan đến điện thoại (ví dụ: thời tiết, nấu ăn, chính trị): TUYỆT ĐỐI KHÔNG được tự suy đoán hoặc bịa ra lỗi kỹ thuật để tư vấn. Thay vào đó, hãy trả lời đúng nguyên văn: 'Dạ, em chưa hiểu rõ ý của anh/chị. Anh/chị vui lòng cung cấp thêm thông tin hoặc mô tả chi tiết lỗi điện thoại đang gặp phải để em hỗ trợ nhé!'
    5. KHI KHÔNG CÓ DỮ LIỆU: Nói rõ: "Dạ, hiện tại hệ thống chưa có thông tin cụ thể về trường hợp này. Anh/chị vui lòng để lại số điện thoại hoặc mang máy ra cửa hàng gần nhất để kỹ thuật viên kiểm tra ạ."
    """
    return prompt

def ask_rag(question):
    faqs, filters = retrieve_faqs(question)
    context = build_context(faqs)
    
    budget_min = filters.get("budget_min")
    budget_max = filters.get("budget_max")
    brand = filters.get("brand")
    
    if budget_min is not None or budget_max is not None or brand is not None:
        try:
            recs = recommend_phones(budget_min=budget_min, budget_max=budget_max, preferred_brand=brand)
            if recs:
                context += "\n--- DANH SÁCH ĐIỆN THOẠI ĐỀ XUẤT (TỪ HỆ THỐNG KINH DOANH) ---\n"
                for i, r in enumerate(recs[:5], start=1):
                    price = r.get('promo_price') or r.get('listed_price', 0)
                    context += f"{i}. Tên máy: {r['name']} | Giá: {price:,} đ | Tồn kho: {r.get('stock_quantity', 0)}\n"
            else:
                if budget_min is not None or budget_max is not None:
                    context += "\n--- DANH SÁCH ĐIỆN THOẠI ĐỀ XUẤT (TỪ HỆ THỐNG KINH DOANH) ---\n"
                    context += "KHÔNG TÌM THẤY SẢN PHẨM PHÙ HỢP\n"
        except Exception as e:
            print("Lỗi khi gọi recommend_phones:", e)
            
    prompt = build_prompt(context, question)
    answer = generate_answer(prompt)
    return {
        "answer": answer,
        "faqs": faqs
    }