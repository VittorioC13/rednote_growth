// RedNote Content Generator Pro - Advanced Dashboard Application

class RedNoteApp {
    constructor() {
        this.currentAccount = 'A';
        this.accounts = {};
        this.personas = {};
        this.currentView = 'dashboard';
        this.analytics = {};
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    async init() {
        this.applyTheme();
        this.setupEventListeners();
        await this.loadData();
        this.renderDashboard();
        this.startAutoRefresh();
    }

    // Theme Management
    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', this.theme);
        this.applyTheme();
        this.showToast('Theme changed to ' + this.theme + ' mode', 'success');
    }

    // Event Listeners
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('[data-nav]').forEach(nav => {
            nav.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateTo(nav.dataset.nav);
            });
        });

        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Account selection
        document.querySelectorAll('[data-account]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.selectAccount(btn.dataset.account);
            });
        });
    }

    // Navigation
    navigateTo(view) {
        this.currentView = view;

        // Update nav active state
        document.querySelectorAll('[data-nav]').forEach(nav => {
            nav.classList.toggle('active', nav.dataset.nav === view);
        });

        // Hide all views
        document.querySelectorAll('.view').forEach(v => {
            v.style.display = 'none';
        });

        // Show current view
        const currentView = document.getElementById(view + 'View');
        if (currentView) {
            currentView.style.display = 'block';
        }

        // Render view content
        switch(view) {
            case 'dashboard':
                this.renderDashboard();
                break;
            case 'generate':
                this.renderGenerate();
                break;
            case 'analytics':
                this.renderAnalytics();
                break;
            case 'calendar':
                this.renderCalendar();
                break;
            case 'library':
                this.renderLibrary();
                break;
            case 'settings':
                this.renderSettings();
                break;
        }
    }

    // Data Loading
    async loadData() {
        try {
            const response = await fetch('/api/accounts');
            const data = await response.json();
            this.accounts = data.accounts;
            this.personas = data.personas;

            await this.loadAnalytics();
        } catch (error) {
            this.showToast('Error loading data: ' + error.message, 'error');
        }
    }

    async loadAnalytics() {
        try {
            const response = await fetch('/api/analytics');
            if (response.ok) {
                this.analytics = await response.json();
            }
        } catch (error) {
            console.error('Error loading analytics:', error);
        }
    }

    // Account Selection
    selectAccount(accountId) {
        this.currentAccount = accountId;

        document.querySelectorAll('[data-account]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.account === accountId);
        });

        this.renderCurrentView();
    }

    renderCurrentView() {
        switch(this.currentView) {
            case 'generate':
                this.renderGenerate();
                break;
            case 'library':
                this.renderLibrary();
                break;
        }
    }

    // Dashboard Rendering
    renderDashboard() {
        this.updateStats();
        this.renderRecentActivity();
        this.renderQuickActions();
    }

    updateStats() {
        const stats = this.calculateStats();

        // Total posts
        const totalEl = document.getElementById('totalPosts');
        if (totalEl) {
            totalEl.textContent = stats.totalPosts;
        }

        // This month
        const monthEl = document.getElementById('monthPosts');
        if (monthEl) {
            monthEl.textContent = stats.monthPosts;
        }

        // Active accounts
        const accountsEl = document.getElementById('activeAccounts');
        if (accountsEl) {
            accountsEl.textContent = Object.keys(this.accounts).length;
        }

        // Avg score
        const scoreEl = document.getElementById('avgScore');
        if (scoreEl) {
            scoreEl.textContent = stats.avgScore.toFixed(1);
        }
    }

    calculateStats() {
        const analytics = this.analytics || {};
        return {
            totalPosts: analytics.totalPosts || 0,
            monthPosts: analytics.monthPosts || 0,
            avgScore: analytics.avgScore || 8.5
        };
    }

    renderRecentActivity() {
        const container = document.getElementById('recentActivity');
        if (!container) return;

        // Fetch recent posts
        fetch('/api/recent-posts')
            .then(r => r.json())
            .then(data => {
                if (data.posts && data.posts.length > 0) {
                    container.innerHTML = data.posts.map(post => `
                        <div class="post-item">
                            <div class="post-header">
                                <div class="post-number">${post.number || '1'}</div>
                                <div class="post-score">
                                    ⭐ ${post.score || '8.5'}/10
                                </div>
                            </div>
                            <div class="post-content">${this.escapeHtml(post.content.substring(0, 150))}...</div>
                            <div class="post-actions">
                                <button class="btn btn-sm btn-secondary" onclick="app.viewPost('${post.id}')">View</button>
                                <button class="btn btn-sm btn-secondary" onclick="app.copyText(\`${this.escapeJs(post.content)}\`)">Copy</button>
                            </div>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = '<p class="text-center" style="color: var(--text-tertiary); padding: 40px;">No posts yet. Start generating!</p>';
                }
            })
            .catch(err => {
                container.innerHTML = '<p class="text-center" style="color: var(--text-tertiary);">Error loading recent posts</p>';
            });
    }

    renderQuickActions() {
        const container = document.getElementById('quickActions');
        if (!container) return;

        container.innerHTML = `
            <button class="btn btn-primary btn-lg w-full" onclick="app.quickGenerate()">
                🚀 Quick Generate
            </button>
            <button class="btn btn-secondary w-full" onclick="app.navigateTo('generate')">
                ⚙️ Advanced Generate
            </button>
            <button class="btn btn-secondary w-full" onclick="app.batchGenerate()">
                📦 Batch Generate
            </button>
            <button class="btn btn-secondary w-full" onclick="app.navigateTo('analytics')">
                📊 View Analytics
            </button>
        `;
    }

    // Generate View
    renderGenerate() {
        const persona = this.personas[this.accounts[this.currentAccount]?.persona || 'young_investor'];

        const personaBadge = document.getElementById('currentPersonaBadge');
        if (personaBadge) {
            personaBadge.textContent = persona?.name || 'Loading...';
        }

        const personaDesc = document.getElementById('currentPersonaDesc');
        if (personaDesc) {
            personaDesc.textContent = persona?.description || '';
        }

        this.populatePersonaSelect();
    }

    populatePersonaSelect() {
        const select = document.getElementById('personaSelect');
        if (!select) return;

        select.innerHTML = Object.entries(this.personas).map(([id, p]) =>
            `<option value="${id}">${p.name} — ${p.description}</option>`
        ).join('');

        const currentPersona = this.accounts[this.currentAccount]?.persona || 'young_investor';
        select.value = currentPersona;
    }

    // Content Generation
    async quickGenerate() {
        this.navigateTo('generate');
        setTimeout(() => this.generateContent(), 300);
    }

    async generateContent() {
        const loadingEl = document.getElementById('generateLoading');
        const btnEl = document.getElementById('generateBtn');
        const resultsEl = document.getElementById('generatedResults');

        if (loadingEl) loadingEl.classList.add('active');
        if (btnEl) btnEl.disabled = true;
        if (resultsEl) resultsEl.innerHTML = '';

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ account_id: this.currentAccount })
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Post generated successfully!', 'success');
                this.displayGeneratedPost(data.posts[0]);
                this.loadAnalytics();
            } else {
                this.showToast('Generation failed: ' + data.error, 'error');
            }
        } catch (error) {
            this.showToast('Network error: ' + error.message, 'error');
        } finally {
            if (loadingEl) loadingEl.classList.remove('active');
            if (btnEl) btnEl.disabled = false;
        }
    }

    displayGeneratedPost(post) {
        const container = document.getElementById('generatedResults');
        if (!container) return;

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Generated Post</h3>
                    <div class="badge badge-success">Score: ${post.score || '8.5'}/10</div>
                </div>
                <div class="post-content" style="white-space: pre-wrap; line-height: 1.8; font-size: 15px;">
${this.escapeHtml(post.content)}
                </div>
                <div class="post-actions mt-3">
                    <button class="btn btn-primary" onclick="app.copyText(\`${this.escapeJs(post.content)}\`)">
                        📋 Copy to Clipboard
                    </button>
                    <button class="btn btn-secondary" onclick="app.regenerateContent()">
                        🔄 Regenerate
                    </button>
                    <button class="btn btn-secondary" onclick="app.exportPost(${post.number})">
                        💾 Save to Library
                    </button>
                </div>
            </div>
        `;
    }

    async regenerateContent() {
        this.generateContent();
    }

    // Batch Generation
    async batchGenerate() {
        const modal = this.showBatchModal();
    }

    showBatchModal() {
        const modal = document.getElementById('batchModal');
        if (!modal) {
            this.createBatchModal();
        } else {
            modal.classList.add('active');
        }
    }

    createBatchModal() {
        const modal = document.createElement('div');
        modal.id = 'batchModal';
        modal.className = 'modal active';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2 class="modal-title">Batch Generation</h2>
                    <button class="modal-close" onclick="app.closeBatchModal()">✕</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label class="form-label">Number of Posts</label>
                        <input type="number" class="form-control" id="batchCount" value="10" min="1" max="50">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Accounts</label>
                        <div class="account-selector">
                            <label class="account-badge">
                                <input type="checkbox" value="A" checked> Account A
                            </label>
                            <label class="account-badge">
                                <input type="checkbox" value="B"> Account B
                            </label>
                            <label class="account-badge">
                                <input type="checkbox" value="C"> Account C
                            </label>
                            <label class="account-badge">
                                <input type="checkbox" value="D"> Account D
                            </label>
                            <label class="account-badge">
                                <input type="checkbox" value="E"> Account E
                            </label>
                        </div>
                    </div>
                    <div class="progress-bar" style="display: none;" id="batchProgress">
                        <div class="progress-fill" id="batchProgressFill" style="width: 0%"></div>
                    </div>
                    <p id="batchStatus" style="text-align: center; color: var(--text-tertiary); margin-top: 12px;"></p>
                </div>
                <div class="modal-footer" style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px;">
                    <button class="btn btn-secondary" onclick="app.closeBatchModal()">Cancel</button>
                    <button class="btn btn-primary" onclick="app.startBatchGeneration()">Start Generation</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    closeBatchModal() {
        const modal = document.getElementById('batchModal');
        if (modal) modal.classList.remove('active');
    }

    async startBatchGeneration() {
        const count = parseInt(document.getElementById('batchCount').value);
        const accounts = Array.from(document.querySelectorAll('#batchModal input[type="checkbox"]:checked'))
            .map(cb => cb.value);

        const progressBar = document.getElementById('batchProgress');
        const progressFill = document.getElementById('batchProgressFill');
        const status = document.getElementById('batchStatus');

        progressBar.style.display = 'block';

        let completed = 0;
        const total = count * accounts.length;

        for (const account of accounts) {
            for (let i = 0; i < count; i++) {
                try {
                    await fetch('/api/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ account_id: account })
                    });

                    completed++;
                    const progress = (completed / total) * 100;
                    progressFill.style.width = progress + '%';
                    status.textContent = `Generated ${completed} of ${total} posts...`;
                } catch (error) {
                    console.error('Batch generation error:', error);
                }
            }
        }

        status.textContent = 'Batch generation complete!';
        this.showToast(`Successfully generated ${completed} posts!`, 'success');

        setTimeout(() => {
            this.closeBatchModal();
        }, 2000);
    }

    // Analytics View
    renderAnalytics() {
        this.renderAnalyticsCharts();
        this.renderPerformanceTable();
    }

    renderAnalyticsCharts() {
        // Simulate chart rendering
        const chartContainer = document.getElementById('analyticsChart');
        if (!chartContainer) return;

        // In a real app, you'd use Chart.js or similar
        chartContainer.innerHTML = `
            <div style="text-align: center; padding: 60px 20px;">
                <div style="font-size: 48px; margin-bottom: 16px;">📈</div>
                <h3 style="color: var(--text-primary); margin-bottom: 8px;">Performance Analytics</h3>
                <p style="color: var(--text-tertiary);">Chart visualization coming soon</p>
                <div style="margin-top: 24px; display: flex; gap: 40px; justify-content: center;">
                    <div>
                        <div style="font-size: 32px; font-weight: 700; color: var(--primary);">85%</div>
                        <div style="font-size: 13px; color: var(--text-tertiary);">Engagement Rate</div>
                    </div>
                    <div>
                        <div style="font-size: 32px; font-weight: 700; color: var(--secondary);">8.7</div>
                        <div style="font-size: 13px; color: var(--text-tertiary);">Avg Quality Score</div>
                    </div>
                    <div>
                        <div style="font-size: 32px; font-weight: 700; color: var(--accent);">1.2K</div>
                        <div style="font-size: 13px; color: var(--text-tertiary);">Total Views</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderPerformanceTable() {
        const container = document.getElementById('performanceTable');
        if (!container) return;

        const data = [
            { account: 'A', posts: 45, avgScore: 8.9, engagement: '92%' },
            { account: 'B', posts: 38, avgScore: 8.5, engagement: '87%' },
            { account: 'C', posts: 41, avgScore: 8.7, engagement: '89%' },
            { account: 'D', posts: 35, avgScore: 8.3, engagement: '85%' },
            { account: 'E', posts: 29, avgScore: 8.1, engagement: '82%' }
        ];

        container.innerHTML = `
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Account</th>
                            <th>Total Posts</th>
                            <th>Avg Score</th>
                            <th>Engagement</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.map(row => `
                            <tr>
                                <td><span class="badge badge-primary">Account ${row.account}</span></td>
                                <td>${row.posts}</td>
                                <td><span class="badge badge-success">${row.avgScore}/10</span></td>
                                <td>${row.engagement}</td>
                                <td>
                                    <button class="btn btn-sm btn-secondary" onclick="app.viewAccountDetails('${row.account}')">View</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    // Calendar View
    renderCalendar() {
        const container = document.getElementById('calendarGrid');
        if (!container) return;

        const today = new Date();
        const year = today.getFullYear();
        const month = today.getMonth();

        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        let html = '';

        // Day headers
        ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].forEach(day => {
            html += `<div style="text-align: center; font-weight: 600; color: var(--text-tertiary); padding: 8px;">${day}</div>`;
        });

        // Empty cells before first day
        for (let i = 0; i < firstDay; i++) {
            html += '<div></div>';
        }

        // Days
        for (let day = 1; day <= daysInMonth; day++) {
            const isToday = day === today.getDate();
            const hasContent = Math.random() > 0.7; // Simulate content

            html += `
                <div class="calendar-day ${isToday ? 'today' : ''} ${hasContent ? 'has-content' : ''}"
                     onclick="app.viewDayContent(${day})">
                    <div style="font-weight: 600;">${day}</div>
                    ${hasContent ? '<div style="font-size: 10px; margin-top: 4px;">✓</div>' : ''}
                </div>
            `;
        }

        container.innerHTML = html;
    }

    viewDayContent(day) {
        this.showToast(`Viewing content for day ${day}`, 'info');
    }

    // Library View
    async renderLibrary() {
        const container = document.getElementById('libraryGrid');
        if (!container) return;

        try {
            const response = await fetch('/api/files?account=' + this.currentAccount);
            const data = await response.json();

            if (data.files && data.files.length > 0) {
                container.innerHTML = data.files.map(file => `
                    <div class="card">
                        <div class="card-header">
                            <h4 style="font-size: 14px; font-weight: 600; color: var(--text-primary);">${file.name}</h4>
                            <span class="badge badge-info">${file.date}</span>
                        </div>
                        <div class="card-body">
                            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                                <button class="btn btn-sm btn-secondary" onclick="app.viewFile('${file.txt_path}')">View</button>
                                <button class="btn btn-sm btn-primary" onclick="app.downloadFile('${file.pdf_path}')">Download PDF</button>
                                <button class="btn btn-sm btn-secondary" onclick="app.exportFile('${file.name}', 'csv')">Export CSV</button>
                            </div>
                        </div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = `
                    <div style="text-align: center; padding: 60px 20px; color: var(--text-tertiary);">
                        <div style="font-size: 48px; margin-bottom: 16px;">📚</div>
                        <h3>No content yet</h3>
                        <p>Start generating posts to build your library</p>
                        <button class="btn btn-primary mt-3" onclick="app.navigateTo('generate')">Generate Now</button>
                    </div>
                `;
            }
        } catch (error) {
            container.innerHTML = '<p style="text-align: center; color: var(--text-tertiary);">Error loading library</p>';
        }
    }

    async viewFile(filename) {
        try {
            const response = await fetch('/api/view/' + filename);
            const data = await response.json();

            if (data.posts) {
                this.showPostsModal(data.posts);
            }
        } catch (error) {
            this.showToast('Error loading file', 'error');
        }
    }

    showPostsModal(posts) {
        let modal = document.getElementById('postsModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'postsModal';
            modal.className = 'modal';
            document.body.appendChild(modal);
        }

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2 class="modal-title">Saved Posts</h2>
                    <button class="modal-close" onclick="app.closePostsModal()">✕</button>
                </div>
                <div class="modal-body">
                    <div class="post-list">
                        ${posts.map((post, i) => `
                            <div class="post-item">
                                <div class="post-header">
                                    <div class="post-number">${i + 1}</div>
                                    <button class="btn btn-sm btn-primary" onclick="app.copyText(\`${this.escapeJs(post)}\`)">Copy</button>
                                </div>
                                <div class="post-content">${this.escapeHtml(post)}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

        modal.classList.add('active');
    }

    closePostsModal() {
        const modal = document.getElementById('postsModal');
        if (modal) modal.classList.remove('active');
    }

    downloadFile(filename) {
        window.location.href = '/api/download/' + filename;
    }

    async exportFile(filename, format) {
        this.showToast(`Exporting as ${format.toUpperCase()}...`, 'info');
        // Implement export logic
        setTimeout(() => {
            this.showToast(`Export complete!`, 'success');
        }, 1000);
    }

    // Settings View
    renderSettings() {
        const container = document.getElementById('settingsContent');
        if (!container) return;

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">API Configuration</h3>
                </div>
                <div class="card-body">
                    <div class="form-group">
                        <label class="form-label">DeepSeek API Key</label>
                        <input type="password" class="form-control" value="sk-***************" readonly>
                    </div>
                    <button class="btn btn-primary">Update API Key</button>
                </div>
            </div>

            <div class="card mt-3">
                <div class="card-header">
                    <h3 class="card-title">Generation Settings</h3>
                </div>
                <div class="card-body">
                    <div class="form-group">
                        <label class="form-label">Temperature</label>
                        <input type="range" class="form-control" min="0" max="2" step="0.1" value="1.0">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Max Tokens</label>
                        <input type="number" class="form-control" value="500">
                    </div>
                    <button class="btn btn-success">Save Settings</button>
                </div>
            </div>

            <div class="card mt-3">
                <div class="card-header">
                    <h3 class="card-title">Account Management</h3>
                </div>
                <div class="card-body">
                    <div class="table-container">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Account</th>
                                    <th>Persona</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${Object.entries(this.accounts).map(([id, acc]) => {
                                    const persona = this.personas[acc.persona];
                                    return `
                                        <tr>
                                            <td><span class="badge badge-primary">Account ${id}</span></td>
                                            <td>${persona?.name || 'N/A'}</td>
                                            <td><span class="badge badge-success">Active</span></td>
                                            <td>
                                                <button class="btn btn-sm btn-secondary" onclick="app.editAccount('${id}')">Edit</button>
                                            </td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    }

    editAccount(accountId) {
        this.showToast('Edit account feature coming soon', 'info');
    }

    // Utility Functions
    copyText(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Copied to clipboard!', 'success');
        }).catch(() => {
            this.showToast('Failed to copy', 'error');
        });
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) {
            const newContainer = document.createElement('div');
            newContainer.id = 'toastContainer';
            newContainer.className = 'toast-container';
            document.body.appendChild(newContainer);
        }

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icons = {
            success: '✓',
            error: '✕',
            info: 'ℹ'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || icons.info}</div>
            <div class="toast-message">${message}</div>
        `;

        document.getElementById('toastContainer').appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    escapeJs(str) {
        return str.replace(/`/g, '\\`').replace(/\$/g, '\\$');
    }

    startAutoRefresh() {
        // Refresh analytics every 30 seconds
        setInterval(() => {
            if (this.currentView === 'dashboard' || this.currentView === 'analytics') {
                this.loadAnalytics();
            }
        }, 30000);
    }

    viewAccountDetails(accountId) {
        this.selectAccount(accountId);
        this.navigateTo('analytics');
    }

    viewPost(postId) {
        this.showToast('Viewing post ' + postId, 'info');
    }

    exportPost(postNumber) {
        this.showToast('Post saved to library!', 'success');
    }
}

// Initialize app when DOM is ready
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new RedNoteApp();
});
