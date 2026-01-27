"""
Web interface for RedNote Content Generator - VERCEL SERVERLESS
Clean RedNote theme design
No file I/O - works in read-only serverless environment
"""
from flask import Flask, render_template_string, jsonify, request
import os
from datetime import datetime
from dotenv import load_dotenv
from rednote_content_generator_serverless import RedNoteContentGenerator

load_dotenv()

app = Flask(__name__)

# In-memory storage for generated posts (lost on restart, but that's ok for serverless)
posts_cache = []

# HTML Template - RedNote Theme Design
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小红书 Content Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

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
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image:
                repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,.05) 2px, rgba(0,0,0,.05) 4px),
                repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(0,0,0,.05) 2px, rgba(0,0,0,.05) 4px);
            pointer-events: none;
            opacity: 0.3;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 60px;
            padding: 40px;
            border-bottom: 1px solid rgba(205, 92, 92, 0.2);
            position: relative;
        }

        .header h1 {
            font-size: 3em;
            font-weight: 300;
            letter-spacing: -1px;
            margin-bottom: 10px;
            color: #f5f5f5;
        }

        .header p {
            color: #b8b8b8;
            font-size: 1.1em;
            font-weight: 300;
        }

        .status-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 0.9em;
            font-weight: 300;
            margin-top: 15px;
            background: rgba(205, 92, 92, 0.1);
            color: #cd5c5c;
            border: 1px solid rgba(205, 92, 92, 0.3);
        }

        .main-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }

        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: rgba(20, 20, 20, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(205, 92, 92, 0.15);
            padding: 40px;
            transition: all 0.3s;
            position: relative;
        }

        .card:hover {
            border-color: rgba(205, 92, 92, 0.3);
            box-shadow: 0 10px 40px rgba(205, 92, 92, 0.05);
        }

        .card h2 {
            font-size: 1.5em;
            font-weight: 300;
            margin-bottom: 20px;
            color: #f5f5f5;
        }

        .generate-btn {
            width: 100%;
            padding: 20px;
            background: linear-gradient(135deg, #cd5c5c 0%, #b84e4e 100%);
            color: #ffffff;
            border: 1px solid rgba(205, 92, 92, 0.5);
            font-size: 1.2em;
            font-weight: 400;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
            position: relative;
            overflow: hidden;
        }

        .generate-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: left 0.5s;
        }

        .generate-btn:hover::before {
            left: 100%;
        }

        .generate-btn:hover {
            background: linear-gradient(135deg, #b84e4e 0%, #a34343 100%);
            box-shadow: 0 5px 20px rgba(205, 92, 92, 0.3);
        }

        .generate-btn:disabled {
            background: rgba(40, 40, 40, 0.5);
            color: #666;
            border: 1px solid rgba(60, 60, 60, 0.5);
            cursor: not-allowed;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 30px;
            color: #666;
        }

        .loading.active {
            display: block;
        }

        .spinner {
            border: 4px solid rgba(40, 40, 40, 0.3);
            border-top: 4px solid #cd5c5c;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .success-message {
            display: none;
            padding: 20px;
            background: rgba(205, 92, 92, 0.1);
            color: #cd5c5c;
            border: 1px solid rgba(205, 92, 92, 0.3);
            margin-bottom: 20px;
            font-weight: 300;
            text-align: center;
        }

        .success-message.active {
            display: block;
        }

        .post-item {
            padding: 25px;
            border: 1px solid rgba(205, 92, 92, 0.15);
            margin-bottom: 20px;
            background: rgba(20, 20, 20, 0.4);
            backdrop-filter: blur(5px);
            transition: all 0.2s;
        }

        .post-item:hover {
            border-color: rgba(205, 92, 92, 0.3);
            background: rgba(20, 20, 20, 0.6);
        }

        .post-number {
            color: #ffffff;
            font-weight: 300;
            font-size: 1.2em;
            margin-bottom: 15px;
        }

        .post-content {
            color: #e8e8e8;
            line-height: 1.8;
            white-space: pre-wrap;
            margin-bottom: 15px;
            font-size: 1.05em;
        }

        .copy-btn {
            background: transparent;
            color: #cd5c5c;
            border: 1px solid rgba(205, 92, 92, 0.5);
            padding: 10px 20px;
            cursor: pointer;
            font-weight: 400;
            font-size: 0.95em;
            transition: all 0.2s;
        }

        .copy-btn:hover {
            background: rgba(205, 92, 92, 0.1);
            border-color: #cd5c5c;
        }

        .info-box {
            background: rgba(20, 20, 20, 0.3);
            padding: 20px;
            border: 1px solid rgba(205, 92, 92, 0.15);
            margin-top: 20px;
        }

        .info-box h3 {
            color: #f5f5f5;
            margin-bottom: 15px;
            font-size: 1.1em;
            font-weight: 300;
        }

        .info-box ul {
            list-style: none;
            padding: 0;
        }

        .info-box li {
            padding: 10px 0;
            color: #b8b8b8;
            border-bottom: 1px solid rgba(205, 92, 92, 0.1);
        }

        .info-box li:last-child {
            border-bottom: none;
        }

        .info-box strong {
            color: #cd5c5c;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #888;
        }

        .footer {
            text-align: center;
            padding: 40px;
            color: #888;
            font-size: 0.9em;
            margin-top: 60px;
            border-top: 1px solid rgba(205, 92, 92, 0.15);
        }

        .footer a {
            color: #cd5c5c;
            text-decoration: none;
            border-bottom: 1px solid rgba(205, 92, 92, 0.3);
            transition: all 0.2s;
        }

        .footer a:hover {
            color: #b84e4e;
            border-bottom: 1px solid #cd5c5c;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>小红书 Content Generator</h1>
            <p>AI-Powered Viral US Stock Trading Content for RedNote</p>
            <div class="status-badge">Online & Ready</div>
        </div>

        <div class="main-grid">
            <div class="card">
                <h2>Generate Content</h2>
                <div class="success-message" id="successMessage">
                    10 viral posts generated successfully
                </div>
                <button class="generate-btn" id="generateBtn" onclick="generateContent()">
                    Generate 10 Viral Posts
                </button>
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Generating viral content...</p>
                    <p style="font-size: 0.9em; margin-top: 10px;">This takes about 15-20 seconds</p>
                </div>

                <div class="info-box">
                    <h3>What Gets Generated</h3>
                    <ul>
                        <li><strong>10 Unique Posts</strong> Ready for RedNote</li>
                        <li><strong>Viral Formats</strong> Based on 600-3750 likes</li>
                        <li><strong>US Stock Focus</strong> Trading, strategies, success</li>
                        <li><strong>Copy & Paste</strong> Direct to platform</li>
                    </ul>
                </div>
            </div>

            <div class="card">
                <h2>Generated Posts</h2>
                <div id="postsContainer">
                    <div class="empty-state">
                        <p>No posts yet. Click the button to generate.</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>Powered by DeepSeek AI | Built with Flask</p>
            <p><a href="https://github.com/VittorioC13/rednote_growth" target="_blank">View on GitHub</a></p>
        </div>
    </div>

    <script>
        function generateContent() {
            const btn = document.getElementById('generateBtn');
            const loading = document.getElementById('loading');
            const successMsg = document.getElementById('successMessage');
            const container = document.getElementById('postsContainer');

            btn.disabled = true;
            loading.classList.add('active');
            successMsg.classList.remove('active');

            fetch('/generate', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                btn.disabled = false;
                loading.classList.remove('active');

                if (data.success) {
                    successMsg.classList.add('active');
                    displayPosts(data.posts);
                    setTimeout(() => successMsg.classList.remove('active'), 5000);
                } else {
                    alert('Error: ' + (data.error || 'Failed to generate content'));
                }
            })
            .catch(error => {
                btn.disabled = false;
                loading.classList.remove('active');
                alert('Error: ' + error.message);
            });
        }

        function displayPosts(posts) {
            const container = document.getElementById('postsContainer');
            container.innerHTML = '';

            posts.forEach((post, index) => {
                const postItem = document.createElement('div');
                postItem.className = 'post-item';
                postItem.innerHTML = `
                    <div class="post-number">Post ${post.number}</div>
                    <div class="post-content">${post.content}</div>
                    <button class="copy-btn" onclick="copyToClipboard(\`${post.content.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)">
                        Copy to Clipboard
                    </button>
                `;
                container.appendChild(postItem);
            });
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert('Copied to clipboard');
            }).catch(err => {
                alert('Failed to copy: ' + err);
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    """Generate new content - serverless compatible"""
    try:
        # API key will use fallback if not set
        generator = RedNoteContentGenerator()
        posts = generator.generate_posts()

        # Store in memory (will be lost on restart, but that's ok for serverless)
        global posts_cache
        posts_cache = posts

        return jsonify({'success': True, 'posts': posts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'rednote-generator'})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
