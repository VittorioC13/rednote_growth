"""
Multi-account web interface for RedNote Content Generator - VERCEL SERVERLESS
Supports 5 independent accounts with persona-based content generation
No file I/O - works in read-only serverless environment
"""
from flask import Flask, render_template_string, jsonify, request
import os
from datetime import datetime
from dotenv import load_dotenv
from rednote_content_generator_serverless import RedNoteContentGenerator, PERSONAS, DEFAULT_ACCOUNTS
import copy

load_dotenv()

app = Flask(__name__)

# In-memory storage (lost on restart, that's ok for serverless)
accounts_store = copy.deepcopy(DEFAULT_ACCOUNTS)
posts_cache = {}  # keyed by account_id

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RedNote Content Generator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d1f1f 50%, #3d2626 100%);
            color: #e8e8e8;
            min-height: 100vh;
            padding: 40px 20px;
            line-height: 1.6;
            position: relative;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-image:
                repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,.05) 2px, rgba(0,0,0,.05) 4px),
                repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(0,0,0,.05) 2px, rgba(0,0,0,.05) 4px);
            pointer-events: none;
            opacity: 0.3;
        }

        .container { max-width: 960px; margin: 0 auto; position: relative; }

        /* Header */
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 36px;
            border-bottom: 1px solid rgba(205, 92, 92, 0.15);
        }
        .header h1 {
            font-size: 2.2em;
            font-weight: 300;
            letter-spacing: -0.5px;
            color: #f0f0f0;
            margin-bottom: 8px;
        }
        .header p { color: #777; font-size: 0.95em; font-weight: 300; }
        .status-badge {
            display: inline-block;
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 300;
            margin-top: 12px;
            background: rgba(205, 92, 92, 0.1);
            color: #cd5c5c;
            border: 1px solid rgba(205, 92, 92, 0.25);
        }

        /* Account Tabs */
        .account-tabs {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-bottom: 28px;
        }
        .tab {
            width: 48px; height: 48px;
            border-radius: 50%;
            border: 1.5px solid rgba(205, 92, 92, 0.2);
            background: rgba(20, 20, 20, 0.5);
            color: #666;
            font-size: 0.95em;
            font-weight: 400;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .tab:hover { border-color: rgba(205, 92, 92, 0.5); color: #cd5c5c; }
        .tab.active {
            background: rgba(205, 92, 92, 0.15);
            color: #cd5c5c;
            border-color: rgba(205, 92, 92, 0.6);
            box-shadow: 0 0 12px rgba(205, 92, 92, 0.15);
        }

        /* Account Panel */
        .account-panel {
            background: rgba(20, 20, 20, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(205, 92, 92, 0.12);
            border-radius: 4px;
            padding: 32px;
            margin-bottom: 28px;
            transition: border-color 0.3s;
        }
        .account-panel:hover { border-color: rgba(205, 92, 92, 0.25); }

        .panel-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 22px;
        }
        .panel-header h2 { color: #f0f0f0; font-size: 1.2em; font-weight: 300; }
        .persona-badge {
            display: inline-block;
            padding: 4px 12px;
            background: rgba(205, 92, 92, 0.12);
            color: #cd5c5c;
            border: 1px solid rgba(205, 92, 92, 0.3);
            border-radius: 3px;
            font-size: 0.78em;
            font-weight: 400;
        }

        /* Persona Selector */
        .persona-row {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 6px;
        }
        .persona-row label { color: #888; font-size: 0.85em; font-weight: 400; white-space: nowrap; min-width: 32px; }
        .persona-row select {
            flex: 1;
            padding: 8px 32px 8px 10px;
            border: 1px solid rgba(205, 92, 92, 0.2);
            border-radius: 3px;
            font-size: 0.85em;
            color: #ccc;
            background: rgba(30, 30, 30, 0.8);
            cursor: pointer;
            outline: none;
            transition: border-color 0.2s;
            appearance: none;
            -webkit-appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 10px center;
        }
        .persona-row select:focus { border-color: rgba(205, 92, 92, 0.5); }
        .persona-row select option { background: #1e1e1e; color: #ccc; }
        .save-persona-btn {
            display: none;
            padding: 6px 14px;
            background: rgba(82, 196, 26, 0.15);
            color: #52c41a;
            border: 1px solid rgba(82, 196, 26, 0.3);
            border-radius: 3px;
            font-size: 0.78em;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s;
        }
        .save-persona-btn:hover { background: rgba(82, 196, 26, 0.25); }
        .persona-desc { color: #555; font-size: 0.8em; margin-bottom: 24px; margin-left: 44px; }

        /* Generate */
        .generate-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #cd5c5c 0%, #b84e4e 100%);
            color: #fff;
            border: 1px solid rgba(205, 92, 92, 0.4);
            border-radius: 3px;
            font-size: 1em;
            font-weight: 400;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 18px;
            position: relative;
            overflow: hidden;
        }
        .generate-btn::before {
            content: '';
            position: absolute;
            top: 0; left: -100%;
            width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
            transition: left 0.5s;
        }
        .generate-btn:hover::before { left: 100%; }
        .generate-btn:hover {
            background: linear-gradient(135deg, #b84e4e 0%, #a34343 100%);
            box-shadow: 0 4px 16px rgba(205, 92, 92, 0.25);
        }
        .generate-btn:disabled {
            background: rgba(40, 40, 40, 0.5);
            color: #555;
            border-color: rgba(60, 60, 60, 0.4);
            cursor: not-allowed;
            box-shadow: none;
        }

        /* Loading */
        .loading { display: none; text-align: center; padding: 28px 0; }
        .loading.active { display: block; }
        .spinner {
            border: 3px solid rgba(40, 40, 40, 0.4);
            border-top: 3px solid #cd5c5c;
            border-radius: 50%;
            width: 36px; height: 36px;
            animation: spin 0.9s linear infinite;
            margin: 0 auto 12px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .loading p { color: #555; font-size: 0.85em; font-weight: 300; }

        /* Success */
        .success-message {
            display: none;
            padding: 10px 16px;
            background: rgba(82, 196, 26, 0.08);
            color: #52c41a;
            border: 1px solid rgba(82, 196, 26, 0.2);
            border-radius: 3px;
            margin-bottom: 18px;
            font-size: 0.82em;
            font-weight: 300;
        }
        .success-message.active { display: block; }

        /* Posts Grid */
        .posts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 8px; }
        @media (max-width: 700px) { .posts-grid { grid-template-columns: 1fr; } }

        .post-card {
            background: rgba(20, 20, 20, 0.4);
            border: 1px solid rgba(205, 92, 92, 0.12);
            border-radius: 3px;
            padding: 18px 16px 14px 42px;
            position: relative;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        .post-card:hover {
            border-color: rgba(205, 92, 92, 0.3);
            box-shadow: 0 4px 14px rgba(205, 92, 92, 0.08);
        }
        .post-num {
            position: absolute;
            top: 15px; left: 14px;
            width: 22px; height: 22px;
            background: rgba(205, 92, 92, 0.15);
            color: #cd5c5c;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.7em;
            font-weight: 400;
        }
        .post-content {
            color: #bbb;
            line-height: 1.6;
            font-size: 0.85em;
            white-space: pre-wrap;
            max-height: 180px;
            overflow: hidden;
            -webkit-mask-image: linear-gradient(to bottom, black 60%, transparent);
            mask-image: linear-gradient(to bottom, black 60%, transparent);
        }
        .post-card.expanded .post-content { max-height: none; -webkit-mask-image: none; mask-image: none; }
        .post-actions { display: flex; gap: 6px; margin-top: 10px; }
        .copy-btn, .expand-btn {
            padding: 4px 10px;
            border: 1px solid rgba(205, 92, 92, 0.2);
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.75em;
            color: #888;
            background: transparent;
            transition: all 0.2s;
        }
        .copy-btn:hover { background: rgba(205, 92, 92, 0.1); color: #cd5c5c; border-color: rgba(205, 92, 92, 0.4); }
        .expand-btn:hover { background: rgba(255,255,255,0.05); color: #aaa; }
        .copy-btn.copied { background: rgba(82, 196, 26, 0.12); color: #52c41a; border-color: rgba(82, 196, 26, 0.3); }

        .empty-state { text-align: center; color: #444; padding: 40px 16px; font-size: 0.85em; font-weight: 300; }

        .footer {
            text-align: center;
            padding: 32px;
            color: #555;
            font-size: 0.8em;
            margin-top: 20px;
            border-top: 1px solid rgba(205, 92, 92, 0.1);
        }
        /* no links in footer */
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>RedNote Content Generator</h1>
        <p>5-Account Multi-Persona System</p>
        <div class="status-badge" id="statusBadge">Online</div>
    </div>

    <div class="account-tabs" id="accountTabs">
        <button class="tab active" data-account="A" onclick="selectAccount('A')">A</button>
        <button class="tab" data-account="B" onclick="selectAccount('B')">B</button>
        <button class="tab" data-account="C" onclick="selectAccount('C')">C</button>
        <button class="tab" data-account="D" onclick="selectAccount('D')">D</button>
        <button class="tab" data-account="E" onclick="selectAccount('E')">E</button>
    </div>

    <div class="account-panel" id="accountPanel">
        <div class="panel-header">
            <h2 id="accountTitle">Account A</h2>
            <span class="persona-badge" id="personaBadge">Loading</span>
        </div>
        <div class="persona-row">
            <label>人设</label>
            <select id="personaSelect" onchange="onPersonaChange()"></select>
            <button class="save-persona-btn" id="savePersonaBtn" onclick="savePersona()">Save</button>
        </div>
        <p class="persona-desc" id="personaDesc"></p>

        <button class="generate-btn" id="generateBtn" onclick="generateContent()">
            Generate Posts for Account A
        </button>
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Generating content...</p>
        </div>
        <div class="success-message" id="successMessage">Posts generated.</div>
        <div class="posts-grid" id="postsGrid"></div>
    </div>

    <div class="footer">
        <p>Powered by DeepSeek AI</p>
    </div>
</div>

<script>
let currentAccount = 'A';
let accounts = {};
let personas = {};
let originalPersona = '';
let currentPosts = [];

// Init
fetch('/accounts').then(r => r.json()).then(data => {
    accounts = data.accounts;
    personas = data.personas;
    populatePersonaSelect();
    updatePanel();
});

function populatePersonaSelect() {
    const sel = document.getElementById('personaSelect');
    sel.innerHTML = '';
    Object.entries(personas).forEach(([id, p]) => {
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = p.name + ' — ' + p.description;
        sel.appendChild(opt);
    });
}

function selectAccount(id) {
    currentAccount = id;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-account="' + id + '"]').classList.add('active');
    updatePanel();
    document.getElementById('postsGrid').innerHTML = '';
    document.getElementById('successMessage').classList.remove('active');
    currentPosts = [];
}

function updatePanel() {
    const acc = accounts[currentAccount];
    const persona = personas[acc.persona];
    originalPersona = acc.persona;
    document.getElementById('accountTitle').textContent = 'Account ' + currentAccount;
    document.getElementById('personaBadge').textContent = persona.name;
    document.getElementById('personaSelect').value = acc.persona;
    document.getElementById('personaDesc').textContent = persona.description;
    document.getElementById('generateBtn').textContent = 'Generate Posts for Account ' + currentAccount;
    document.getElementById('savePersonaBtn').style.display = 'none';
}

function onPersonaChange() {
    const sel = document.getElementById('personaSelect');
    const saveBtn = document.getElementById('savePersonaBtn');
    const desc = document.getElementById('personaDesc');
    const badge = document.getElementById('personaBadge');
    const p = personas[sel.value];
    desc.textContent = p.description;
    badge.textContent = p.name;
    saveBtn.style.display = (sel.value !== originalPersona) ? 'inline-block' : 'none';
}

function savePersona() {
    const sel = document.getElementById('personaSelect');
    accounts[currentAccount].persona = sel.value;
    originalPersona = sel.value;
    fetch('/accounts/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({account_id: currentAccount, persona: sel.value})
    }).then(r => r.json()).then(data => {
        document.getElementById('savePersonaBtn').style.display = 'none';
        if (!data.success) alert('Failed to save persona');
    });
}

function generateContent() {
    const btn = document.getElementById('generateBtn');
    const loading = document.getElementById('loading');
    const successMsg = document.getElementById('successMessage');
    const postsGrid = document.getElementById('postsGrid');

    btn.disabled = true;
    loading.classList.add('active');
    successMsg.classList.remove('active');
    postsGrid.innerHTML = '';

    fetch('/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({account_id: currentAccount})
    })
    .then(r => r.json())
    .then(data => {
        btn.disabled = false;
        loading.classList.remove('active');
        if (data.success) {
            successMsg.classList.add('active');
            currentPosts = data.posts;
            renderPosts(data.posts);
            setTimeout(() => successMsg.classList.remove('active'), 4000);
        } else {
            alert('Error: ' + (data.error || 'Generation failed'));
        }
    })
    .catch(err => {
        btn.disabled = false;
        loading.classList.remove('active');
        alert('Network error: ' + err);
    });
}

function renderPosts(posts) {
    const grid = document.getElementById('postsGrid');
    grid.innerHTML = '';
    posts.forEach((post, i) => {
        const card = document.createElement('div');
        card.className = 'post-card';
        card.innerHTML =
            '<div class="post-num">' + post.number + '</div>' +
            '<div class="post-content">' + escapeHtml(post.content) + '</div>' +
            '<div class="post-actions">' +
                '<button class="copy-btn" onclick="copyPost(' + i + ')">Copy</button>' +
                '<button class="expand-btn" onclick="toggleExpand(this)">Expand</button>' +
            '</div>';
        grid.appendChild(card);
    });
}

function copyPost(index) {
    navigator.clipboard.writeText(currentPosts[index].content).then(() => {
        const btns = document.querySelectorAll('.copy-btn');
        btns[index].textContent = 'Copied';
        btns[index].classList.add('copied');
        setTimeout(() => { btns[index].textContent = 'Copy'; btns[index].classList.remove('copied'); }, 1500);
    });
}

function toggleExpand(btn) {
    const card = btn.closest('.post-card');
    card.classList.toggle('expanded');
    btn.textContent = card.classList.contains('expanded') ? 'Less' : 'Expand';
}

function escapeHtml(str) {
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
</script>
</body>
</html>
"""


@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/accounts')
def get_accounts():
    """Return current account configs and persona definitions"""
    return jsonify({
        'accounts': accounts_store,
        'personas': PERSONAS
    })


@app.route('/accounts/update', methods=['POST'])
def update_account():
    """Update a single account's persona"""
    data = request.get_json()
    account_id = data.get('account_id')
    persona = data.get('persona')
    if account_id in accounts_store and persona in PERSONAS:
        accounts_store[account_id]['persona'] = persona
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Invalid account or persona'})


@app.route('/generate', methods=['POST'])
def generate():
    """Generate content for a specific account using its persona"""
    try:
        data = request.get_json() or {}
        account_id = data.get('account_id', 'A')
        persona_id = accounts_store.get(account_id, {}).get('persona', 'young_investor')

        generator = RedNoteContentGenerator(persona_id=persona_id)
        posts = generator.generate_posts()

        posts_cache[account_id] = posts

        return jsonify({'success': True, 'posts': posts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'rednote-generator'})


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
