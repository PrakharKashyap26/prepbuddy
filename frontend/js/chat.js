document.addEventListener("DOMContentLoaded", () => {
    // 1. Enforce Authentication Guard
    if (!checkAuth()) return;
    
    // 2. Fetch conversational history
    loadChatHistory();
    
    // 3. Setup event listeners
    const sendBtn = document.getElementById("chat-send-btn");
    const inputField = document.getElementById("chat-input-text");
    const clearBtn = document.getElementById("chat-clear-btn");
    
    if (sendBtn) {
        sendBtn.addEventListener("click", sendMessage);
    }
    if (inputField) {
        inputField.addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendMessage();
        });
    }
    if (clearBtn) {
        clearBtn.addEventListener("click", clearHistory);
    }
    
    // Setup click triggers for Socratic prompt helper suggestions
    const promptTags = document.querySelectorAll(".prompt-tag");
    promptTags.forEach(tag => {
        tag.addEventListener("click", () => {
            if (inputField) {
                inputField.value = tag.textContent;
                inputField.focus();
            }
        });
    });
});

async function loadChatHistory() {
    const scrollContainer = document.getElementById("chat-scroll-container");
    const emptyState = document.getElementById("chat-empty-state");
    
    try {
        const response = await authFetch("/chat/history");
        if (!response.ok) {
            throw new Error("Could not pull chat logs.");
        }
        
        const history = await response.json();
        
        if (scrollContainer) {
            scrollContainer.innerHTML = "";
            
            if (history.length === 0) {
                if (emptyState) emptyState.style.display = "flex";
                return;
            }
            
            if (emptyState) emptyState.style.display = "none";
            
            history.forEach(chat => {
                appendChatBubble("user", chat.message, chat.timestamp);
                appendChatBubble("ai", chat.response, chat.timestamp);
            });
            
            scrollChatToBottom();
        }
        
    } catch (e) {
        console.error("Chat Logs Load Error:", e);
        showAlert("Failed to retrieve chat history.", "error");
    }
}

function appendChatBubble(role, text, timestampStr = null) {
    const scrollContainer = document.getElementById("chat-scroll-container");
    const emptyState = document.getElementById("chat-empty-state");
    
    if (emptyState) emptyState.style.display = "none";
    if (!scrollContainer) return;
    
    const row = document.createElement("div");
    row.classList.add("chat-row", role === "user" ? "chat-row-user" : "chat-row-ai");
    
    // Format timestamp
    const date = timestampStr ? new Date(timestampStr) : new Date();
    const formattedTime = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    row.innerHTML = `
        <div class="chat-bubble ${role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'}">
            <div class="bubble-text">${formatMessageText(text)}</div>
            <span class="chat-time">${formattedTime}</span>
        </div>
    `;
    
    scrollContainer.appendChild(row);
}

async function sendMessage() {
    const inputField = document.getElementById("chat-input-text");
    if (!inputField) return;
    
    const text = inputField.value.trim();
    if (!text) return;
    
    // 1. Clear input field immediately
    inputField.value = "";
    
    // 2. Append user bubble locally
    appendChatBubble("user", text);
    scrollChatToBottom();
    
    // 3. Append temporary loading bubble for AI
    const scrollContainer = document.getElementById("chat-scroll-container");
    const loadingRow = document.createElement("div");
    loadingRow.classList.add("chat-row", "chat-row-ai");
    loadingRow.id = "chat-ai-loading-bubble";
    loadingRow.innerHTML = `
        <div class="chat-bubble chat-bubble-ai">
            <div class="bubble-text"><i class="fa-solid fa-circle-notch fa-spin"></i> Buddy is formulating guiding hints...</div>
        </div>
    `;
    scrollContainer.appendChild(loadingRow);
    scrollChatToBottom();
    
    // Get target practice topic (defaults to current user skill if cached)
    let topic = null;
    try {
        const cachedUser = JSON.parse(localStorage.getItem("prepbuddy_user"));
        if (cachedUser) topic = cachedUser.skill;
    } catch (_) {}
    
    try {
        const response = await authFetch("/chat", {
            method: "POST",
            body: JSON.stringify({ message: text, topic: topic })
        });
        
        // Remove loading bubble
        const loader = document.getElementById("chat-ai-loading-bubble");
        if (loader) loader.remove();
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "AI message post failed.");
        }
        
        const chatOut = await response.json();
        
        // Append AI response bubble
        appendChatBubble("ai", chatOut.response, chatOut.timestamp);
        scrollChatToBottom();
        
    } catch (error) {
        console.error("Post Chat Message Error:", error);
        const loader = document.getElementById("chat-ai-loading-bubble");
        if (loader) loader.remove();
        
        appendChatBubble("ai", "Sorry, I had trouble connecting. Please check your local server or API configurations.");
        scrollChatToBottom();
    }
}

async function clearHistory() {
    if (!confirm("Are you sure you want to clear all conversation history? This cannot be undone.")) {
        return;
    }
    
    try {
        const response = await authFetch("/chat/history", {
            method: "DELETE"
        });
        
        if (!response.ok) {
            throw new Error("Could not wipe chat history.");
        }
        
        const scrollContainer = document.getElementById("chat-scroll-container");
        const emptyState = document.getElementById("chat-empty-state");
        
        if (scrollContainer) scrollContainer.innerHTML = "";
        if (emptyState) emptyState.style.display = "flex";
        
        showAlert("Conversation logs successfully cleared.");
        
    } catch (e) {
        console.error("Clear Chat History Error:", e);
        showAlert("Failed to wipe history log.", "error");
    }
}

function scrollChatToBottom() {
    const scrollContainer = document.getElementById("chat-scroll-container");
    if (scrollContainer) {
        // Immediate scroll anchor
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
        
        // Micro-timeout fallback to guarantee capture of DOM layout reflows
        setTimeout(() => {
            scrollContainer.scrollTop = scrollContainer.scrollHeight;
        }, 50);
    }
}

// Formatter to render Markdown code snippets, bullets, and spacing securely
function formatMessageText(text) {
    let escaped = escapeHTML(text);
    
    // 1. Format fenced code blocks: ```lang\ncode\n```
    escaped = escaped.replace(/```(?:[a-zA-Z0-9]+)?\n([\s\S]+?)\n```/g, (match, code) => {
        return `<pre><code>${code}</code></pre>`;
    });
    
    // 2. Format inline code highlights: `code`
    escaped = escaped.replace(/`([^`\n]+)`/g, '<code>$1</code>');
    
    // 3. Format lists/bullet points: \n- item
    escaped = escaped.replace(/(?:^|\n)[-*]\s+([^\n]+)/g, '<br>&bull; $1');
    
    // 4. Format generic spacing line breaks
    escaped = escaped.replace(/\n/g, '<br>');
    
    return escaped;
}

// Helper to escape HTML tags to prevent XSS issues
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}
