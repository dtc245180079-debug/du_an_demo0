document.addEventListener("DOMContentLoaded", function () {
    const chatBtn = document.getElementById("chat-button");
    const chatWin = document.getElementById("chat-window");
    const chatClose = document.getElementById("chat-close");
    const chatInput = document.getElementById("chat-input");
    const chatSend = document.getElementById("chat-send");
    const chatMessages = document.getElementById("chat-messages");

    // Mở/Đóng chat
    if (chatBtn && chatWin) {
        chatBtn.addEventListener("click", () => { chatWin.classList.add("show"); if (chatInput) chatInput.focus(); });
    }
    if (chatClose && chatWin) {
        chatClose.addEventListener("click", () => chatWin.classList.remove("show"));
    }

    function formatMessageText(text) {
        if (!text) return "";
        const escaped = text.trim()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
        return escaped.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    }

    function addMessage(text, sender) {
        if (!chatMessages) return;
        const msgDiv = document.createElement("div");
        msgDiv.className = `chat-message ${sender}`;
        const content = document.createElement("div");
        content.className = "message-content";
        if (sender === "bot") {
            content.innerHTML = formatMessageText(text);
        } else {
            content.textContent = text;
        }
        msgDiv.appendChild(content);
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage() {
        if (!chatInput) return;
        const question = chatInput.value.trim();
        if (!question) return;

        addMessage(question, "user");
        chatInput.value = "";

        // Hiện trạng thái typing sinh động
        const typingId = "typing-" + Date.now();
        const typingDiv = document.createElement("div");
        typingDiv.className = "chat-message bot";
        typingDiv.id = typingId;
        typingDiv.innerHTML = `
            <div class="message-content" style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 13px; color: #475569;">Trợ lý AI đang tra cứu & trả lời...</span>
                <span class="typing-dots" style="display: inline-flex; gap: 3px;">
                    <span style="width: 5px; height: 5px; background: #2563eb; border-radius: 50%; animation: bounce 1.2s infinite ease-in-out;"></span>
                    <span style="width: 5px; height: 5px; background: #2563eb; border-radius: 50%; animation: bounce 1.2s infinite ease-in-out 0.2s;"></span>
                    <span style="width: 5px; height: 5px; background: #2563eb; border-radius: 50%; animation: bounce 1.2s infinite ease-in-out 0.4s;"></span>
                </span>
            </div>
            <style>
                @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1.0); } }
            </style>
        `;
        if (chatMessages) {
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: question })
            });
            const data = await response.json();

            const typingEl = document.getElementById(typingId);
            if (typingEl) typingEl.remove();

            if (data.success) {
                addMessage(data.answer, "bot");
            } else {
                addMessage("Lỗi: " + data.message, "bot");
            }
        } catch (error) {
            const typingEl = document.getElementById(typingId);
            if (typingEl) typingEl.remove();
            addMessage("Không thể kết nối tới máy chủ.", "bot");
        }
    }

    chatSend.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            sendMessage();
        }
    });
});