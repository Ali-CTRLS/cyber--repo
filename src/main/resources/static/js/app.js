// ===========================
//   CyberSecure – app.js
// ===========================
const API_BASE = '/api';
let currentFolderId = null;
let pathStack = [{ id: 'root', name: 'Root' }];
let currentView = 'files';

// ---- Init ----
document.addEventListener('DOMContentLoaded', () => {
    init();
});

async function init() {
    const token = localStorage.getItem('jwt_token');
    if (!token) {
        await handleDefaultAuth();
    }
    await fetchUserProfile();
    await fetchFolders();
    await fetchTemplatesBar();
    setupEventListeners();
}

// ---- View Switching ----
function switchView(viewName, event) {
    if (event) event.preventDefault();

    // Update nav active state
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    const activeLink = document.getElementById('nav-' + viewName);
    if (activeLink) activeLink.classList.add('active');

    // Hide all views
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));

    // Show target view
    const target = document.getElementById('view-' + viewName);
    if (target) target.classList.add('active');

    currentView = viewName;

    // Trigger view-specific data load
    if (viewName === 'templates') loadTemplatesView();
    if (viewName === 'shared') loadSharedView();
    if (viewName === 'settings') loadSettingsView();
}

// ---- Auth ----
async function handleDefaultAuth() {
    try {
        const resp = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: 'admin', password: 'password' })
        });
        if (resp.ok) {
            const data = await resp.json();
            localStorage.setItem('jwt_token', data.token);
        } else {
            await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: 'admin', password: 'password' })
            });
            await handleDefaultAuth();
        }
    } catch (e) {
        console.error('Auth failed', e);
    }
}

function logout() {
    localStorage.removeItem('jwt_token');
    showToast('Signed out successfully');
    setTimeout(() => location.reload(), 1000);
}

// ---- User Profile ----
async function fetchUserProfile() {
    const data = await apiFetch(`${API_BASE}/files/me`);
    if (data && data.username) {
        const uname = data.username;
        document.getElementById('username').textContent = uname;
        document.getElementById('avatarLetter').textContent = uname.charAt(0).toUpperCase();
        document.getElementById('settingsUsername').textContent = uname;
    }
}

// ---- FILES VIEW ----
async function fetchFolders(folderId = null) {
    currentFolderId = folderId;
    const grid = document.getElementById('fileGrid');
    grid.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Syncing secure volume...</p></div>';

    try {
        const subfoldersUrl = folderId
            ? `${API_BASE}/folders/${folderId}/subfolders`
            : `${API_BASE}/folders`;
        const subfolders = await apiFetch(subfoldersUrl) || [];

        const filesUrl = folderId
            ? `${API_BASE}/files?folderId=${folderId}`
            : `${API_BASE}/files`;
        const files = await apiFetch(filesUrl) || [];

        renderExplorer(subfolders, files);
    } catch (e) {
        grid.innerHTML = '<p class="error-msg">⚠ Failed to load content.</p>';
    }
}

function filterGrid() {
    const query = document.getElementById('fileSearch').value.toLowerCase();
    document.querySelectorAll('#fileGrid .item-card').forEach(card => {
        const name = card.querySelector('.item-name').textContent.toLowerCase();
        card.style.display = name.includes(query) ? '' : 'none';
    });
}

async function fetchTemplatesBar() {
    const templates = await apiFetch(`${API_BASE}/folders/templates`) || [];
    const container = document.getElementById('templatesList');
    container.innerHTML = '';
    templates.forEach(t => {
        const btn = document.createElement('button');
        btn.className = 'btn-secondary';
        btn.style.cssText = 'font-size:0.8rem;padding:4px 12px;margin-right:8px;';
        btn.innerHTML = `Apply ${t.name}`;
        btn.onclick = () => applyTemplate(t.id);
        container.appendChild(btn);
    });
}

async function applyTemplate(id) {
    await apiFetch(`${API_BASE}/folders/apply-template/${id}`, { method: 'POST' });
    showToast('Template applied!');
    fetchFolders(currentFolderId);
}

function renderExplorer(subfolders, files) {
    const grid = document.getElementById('fileGrid');
    grid.innerHTML = '';

    subfolders.forEach(folder => {
        const card = createItemCard(folder.name, '📁', () => {
            pathStack.push({ id: folder.id, name: folder.name });
            updateBreadcrumb();
            fetchFolders(folder.id);
        }, folder.id, true);
        grid.appendChild(card);
    });

    files.forEach(file => {
        const card = createItemCard(file.fileName, getFileIcon(file.fileName), null, file.id);
        grid.appendChild(card);
    });

    if (subfolders.length === 0 && files.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <div style="font-size:3rem;margin-bottom:12px;">📂</div>
                <p>This folder is empty</p>
                <p style="color:var(--text-muted);font-size:0.85rem;margin-top:4px;">Upload files or apply a template to get started</p>
            </div>`;
    }
}

function getFileIcon(name) {
    if (!name) return '📄';
    const ext = name.split('.').pop().toLowerCase();
    const icons = {
        pdf: '📕', doc: '📝', docx: '📝', xls: '📊', xlsx: '📊',
        ppt: '📊', pptx: '📊', jpg: '🖼️', jpeg: '🖼️', png: '🖼️',
        gif: '🖼️', mp4: '🎬', mp3: '🎵', zip: '🗜️', rar: '🗜️',
        txt: '📃', js: '⚙️', java: '☕', py: '🐍', json: '{}',
    };
    return icons[ext] || '📄';
}

function createItemCard(name, icon, onClick, id = null, isFolder = false) {
    const div = document.createElement('div');
    div.className = 'item-card';
    if (onClick) div.onclick = onClick;

    div.innerHTML = `
        <div class="item-icon">${icon}</div>
        <div class="item-name" title="${name}">${name}</div>
        <div class="item-actions">
            ${!isFolder ? `<button class="action-btn" title="Share" onclick="event.stopPropagation(); shareFile(${id})">🔗</button>` : ''}
            <button class="action-btn" title="Delete" onclick="event.stopPropagation(); deleteItem(${id}, this, ${isFolder})">🗑️</button>
        </div>
    `;
    return div;
}

async function deleteItem(id, btn, isFolder = false) {
    if (!id || !confirm(`Delete this ${isFolder ? 'folder' : 'file'}?`)) return;
    const url = isFolder ? `${API_BASE}/folders/${id}` : `${API_BASE}/files/${id}`;
    const res = await apiFetch(url, { method: 'DELETE' });
    if (res !== null) {
        showToast(`${isFolder ? 'Folder' : 'File'} deleted`);
        fetchFolders(currentFolderId);
    }
}

function updateBreadcrumb() {
    const container = document.getElementById('breadcrumb');
    container.innerHTML = '';
    pathStack.forEach((crumb, index) => {
        const span = document.createElement('span');
        span.className = 'crumb';
        span.textContent = crumb.name;
        span.onclick = () => {
            pathStack = pathStack.slice(0, index + 1);
            updateBreadcrumb();
            fetchFolders(crumb.id === 'root' ? null : crumb.id);
        };
        container.appendChild(span);
    });
}

// ---- TEMPLATES VIEW ----
async function loadTemplatesView() {
    const grid = document.getElementById('templatesGrid');
    grid.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Loading templates...</p></div>';
    const templates = await apiFetch(`${API_BASE}/folders/templates`) || [];
    grid.innerHTML = '';

    if (templates.length === 0) {
        grid.innerHTML = '<div class="empty-state"><p>No templates available</p></div>';
        return;
    }

    const icons = ['🗂️', '📁', '📦', '🗃️', '📋'];
    templates.forEach((t, i) => {
        const card = document.createElement('div');
        card.className = 'template-card';
        card.innerHTML = `
            <div class="template-icon">${icons[i % icons.length]}</div>
            <h3>${t.name}</h3>
            <p>${t.description || 'Pre-built folder structure for quick organization'}</p>
            <button class="btn-primary" onclick="applyTemplateFromView(${t.id})">
                <span class="icon">▶</span> Apply Template
            </button>
        `;
        grid.appendChild(card);
    });
}

async function applyTemplateFromView(id) {
    await apiFetch(`${API_BASE}/folders/apply-template/${id}`, { method: 'POST' });
    showToast('✅ Template applied! Switch to My Files to view the new structure.');
    await fetchTemplatesBar();
}

// ---- SHARED VIEW ----
async function loadSharedView() {
    const tableBody = document.getElementById('sharedLinksTable');
    tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;">Loading shared links...</td></tr>';
    
    const shares = await apiFetch(`${API_BASE}/files/shares`) || [];
    tableBody.innerHTML = '';

    if (shares.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-muted);">No active share links found.</td></tr>';
        return;
    }

    shares.forEach(s => {
        const tr = document.createElement('tr');
        const expiryDate = new Date(s.expiresAt).toLocaleString();
        tr.innerHTML = `
            <td><strong>${s.fileName}</strong></td>
            <td>${expiryDate}</td>
            <td><span class="badge ${s.active ? 'badge-active' : 'badge-expired'}">${s.active ? 'Active' : 'Expired'}</span></td>
            <td>
                <button class="btn-secondary" style="padding:4px 8px;font-size:0.8rem;" onclick="revokeLink('${s.token}')">Revoke</button>
            </td>
        `;
        tableBody.appendChild(tr);
    });
}

async function revokeLink(token) {
    if (!confirm('Revoke this share link?')) return;
    await apiFetch(`${API_BASE}/files/shares/${token}`, { method: 'DELETE' });
    showToast('Link revoked');
    loadSharedView();
}

// ---- SETTINGS VIEW ----
async function loadSettingsView() {
    // Refresh the username in settings
    const uname = document.getElementById('username').textContent;
    if (uname && uname !== 'Loading...') {
        document.getElementById('settingsUsername').textContent = uname;
    }
}

// ---- SHARE MODAL ----
async function shareFile(id) {
    const data = await apiFetch(`${API_BASE}/files/share`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fileId: id, expiresMinutes: 60 })
    });
    if (data && data.shareUrl) {
        document.getElementById('shareUrl').value = window.location.origin + data.shareUrl;
        document.getElementById('shareModal').style.display = 'flex';
    } else {
        showToast('⚠ Could not generate share link');
    }
}

function copyShareLink() {
    const input = document.getElementById('shareUrl');
    input.select();
    document.execCommand('copy');
    showToast('Link copied to clipboard!');
}

function closeModal() {
    document.getElementById('shareModal').style.display = 'none';
}

// ---- EVENT LISTENERS ----
function setupEventListeners() {
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');
    const newFolderBtn = document.getElementById('newFolderBtn');

    if (newFolderBtn) {
        newFolderBtn.onclick = async () => {
            const name = prompt('Enter folder name:');
            if (name) {
                await apiFetch(`${API_BASE}/folders`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, parentId: currentFolderId })
                });
                showToast('Folder created');
                fetchFolders(currentFolderId);
            }
        };
    }

    uploadBtn.onclick = () => fileInput.click();
    fileInput.onchange = async () => {
        if (fileInput.files.length > 0) {
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            if (currentFolderId) formData.append('folderId', currentFolderId);

            showToast('⏳ Uploading...');
            await apiFetch(`${API_BASE}/files/upload`, { method: 'POST', body: formData }, true);
            showToast('✅ File uploaded!');
            fetchFolders(currentFolderId);
            fileInput.value = '';
        }
    };
}

// ---- API HELPER ----
async function apiFetch(url, options = {}, isMultipart = false) {
    const token = localStorage.getItem('jwt_token');
    const headers = options.headers || {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const finalOptions = { ...options, headers };
    try {
        const response = await fetch(url, finalOptions);
        if (response.status === 401 || response.status === 403) {
            localStorage.removeItem('jwt_token');
            await handleDefaultAuth();
            return apiFetch(url, options, isMultipart);
        }
        if (response.status === 204 || response.status === 200 && response.headers.get('content-length') === '0') return true;
        const text = await response.text();
        return text ? JSON.parse(text) : null;
    } catch (e) {
        console.error('API error:', url, e);
        return null;
    }
}

// ---- TOAST ----
function showToast(msg) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}
