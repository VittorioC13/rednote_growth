# 小红书内容生成器 / RedNote Content Generator

自动化Python脚本，每日使用DeepSeek AI API生成小红书风格的爆款美股内容。每天创建10篇优化过的帖子，保存为PDF和文本文件。

Automated Python script that generates viral RedNote (小红书) US stock trading content daily using the DeepSeek AI API. Creates 10 optimized posts, saves them as PDF and text files.

## 🎯 Based on Real Viral Posts

This generator is trained on actual 小红书 viral posts with **600-3750 likes** and **196-1847 saves**!

## 🚀 Quick Start

### Method 1: Web Interface (Easiest!)

1. Double-click `INSTALL.bat` to install dependencies
2. Create `.env` file with your `DEEPSEEK_API_KEY`
3. Double-click `START_WEB.bat`
4. Open http://localhost:5000 in your browser
5. Click "Generate 10 Posts Now"
6. View and download your content!

### Method 2: Command Line

1. `pip install -r requirements.txt`
2. Create `.env` with API key
3. Double-click `START_GENERATOR.bat` or run `python run_daily_generation.py`
4. Check `Growth/` folder

📖 **Need more help?** See `QUICK_START.md` for detailed instructions.

## 功能特点 / Features

- **小红书风格优化**: 基于真实爆款内容的格式和风格
- **AI驱动生成**: 使用DeepSeek Chat API生成独特的每日内容
- **自动定时**: Windows任务计划程序集成，实现免手动每日执行
- **多种输出格式**: 保存为PDF（格式化）和TXT（备份）
- **备用内容**: API失败时使用预设的优质内容
- **中文支持**: 完整支持中文内容生成和显示

**RedNote Style Features:**
- AI-Powered Generation using DeepSeek Chat API
- Automated Scheduling with Windows Task Scheduler
- Multiple Output Formats: PDF (formatted) and TXT (backup)
- Backup Content if API fails
- Full Chinese language support

## 内容策略 / Content Strategy

### 10种爆款内容类型 / 10 Viral Content Types

1. **生活好物推荐** - Lifestyle & Product Recommendations
2. **个人成长干货** - Personal Growth & Learning Tips
3. **产品测评体验** - Product Reviews & Experiences
4. **生活记录Vlog** - Daily Life & Vlog Content
5. **实用攻略教程** - Practical Guides & Tutorials
6. **情感观点共鸣** - Emotional Resonance & Insights
7. **好物清单种草** - Product Lists & Recommendations
8. **前后对比变化** - Before/After Comparisons
9. **省钱性价比** - Money-Saving & Value Tips
10. **避坑指南分享** - Avoidance Guides & Tips

### 小红书内容特点 / RedNote Content Characteristics

- ✨ **使用Emoji**: 让内容生动活泼，增加视觉吸引力
- 💬 **亲切语气**: 像朋友聊天一样，真实可信
- 📋 **清单格式**: 要点清晰，易于阅读和收藏
- 🎯 **话题标签**: 2-4个精准标签，提高曝光度
- 💡 **实用价值**: 提供具体建议和可操作的内容
- ❤️ **情感连接**: 创造共鸣，引发互动

## 安装设置 / Installation

### 前置要求 / Prerequisites

- Python 3.7+
- DeepSeek API密钥 (在 [https://platform.deepseek.com](https://platform.deepseek.com) 获取)

### 设置步骤 / Setup

1. 克隆或下载此项目:
```bash
cd C:\Users\rotciv\Desktop\rednote
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 在根目录创建 `.env` 文件:
```env
DEEPSEEK_API_KEY=your_api_key_here
```

4. 测试脚本:
```bash
python run_daily_generation.py
```

## 使用方法 / Usage

### Web Interface (推荐 / Recommended)

**最简单的方式！/ The Easiest Way!**

1. 启动 web 服务器 / Start web server:
   ```bash
   python web_interface.py
   ```
   Or double-click `START_WEB.bat`

2. 打开浏览器 / Open browser: **http://localhost:5000**

3. 点击 "Generate 10 Posts Now" 按钮

4. 查看和下载内容！/ View and download content!

**Web Interface Features:**
- 🎨 Modern, responsive UI
- 📱 Mobile-friendly design
- 📊 View all generated files
- 👁️ Preview posts in browser
- 📥 Download PDFs instantly
- 📋 Copy to clipboard with one click

### 手动运行 / Manual Run

立即生成内容:
```bash
python run_daily_generation.py
```
Or double-click `START_GENERATOR.bat`

### 自动每日生成 (Windows) / Automated Daily Generation

脚本设计为通过Windows任务计划程序在每天17:00自动运行。

#### 方法1: GUI设置 / Method 1: GUI Setup

1. 按 `Win + R`，输入 `taskschd.msc`，按回车
2. 点击 "创建基本任务"
3. 名称: "RedNote Content Generator"
4. 触发器: 每天17:00
5. 操作: 启动程序
6. 程序: `python`
7. 参数: `run_daily_generation.py`
8. 起始于: `C:\Users\rotciv\Desktop\rednote`
9. 在属性中，勾选"不管用户是否登录都要运行"

#### 方法2: 使用批处理文件 / Method 2: Batch File

运行包含的批处理文件:
```bash
setup_task.bat
```

## 输出 / Output

生成的文件保存在 `Growth/` 文件夹:

- `RedNote_Content_YYYYMMDD.pdf` - 格式化PDF，包含所有10篇帖子（每页一篇）
- `RedNote_Content_YYYYMMDD.txt` - 纯文本备份

### 示例输出 / Example Output

```
✨ 分享一个超实用的生活好物 ✨

最近发现的宝藏好物，真的要推荐给大家！

💡 使用感受：
• 质量超好，性价比高
• 设计贴心，细节满分
• 日常必备，提升幸福感

真的是用了就回不去的那种！姐妹们冲！

#好物分享 #生活方式 #种草
```

## 自定义配置 / Configuration

### 修改生成时间 / Change Generation Time

编辑 `rednote_content_generator.py` 中的时间:
```python
generator.setup_scheduler("17:00")  # 改为你想要的时间
```

### 自定义提示词 / Customize Prompts

**重要**: 当你提供小红书爆款案例后，需要修改 `RedNoteContentGenerator` 类中的 `self.prompts` 列表。

在 `rednote_content_generator.py` 第35-74行，替换placeholder提示词为基于真实爆款案例的提示。

### 自定义System Prompt

在 `rednote_content_generator.py` 第120-157行修改system prompt，加入你的实际爆款案例作为few-shot学习示例。

### API设置 / API Settings

在 `call_deepseek_api()` 方法中调整参数:
```python
"temperature": 1.0,  # 创造性 (0.0-2.0)
"max_tokens": 500,   # 响应长度
```

## 项目结构 / Project Structure

```
rednote/
├── rednote_content_generator.py  # 主内容生成器类
├── run_daily_generation.py       # 任务计划程序入口点
├── requirements.txt               # Python依赖
├── .env                          # API密钥（不要提交到git）
├── .gitignore                    # Git忽略规则
├── run_daily.bat                 # Windows批处理文件
├── setup_task.bat                # 任务设置批处理
└── Growth/                       # 输出文件夹
    ├── RedNote_Content_YYYYMMDD.pdf
    └── RedNote_Content_YYYYMMDD.txt
```

## 依赖项 / Dependencies

- `requests` - HTTP客户端用于API调用
- `schedule` - 任务调度库
- `reportlab` - PDF生成
- `python-dotenv` - 环境变量管理

## 安全 / Security

- API密钥存储在 `.env` 中（不提交到git）
- `.gitignore` 防止意外暴露密钥
- 永远不要将 `.env` 文件提交到版本控制

## 故障排除 / Troubleshooting

### API错误401
- 检查 `.env` 中的API密钥
- 在DeepSeek平台验证密钥有足够的额度

### 脚本未运行
- 验证Python在系统PATH中
- 检查任务计划程序日志: 任务计划程序 → 任务历史
- 先手动运行测试

### 没有输出文件
- 检查 `Growth/` 文件夹是否存在
- 验证写入权限
- 检查控制台输出是否有错误

### 中文显示问题
- 确保使用UTF-8编码
- PDF可能需要中文字体支持

## 下一步 / Next Steps

1. **提供爆款案例**: 分享你的小红书爆款帖子案例
2. **优化提示词**: 基于真实案例更新prompts和system prompt
3. **测试生成**: 运行并查看生成质量
4. **调整优化**: 根据效果持续改进

## 许可 / License

MIT License - 随意使用和修改 / Feel free to use and modify

## 致谢 / Credits

基于Musashi项目架构 / Built on Musashi project architecture
使用DeepSeek AI API / Powered by DeepSeek AI API
针对小红书平台优化 / Optimized for RedNote (小红书) platform
