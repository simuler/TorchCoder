const API_BASE = window.location.origin;
const DEFAULT_EDITOR_TEXT = "# 请选择一道题目开始编码。\n";
const DIFFICULTY_LABELS = {
    Easy: "简单",
    Medium: "中等",
    Hard: "困难",
};
const STATUS_LABELS = {
    todo: "未开始",
    attempted: "已尝试",
    solved: "已完成",
};

const state = {
    auth: {
        authenticated: false,
        user: null,
        current_task_id: null,
    },
    tasks: [],
    progress: {},
    currentTask: null,
    editor: null,
    authMode: "login",
    autosaveTimer: null,
    suppressEditorEvents: false,
    collapsedCategories: new Set(),
    pendingAuthContext: null,
};

const ui = {
    authBanner: document.getElementById("authBanner"),
    authBannerBtn: document.getElementById("authBannerBtn"),
    authControls: document.getElementById("authControls"),
    authError: document.getElementById("authError"),
    authForm: document.getElementById("authForm"),
    authHelpText: document.getElementById("authHelpText"),
    authModal: document.getElementById("authModal"),
    authModalClose: document.getElementById("authModalClose"),
    authModalModeLabel: document.getElementById("authModalModeLabel"),
    authModalTitle: document.getElementById("authModalTitle"),
    authPassword: document.getElementById("authPassword"),
    authSubmitBtn: document.getElementById("authSubmitBtn"),
    authUsername: document.getElementById("authUsername"),
    closeResultsBtn: document.getElementById("closeResultsBtn"),
    closeSolutionBtn: document.getElementById("closeSolutionBtn"),
    copySolutionBtn: document.getElementById("copySolutionBtn"),
    descriptionContent: document.getElementById("descriptionContent"),
    editorTaskMeta: document.getElementById("editorTaskMeta"),
    emptyState: document.getElementById("emptyState"),
    exampleCode: document.getElementById("exampleCode"),
    exampleSection: document.getElementById("exampleSection"),
    guestNotice: document.getElementById("guestNotice"),
    hintBtn: document.getElementById("hintBtn"),
    hintContent: document.getElementById("hintContent"),
    problemDifficulty: document.getElementById("problemDifficulty"),
    problemFunction: document.getElementById("problemFunction"),
    problemTitle: document.getElementById("problemTitle"),
    problemView: document.getElementById("problemView"),
    progressBtn: document.getElementById("progressBtn"),
    progressContent: document.getElementById("progressContent"),
    progressModal: document.getElementById("progressModal"),
    progressModalClose: document.getElementById("progressModalClose"),
    randomBtn: document.getElementById("randomBtn"),
    resetBtn: document.getElementById("resetBtn"),
    resultsCount: document.getElementById("resultsCount"),
    resultsList: document.getElementById("resultsList"),
    resultsPanel: document.getElementById("resultsPanel"),
    resultsTime: document.getElementById("resultsTime"),
    runBtn: document.getElementById("runBtn"),
    saveStatus: document.getElementById("saveStatus"),
    signatureCode: document.getElementById("signatureCode"),
    signatureSection: document.getElementById("signatureSection"),
    solutionCode: document.getElementById("solutionCode"),
    solutionContent: document.getElementById("solutionContent"),
    solutionEmpty: document.getElementById("solutionEmpty"),
    solutionLoading: document.getElementById("solutionLoading"),
    solutionMarkdown: document.getElementById("solutionMarkdown"),
    solutionModal: document.getElementById("solutionModal"),
    solutionPanel: document.getElementById("solutionPanel"),
    solutionToggleBtn: document.getElementById("solutionToggleBtn"),
    solvedCount: document.getElementById("solvedCount"),
    tabSwitchButtons: Array.from(document.querySelectorAll(".tab-switch-btn")),
    taskList: document.getElementById("taskList"),
    toastHost: document.getElementById("toastHost"),
    totalCount: document.getElementById("totalCount"),
    workspaceLayout: document.getElementById("workspaceLayout"),
};

marked.setOptions({
    breaks: true,
    gfm: true,
});

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function updateSaveStatus(text, tone = "") {
    ui.saveStatus.textContent = text;
    ui.saveStatus.className = "status-pill";
    if (tone) {
        ui.saveStatus.classList.add(tone);
    }
}

function formatClock(ts) {
    if (!ts) {
        return "";
    }
    const date = new Date(ts);
    if (Number.isNaN(date.getTime())) {
        return "";
    }
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function formatDuration(seconds) {
    if (!seconds && seconds !== 0) {
        return "";
    }
    return `${(seconds * 1000).toFixed(1)} 毫秒`;
}

function formatDifficultyLabel(difficulty) {
    return DIFFICULTY_LABELS[difficulty] || difficulty || "";
}

function formatStatusLabel(status) {
    return STATUS_LABELS[status] || status || "";
}

function renderMarkdown(target, markdown) {
    target.innerHTML = markdown ? marked.parse(markdown) : "<p>暂无内容。</p>";
    if (window.renderMathInElement) {
        window.renderMathInElement(target, {
            delimiters: [
                { left: "$$", right: "$$", display: true },
                { left: "$", right: "$", display: false },
            ],
            throwOnError: false,
        });
    }
}

async function apiFetch(path, options = {}) {
    const headers = new Headers(options.headers || {});
    if (options.body && !headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }

    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        credentials: "same-origin",
        headers,
        body:
            options.body && typeof options.body !== "string"
                ? JSON.stringify(options.body)
                : options.body,
    });

    const raw = await response.text();
    let payload = null;
    if (raw) {
        try {
            payload = JSON.parse(raw);
        } catch {
            payload = raw;
        }
    }

    if (!response.ok) {
        const detail =
            (payload && typeof payload === "object" && payload.detail) ||
            "请求失败。";
        const error = new Error(detail);
        error.status = response.status;
        error.payload = payload;
        throw error;
    }

    return payload;
}

function openAuthModal(mode = "login") {
    setAuthMode(mode);
    ui.authError.classList.add("hidden");
    ui.authError.textContent = "";
    ui.authModal.classList.add("show");
    ui.authUsername.focus();
}

function closeAuthModal() {
    ui.authModal.classList.remove("show");
}

function setAuthMode(mode) {
    state.authMode = mode;
    ui.tabSwitchButtons.forEach((button) => {
        button.classList.toggle("active", button.dataset.authMode === mode);
    });

    const isRegister = mode === "register";
    ui.authModalModeLabel.textContent = isRegister ? "注册账号" : "账号";
    ui.authModalTitle.textContent = isRegister ? "注册" : "登录";
    ui.authHelpText.textContent = isRegister
        ? "用户名可使用字母、数字、点号、下划线或短横线，密码至少 8 位。"
        : "登录后可恢复上次打开的题目，并找回已保存的草稿。";
    ui.authSubmitBtn.innerHTML = isRegister
        ? '<i class="ri-user-add-line"></i><span>注册</span>'
        : '<i class="ri-login-box-line"></i><span>登录</span>';
    ui.authPassword.autocomplete = isRegister ? "new-password" : "current-password";
}

function getTaskProgress(taskId) {
    return (
        state.progress[taskId] || {
            status: "todo",
            attempts: 0,
            best_time: null,
            has_draft: false,
            draft_updated_at: null,
        }
    );
}

function bindAuthCtas(root) {
    root.querySelectorAll("[data-open-auth]").forEach((button) => {
        button.addEventListener("click", () => openAuthModal(button.dataset.openAuth || "login"));
    });
}

function snapshotPendingAuthContext(taskIdOverride = state.currentTask?.id || null) {
    state.pendingAuthContext = {
        taskId: taskIdOverride,
        editorCode: state.editor ? state.editor.getValue() : "",
    };
}

function renderWorkspaceState() {
    const hasTask = Boolean(state.currentTask);
    ui.emptyState.classList.toggle("hidden", hasTask);
    ui.problemView.classList.toggle("hidden", !hasTask);

    if (hasTask) {
        return;
    }

    if (state.auth.authenticated) {
        ui.emptyState.innerHTML = `
            <i class="ri-layout-masonry-line"></i>
            <div class="empty-state-copy">
                <h2>请选择题目</h2>
                <p>可以从侧边栏挑选题目，或使用“随机一题”继续你的账号练习空间。</p>
            </div>
        `;
        return;
    }

    ui.emptyState.innerHTML = `
        <i class="ri-door-lock-box-line"></i>
        <div class="empty-state-copy">
            <h2>注册或登录后开始练习</h2>
            <p>当前站点仅向已登录用户开放题目、题解、草稿和提交功能。</p>
        </div>
        <div class="empty-state-actions">
            <button class="primary-btn" type="button" data-open-auth="register">
                <i class="ri-user-add-line"></i>
                <span>注册账号</span>
            </button>
            <button class="ghost-btn" type="button" data-open-auth="login">
                <i class="ri-login-box-line"></i>
                <span>登录</span>
            </button>
        </div>
    `;
    bindAuthCtas(ui.emptyState);
}

function applySignedOutState({
    preservePendingAuth = false,
    openAuth = false,
    authMode = "login",
    toastMessage = "",
} = {}) {
    clearTimeout(state.autosaveTimer);
    if (preservePendingAuth) {
        snapshotPendingAuthContext();
    } else {
        state.pendingAuthContext = null;
    }

    state.auth = {
        authenticated: false,
        user: null,
        current_task_id: null,
    };
    state.tasks = [];
    state.progress = {};
    state.currentTask = null;

    hideResults();
    hideSolutionPanel();
    setEditorValue(DEFAULT_EDITOR_TEXT);
    ui.solvedCount.textContent = "0";
    ui.totalCount.textContent = "0";
    renderAuthControls();
    renderTaskList();
    renderWorkspaceState();
    updateSaveStatus("注册或登录后开始练习", "warning");

    if (toastMessage) {
        showToast(toastMessage, "warning", 3600);
    }
    if (openAuth) {
        openAuthModal(authMode);
    }
}

function handleAuthError(error, options = {}) {
    if (error.status !== 401) {
        return false;
    }

    applySignedOutState({
        preservePendingAuth: options.preservePendingAuth ?? true,
        openAuth: true,
        authMode: options.authMode || "login",
        toastMessage: options.toastMessage || error.message || "请先登录后继续。",
    });
    return true;
}

async function loadProtectedData() {
    try {
        await Promise.all([loadTasks(), loadProgress()]);
        return true;
    } catch (error) {
        if (handleAuthError(error, { preservePendingAuth: false, authMode: "login" })) {
            return false;
        }
        throw error;
    }
}

function renderAuthControls() {
    ui.guestNotice.classList.toggle("hidden", state.auth.authenticated);
    document.querySelectorAll(".filter-btn").forEach((button) => {
        button.disabled = !state.auth.authenticated;
    });
    ui.randomBtn.innerHTML = state.auth.authenticated
        ? '<i class="ri-shuffle-line"></i><span>随机一题</span>'
        : '<i class="ri-login-box-line"></i><span>登录后开始</span>';

    if (state.auth.authenticated) {
        ui.authControls.innerHTML = `
            <div class="user-chip">
                <i class="ri-user-3-line"></i>
                <span>${escapeHtml(state.auth.user.username)}</span>
            </div>
            <button class="ghost-btn" id="logoutBtn" type="button">
                <i class="ri-logout-box-r-line"></i>
                <span>退出登录</span>
            </button>
        `;
        document.getElementById("logoutBtn").addEventListener("click", logout);
    } else {
        ui.authControls.innerHTML = `
            <button class="ghost-btn" id="loginBtn" type="button">
                <i class="ri-login-box-line"></i>
                <span>登录</span>
            </button>
            <button class="ghost-btn" id="registerBtn" type="button">
                <i class="ri-user-add-line"></i>
                <span>注册</span>
            </button>
        `;
        document.getElementById("loginBtn").addEventListener("click", () => openAuthModal("login"));
        document.getElementById("registerBtn").addEventListener("click", () => openAuthModal("register"));
    }

    const showBanner = !state.auth.authenticated && Boolean(state.currentTask);
    ui.authBanner.classList.toggle("hidden", !showBanner);
}

function renderTaskList() {
    if (!state.auth.authenticated) {
        ui.taskList.innerHTML = `
            <div class="task-gate-card">
                <div class="section-label">需要登录</div>
                <h3>登录后解锁题库</h3>
                <p>在这个站点上，浏览题目、查看题解、保存草稿和提交代码都需要先登录。</p>
                <div class="task-gate-actions">
                    <button class="primary-btn" type="button" data-open-auth="register">
                        <i class="ri-user-add-line"></i>
                        <span>注册账号</span>
                    </button>
                    <button class="ghost-btn" type="button" data-open-auth="login">
                        <i class="ri-login-box-line"></i>
                        <span>登录</span>
                    </button>
                </div>
            </div>
        `;
        bindAuthCtas(ui.taskList);
        return;
    }

    const activeFilter = document.querySelector(".filter-btn.active")?.dataset.filter || "all";
    const filteredTasks = state.tasks.filter((task) => {
        if (activeFilter === "all") {
            return true;
        }
        return getTaskProgress(task.id).status === activeFilter;
    });

    const groups = new Map();
    filteredTasks.forEach((task) => {
        const category = task.category || "未分类";
        if (!groups.has(category)) {
            groups.set(category, []);
        }
        groups.get(category).push(task);
    });

    ui.taskList.innerHTML = Array.from(groups.entries())
        .map(([category, categoryTasks]) => {
            const collapsed = state.collapsedCategories.has(category);
            const tasksMarkup = categoryTasks
                .map((task) => {
                    const progress = getTaskProgress(task.id);
                    const isActive = state.currentTask?.id === task.id;
                    const statusIcon =
                        progress.status === "solved"
                            ? '<i class="ri-checkbox-circle-line solved"></i>'
                            : progress.status === "attempted"
                              ? '<i class="ri-edit-circle-line attempted"></i>'
                              : '<i class="ri-checkbox-blank-circle-line"></i>';
                    const statusLabel =
                        progress.status === "solved"
                            ? "已完成"
                            : progress.status === "attempted"
                              ? "已尝试"
                              : "未开始";
                    const extra = [];
                    if (progress.attempts) {
                        extra.push(`尝试 ${progress.attempts} 次`);
                    }
                    if (progress.has_draft) {
                        extra.push("已保存草稿");
                    }
                    if (progress.best_time) {
                        extra.push(`最佳 ${formatDuration(progress.best_time)}`);
                    }

                    return `
                        <div class="task-item ${isActive ? "active" : ""}" data-task-id="${task.id}">
                            <div class="task-item-head">
                                <span class="task-id">${task.id}</span>
                                <span class="task-difficulty ${task.difficulty}">${escapeHtml(task.difficulty_label || formatDifficultyLabel(task.difficulty))}</span>
                            </div>
                            <div class="task-title">${escapeHtml(task.title)}</div>
                            <div class="task-item-status">
                                <span>${statusIcon}${statusLabel}</span>
                                <span>${escapeHtml(extra.join(" | ") || "尚未开始")}</span>
                            </div>
                        </div>
                    `;
                })
                .join("");

            return `
                <div class="category-group ${collapsed ? "collapsed" : ""}" data-category="${escapeHtml(category)}">
                    <div class="category-header" data-category-toggle="${escapeHtml(category)}">
                        <div class="category-title">
                            <i class="ri-arrow-down-s-line"></i>
                            <span>${escapeHtml(category)}</span>
                        </div>
                        <span class="category-count">${categoryTasks.length}</span>
                    </div>
                    <div class="category-tasks">${tasksMarkup}</div>
                </div>
            `;
        })
        .join("");

    ui.taskList.querySelectorAll(".task-item").forEach((item) => {
        item.addEventListener("click", () => loadTask(item.dataset.taskId));
    });

    ui.taskList.querySelectorAll("[data-category-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const category = button.dataset.categoryToggle;
            if (state.collapsedCategories.has(category)) {
                state.collapsedCategories.delete(category);
            } else {
                state.collapsedCategories.add(category);
            }
            renderTaskList();
        });
    });
}

async function loadSession() {
    const data = await apiFetch("/api/auth/me");
    state.auth = data;
    renderAuthControls();
    renderTaskList();
    renderWorkspaceState();
}

async function loadTasks() {
    const data = await apiFetch("/api/tasks");
    state.tasks = data.tasks;
    ui.totalCount.textContent = String(data.tasks.length);
    renderTaskList();
}

async function loadProgress() {
    const data = await apiFetch("/api/progress");
    state.progress = {};
    data.tasks.forEach((task) => {
        state.progress[task.id] = task;
    });
    ui.solvedCount.textContent = String(data.solved);
    ui.totalCount.textContent = String(data.total);
    if (state.auth.authenticated) {
        state.auth.current_task_id = data.current_task_id;
    }
    renderTaskList();
}

function setEditorValue(value) {
    if (!state.editor) {
        return;
    }
    state.suppressEditorEvents = true;
    state.editor.setValue(value || "");
    state.suppressEditorEvents = false;
}

function selectTask(task) {
    state.currentTask = {
        ...task,
        solutionLoaded: false,
        solutionMarkdown: "",
        solutionCode: "",
    };
    state.auth.current_task_id = task.id;

    renderWorkspaceState();
    renderAuthControls();

    ui.problemTitle.textContent = task.title;
    ui.problemDifficulty.textContent = task.difficulty_label || formatDifficultyLabel(task.difficulty);
    ui.problemDifficulty.className = `task-difficulty ${task.difficulty}`;
    ui.problemFunction.textContent = task.function_name;
    ui.editorTaskMeta.textContent = `${task.id} | ${task.function_name}`;
    ui.hintContent.textContent = task.hint || "暂无提示。";

    if (task.signature) {
        ui.signatureCode.textContent = task.signature;
        ui.signatureSection.classList.remove("hidden");
    } else {
        ui.signatureSection.classList.add("hidden");
    }

    if (task.example) {
        ui.exampleCode.textContent = task.example;
        ui.exampleSection.classList.remove("hidden");
    } else {
        ui.exampleSection.classList.add("hidden");
    }

    renderMarkdown(ui.descriptionContent, task.description || "暂无题目说明。");
    setEditorValue(task.saved_code ?? task.template ?? DEFAULT_EDITOR_TEXT);

    if (task.saved_at) {
        updateSaveStatus(`已保存 ${formatClock(task.saved_at)}`, "success");
    } else if (state.auth.authenticated) {
        updateSaveStatus("自动保存已就绪", "pending");
    } else {
        updateSaveStatus("登录后可保存进度", "warning");
    }

    ui.solutionToggleBtn.disabled = !task.has_solution;
    ui.solutionToggleBtn.innerHTML = task.has_solution
        ? '<i class="ri-book-open-line"></i><span>参考题解</span>'
        : '<i class="ri-lock-2-line"></i><span>暂无题解</span>';
    hideSolutionPanel();
    hideResults();
    renderTaskList();
}

async function loadTask(taskId) {
    if (!state.auth.authenticated) {
        snapshotPendingAuthContext(taskId);
        openAuthModal("login");
        return;
    }

    try {
        const task = await apiFetch(`/api/tasks/${taskId}`);
        selectTask(task);
    } catch (error) {
        if (handleAuthError(error, { preservePendingAuth: true, authMode: "login" })) {
            return;
        }
        showToast(error.message || "加载题目失败。", "error");
    }
}

async function getRandomTask() {
    if (!state.auth.authenticated) {
        openAuthModal("register");
        return;
    }

    try {
        const task = await apiFetch("/api/random");
        await loadTask(task.id);
    } catch (error) {
        if (handleAuthError(error, { preservePendingAuth: false, authMode: "login" })) {
            return;
        }
        showToast(error.message || "随机选题失败。", "error");
    }
}

function handleEditorChange() {
    if (state.suppressEditorEvents || !state.currentTask) {
        return;
    }
    if (!state.auth.authenticated) {
        updateSaveStatus("注册或登录后开始练习", "warning");
        return;
    }

    updateSaveStatus("有未保存的修改", "pending");
    clearTimeout(state.autosaveTimer);
    state.autosaveTimer = setTimeout(() => {
        saveWorkspace();
    }, 900);
}

async function saveWorkspace(codeOverride = null, { quiet = true } = {}) {
    if (!state.auth.authenticated || !state.currentTask) {
        return false;
    }

    updateSaveStatus("保存中...", "pending");

    try {
        const payload = await apiFetch(`/api/tasks/${state.currentTask.id}/workspace`, {
            method: "PUT",
            body: {
                code: codeOverride ?? state.editor.getValue(),
            },
        });
        const code = codeOverride ?? state.editor.getValue();
        state.currentTask.saved_code = code;
        state.currentTask.saved_at = payload.saved_at;
        state.progress[state.currentTask.id] = {
            ...getTaskProgress(state.currentTask.id),
            has_draft: Boolean(code.trim()),
            draft_updated_at: payload.saved_at,
        };
        updateSaveStatus(`已保存 ${formatClock(payload.saved_at)}`, "success");
        renderTaskList();
        return true;
    } catch (error) {
        if (handleAuthError(error, { preservePendingAuth: true, authMode: "login" })) {
            return false;
        }

        updateSaveStatus("保存失败", "error");
        if (!quiet) {
            showToast(error.message || "自动保存失败。", "error");
        }
        return false;
    }
}

async function submitCode() {
    if (!state.currentTask || !state.editor) {
        return;
    }

    clearTimeout(state.autosaveTimer);
    ui.runBtn.disabled = true;
    ui.runBtn.innerHTML = '<i class="ri-loader-4-line ri-spin"></i><span>运行中</span>';

    try {
        const result = await apiFetch("/api/submit", {
            method: "POST",
            body: {
                task_id: state.currentTask.id,
                code: state.editor.getValue(),
            },
        });

        showResults(result);
        await loadProgress();
        updateSaveStatus("已保存本次运行结果", "success");

        showToast(
            result.success ? "全部测试通过。" : `已通过 ${result.passed}/${result.total} 个测试。`,
            result.success ? "success" : "warning",
        );
    } catch (error) {
        if (handleAuthError(error, { preservePendingAuth: true, authMode: "login" })) {
            return;
        }
        showToast(error.message || "提交失败。", "error");
    } finally {
        ui.runBtn.disabled = false;
        ui.runBtn.innerHTML = '<i class="ri-play-line"></i><span>运行测试</span>';
    }
}

function showResults(result) {
    ui.resultsCount.textContent = `已通过 ${result.passed}/${result.total} 个测试`;
    ui.resultsTime.textContent = `总耗时 ${formatDuration(result.total_time)}`;
    ui.resultsList.innerHTML = result.results
        .map((entry, index) => {
            const rowClass = entry.passed ? "pass" : "fail";
            const iconClass = entry.passed ? "result-pass ri-checkbox-circle-line" : "result-fail ri-close-circle-line";
            return `
                <div class="result-row ${rowClass}">
                    <div class="result-main">
                        <div class="result-name">
                            <i class="${iconClass}"></i>
                            <span>测试 ${index + 1}：${escapeHtml(entry.name)}</span>
                        </div>
                        <span class="result-time">${formatDuration(entry.time)}</span>
                    </div>
                    ${entry.error ? `<div class="result-error">${escapeHtml(entry.error)}</div>` : ""}
                </div>
            `;
        })
        .join("");
    ui.resultsPanel.classList.add("show");
}

function hideResults() {
    ui.resultsPanel.classList.remove("show");
}

function resetCode() {
    if (!state.currentTask || !state.editor) {
        return;
    }
    setEditorValue(state.currentTask.template || "");
    if (state.auth.authenticated) {
        saveWorkspace(state.currentTask.template || "", { quiet: false });
    } else {
        updateSaveStatus("已在本地重置", "warning");
    }
}

function showHint() {
    if (!state.currentTask) {
        return;
    }
    showToast(state.currentTask.hint || "暂无提示。", "info", 4500);
}

function hideSolutionPanel() {
    ui.solutionModal.classList.remove("show");
    ui.solutionToggleBtn.innerHTML = state.currentTask?.has_solution
        ? '<i class="ri-book-open-line"></i><span>参考题解</span>'
        : '<i class="ri-lock-2-line"></i><span>暂无题解</span>';
}

async function toggleSolutionPanel() {
    if (!state.currentTask || !state.currentTask.has_solution) {
        return;
    }

    const willOpen = !ui.solutionModal.classList.contains("show");
    if (!willOpen) {
        hideSolutionPanel();
        return;
    }

    ui.solutionModal.classList.add("show");
    ui.solutionToggleBtn.innerHTML = '<i class="ri-book-open-line"></i><span>关闭题解</span>';

    if (!state.currentTask.solutionLoaded) {
        await loadSolution(state.currentTask.id);
    }
}

async function loadSolution(taskId) {
    ui.solutionEmpty.classList.add("hidden");
    ui.solutionContent.classList.add("hidden");
    ui.solutionLoading.classList.remove("hidden");

    try {
        const data = await apiFetch(`/api/tasks/${taskId}/solution`);
        if (!state.currentTask || state.currentTask.id !== taskId) {
            return;
        }
        state.currentTask.solutionLoaded = true;
        state.currentTask.solutionMarkdown = data.markdown || "";
        state.currentTask.solutionCode = data.code || "# 暂无题解代码";
        renderMarkdown(ui.solutionMarkdown, state.currentTask.solutionMarkdown);
        ui.solutionCode.textContent = state.currentTask.solutionCode;
        ui.solutionContent.classList.remove("hidden");
    } catch (error) {
        if (handleAuthError(error, { preservePendingAuth: true, authMode: "login" })) {
            hideSolutionPanel();
            return;
        }
        ui.solutionEmpty.classList.remove("hidden");
        ui.solutionEmpty.innerHTML = `
            <i class="ri-error-warning-line"></i>
            <p>${escapeHtml(error.message || "加载参考题解失败。")}</p>
        `;
    } finally {
        ui.solutionLoading.classList.add("hidden");
    }
}

async function copySolutionCode() {
    try {
        await navigator.clipboard.writeText(ui.solutionCode.textContent || "");
        showToast("题解代码已复制。", "success");
    } catch {
        showToast("复制失败。", "error");
    }
}

function showProgressModal() {
    if (!state.auth.authenticated) {
        ui.progressContent.innerHTML = `
            <p style="margin-bottom: 16px; color: var(--text-secondary);">
                当前站点的完整练习流程基于账号提供。登录或注册后即可解锁题目、草稿与进度同步。
            </p>
            <div class="task-gate-actions">
                <button class="primary-btn" id="progressRegisterBtn" type="button">
                    <i class="ri-user-add-line"></i>
                    <span>注册账号</span>
                </button>
                <button class="ghost-btn" id="progressLoginBtn" type="button">
                    <i class="ri-login-box-line"></i>
                    <span>登录</span>
                </button>
            </div>
        `;
        ui.progressModal.classList.add("show");
        document.getElementById("progressRegisterBtn").addEventListener("click", () => {
            ui.progressModal.classList.remove("show");
            openAuthModal("register");
        });
        document.getElementById("progressLoginBtn").addEventListener("click", () => {
            ui.progressModal.classList.remove("show");
            openAuthModal("login");
        });
        return;
    }

    const progressEntries = Object.values(state.progress);
    const solved = progressEntries.filter((entry) => entry.status === "solved").length;
    const attempted = progressEntries.filter((entry) => entry.status === "attempted").length;
    const drafts = progressEntries.filter((entry) => entry.has_draft).length;
    const total = state.tasks.length;

    ui.progressContent.innerHTML = `
        <div class="progress-summary">
            <div class="summary-card">
                <div class="summary-value">${solved}</div>
                <div class="summary-label">已完成</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">${attempted}</div>
                <div class="summary-label">已尝试</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">${drafts}</div>
                <div class="summary-label">草稿数</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">${total}</div>
                <div class="summary-label">题目总数</div>
            </div>
        </div>
        <div class="progress-list">
            ${state.tasks
                .map((task) => {
                    const entry = getTaskProgress(task.id);
                    const meta = [];
                    meta.push(formatStatusLabel(entry.status));
                    if (entry.attempts) {
                        meta.push(`尝试 ${entry.attempts} 次`);
                    }
                    if (entry.best_time) {
                        meta.push(`最佳 ${formatDuration(entry.best_time)}`);
                    }
                    if (entry.draft_updated_at) {
                        meta.push(`草稿 ${formatClock(entry.draft_updated_at)}`);
                    }
                    return `
                        <div class="progress-item">
                            <div>
                                <div>${escapeHtml(task.title)}</div>
                                <div class="progress-item-meta">${escapeHtml(meta.join(" | "))}</div>
                            </div>
                            <span class="task-difficulty ${task.difficulty}">${escapeHtml(task.difficulty_label || formatDifficultyLabel(task.difficulty))}</span>
                            <button class="ghost-btn" type="button" data-resume-task="${task.id}">
                                <i class="ri-arrow-right-up-line"></i>
                                <span>打开</span>
                            </button>
                        </div>
                    `;
                })
                .join("")}
        </div>
        <div class="progress-modal-actions">
            <button class="ghost-btn" id="resetProgressBtn" type="button">
                <i class="ri-delete-bin-6-line"></i>
                <span>重置我的进度</span>
            </button>
        </div>
    `;

    ui.progressModal.classList.add("show");

    ui.progressContent.querySelectorAll("[data-resume-task]").forEach((button) => {
        button.addEventListener("click", async () => {
            ui.progressModal.classList.remove("show");
            await loadTask(button.dataset.resumeTask);
        });
    });

    document.getElementById("resetProgressBtn").addEventListener("click", resetProgress);
}

async function resetProgress() {
    const confirmed = window.confirm(
        "要重置当前账号的全部进度和草稿吗？此操作无法撤销。",
    );
    if (!confirmed) {
        return;
    }

    try {
        await apiFetch("/api/reset", { method: "POST" });
        ui.progressModal.classList.remove("show");
        await loadProgress();
        if (state.currentTask) {
            await loadTask(state.currentTask.id);
        }
        showToast("账号进度已重置。", "success");
    } catch (error) {
        if (handleAuthError(error, { preservePendingAuth: true, authMode: "login" })) {
            ui.progressModal.classList.remove("show");
            return;
        }
        showToast(error.message || "重置进度失败。", "error");
    }
}

function hideProgressModal() {
    ui.progressModal.classList.remove("show");
}

function showToast(message, type = "info", duration = 3000) {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    ui.toastHost.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
}

async function handleAuthSubmit(event) {
    event.preventDefault();
    ui.authError.classList.add("hidden");
    ui.authError.textContent = "";
    ui.authSubmitBtn.disabled = true;

    const username = ui.authUsername.value.trim();
    const password = ui.authPassword.value;
    const resumeContext = state.pendingAuthContext || {
        taskId: state.currentTask?.id || null,
        editorCode: state.editor ? state.editor.getValue() : "",
    };

    try {
        const data = await apiFetch(`/api/auth/${state.authMode}`, {
            method: "POST",
            body: { username, password },
        });

        state.auth = data;
        renderAuthControls();
        closeAuthModal();
        const loaded = await loadProtectedData();
        if (!loaded) {
            return;
        }
        state.pendingAuthContext = null;

        if (resumeContext.taskId && resumeContext.editorCode.trim()) {
            await loadTask(resumeContext.taskId);
            await saveWorkspace(resumeContext.editorCode, { quiet: true });
        } else if (resumeContext.taskId) {
            await loadTask(resumeContext.taskId);
        } else if (state.auth.current_task_id) {
            await loadTask(state.auth.current_task_id);
        } else {
            renderWorkspaceState();
        }

        showToast(
            state.authMode === "register"
                ? "账号创建成功，自动保存已启用。"
                : "登录成功。",
            "success",
        );
    } catch (error) {
        ui.authError.textContent = error.message || "认证失败。";
        ui.authError.classList.remove("hidden");
    } finally {
        ui.authSubmitBtn.disabled = false;
    }
}

async function logout() {
    try {
        await apiFetch("/api/auth/logout", { method: "POST" });
        ui.progressModal.classList.remove("show");
        applySignedOutState();
        showToast("已退出登录。", "success");
    } catch (error) {
        showToast(error.message || "退出登录失败。", "error");
    }
}

function bindStaticEvents() {
    document.querySelectorAll(".filter-btn").forEach((button) => {
        button.addEventListener("click", () => {
            document.querySelectorAll(".filter-btn").forEach((item) => item.classList.remove("active"));
            button.classList.add("active");
            renderTaskList();
        });
    });

    ui.authBannerBtn.addEventListener("click", () => openAuthModal("register"));
    ui.authForm.addEventListener("submit", handleAuthSubmit);
    ui.authModalClose.addEventListener("click", closeAuthModal);
    ui.progressBtn.addEventListener("click", showProgressModal);
    ui.progressModalClose.addEventListener("click", hideProgressModal);
    ui.randomBtn.addEventListener("click", getRandomTask);
    ui.resetBtn.addEventListener("click", resetCode);
    ui.hintBtn.addEventListener("click", showHint);
    ui.runBtn.addEventListener("click", submitCode);
    ui.solutionToggleBtn.addEventListener("click", toggleSolutionPanel);
    ui.closeSolutionBtn.addEventListener("click", hideSolutionPanel);
    ui.closeResultsBtn.addEventListener("click", hideResults);
    ui.copySolutionBtn.addEventListener("click", copySolutionCode);

    ui.tabSwitchButtons.forEach((button) => {
        button.addEventListener("click", () => setAuthMode(button.dataset.authMode));
    });

    document.addEventListener("keydown", (event) => {
        if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
            if (!ui.authModal.classList.contains("show")) {
                event.preventDefault();
                submitCode();
            }
        }
    });

    ui.authModal.addEventListener("click", (event) => {
        if (event.target === ui.authModal) {
            closeAuthModal();
        }
    });

    ui.progressModal.addEventListener("click", (event) => {
        if (event.target === ui.progressModal) {
            hideProgressModal();
        }
    });

    ui.solutionModal.addEventListener("click", (event) => {
        if (event.target === ui.solutionModal) {
            hideSolutionPanel();
        }
    });
}

function initEditor() {
    window.require.config({
        paths: { vs: "https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs" },
    });

    window.require(["vs/editor/editor.main"], () => {
        monaco.editor.defineTheme("torchcoder-ivory", {
            base: "vs",
            inherit: true,
            rules: [
                { token: "comment", foreground: "6b6257" },
                { token: "keyword", foreground: "4d329f" },
                { token: "string", foreground: "8b5d16" },
                { token: "number", foreground: "167653" },
            ],
            colors: {
                "editor.background": "#fffdf8",
                "editor.foreground": "#171512",
                "editorLineNumber.foreground": "#8c8275",
                "editorLineNumber.activeForeground": "#171512",
                "editorCursor.foreground": "#6e50c8",
                "editor.selectionBackground": "#ded4f7",
                "editor.lineHighlightBackground": "#f7f1e7",
            },
        });

        state.editor = monaco.editor.create(document.getElementById("editor"), {
            value: DEFAULT_EDITOR_TEXT,
            language: "python",
            theme: "torchcoder-ivory",
            automaticLayout: true,
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 14,
            insertSpaces: true,
            minimap: { enabled: false },
            padding: { top: 16 },
            renderLineHighlight: "line",
            scrollBeyondLastLine: false,
            tabSize: 4,
        });

        state.editor.onDidChangeModelContent(handleEditorChange);
        bootstrap().catch((error) => {
            console.error(error);
            showToast("应用初始化失败。", "error");
        });
    });
}

async function bootstrap() {
    await loadSession();
    if (!state.auth.authenticated) {
        applySignedOutState();
        return;
    }

    const loaded = await loadProtectedData();
    if (!loaded) {
        return;
    }

    if (state.auth.authenticated && state.auth.current_task_id) {
        const taskExists = state.tasks.some((task) => task.id === state.auth.current_task_id);
        if (taskExists) {
            await loadTask(state.auth.current_task_id);
            return;
        }
    }

    renderWorkspaceState();
}

bindStaticEvents();
initEditor();
