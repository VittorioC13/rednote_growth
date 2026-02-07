# Persona Setup Guide

## System Overview

The generator now creates **1 high-quality post per click** instead of 10 posts. Token allocation has been increased from 500 to 2000 tokens for better quality content.

## 5 Account Structure (A, B, C, D, E)

Each account can have a different persona (人设). Currently configured:

### Current Default Personas:

1. **Account A** - 年轻暴富 (Young Investor)
   - 18-21岁年轻投资者，成功故事为主，语气自信积极

2. **Account B** - 策略大师 (Strategy Master)
   - 策略分析师，教育性内容，专业术语丰富

3. **Account C** - 透明实盘 (Transparent Trader)
   - 实盘记录者，诚实分享盈亏，社区感强

4. **Account D** - 发现达人 (Trend Hunter)
   - 热点猎人，短小精悍，制造FOMO感

5. **Account E** - 哲学投资者 (Philosopher)
   - 投资哲学家，人生感悟，长期智慧

## How to Customize Personas

### Step 1: Prepare Your Content

For each account (A, B, C, D, E), you should provide:

1. **Persona Name** (人设名称)
   - Short, catchy name for the persona
   - Example: "技术分析大神", "价值投资者", "期权玩家"

2. **Persona Description** (人设描述)
   - Brief description of the persona's characteristics
   - Example: "专注技术分析的交易者，图表流派，短线为主"

3. **Voice/Tone** (语气和风格)
   - How this persona speaks
   - Emoji usage style
   - Terminology preferences
   - Example: "语气专业冷静，图表数据为主，emoji使用📊📈，专业术语频繁"

4. **Sample Content** (样本内容)
   - Provide 3-5 examples of posts in this persona's style
   - These will be used to train the AI to match the voice

### Step 2: Content Format

When you're ready to feed content for each account, provide it in this format:

```
ACCOUNT: A
PERSONA NAME: [Your persona name]
DESCRIPTION: [Brief description]
VOICE: [How they speak/write]

SAMPLE POSTS:
---
[Sample post 1]
---
[Sample post 2]
---
[Sample post 3]
---
```

### Step 3: I Will Update the Code

Once you provide the 5 personas and their sample content, I will:
1. Update the `PERSONAS` dictionary in `rednote_content_generator.py`
2. Update the system prompts with your sample content
3. Update the prompt templates to match each persona's style
4. Test the generation to ensure quality

## Example Customization Request

```
ACCOUNT: A
PERSONA NAME: 技术分析大神
DESCRIPTION: 专注技术分析的日内交易者，看图说话，精准入场
VOICE: 语气简洁专业，图表数据为主，关键点位标注清楚。emoji使用适中（📊📈⚡），专业术语如"支撑位""阻力位""突破"频繁使用。

SAMPLE POSTS:
---
$SPY 今日分析 📊

开盘价: 445.20
关键支撑: 443.50
关键阻力: 447.80

⚡ 15分钟图出现金叉信号
预期突破447.80后看451

止损: 443.50下方
#美股 #技术分析
---
[more samples...]
```

## Ready to Proceed

The system is now configured to:
✅ Generate 1 high-quality post per click
✅ Allocate 2000 tokens for better quality
✅ Support 5 independent accounts (A-E)
✅ Each account has its own persona
✅ Each persona has unique voice and style

**Please provide your 5 personas and sample content whenever you're ready!**
