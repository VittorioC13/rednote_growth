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
            background: linear-gradient(135deg, #FF2442 0%, #FF6B6B 50%, #FFA07A 100%);
            min-height: 100vh;
            padding: 40px 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 60px;
            padding: 40px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }

        .header h1 {
            font-size: 3em;
            font-weight: 300;
            letter-spacing: -1px;
            margin-bottom: 10px;
            color: #FF2442;
        }

        .header p {
            color: #666;
            font-size: 1.1em;
            font-weight: 300;
        }

        .status-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 0.9em;
            font-weight: 600;
            margin-top: 15px;
            background: #52C41A;
            color: white;
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
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            transition: transform 0.3s;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        .card h2 {
            font-size: 1.5em;
            font-weight: 300;
            margin-bottom: 20px;
            color: #333;
        }

        .generate-btn {
            width: 100%;
            padding: 20px;
            background: linear-gradient(135deg, #FF2442 0%, #FF6B6B 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.2em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
        }

        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(255, 36, 66, 0.4);
        }

        .generate-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
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
            border: 4px solid #f3f3f3;
            border-top: 4px solid #FF2442;
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
            background: #F6FFED;
            color: #52C41A;
            border-radius: 12px;
            margin-bottom: 20px;
            font-weight: 600;
            text-align: center;
        }

        .success-message.active {
            display: block;
        }

        .post-item {
            padding: 25px;
            border: 1px solid #f0f0f0;
            border-radius: 12px;
            margin-bottom: 20px;
            background: #FFF5F5;
            transition: all 0.2s;
        }

        .post-item:hover {
            border-color: #FF2442;
            box-shadow: 0 5px 15px rgba(255, 36, 66, 0.1);
        }

        .post-number {
            color: #FF2442;
            font-weight: 700;
            font-size: 1.2em;
            margin-bottom: 15px;
        }

        .post-content {
            color: #333;
            line-height: 1.8;
            white-space: pre-wrap;
            margin-bottom: 15px;
            font-size: 1.05em;
        }

        .copy-btn {
            background: #FF2442;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.95em;
            transition: all 0.2s;
        }

        .copy-btn:hover {
            background: #E01F3B;
            transform: translateY(-1px);
        }

        .info-box {
            background: #FFF5F5;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
        }

        .info-box h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.1em;
            font-weight: 600;
        }

        .info-box ul {
            list-style: none;
            padding: 0;
        }

        .info-box li {
            padding: 10px 0;
            color: #666;
            border-bottom: 1px solid #ffe0e0;
        }

        .info-box li:last-child {
            border-bottom: none;
        }

        .info-box strong {
            color: #FF2442;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }

        .empty-state-icon {
            font-size: 4em;
            margin-bottom: 20px;
        }

        .footer {
            text-align: center;
            padding: 40px;
            color: white;
            font-size: 0.9em;
            margin-top: 60px;
        }

        .footer a {
            color: white;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📕 小红书 Content Generator</h1>
            <p>AI-Powered Viral US Stock Trading Content for RedNote</p>
            <div class="status-badge">✓ Online & Ready</div>
        </div>

        <div class="main-grid">
            <div class="card">
                <h2>Generate Content</h2>
                <div class="success-message" id="successMessage">
                    ✓ 10 viral posts generated successfully!
                </div>
                <button class="generate-btn" id="generateBtn" onclick="generateContent()">
                    🚀 Generate 10 Viral Posts
                </button>
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Generating viral 美股 content...</p>
                    <p style="font-size: 0.9em; margin-top: 10px;">This takes about 15-20 seconds</p>
                </div>

                <div class="info-box">
                    <h3>What Gets Generated:</h3>
                    <ul>
                        <li><strong>10 Unique Posts</strong> - Ready for 小红书</li>
                        <li><strong>Viral Formats</strong> - Based on 600-3750 likes</li>
                        <li><strong>US Stock Focus</strong> - Trading, strategies, success</li>
                        <li><strong>Copy & Paste</strong> - Direct to 小红书</li>
                    </ul>
                </div>
            </div>

            <div class="card">
                <h2>Generated Posts</h2>
                <div id="postsContainer">
                    <div class="empty-state">
                        <div class="empty-state-icon">📝</div>
                        <p>No posts yet. Click the button to generate!</p>
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
                        📋 Copy to Clipboard
                    </button>
                `;
                container.appendChild(postItem);
            });
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert('✓ Copied to clipboard!');
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
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured. Set DEEPSEEK_API_KEY environment variable.'})

        generator = RedNoteContentGenerator(api_key)
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
