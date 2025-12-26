// Configuration
const API_BASE_URL = "http://127.0.0.1:8000/api";

// State
let allRequests = [];
let currentRequestId = null;

// ===== INITIALIZATION =====
document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 App initialized");
    setupEventListeners();
    loadRequests();
});

function setupEventListeners() {
    // Navigation - ИСПРАВЛЕНО
    document.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault(); // ✅ ДОБАВЬТЕ
            const tab = e.currentTarget.dataset.tab; // ✅ ИСПОЛЬЗУЙТЕ currentTarget
            console.log("Switching to tab:", tab); // Для отладки
            switchTab(tab);
        });
    });

    // Form
    const createForm = document.getElementById("create-form");
    if (createForm) {
        createForm.addEventListener("submit", handleCreateRequest);
    }

    // Filters
    const searchInput = document.getElementById("search-input");
    const statusFilter = document.getElementById("status-filter");

    if (searchInput) searchInput.addEventListener("input", filterRequests);
    if (statusFilter) statusFilter.addEventListener("change", filterRequests);

    // Modals
    document.querySelectorAll(".modal-close").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const modal = e.currentTarget.closest(".modal");
            if (modal) {
                modal.classList.remove("active");
            }
        });
    });

    // Close modal on background click
    document.querySelectorAll(".modal").forEach(modal => {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                modal.classList.remove("active");
            }
        });
    });
}

// ===== TAB SWITCHING =====
function switchTab(tabName) {
    console.log("switchTab called with:", tabName); // Для отладки

    // Hide all tabs
    document.querySelectorAll(".tab-content").forEach(tab => {
        tab.classList.remove("active");
    });

    // Remove active from all nav links
    document.querySelectorAll(".nav-link").forEach(link => {
        link.classList.remove("active");
    });

    // Show selected tab
    const tabElement = document.getElementById(`${tabName}-tab`);
    if (tabElement) {
        tabElement.classList.add("active");
        console.log("Activated tab:", `${tabName}-tab`);
    } else {
        console.error("Tab not found:", `${tabName}-tab`);
    }

    // Mark nav link active
    const navLink = document.querySelector(`[data-tab="${tabName}"]`);
    if (navLink) {
        navLink.classList.add("active");
    }

    // Load data if dashboard
    if (tabName === "dashboard") {
        loadRequests();
    }
}

// ===== LOAD REQUESTS =====
async function loadRequests() {
    const grid = document.getElementById("requests-grid");
    grid.innerHTML = '<div class="loading">⏳ Загрузка...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/requests`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        allRequests = await response.json();
        displayRequests(allRequests);
    } catch (error) {
        console.error("Error loading requests:", error);
        grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">❌</div>
                <p>Ошибка загрузки: ${error.message}</p>
            </div>
        `;
        showToast(`Ошибка загрузки: ${error.message}`, "error");
    }
}

// ===== DISPLAY REQUESTS =====
function displayRequests(requests) {
    const grid = document.getElementById("requests-grid");

    if (requests.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <p>Заявок нет</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = requests.map(req => createRequestCard(req)).join("");
}

// ===== CREATE REQUEST CARD =====
function createRequestCard(request) {
    const deadline = new Date(request.deadline);
    const now = new Date();
    const isOverdue = deadline < now && request.status === "active";
    const daysLeft = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24));

    return `
        <div class="request-card">
            <div class="card-header">
                <div class="card-title">${escapeHtml(request.title)}</div>
                <span class="card-status status-${request.status}">
                    ${getStatusLabel(request.status)}
                </span>
            </div>

            <div class="card-meta">
                <div class="meta-item">
                    <span class="meta-label">👤 Студент</span>
                    <span class="meta-value">${escapeHtml(request.student_name)}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">📅 Дедлайн</span>
                    <span class="meta-value">${formatDate(deadline)}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">⏱️ Осталось</span>
                    <span class="meta-value ${isOverdue ? 'overdue' : ''}">
                        ${isOverdue ? '⚠️ ПРОСРОЧЕНО' : `${daysLeft} дней`}
                    </span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">🆔 ID</span>
                    <span class="meta-value">#${request.id}</span>
                </div>
            </div>

            ${request.description ? `
                <div style="color: var(--text-secondary); font-size: 0.9rem;">
                    <strong>📝 Описание:</strong><br>
                    ${escapeHtml(request.description)}
                </div>
            ` : ''}

            <div class="card-actions" style="margin-top: auto;">
                <button class="btn btn-primary" onclick="openDetailModal(${request.id})">
                    <i class="fas fa-eye"></i> Открыть
                </button>
                <button class="btn btn-warning" onclick="openRescheduleModal(${request.id})">
                    <i class="fas fa-calendar"></i> Перенести
                </button>
                ${request.status === 'active' ? `
                    <button class="btn btn-success" onclick="completeRequest(${request.id})">
                        <i class="fas fa-check"></i> Завершить
                    </button>
                ` : ''}
                <button class="btn btn-danger" onclick="deleteRequest(${request.id})">
                    <i class="fas fa-trash"></i> Удалить
                </button>
            </div>
        </div>
    `;
}

// ===== HANDLE CREATE REQUEST =====
async function handleCreateRequest(e) {
    e.preventDefault();

    const title = document.getElementById("title").value.trim();
    const student = document.getElementById("student").value.trim();
    const date = document.getElementById("deadline-date").value;
    const time = document.getElementById("deadline-time").value;
    const description = document.getElementById("description").value.trim();

    if (!title || !student || !date || !time) {
        showToast("Заполните все обязательные поля", "error");
        return;
    }

    // Combine date and time
    const deadline = new Date(`${date}T${time}:00`).toISOString();

    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Создаю...';

    try {
        const response = await fetch(`${API_BASE_URL}/requests`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                title,
                student_name: student,
                deadline,
                description: description || null
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Ошибка создания");
        }

        showToast("✅ Заявка создана!", "success");
        e.target.reset();
        await loadRequests();
        switchTab("dashboard");
    } catch (error) {
        console.error("Error:", error);
        showToast(`❌ ${error.message}`, "error");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-plus"></i> Создать';
    }
}

// ===== OPEN DETAIL MODAL =====
function openDetailModal(id) {
    const request = allRequests.find(r => r.id === id);
    if (!request) return;

    const modal = document.getElementById("detail-modal");
    const deadline = new Date(request.deadline);
    const now = new Date();
    const isOverdue = deadline < now && request.status === "active";
    const daysLeft = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24));

    document.getElementById("detail-id").textContent = `#${request.id}`;
    document.getElementById("detail-title").textContent = request.title;
    document.getElementById("detail-student").textContent = request.student_name;
    document.getElementById("detail-status").innerHTML = `<span class="card-status status-${request.status}">${getStatusLabel(request.status)}</span>`;
    document.getElementById("detail-deadline").textContent = formatDate(deadline);
    document.getElementById("detail-remaining").innerHTML = isOverdue
        ? '<span style="color: var(--danger);">⚠️ ПРОСРОЧЕНО</span>'
        : `<span>${daysLeft} дней</span>`;
    document.getElementById("detail-description").textContent = request.description || "Нет описания";
    document.getElementById("detail-created").textContent = formatDate(new Date(request.created_at));
    document.getElementById("detail-updated").textContent = formatDate(new Date(request.updated_at));

    // Action buttons
    const actions = document.getElementById("detail-actions");
    actions.innerHTML = `
        ${request.status === 'active' ? `
            <button class="btn btn-success" onclick="completeRequest(${request.id}); closeModal('detail-modal')">
                <i class="fas fa-check-double"></i> Завершить
            </button>
        ` : ''}
        <button class="btn btn-warning" onclick="openRescheduleModal(${request.id})">
            <i class="fas fa-calendar"></i> Перенести
        </button>
        <button class="btn btn-danger" onclick="deleteRequest(${request.id}); closeModal('detail-modal')">
            <i class="fas fa-trash"></i> Удалить
        </button>
    `;

    modal.classList.add("active");
    currentRequestId = id;
}

// ===== COMPLETE REQUEST =====
async function completeRequest(id) {
    if (!confirm("Завершить эту заявку?")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/requests/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: "completed" })
        });

        if (!response.ok) {
            throw new Error("Ошибка завершения");
        }

        showToast("✅ Заявка завершена!", "success");
        await loadRequests();
    } catch (error) {
        showToast(`❌ ${error.message}`, "error");
    }
}

// ===== DELETE REQUEST =====
async function deleteRequest(id) {
    if (!confirm("Удалить эту заявку?")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/requests/${id}`, {
            method: "DELETE"
        });

        if (!response.ok) {
            throw new Error("Ошибка удаления");
        }

        showToast("✅ Заявка удалена!", "success");
        await loadRequests();
    } catch (error) {
        showToast(`❌ ${error.message}`, "error");
    }
}

// ===== OPEN RESCHEDULE MODAL =====
function openRescheduleModal(id) {
    currentRequestId = id;
    document.getElementById("reschedule-date").value = "";
    document.getElementById("reschedule-time").value = "23:59";
    document.getElementById("reschedule-modal").classList.add("active");
}

// ===== SAVE RESCHEDULE =====
async function saveReschedule() {
    if (!currentRequestId) return;

    const date = document.getElementById("reschedule-date").value;
    const time = document.getElementById("reschedule-time").value;

    if (!date || !time) {
        showToast("Заполните дату и время", "error");
        return;
    }

    const newDeadline = new Date(`${date}T${time}:00`).toISOString();

    try {
        const response = await fetch(`${API_BASE_URL}/requests/${currentRequestId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ deadline: newDeadline })
        });

        if (!response.ok) {
            throw new Error("Ошибка переноса");
        }

        showToast("✅ Дедлайн перенесён!", "success");
        closeModal("reschedule-modal");
        await loadRequests();
    } catch (error) {
        showToast(`❌ ${error.message}`, "error");
    }
}

// ===== FILTER REQUESTS =====
function filterRequests() {
    const search = document.getElementById("search-input").value.toLowerCase();
    const status = document.getElementById("status-filter").value;

    let filtered = allRequests;

    if (search) {
        filtered = filtered.filter(r =>
            r.title.toLowerCase().includes(search) ||
            r.student_name.toLowerCase().includes(search)
        );
    }

    if (status) {
        filtered = filtered.filter(r => r.status === status);
    }

    displayRequests(filtered);
}

// ===== UTILITIES =====
function closeModal(id) {
    document.getElementById(id).classList.remove("active");
}

function getStatusLabel(status) {
    const labels = {
        active: "🔴 Активная",
        completed: "✅ Завершена",
        cancelled: "❌ Отменена"
    };
    return labels[status] || status;
}

function formatDate(date) {
    return new Intl.DateTimeFormat("ru-RU", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    }).format(date);
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = "slideInRight 0.3s ease reverse";
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
