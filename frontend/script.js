/**
 * Chatbot Kinh Tế Việt Nam — Frontend Logic
 *
 * Handles:
 *  - Google OAuth 2.0 login with Cloud-Sync Polling
 *  - Chat message send/receive via API
 *  - Message rendering with sources
 *  - Session stats tracking
 *  - Sidebar toggle (mobile)
 *  - Health check polling
 *  - Multi-tab logout sync
 *
 * References:
 *  - docs/DOCS-main/skill_frontend_architecture.md
 *  - docs/DOCS-main/skill_coding_conventions.md
 */

// ------------------------------------------------------------------
// Config & State
// ------------------------------------------------------------------
const API_BASE = window.location.origin;

const state = {
    messages: [],
    isLoading: false,
    totalQuestions: 0,
    totalTime: 0,
    totalDocs: 0,
    llmProvider: "-",
    isOnline: false,
    // Auth state
    isLoggedIn: false,
    user: null,
    token: null,
    pollInterval: null,
};

// ------------------------------------------------------------------
// DOM References
// ------------------------------------------------------------------
const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const btnSend = document.getElementById("btnSend");
const welcomeScreen = document.getElementById("welcomeScreen");
const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");

// Stats elements
const statQuestions = document.getElementById("statQuestions");
const statAvgTime = document.getElementById("statAvgTime");
const statDocs = document.getElementById("statDocs");
const statLLM = document.getElementById("statLLM");
const llmName = document.getElementById("llmName");

// Auth elements
const loginOverlay = document.getElementById("loginOverlay");
const appContainer = document.getElementById("appContainer");
const btnGoogleLogin = document.getElementById("btnGoogleLogin");
const loginPolling = document.getElementById("loginPolling");
const userProfileSection = document.getElementById("userProfileSection");
const userAvatar = document.getElementById("userAvatar");
const userName = document.getElementById("userName");
const userEmail = document.getElementById("userEmail");

// ------------------------------------------------------------------
// AUTHENTICATION
// ------------------------------------------------------------------

/**
 * Initialize auth state on page load.
 * Check localStorage for existing token and verify with server.
 */
async function initAuth() {
    const savedToken = localStorage.getItem("auth_token");
    const savedUser = localStorage.getItem("auth_user");

    if (savedToken && savedUser) {
        try {
            const formData = new FormData();
            formData.append("token", savedToken);

            const res = await fetch(`${API_BASE}/api/v1/auth/verify`, {
                method: "POST",
                body: formData,
            });

            if (res.ok) {
                const data = await res.json();
                state.token = savedToken;
                state.user = data.user || JSON.parse(savedUser);
                state.isLoggedIn = true;
                showApp();
                return;
            }
        } catch (e) {
            console.warn("Token verification failed:", e);
        }

        // Token invalid — clear storage
        localStorage.removeItem("auth_token");
        localStorage.removeItem("auth_user");
    }

    showLogin();
}

/**
 * Show login screen, hide app.
 */
function showLogin() {
    loginOverlay.style.display = "flex";
    appContainer.style.display = "none";
    state.isLoggedIn = false;
}

/**
 * Show app, hide login screen. Load user profile and chat history.
 */
function showApp() {
    loginOverlay.style.display = "none";
    appContainer.style.display = "flex";

    if (state.user) {
        userProfileSection.style.display = "block";
        userName.textContent = state.user.name || "Người dùng";
        userEmail.textContent = state.user.email || "";

        if (state.user.picture) {
            userAvatar.src = state.user.picture;
            userAvatar.style.display = "block";
            // Avatar fallback: ẩn ảnh nếu load lỗi
            userAvatar.onerror = function () {
                this.style.display = "none";
            };
        } else {
            userAvatar.style.display = "none";
        }
    }

    loadChatHistory();

    if (chatInput) chatInput.focus();
}

/**
 * Load lịch sử chat của user từ database.
 */
async function loadChatHistory() {
    if (!state.token) return;

    try {
        const res = await fetch(`${API_BASE}/api/chat/history`, {
            headers: { Authorization: `Bearer ${state.token}` },
        });

        if (!res.ok) return;

        const data = await res.json();
        // Xử lý response theo chuẩn ApiSuccess
        const responseData = data.data || data;
        const messages = responseData.messages || [];

        if (messages.length > 0) {
            if (welcomeScreen) welcomeScreen.style.display = "none";

            messages.forEach((msg) => {
                if (msg.role === "user") {
                    addMessage("user", msg.content);
                } else {
                    addMessage("bot", msg.content, {
                        time: msg.response_time,
                        docsCount: msg.num_docs,
                        sources: msg.sources || [],
                    });
                }
            });

            const botMessages = messages.filter((m) => m.role === "bot");
            state.totalQuestions = botMessages.length;
            state.totalTime = botMessages.reduce((sum, m) => sum + (m.response_time || 0), 0);
            state.totalDocs = botMessages.reduce((sum, m) => sum + (m.num_docs || 0), 0);
            updateStats();
        }
    } catch (e) {
        console.warn("Could not load chat history:", e);
    }
}

/**
 * Handle Google login button click.
 * Implements Cloud-Sync Polling flow.
 */
async function handleGoogleLogin() {
    const sessionId = crypto.randomUUID();

    btnGoogleLogin.style.display = "none";
    loginPolling.style.display = "flex";

    try {
        const formData = new FormData();
        formData.append("session_id", sessionId);

        const createRes = await fetch(`${API_BASE}/api/v1/auth/login-session`, {
            method: "POST",
            body: formData,
        });

        if (!createRes.ok) {
            throw new Error("Không thể tạo phiên đăng nhập.");
        }

        // Polling for session status
        state.pollInterval = setInterval(async () => {
            try {
                const res = await fetch(`${API_BASE}/api/v1/auth/login-session/${sessionId}`);
                if (!res.ok) return;

                const data = await res.json();

                if (data.status === "completed" && data.token) {
                    clearInterval(state.pollInterval);
                    state.pollInterval = null;
                    onLoginSuccess(data.user, data.token);
                }
            } catch (pollErr) {
                console.warn("Polling error:", pollErr);
            }
        }, 2000);

        // Open Google OAuth
        const loginUrl = `${API_BASE}/api/v1/auth/google/login/flutter?session_id=${sessionId}`;

        if (window.FlutterBridge) {
            window.FlutterBridge.postMessage(`GOOGLE_LOGIN:${sessionId}`);
        } else {
            window.open(loginUrl, "_blank", "width=500,height=700,left=200,top=100");
        }

        // Timeout: 10 phút
        setTimeout(() => {
            if (state.pollInterval) {
                cancelPolling();
                alert("Phiên đăng nhập đã hết hạn. Vui lòng thử lại.");
            }
        }, 10 * 60 * 1000);
    } catch (err) {
        console.error("Login error:", err);
        cancelPolling();
        alert(`Lỗi đăng nhập: ${err.message}`);
    }
}

/**
 * Cancel polling and reset login UI.
 */
function cancelPolling() {
    if (state.pollInterval) {
        clearInterval(state.pollInterval);
        state.pollInterval = null;
    }
    btnGoogleLogin.style.display = "flex";
    loginPolling.style.display = "none";
}

/**
 * Handle successful login — persist token and show app.
 *
 * @param {Object} user - User info object from server.
 * @param {string} token - JWT access token.
 */
function onLoginSuccess(user, token) {
    state.token = token;
    state.user = user;
    state.isLoggedIn = true;

    localStorage.setItem("auth_token", token);
    localStorage.setItem("auth_user", JSON.stringify(user));

    showApp();
}

/**
 * Handle logout — clear token, reset state, show login.
 */
function handleLogout() {
    state.token = null;
    state.user = null;
    state.isLoggedIn = false;

    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_user");

    clearChat();
    showLogin();
}

// ------------------------------------------------------------------
// HEALTH CHECK
// ------------------------------------------------------------------

/**
 * Poll server health status and update UI indicators.
 */
async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE}/api/health`);
        const data = await res.json();

        // Xử lý response theo chuẩn ApiSuccess
        const healthData = data.data || data;

        state.isOnline = healthData.model_loaded;
        state.llmProvider = healthData.llm_provider || "-";

        statusDot.className = `status-dot ${healthData.model_loaded ? "online" : ""}`;
        statusText.textContent = healthData.model_loaded ? "Sẵn sàng" : "Đang khởi tạo...";

        const displayName = {
            openai: "OpenAI",
            gemini: "Gemini",
            groq: "Groq",
        };
        llmName.textContent = displayName[healthData.llm_provider] || healthData.llm_provider;
        statLLM.textContent = (displayName[healthData.llm_provider] || healthData.llm_provider || "").slice(0, 7);
    } catch (e) {
        statusDot.className = "status-dot offline";
        statusText.textContent = "Không kết nối";
        state.isOnline = false;
    }
}

checkHealth();
setInterval(checkHealth, 10000);

// ------------------------------------------------------------------
// CHAT FUNCTIONALITY
// ------------------------------------------------------------------

/**
 * Update session stats display.
 */
function updateStats() {
    statQuestions.textContent = state.totalQuestions;
    const avg =
        state.totalQuestions > 0
            ? (state.totalTime / state.totalQuestions).toFixed(1) + "s"
            : "0s";
    statAvgTime.textContent = avg;
    statDocs.textContent = state.totalDocs;
}

/**
 * Create a message element and append to chat area.
 *
 * @param {string} role - "user" or "bot".
 * @param {string} content - Message text content.
 * @param {Object} meta - Optional metadata (time, docsCount, sources).
 * @returns {HTMLElement} The created message div.
 */
function addMessage(role, content, meta = {}) {
    if (welcomeScreen) {
        welcomeScreen.style.display = "none";
    }

    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = role === "user" ? "U" : "AI";

    const body = document.createElement("div");
    body.className = "message-body";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = content;

    body.appendChild(bubble);

    // Meta info (thời gian, số tài liệu)
    if (meta.time !== undefined) {
        const metaDiv = document.createElement("div");
        metaDiv.className = "message-meta";
        metaDiv.innerHTML = `${meta.time}s`;
        if (meta.docsCount !== undefined) {
            metaDiv.innerHTML += ` &nbsp;&middot;&nbsp; ${meta.docsCount} tài liệu`;
        }
        body.appendChild(metaDiv);
    }

    // Source documents
    if (meta.sources && meta.sources.length > 0) {
        const toggleBtn = document.createElement("button");
        toggleBtn.className = "sources-toggle";
        toggleBtn.innerHTML = `Xem ${meta.sources.length} tài liệu nguồn <span class="arrow">&#9660;</span>`;

        const panel = document.createElement("div");
        panel.className = "sources-panel";

        meta.sources.forEach((src, i) => {
            const card = document.createElement("div");
            card.className = "source-card";

            const sourceName = src.source || "Không rõ nguồn";
            const fileName = sourceName.split("/").pop();

            card.innerHTML = `
                <div class="source-card-title">Tài liệu ${i + 1} -- ${fileName}</div>
                ${src.content}
            `;
            panel.appendChild(card);
        });

        toggleBtn.addEventListener("click", () => {
            toggleBtn.classList.toggle("open");
            panel.classList.toggle("open");
        });

        body.appendChild(toggleBtn);
        body.appendChild(panel);
    }

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(body);
    chatMessages.appendChild(msgDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    return msgDiv;
}

/**
 * Show typing indicator while waiting for response.
 */
function showTyping() {
    const msgDiv = document.createElement("div");
    msgDiv.className = "message bot";
    msgDiv.id = "typingMsg";

    msgDiv.innerHTML = `
        <div class="avatar">AI</div>
        <div class="message-body">
            <div class="bubble">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>
    `;

    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Remove typing indicator from chat.
 */
function hideTyping() {
    const el = document.getElementById("typingMsg");
    if (el) el.remove();
}

// ------------------------------------------------------------------
// Send Message
// ------------------------------------------------------------------

/**
 * Send user message to backend and display response.
 */
async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text || state.isLoading) return;

    addMessage("user", text);
    chatInput.value = "";
    autoResize(chatInput);

    state.isLoading = true;
    btnSend.disabled = true;
    chatInput.disabled = true;

    showTyping();

    try {
        const headers = { "Content-Type": "application/json" };
        if (state.token) {
            headers["Authorization"] = `Bearer ${state.token}`;
        }

        const res = await fetch(`${API_BASE}/api/chat`, {
            method: "POST",
            headers: headers,
            body: JSON.stringify({ question: text }),
        });

        hideTyping();

        if (!res.ok) {
            const err = await res.json();
            const errMsg = err.message || err.detail || "Không thể xử lý câu hỏi.";
            addMessage("bot", `[LỖI] ${errMsg}`);
            return;
        }

        const data = await res.json();
        // Xử lý response theo chuẩn ApiSuccess
        const chatData = data.data || data;

        addMessage("bot", chatData.answer, {
            time: chatData.response_time,
            docsCount: chatData.num_docs_graded,
            sources: chatData.sources || [],
        });

        state.totalQuestions++;
        state.totalTime += chatData.response_time;
        state.totalDocs += chatData.num_docs_graded;
        updateStats();
    } catch (e) {
        hideTyping();
        addMessage("bot", "[LỖI] Không thể kết nối đến server. Vui lòng kiểm tra server đang chạy.");
    } finally {
        state.isLoading = false;
        btnSend.disabled = false;
        chatInput.disabled = false;
        chatInput.focus();
    }
}

// ------------------------------------------------------------------
// Input Handlers
// ------------------------------------------------------------------

function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function autoResize(el) {
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 120) + "px";
}

// ------------------------------------------------------------------
// Suggestion Chips
// ------------------------------------------------------------------

function askSuggestion(chipEl) {
    chatInput.value = chipEl.textContent;
    sendMessage();
}

// ------------------------------------------------------------------
// Clear Chat
// ------------------------------------------------------------------

/**
 * Clear all chat messages and reset stats. Also clears server history.
 */
async function clearChat() {
    const messages = chatMessages.querySelectorAll(".message");
    messages.forEach((m) => m.remove());

    if (welcomeScreen) {
        welcomeScreen.style.display = "flex";
    }

    state.totalQuestions = 0;
    state.totalTime = 0;
    state.totalDocs = 0;
    updateStats();

    if (state.token) {
        try {
            await fetch(`${API_BASE}/api/chat/history`, {
                method: "DELETE",
                headers: { Authorization: `Bearer ${state.token}` },
            });
        } catch (e) {
            console.warn("Could not clear server history:", e);
        }
    }
}

// ------------------------------------------------------------------
// Sidebar Toggle (Mobile)
// ------------------------------------------------------------------

function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("open");

    let overlay = document.querySelector(".sidebar-overlay");
    if (!overlay) {
        overlay = document.createElement("div");
        overlay.className = "sidebar-overlay";
        overlay.addEventListener("click", toggleSidebar);
        document.body.appendChild(overlay);
    }
    overlay.classList.toggle("active");
}

// ------------------------------------------------------------------
// Multi-Tab Logout Sync (skill_security_authentication.md Section 6.4)
// ------------------------------------------------------------------

window.addEventListener("storage", (e) => {
    // Khi tab khác xóa token (logout), tab hiện tại cũng cập nhật
    if (e.key === "auth_token" && e.newValue === null) {
        state.token = null;
        state.user = null;
        state.isLoggedIn = false;
        showLogin();
    }
});

// ------------------------------------------------------------------
// Initialize on load
// ------------------------------------------------------------------

window.addEventListener("load", () => {
    initAuth();
});
