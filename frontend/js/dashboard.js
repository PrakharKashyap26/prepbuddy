document.addEventListener("DOMContentLoaded", () => {
    // 1. Enforce Authentication Guard
    if (!checkAuth()) return;
    
    // 2. Fetch Progress Statistics
    loadDashboardData();
});

async function loadDashboardData() {
    const greetingEl = document.getElementById("welcome-greeting");
    const skillEl = document.getElementById("welcome-skill-badge");
    const statCoursesEl = document.getElementById("stat-saved-courses-val");
    const statChatsEl = document.getElementById("stat-chat-sessions-val");
    const statTopicsEl = document.getElementById("stat-topics-practiced-val");
    const tableBodyEl = document.getElementById("activity-table-body");
    const emptyStateEl = document.getElementById("empty-activity-log");
    
    try {
        const response = await authFetch("/progress");
        if (!response.ok) {
            throw new Error("Could not retrieve progress dashboard analytics.");
        }
        
        const data = await response.json();
        
        // Update user greeting and target skill
        if (greetingEl) greetingEl.textContent = `Welcome back, ${data.name}!`;
        if (skillEl) skillEl.textContent = data.skill;
        
        // Update stat counters
        if (statCoursesEl) statCoursesEl.textContent = data.saved_courses_count;
        if (statChatsEl) statChatsEl.textContent = data.chat_sessions_count;
        if (statTopicsEl) statTopicsEl.textContent = data.topics_practiced_count;
        
        // Populate recent activity log
        if (tableBodyEl) {
            tableBodyEl.innerHTML = "";
            
            if (!data.progress || data.progress.length === 0) {
                if (emptyStateEl) emptyStateEl.style.display = "block";
                return;
            }
            
            if (emptyStateEl) emptyStateEl.style.display = "none";
            
            // Loop through progress entries and build rows
            data.progress.forEach(item => {
                const row = document.createElement("tr");
                
                // Format timestamp nicely
                const accessDate = new Date(item.last_accessed);
                const formattedTime = accessDate.toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                row.innerHTML = `
                    <td><span class="topic-badge">${item.topic}</span></td>
                    <td><strong>${item.chat_count}</strong> chats</td>
                    <td class="timestamp-col">${formattedTime}</td>
                `;
                tableBodyEl.appendChild(row);
            });
        }
        
    } catch (error) {
        console.error("Dashboard Load Error:", error);
        showAlert("Failed to load dashboard statistics. Please refresh the page.", "error");
    }
}
