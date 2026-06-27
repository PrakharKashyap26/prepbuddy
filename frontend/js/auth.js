// API Base Url endpoint
const API_URL = "http://127.0.0.1:8000";

// --- Token Store Accessors ---
function getToken() {
    return localStorage.getItem("prepbuddy_token");
}

function saveToken(token) {
    localStorage.setItem("prepbuddy_token", token);
}

function clearToken() {
    localStorage.removeItem("prepbuddy_token");
    localStorage.removeItem("prepbuddy_user");
}

// --- Protected Page Guard ---
function checkAuth() {
    const token = getToken();
    if (!token) {
        // Redirect to login if token is missing
        window.location.href = "login.html";
        return false;
    }
    return true;
}

// --- Custom Auth-Augmented Fetch Wrapper ---
async function authFetch(endpoint, options = {}) {
    const token = getToken();
    
    // Setup standard headers
    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };
    
    // Inject JWT authorization header if available
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    
    const config = {
        ...options,
        headers
    };
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, config);
        
        // Handle unauthorized token state
        if (response.status === 401) {
            clearToken();
            window.location.href = "login.html";
            throw new Error("Session expired. Please log in again.");
        }
        
        return response;
    } catch (error) {
        console.error("API Request Error:", error);
        throw error;
    }
}

// --- Dynamic Notification Injector ---
function showAlert(message, type = "success") {
    // Remove existing banners if present
    const existing = document.querySelector(".alert-banner");
    if (existing) existing.remove();
    
    const banner = document.createElement("div");
    banner.classList.add("alert-banner", `alert-${type}`);
    banner.innerHTML = `
        <i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}" style="margin-right:0.5rem;"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(banner);
    
    // Automatically fade out banner
    setTimeout(() => {
        banner.style.transition = "opacity 0.4s ease";
        banner.style.opacity = "0";
        setTimeout(() => banner.remove(), 400);
    }, 3500);
}

// --- Global UI Hook for Sidebar User labels & Form Submit handlers ---
document.addEventListener("DOMContentLoaded", async () => {
    // Check if on authentication pages
    const path = window.location.pathname;
    
    // Bind Form Submit Listeners
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", handleLoginSubmit);
    }
    
    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", handleRegisterSubmit);
    }
    
    if (path.includes("login.html") || path.includes("register.html")) {
        return;
    }
    
    const token = getToken();
    if (!token) return;
    
    // Try to update current user metadata in sidebar from local cache or API
    try {
        let user = JSON.parse(localStorage.getItem("prepbuddy_user"));
        if (!user) {
            const res = await authFetch("/me");
            if (res.ok) {
                user = await res.json();
                localStorage.setItem("prepbuddy_user", JSON.stringify(user));
            }
        }
        
        if (user) {
            // Update labels in HTML sidebar
            const nameLabel = document.getElementById("sidebar-user-name");
            const skillLabel = document.getElementById("sidebar-user-skill");
            const avatarLabel = document.getElementById("sidebar-avatar-initials");
            
            if (nameLabel) nameLabel.textContent = user.name;
            if (skillLabel) skillLabel.textContent = `Skill: ${user.skill}`;
            if (avatarLabel) {
                const initials = user.name.split(" ").map(n => n[0]).join("").toUpperCase().substring(0, 2);
                avatarLabel.textContent = initials;
            }
        }
    } catch (e) {
        console.warn("Could not bind sidebar user details:", e);
    }
});

// --- Login Form Submit Handler ---
async function handleLoginSubmit(e) {
    e.preventDefault();
    
    const emailEl = document.getElementById("login-email");
    const passwordEl = document.getElementById("login-password");
    const submitBtn = e.target.querySelector("button[type='submit']");
    
    if (!emailEl || !passwordEl) return;
    
    const email = emailEl.value.trim();
    const password = passwordEl.value;
    
    if (!email || !password) {
        showAlert("Please enter your email and password.", "error");
        return;
    }
    
    // Loading State
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Checking credentials...`;
    }
    
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Authentication failed. Check your password.");
        }
        
        const data = await response.json();
        
        // Save access token
        saveToken(data.access_token);
        
        // Load User Details and Cache
        const meRes = await authFetch("/me");
        if (meRes.ok) {
            const user = await meRes.json();
            localStorage.setItem("prepbuddy_user", JSON.stringify(user));
        }
        
        showAlert("Login successful! Loading dashboard...");
        
        setTimeout(() => {
            window.location.href = "dashboard.html";
        }, 800);
        
    } catch (error) {
        console.error("Login Submit Error:", error);
        showAlert(error.message, "error");
        
        // Reset submit button state
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `Sign In`;
        }
    }
}

// --- Register Form Submit Handler ---
async function handleRegisterSubmit(e) {
    e.preventDefault();
    
    const nameEl = document.getElementById("register-name");
    const emailEl = document.getElementById("register-email");
    const passwordEl = document.getElementById("register-password");
    const skillEl = document.getElementById("register-skill");
    const submitBtn = e.target.querySelector("button[type='submit']");
    
    if (!nameEl || !emailEl || !passwordEl || !skillEl) return;
    
    const name = nameEl.value.trim();
    const email = emailEl.value.trim();
    const password = passwordEl.value;
    const skill = skillEl.value.trim();
    
    if (!name || !email || !password || !skill) {
        showAlert("Please fill in all registration fields.", "error");
        return;
    }
    
    if (password.length < 6) {
        showAlert("Password must be at least 6 characters long.", "error");
        return;
    }
    
    // Loading State
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Creating account...`;
    }
    
    try {
        // 1. Create account
        const regResponse = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ name, email, password, skill })
        });
        
        if (!regResponse.ok) {
            const err = await regResponse.json();
            throw new Error(err.detail || "Registration failed. Email might already be taken.");
        }
        
        // 2. Perform auto-login
        const loginResponse = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });
        
        if (!loginResponse.ok) {
            throw new Error("Account created but automatic login failed. Please sign in manually.");
        }
        
        const loginData = await loginResponse.json();
        saveToken(loginData.access_token);
        
        // Load User Details and Cache
        const meRes = await authFetch("/me");
        if (meRes.ok) {
            const user = await meRes.json();
            localStorage.setItem("prepbuddy_user", JSON.stringify(user));
        }
        
        showAlert("Registration successful! Setting up your workspace...");
        
        setTimeout(() => {
            window.location.href = "dashboard.html";
        }, 1000);
        
    } catch (error) {
        console.error("Register Submit Error:", error);
        showAlert(error.message, "error");
        
        // Reset submit button state
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `Create Account`;
        }
    }
}

