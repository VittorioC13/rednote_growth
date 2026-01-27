"""
Simple web interface for RedNote Content Generator
Makes it easy to generate and view 小红书 content
"""
from flask import Flask, render_template_string, jsonify, send_file, request
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from rednote_content_generator import RedNoteContentGenerator
import glob

load_dotenv()

app = Flask(__name__)

# HTML Template with modern UI (RedNote theme)
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Hiragino Sans GB', sans-serif;
            background: linear-gradient(135deg, #FF2442 0%, #FF6B6B 50%, #FFA07A 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            margin-bottom: 30px;
            text-align: center;
        }

        .header h1 {
            color: #FF2442;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 1.1em;
        }

        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            margin-top: 10px;
        }

        .status-ready {
            background: #52C41A;
            color: white;
        }

        .status-error {
            background: #FF2442;
            color: white;
        }

        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }

        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }

        .card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
        }

        .generate-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #FF2442 0%, #FF6B6B 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.2em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 15px;
        }

        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(255, 36, 66, 0.4);
        }

        .generate-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #666;
        }

        .loading.active {
            display: block;
        }

        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #FF2442;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .files-list {
            max-height: 400px;
            overflow-y: auto;
        }

        .file-item {
            padding: 15px;
            border: 1px solid #f0f0f0;
            border-radius: 10px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s;
        }

        .file-item:hover {
            background: #FFF5F5;
            border-color: #FF2442;
        }

        .file-info {
            flex: 1;
        }

        .file-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }

        .file-date {
            font-size: 0.9em;
            color: #666;
        }

        .file-actions {
            display: flex;
            gap: 10px;
        }

        .btn-small {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 600;
            transition: all 0.2s;
        }

        .btn-view {
            background: #FF2442;
            color: white;
        }

        .btn-view:hover {
            background: #E01F3B;
        }

        .btn-download {
            background: #52C41A;
            color: white;
        }

        .btn-download:hover {
            background: #49AA16;
        }

        .success-message {
            display: none;
            padding: 15px;
            background: #F6FFED;
            color: #52C41A;
            border-radius: 10px;
            margin-bottom: 15px;
            font-weight: 600;
        }

        .success-message.active {
            display: block;
        }

        .info-box {
            background: #FFF5F5;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
        }

        .info-box h3 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1em;
        }

        .info-box ul {
            list-style: none;
            padding: 0;
        }

        .info-box li {
            padding: 8px 0;
            color: #666;
            border-bottom: 1px solid #ffe0e0;
        }

        .info-box li:last-child {
            border-bottom: none;
        }

        .info-box strong {
            color: #333;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
        }

        .modal.active {
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 20px;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            width: 90%;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .modal-close {
            background: #FF2442;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        }

        .post-item {
            padding: 20px;
            border: 1px solid #f0f0f0;
            border-radius: 10px;
            margin-bottom: 15px;
            background: #FFF5F5;
        }

        .post-number {
            color: #FF2442;
            font-weight: 700;
            font-size: 1.2em;
            margin-bottom: 10px;
        }

        .post-content {
            color: #333;
            line-height: 1.6;
            white-space: pre-wrap;
            margin-bottom: 10px;
        }

        .copy-btn {
            background: #FF2442;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9em;
        }

        .copy-btn:hover {
            background: #E01F3B;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📕 小红书 Content Generator</h1>
            <p>AI-Powered Viral US Stock Trading Content for RedNote</p>
            <div class="status-badge status-ready" id="statusBadge">
                ✓ Ready to Generate
            </div>
        </div>

        <div class="main-content">
            <div class="card">
                <h2>Generate Content</h2>
                <div class="success-message" id="successMessage">
                    ✓ Content generated successfully!
                </div>
                <button class="generate-btn" id="generateBtn" onclick="generateContent()">
                    🚀 Generate 10 Posts Now
                </button>
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Generating viral 美股 content...</p>
                    <p style="font-size: 0.9em;">This takes about 15-20 seconds</p>
                </div>

                <div class="info-box">
                    <h3>What Gets Generated:</h3>
                    <ul>
                        <li><strong>10 Unique Posts</strong> - Ready for 小红书</li>
                        <li><strong>Viral Formats</strong> - Based on 600-3750 likes posts</li>
                        <li><strong>US Stock Focus</strong> - Trading, strategy, success stories</li>
                        <li><strong>PDF + Text</strong> - Easy to copy & paste</li>
                    </ul>
                </div>
            </div>

            <div class="card">
                <h2>Generated Files</h2>
                <div class="files-list" id="filesList">
                    <p style="color: #666; text-align: center; padding: 40px;">
                        No files yet. Generate your first batch!
                    </p>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal for viewing posts -->
    <div class="modal" id="postsModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Generated Posts</h2>
                <button class="modal-close" onclick="closeModal()">Close</button>
            </div>
            <div id="postsContainer"></div>
        </div>
    </div>

    <script>
        // Load files on page load
        loadFiles();

        function generateContent() {
            const btn = document.getElementById('generateBtn');
            const loading = document.getElementById('loading');
            const successMsg = document.getElementById('successMessage');

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
                    loadFiles();
                    setTimeout(() => successMsg.classList.remove('active'), 5000);
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                btn.disabled = false;
                loading.classList.remove('active');
                alert('Error generating content: ' + error);
            });
        }

        function loadFiles() {
            fetch('/files')
            .then(response => response.json())
            .then(data => {
                const filesList = document.getElementById('filesList');

                if (data.files.length === 0) {
                    filesList.innerHTML = '<p style="color: #666; text-align: center; padding: 40px;">No files yet. Generate your first batch!</p>';
                    return;
                }

                filesList.innerHTML = '';
                data.files.forEach(file => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    fileItem.innerHTML = `
                        <div class="file-info">
                            <div class="file-name">${file.name}</div>
                            <div class="file-date">${file.date}</div>
                        </div>
                        <div class="file-actions">
                            <button class="btn-small btn-view" onclick="viewPosts('${file.txt_path}')">View Posts</button>
                            <button class="btn-small btn-download" onclick="downloadFile('${file.pdf_path}')">Download PDF</button>
                        </div>
                    `;
                    filesList.appendChild(fileItem);
                });
            });
        }

        function viewPosts(txtPath) {
            fetch(`/view/${txtPath}`)
            .then(response => response.json())
            .then(data => {
                const modal = document.getElementById('postsModal');
                const container = document.getElementById('postsContainer');

                container.innerHTML = '';
                data.posts.forEach((post, index) => {
                    const postItem = document.createElement('div');
                    postItem.className = 'post-item';
                    postItem.innerHTML = `
                        <div class="post-number">Post ${index + 1}</div>
                        <div class="post-content">${post}</div>
                        <button class="copy-btn" onclick="copyToClipboard(\`${post.replace(/`/g, '\\`')}\`)">📋 Copy to Clipboard</button>
                    `;
                    container.appendChild(postItem);
                });

                modal.classList.add('active');
            });
        }

        function closeModal() {
            document.getElementById('postsModal').classList.remove('active');
        }

        function downloadFile(pdfPath) {
            window.location.href = `/download/${pdfPath}`;
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert('✓ Copied to clipboard!');
            });
        }

        // Refresh files every 10 seconds
        setInterval(loadFiles, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    """Generate new content"""
    try:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'})

        generator = RedNoteContentGenerator(api_key)
        success = generator.run_daily_generation()

        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/files')
def list_files():
    """List generated files"""
    output_folder = Path('Growth')
    if not output_folder.exists():
        return jsonify({'files': []})

    pdf_files = sorted(output_folder.glob('RedNote_Content_*.pdf'), reverse=True)

    files = []
    for pdf_file in pdf_files:
        txt_file = pdf_file.with_suffix('.txt')
        date_str = pdf_file.stem.split('_')[-1]

        # Format date
        try:
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            formatted_date = date_obj.strftime('%B %d, %Y')
        except:
            formatted_date = date_str

        files.append({
            'name': pdf_file.name,
            'date': formatted_date,
            'pdf_path': pdf_file.name,
            'txt_path': txt_file.name if txt_file.exists() else None
        })

    return jsonify({'files': files})

@app.route('/view/<filename>')
def view_file(filename):
    """View content of text file"""
    try:
        filepath = Path('Growth') / filename
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse posts from text file
        posts = []
        lines = content.split('\n')
        current_post = []

        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                if current_post:
                    posts.append('\n'.join(current_post).strip())
                current_post = [line.split('.', 1)[1].strip() if '.' in line else line]
            elif line.strip() == '-' * 60:
                if current_post:
                    posts.append('\n'.join(current_post).strip())
                    current_post = []
            elif line.strip() and not line.startswith('=') and 'RedNote' not in line and 'Date:' not in line and 'Time:' not in line:
                current_post.append(line)

        if current_post:
            posts.append('\n'.join(current_post).strip())

        return jsonify({'posts': posts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download PDF file"""
    filepath = Path('Growth') / filename
    if not filepath.exists():
        return "File not found", 404

    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("小红书 Content Generator - Web Interface")
    print("="*60)
    print("\nStarting web server...")
    print("Open your browser to: http://localhost:5000")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")

    app.run(debug=False, host='0.0.0.0', port=5000)
