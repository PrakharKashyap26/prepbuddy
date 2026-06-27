document.addEventListener("DOMContentLoaded", () => {
    // 1. Enforce Authentication Guard
    if (!checkAuth()) return;
    
    // 2. Setup tab navigation event listeners
    const searchTabBtn = document.getElementById("tab-search");
    const savedTabBtn = document.getElementById("tab-saved");
    
    if (searchTabBtn && savedTabBtn) {
        searchTabBtn.addEventListener("click", () => switchTab("search"));
        savedTabBtn.addEventListener("click", () => switchTab("saved"));
    }
    
    // 3. Setup Course Search Form listener
    const searchBtn = document.getElementById("courses-search-btn");
    if (searchBtn) {
        searchBtn.addEventListener("click", searchCourses);
    }
    
    // Initialize default view
    switchTab("search");
    
    // Attempt to pre-fill search skill input from cached user details
    try {
        const user = JSON.parse(localStorage.getItem("prepbuddy_user"));
        if (user) {
            const skillInput = document.getElementById("course-skill-input");
            if (skillInput) skillInput.value = user.skill;
        }
    } catch (_) {}
});

let currentTab = "search";

function switchTab(tab) {
    currentTab = tab;
    
    const searchTabBtn = document.getElementById("tab-search");
    const savedTabBtn = document.getElementById("tab-saved");
    const searchControls = document.getElementById("search-controls-wrapper");
    const gridTitle = document.getElementById("courses-grid-title");
    
    // Update active tab buttons states
    if (tab === "search") {
        if (searchTabBtn) searchTabBtn.classList.add("active");
        if (savedTabBtn) savedTabBtn.classList.remove("active");
        if (searchControls) searchControls.style.display = "flex";
        if (gridTitle) gridTitle.textContent = "Search Results";
        
        // Show empty result placeholder if search wasn't fired
        const grid = document.getElementById("courses-display-grid");
        if (grid && grid.children.length === 0) {
            renderEmptyState("Enter a skill and topic above to search resources.");
        }
    } else {
        if (searchTabBtn) searchTabBtn.classList.remove("active");
        if (savedTabBtn) savedTabBtn.classList.add("active");
        if (searchControls) searchControls.style.display = "none";
        if (gridTitle) gridTitle.textContent = "Your Saved Courses";
        
        // Load bookmarks from database
        loadSavedCourses();
    }
}

async function searchCourses() {
    const skillInput = document.getElementById("course-skill-input");
    const topicInput = document.getElementById("course-topic-input");
    const grid = document.getElementById("courses-display-grid");
    
    if (!skillInput || !topicInput || !grid) return;
    
    const skill = skillInput.value.trim();
    const topic = topicInput.value.trim();
    
    if (!skill || !topic) {
        showAlert("Please fill in both Skill and Topic fields.", "error");
        return;
    }
    
    // Render Loading view
    grid.innerHTML = `
        <div class="empty-courses">
            <i class="fa-solid fa-circle-notch fa-spin"></i>
            <p>Searching Google Custom Registry for "${skill} - ${topic}"...</p>
        </div>
    `;
    
    try {
        const response = await authFetch("/courses/search", {
            method: "POST",
            body: JSON.stringify({ skill, topic })
        });
        
        if (!response.ok) {
            throw new Error("Course search request failed.");
        }
        
        const courses = await response.json();
        grid.innerHTML = "";
        
        if (courses.length === 0) {
            renderEmptyState(`No courses found for "${skill} ${topic}". Try revising search keywords.`);
            return;
        }
        
        courses.forEach(course => {
            const card = document.createElement("div");
            card.classList.add("course-card");
            card.innerHTML = `
                <div class="course-card-body">
                    <h3>${escapeHTML(course.title)}</h3>
                    <p>${escapeHTML(course.description)}</p>
                </div>
                <div class="course-card-actions">
                    <a href="${course.url}" target="_blank" rel="noopener"><i class="fa-solid fa-up-right-from-square"></i> Visit Site</a>
                    <button class="btn btn-secondary btn-save-course" data-title="${encodeURIComponent(course.title)}" data-url="${encodeURIComponent(course.url)}" data-desc="${encodeURIComponent(course.description)}">
                        <i class="fa-regular fa-bookmark"></i> Save
                    </button>
                </div>
            `;
            grid.appendChild(card);
        });
        
        // Bind event listeners to new Save buttons
        const saveBtns = grid.querySelectorAll(".btn-save-course");
        saveBtns.forEach(btn => {
            btn.addEventListener("click", saveCourseAction);
        });
        
    } catch (error) {
        console.error("Search Courses Error:", error);
        renderEmptyState("Search failed. Check API credentials or connection status.");
    }
}

async function saveCourseAction(e) {
    const btn = e.currentTarget;
    const title = decodeURIComponent(btn.getAttribute("data-title"));
    const url = decodeURIComponent(btn.getAttribute("data-url"));
    const description = decodeURIComponent(btn.getAttribute("data-desc"));
    
    try {
        const response = await authFetch("/courses/save", {
            method: "POST",
            body: JSON.stringify({ title, url, description })
        });
        
        if (!response.ok) {
            throw new Error("Could not save course bookmark.");
        }
        
        btn.innerHTML = `<i class="fa-solid fa-bookmark" style="color:var(--primary-color);"></i> Saved`;
        btn.disabled = true;
        showAlert("Course saved to your dashboard!");
        
    } catch (err) {
        console.error("Save Course Action Error:", err);
        showAlert("Failed to bookmark course.", "error");
    }
}

async function loadSavedCourses() {
    const grid = document.getElementById("courses-display-grid");
    if (!grid) return;
    
    grid.innerHTML = `
        <div class="empty-courses">
            <i class="fa-solid fa-circle-notch fa-spin"></i>
            <p>Loading your bookmarked courses...</p>
        </div>
    `;
    
    try {
        const response = await authFetch("/courses/saved");
        if (!response.ok) {
            throw new Error("Failed to load saved courses.");
        }
        
        const savedList = await response.json();
        grid.innerHTML = "";
        
        if (savedList.length === 0) {
            renderEmptyState("You haven't bookmarked any courses yet. Go to Search Registry tab to add resources!");
            return;
        }
        
        savedList.forEach(item => {
            const card = document.createElement("div");
            card.classList.add("course-card");
            card.innerHTML = `
                <div class="course-card-body">
                    <h3>${escapeHTML(item.course.title)}</h3>
                    <p>${escapeHTML(item.course.description)}</p>
                </div>
                <div class="course-card-actions">
                    <a href="${item.course.url}" target="_blank" rel="noopener"><i class="fa-solid fa-up-right-from-square"></i> Visit Site</a>
                    <button class="btn btn-danger btn-remove-course" data-id="${item.id}">
                        <i class="fa-solid fa-trash-can"></i> Remove
                    </button>
                </div>
            `;
            grid.appendChild(card);
        });
        
        // Bind event listeners to new Remove buttons
        const removeBtns = grid.querySelectorAll(".btn-remove-course");
        removeBtns.forEach(btn => {
            btn.addEventListener("click", removeCourseAction);
        });
        
    } catch (error) {
        console.error("Load Saved Courses Error:", error);
        renderEmptyState("Could not retrieve bookmarked list.");
    }
}

async function removeCourseAction(e) {
    const btn = e.currentTarget;
    const saveId = btn.getAttribute("data-id");
    
    if (!confirm("Are you sure you want to remove this course from your saved list?")) {
        return;
    }
    
    try {
        const response = await authFetch(`/courses/remove/${saveId}`, {
            method: "DELETE"
        });
        
        if (!response.ok) {
            throw new Error("Could not remove bookmark.");
        }
        
        showAlert("Course removed successfully.");
        // Reload saved view
        loadSavedCourses();
        
    } catch (err) {
        console.error("Remove Course Action Error:", err);
        showAlert("Failed to remove bookmark.", "error");
    }
}

function renderEmptyState(text) {
    const grid = document.getElementById("courses-display-grid");
    if (grid) {
        grid.innerHTML = `
            <div class="empty-courses">
                <i class="fa-regular fa-folder-open"></i>
                <p>${text}</p>
            </div>
        `;
    }
}

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
