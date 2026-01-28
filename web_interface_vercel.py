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
    <title>小红书 Content Generator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #FF2442 0%, #FF6B6B 50%, #FFA07A 100%);
            min-height: 100vh;
            padding: 24px;
        }

        .container { max-width: 960px; margin: 0 auto; }

        /* Header */
        .header {
            background: white;
            padding: 26px 30px;
            border-radius: 18px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
            margin-bottom: 22px;
            text-align: center;
        }
        .header h1 { color: #FF2442; font-size: 1.9em; margin-bottom: 5px; }
        .header p { color: #888; font-size: 0.92em; }
        .status-badge {
            display: inline-block;
            padding: 5px 14px;
            border-radius: 16px;
            font-size: 0.8em;
            font-weight: 600;
            margin-top: 10px;
            background: #52C41A;
            color: white;
        }

        /* Account Tabs */
        .account-tabs {
            display: flex;
            gap: 12px;
            justify-content: center;
            margin-bottom: 22px;
        }
        .tab {
            width: 52px; height: 52px;
            border-radius: 50%;
            border: 2.5px solid #ddd;
            background: white;
            color: #999;
            font-size: 1.1em;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }
        .tab:hover { border-color: #FF2442; color: #FF2442; transform: translateY(-2px); }
        .tab.active {
            background: linear-gradient(135deg, #FF2442, #FF6B6B);
            color: white;
            border-color: transparent;
            box-shadow: 0 4px 16px rgba(255, 36, 66, 0.35);
            transform: translateY(-2px);
        }

        /* Account Panel */
        .account-panel {
            background: white;
            border-radius: 18px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
            padding: 26px;
            margin-bottom: 22px;
        }
        .panel-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .panel-header h2 { color: #222; font-size: 1.35em; }
        .persona-badge {
            display: inline-block;
            padding: 5px 14px;
            background: linear-gradient(135deg, #FF2442, #FF6B6B);
            color: white;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
        }

        /* Persona Selector */
        .persona-row {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 6px;
        }
        .persona-row label { color: #555; font-size: 0.88em; font-weight: 600; white-space: nowrap; }
        .persona-row select {
            flex: 1;
            padding: 9px 34px 9px 12px;
            border: 1.5px solid #e8e8e8;
            border-radius: 10px;
            font-size: 0.88em;
            color: #333;
            background: white;
            cursor: pointer;
            outline: none;
            transition: border-color 0.2s;
            appearance: none;
            -webkit-appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23999' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 10px center;
        }
        .persona-row select:focus { border-color: #FF2442; }
        .save-persona-btn {
            display: none;
            padding: 7px 16px;
            background: #52C41A;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 0.82em;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
        }
        .save-persona-btn:hover { background: #49AA16; }
        .persona-desc { color: #999; font-size: 0.83em; margin-bottom: 20px; margin-left: 50px; }

        /* Generate */
        .generate-btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #FF2442, #FF6B6B);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.08em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s;
            margin-bottom: 14px;
        }
        .generate-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255,36,66,0.4); }
        .generate-btn:disabled { background: #ccc; cursor: not-allowed; transform: none; box-shadow: none; }

        /* Loading */
        .loading { display: none; text-align: center; padding: 22px 0; }
        .loading.active { display: block; }
        .spinner {
            border: 3px solid #f0f0f0;
            border-top: 3px solid #FF2442;
            border-radius: 50%;
            width: 34px; height: 34px;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .loading p { color: #888; font-size: 0.88em; }

        /* Success */
        .success-message {
            display: none;
            padding: 11px 16px;
            background: #F0FFF4;
            color: #52C41A;
            border-radius: 10px;
            margin-bottom: 16px;
            font-weight: 600;
            font-size: 0.88em;
        }
        .success-message.active { display: block; }

        /* Posts Grid */
        .posts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 6px; }
        @media (max-width: 700px) { .posts-grid { grid-template-columns: 1fr; } }

        .post-card {
            background: #FAFAFA;
            border: 1px solid #eee;
            border-radius: 12px;
            padding: 16px 14px 12px 42px;
            position: relative;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        .post-card:hover { border-color: #FF2442; box-shadow: 0 3px 10px rgba(255,36,66,0.1); }
        .post-num {
            position: absolute;
            top: 13px; left: 13px;
            width: 23px; height: 23px;
            background: #FF2442;
            color: white;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.72em;
            font-weight: 700;
        }
        .post-content {
            color: #444;
            line-height: 1.5;
            font-size: 0.86em;
            white-space: pre-wrap;
            max-height: 180px;
            overflow: hidden;
            -webkit-mask-image: linear-gradient(to bottom, black 65%, transparent);
            mask-image: linear-gradient(to bottom, black 65%, transparent);
        }
        .post-card.expanded .post-content { max-height: none; -webkit-mask-image: none; mask-image: none; }
        .post-actions { display: flex; gap: 6px; margin-top: 9px; }
        .copy-btn, .expand-btn {
            padding: 4px 11px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.78em;
            color: #666;
            background: white;
            transition: all 0.2s;
        }
        .copy-btn:hover { background: #FF2442; color: white; border-color: #FF2442; }
        .expand-btn:hover { background: #f0f0f0; }
        .copy-btn.copied { background: #52C41A; color: white; border-color: #52C41A; }

        .empty-state { text-align: center; color: #aaa; padding: 28px 16px; font-size: 0.88em; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📕 小红书 Content Generator</h1>
        <p>5-Account Multi-Persona System</p>
        <div class="status-badge" id="statusBadge">● Ready</div>
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
            <span class="persona-badge" id="personaBadge">年轻暴富</span>
        </div>
        <div class="persona-row">
            <label>人设:</label>
            <select id="personaSelect" onchange="onPersonaChange()"></select>
            <button class="save-persona-btn" id="savePersonaBtn" onclick="savePersona()">Save</button>
        </div>
        <p class="persona-desc" id="personaDesc">Loading...</p>

        <button class="generate-btn" id="generateBtn" onclick="generateContent()">
            🚀 Generate Posts for Account A
        </button>
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Generating posts...</p>
        </div>
        <div class="success-message" id="successMessage">✓ Posts generated successfully!</div>
        <div class="posts-grid" id="postsGrid"></div>
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
    document.getElementById('generateBtn').textContent = '🚀 Generate Posts for Account ' + currentAccount;
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
                '<button class="copy-btn" onclick="copyPost(' + i + ')">📋 Copy</button>' +
                '<button class="expand-btn" onclick="toggleExpand(this)">Expand</button>' +
            '</div>';
        grid.appendChild(card);
    });
}

function copyPost(index) {
    navigator.clipboard.writeText(currentPosts[index].content).then(() => {
        const btns = document.querySelectorAll('.copy-btn');
        btns[index].textContent = '✓ Copied';
        btns[index].classList.add('copied');
        setTimeout(() => { btns[index].textContent = '📋 Copy'; btns[index].classList.remove('copied'); }, 1500);
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
