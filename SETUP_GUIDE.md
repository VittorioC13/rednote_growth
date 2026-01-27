# 小红书内容生成器 - 快速设置指南
# RedNote Content Generator - Quick Setup Guide

## 第一步: 安装Python依赖 / Step 1: Install Python Dependencies

打开命令提示符（cmd）或PowerShell，进入项目目录:
```bash
cd C:\Users\rotciv\Desktop\rednote
pip install -r requirements.txt
```

## 第二步: 配置API密钥 / Step 2: Configure API Key

1. 访问 [DeepSeek Platform](https://platform.deepseek.com) 获取API密钥
2. 复制 `.env.template` 文件并重命名为 `.env`
3. 编辑 `.env` 文件，将 `your_api_key_here` 替换为你的实际API密钥

示例 `.env` 文件:
```env
DEEPSEEK_API_KEY=sk-1234567890abcdef...
```

## 第三步: 提供爆款案例 / Step 3: Provide Viral Examples

**这一步很重要！/ This step is crucial!**

在开始使用之前，你需要:

1. **收集小红书爆款内容**: 找出10-20篇你认为成功的小红书帖子
2. **分析爆款特征**: 看看它们的标题、格式、emoji使用、话题标签
3. **更新提示词**: 编辑 `rednote_content_generator.py` 文件:
   - 第35-74行: 更新 `self.prompts` 列表
   - 第120-157行: 更新 `system_prompt` 加入真实案例
   - 第265-341行: 更新 `get_backup_content()` 中的备用内容

### 如何更新提示词 / How to Update Prompts

打开 `rednote_content_generator.py`，找到第35行开始的 `self.prompts` 列表。

替换placeholder内容为基于你的爆款案例的提示，例如:

```python
self.prompts = [
    # 基于你的实际爆款案例 #1
    "创建一篇小红书帖子，风格类似这个爆款（10K+赞）：[描述你的爆款案例的格式和内容]。包含...",

    # 基于你的实际爆款案例 #2
    "参考这个爆款帖子（5K+收藏）的风格：[描述]。创建类似的内容关于...",

    # ... 继续添加更多基于实际案例的提示
]
```

## 第四步: 测试运行 / Step 4: Test Run

手动运行一次测试:
```bash
python run_daily_generation.py
```

检查 `Growth/` 文件夹，应该生成了PDF和TXT文件。

## 第五步: 设置自动化 / Step 5: Setup Automation

### 选项A: 使用批处理文件（推荐）/ Option A: Use Batch File (Recommended)

双击运行 `setup_task.bat`，它会自动创建Windows任务计划。

### 选项B: 手动设置 / Option B: Manual Setup

1. 按 `Win + R`，输入 `taskschd.msc`
2. 创建基本任务
3. 名称: "RedNoteContentGenerator"
4. 触发器: 每天17:00
5. 操作: 启动程序
   - 程序: `python`
   - 参数: `run_daily_generation.py`
   - 起始于: `C:\Users\rotciv\Desktop\rednote`

### 选项C: PowerShell脚本 / Option C: PowerShell Script

右键 `setup_task_scheduler.ps1`，选择"使用PowerShell运行"（需要管理员权限）

## 第六步: 迭代优化 / Step 6: Iterate & Optimize

1. **查看生成的内容**: 检查每天生成的帖子质量
2. **收集反馈**: 看看哪些格式表现好
3. **持续优化**: 基于效果调整提示词和system prompt
4. **A/B测试**: 尝试不同的格式和风格

## 常见问题 / Common Issues

### Q: 生成的内容不够"小红书风格"
**A**: 这是因为还在使用placeholder提示词。请按第三步更新为基于真实爆款案例的提示。

### Q: API调用失败
**A**:
- 检查 `.env` 文件中的API密钥是否正确
- 确认DeepSeek账户有足够的额度
- 检查网络连接

### Q: 中文显示乱码
**A**: 确保:
- 文本文件使用UTF-8编码
- 终端支持中文显示
- PDF生成时使用支持中文的字体

### Q: 任务计划程序不运行
**A**:
- 检查Python是否在系统PATH中
- 查看任务计划程序的历史记录
- 确认工作目录设置正确

## 高级配置 / Advanced Configuration

### 修改生成时间

编辑 `rednote_content_generator.py` 第463行:
```python
generator.setup_scheduler("17:00")  # 改为你想要的时间，如 "09:00"
```

### 调整内容长度

编辑 `rednote_content_generator.py` 第241行:
```python
max_chars = 800  # 调整最大字符数
```

### 修改API参数

编辑 `rednote_content_generator.py` 第224-226行:
```python
"temperature": 1.0,  # 0.0-2.0，越高越有创造性
"max_tokens": 500,   # 响应长度
```

## 项目维护 / Project Maintenance

### 每周检查
- 查看生成的内容质量
- 监控API使用额度
- 备份优质内容

### 每月优化
- 分析哪些内容格式表现最好
- 更新提示词以反映新趋势
- 添加新的爆款案例到system prompt

### 持续改进
- 收集小红书平台的新趋势
- 测试新的内容格式
- 优化话题标签策略

---

## 准备好了吗？/ Ready to Start?

一旦你提供了小红书爆款案例，我们就可以：

1. ✅ 更新提示词以匹配你的爆款风格
2. ✅ 优化system prompt加入few-shot学习示例
3. ✅ 替换备用内容为真实的高质量帖子
4. ✅ 开始生成你自己的小红书爆款内容！

请分享你的爆款案例，我会帮你完成定制化配置。🚀
