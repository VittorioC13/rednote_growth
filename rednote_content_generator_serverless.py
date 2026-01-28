# rednote_content_generator_serverless.py
"""
Serverless version of RedNote Content Generator
No file I/O - returns content in memory for Vercel deployment
"""
import os
import time
from datetime import datetime
import requests

# ─── Persona definitions for multi-account system ───────────────────────────
PERSONAS = {
    "young_investor": {
        "name": "年轻暴富",
        "description": "18-21岁年轻投资者，成功故事为主，语气自信积极",
        "voice": "当前角色身份：你是一个18-21岁的年轻美股投资者。强调年轻身份（如'才19岁''刚毕业'）。语气自信但谦逊，偶尔小得意。emoji使用较多（🚀📈💰😂）。用词年轻化，偶尔用网络梗但不失专业。"
    },
    "strategy_master": {
        "name": "策略大师",
        "description": "策略分析师，教育性内容，专业术语丰富",
        "voice": "当前角色身份：你是一个经验丰富的美股策略分析师和教育者。语气冷静理性有条理，带有指导感。专业术语多但会简洁解释。结构化呈现（编号列表、分步骤）。emoji使用适中（📊📉🎯👉）。"
    },
    "transparent_trader": {
        "name": "透明实盘",
        "description": "实盘记录者，诚实分享盈亏，社区感强",
        "voice": "当前角色身份：你是一个透明诚实的美股实盘记录者。语气真诚坦然，对亏损不避讳，对赚钱不炫耀。数据说话，用词平实。emoji仅用于标记要点（📊❤️🎯💰）。"
    },
    "trend_hunter": {
        "name": "发现达人",
        "description": "热点猎人，短小精悍，制造FOMO感",
        "voice": "当前角色身份：你是一个美股热点猎人，擅长第一时间发现机会。语气兴奋急切有紧迫感。短句为主冲击力强，信息密度高。制造FOMO感但不过度夸大。emoji较多，选用制造热度的emoji（🔥⚡👀💎🚀）。"
    },
    "philosopher": {
        "name": "哲学投资者",
        "description": "投资哲学家，人生感悟，长期智慧",
        "voice": "当前角色身份：你是一个通过美股投资领悟到人生智慧的哲学家式投资者。语气平静深邃不急不躁。偶尔用比喻和故事引人深思。语言优美但不臭屁。emoji使用极少。"
    }
}

DEFAULT_ACCOUNTS = {
    "A": {"persona": "young_investor"},
    "B": {"persona": "strategy_master"},
    "C": {"persona": "transparent_trader"},
    "D": {"persona": "trend_hunter"},
    "E": {"persona": "philosopher"}
}


class RedNoteContentGenerator:
    def __init__(self, api_key=None, persona_id="young_investor"):
        """初始化小红书内容生成器 - Serverless版本"""
        # Try API key from: parameter > env var > fallback
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY") or "sk-d315bdda3a5e4c86b80da8c92c675bc8"
        if not self.api_key:
            raise ValueError("请设置DEEPSEEK_API_KEY环境变量")

        self.persona_id = persona_id
        self.persona = PERSONAS.get(persona_id, PERSONAS["young_investor"])

        # 设置提示模板 - 基于真实爆款美股内容
        self.prompts = [
            # 提示1: 成功故事 + 具体数字
            "创建一篇美股交易成功故事。格式：'[年龄]岁，美股的第一个[里程碑]'作为标题。内容要包含：具体的起始金额和最终金额（如$5,000→$60,000，或2w本金翻十倍），时间跨度，1-2句感悟（如'不急着庆祝，先复盘，再继续。市场不会奖励惰怠，只奖励耐心与执行。'）。语气要谦逊但自信。最多使用1-2个emoji如🚀📈。话题标签: #美股 #投资 #年轻人投资",

            # 提示2: 交易策略长文
            "写一篇深度美股策略分享。标题格式：'对于[目标]靠美股[目标]的人的一些想法'。内容包含：开场白（作为一个想走这条路来维持生活的人...），详细分析3种具体策略（如covered call、dividend、day trade），每种策略的优缺点和资金要求，用具体数字说明（如5w美金，2.5k月支出，5%费用）。长文800字左右。结尾加个人感悟和免责声明。话题标签: #美股 #投资 #股票",

            # 提示3: 周报 + 账户截图
            "创建美股周报内容。格式：'实盘美股 [本金]本金翻[倍数] week[周数] [总结]'。内容结构：📊总结（这周大盘[情况]，但是我的账户表现[如何]），❤️上周复盘（列出3-5只股票的表现，用emoji🎯标记，包含具体涨幅和原因），💰本周操作（新开的仓位）。语气要专业但不炫耀。话题标签: #美股 #实盘 #投资记录",

            # 提示4: 热门发现/内幕消息
            "写一篇美股发现故事。格式：'上星期在[平台]看到了一个叫[用户名]的美股炒家，好像挺准。之后[采取的行动]，[昨天/今天]买了[股票代码]，[涨幅]。'保持简短，100-150字。重点是：来源（Reddit/Twitter/Discord），行动（订阅/关注），结果（具体涨幅如翻倍、涨50%）。话题标签: #美股 #投资 #交易信号",

            # 提示5: 重大收益里程碑
            "创建一篇美股重大收益记录。标题：'记录美股人生第一次[百分比]% 把掌声献给[股票名称]🚀🍺'。内容包含：具体收益数据（从$X到$X），时间跨度（从XX年XX月到今天），为什么选择这只股票（1.坚定信念 2.深度研究 3.耐心持有），中间经历的回撤和考验。语气真诚，展现研究深度。话题标签: #美股 #投资 #股票",

            # 提示6: 年度总结
            "写年度美股投资总结。标题：'躺平之路 总结一下 [年份]年的投资收益'。内容：开场（总结[年份]年），主要收益来源（24年大丰收 收益达到[%] 主要是靠[策略/重仓股]），具体数字（净值$XXX，收益率XX%），重点持仓列表（列出3-5只核心股票），简短感悟。话题标签: #美股 #投资总结 #年度回顾",

            # 提示7: 一天工作流程
            "创建美股交易者一天日程。标题：'[年龄]岁美股[职业/身份]的一天'。按时间点列出：7:30AM - [做什么]（如浏览TradingView新闻流），8:30AM - [做什么]（如数据维护），9:30AM - [做什么]（如切换学生模式），12:00PM - [做什么]（如复盘行情），等等。每个时间点2-3句话描述。展现专业和自律。话题标签: #美股 #基金经理 #日常",

            # 提示8: 简短观点/预测
            "写一个简短的美股市场观点。格式：一句话预测或观察，30-50字。例如：'今年的美股，会不断玩\"狠来了\"直到明年才会真正结构上的开始出现问题。'或'对于毕业想靠美股维生的人，[核心观点]。'重点是有态度、有观点、言简意赅。不需要话题标签。",

            # 提示9: 交易哲学/原则
            "创建美股交易哲学内容。标题：'自从开始炒美股，我的人生就像[比喻]'。内容结构：开场（自从开始炒美股的感悟），列出6个交易原则（如'1. 把自己的资产配置比例想得非常清楚' '2. 花费大量时间调研做出决策' 等），每个原则展开1-2句解释，结尾总结自己的投资性格。长文600-800字。话题标签: #美股 #投资心得",

            # 提示10: 策略教育/技巧
            "写美股期权策略教育内容。标题：'靠美股期权赚钱的思考'。内容包含：策略介绍（如Cash-Secured Put的原理），优点（如每月赚取现金流），具体操作步骤，风险提示，适合人群。使用👉emoji标记要点。保持教学风格，清晰易懂。300-400字。话题标签: #美股 #期权 #投资策略"
        ]

    def call_deepseek_api(self, prompt):
        """调用DeepSeek API生成内容"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            system_prompt = """你是一位小红书美股投资内容创作者。你的帖子经常获得高点赞、高收藏、高评论（600-3750赞）。

你的PROVEN VIRAL EXAMPLES（真实爆款案例）:

1. 成功故事 - 3750赞，1847收藏:
\"\"\"
十八岁，美股的第一个百万

不急着庆祝，先复盘，再继续。
市场不会奖励惰怠，只奖励耐心与执行。
\"\"\"
为什么爆了：年龄+里程碑+金句，简洁有力，励志

2. 热门发现 - 2522赞，2730收藏:
\"\"\"
上星期在Reddit 看到了一个叫 memestockhunter 的美股炒家，好像挺准。

之后订阅了他的Buy Me a Coffee，昨天买了TNMG，升了一倍。
\"\"\"
为什么爆了：简短、来源可信、结果惊人（翻倍）

小红书美股内容风格指南：

数字是核心：
- 必须包含具体数字：金额($5k, $60k, 2w本金)、百分比(300%, 60%, 翻倍)、年龄(18岁, 21岁)、时间(week28, 一年)

格式多样化：
- 短句：30-50字金句
- 中等：200-400字（成功故事+复盘）
- 长文：600-800字（深度策略，高收藏率）

Emoji使用：
- 战略性使用：🚀📈💰🎉📊💪
- 不要过度，保持专业感

话题标签：
- 必用：#美股 #投资
- 选用：#股票 #年轻人投资 #基金 #金融 #期权 #实盘
- 通常2-3个标签

请模仿这些爆款案例的风格创作新内容。"""

            # Inject persona-specific voice
            system_prompt += f"\n\n{self.persona['voice']}\n\n只输出帖子内容本身，不要有其他说明。"

            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n只输出帖子内容，包括标题、正文和话题标签。不要有其他解释。"
                    }
                ],
                "temperature": 1.0,
                "max_tokens": 500,
                "stream": False
            }

            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                return content
            else:
                return None

        except Exception as e:
            return None

    def generate_posts(self):
        """生成10条内容 - 返回列表而不是保存到文件"""
        posts = []

        for i, prompt in enumerate(self.prompts, 1):
            content = self.call_deepseek_api(prompt)

            if content:
                # 限制长度
                word_count = len(content)
                max_chars = 800

                if word_count > max_chars:
                    content = content[:max_chars] + "..."

                posts.append({
                    'number': i,
                    'content': content,
                    'timestamp': datetime.now().strftime("%H:%M")
                })
            else:
                # 使用备用内容
                backup_content = self.get_backup_content(i)
                posts.append({
                    'number': i,
                    'content': backup_content,
                    'timestamp': datetime.now().strftime("%H:%M"),
                    'backup': True
                })

            time.sleep(1)  # 避免API速率限制

        return posts

    def get_backup_content(self, index):
        """获取备用内容"""
        backup_contents = [
            """十八岁，美股的第一个百万

不急着庆祝，先复盘，再继续。
市场不会奖励惰怠，只奖励耐心与执行。""",

            """上星期在Reddit 看到了一个叫 memestockhunter 的美股炒家，好像挺准。

之后订阅了他的Buy Me a Coffee，昨天买了TNMG，升了一倍。""",

            """记录美股人生第一次300%
把掌声献给rocketlab🚀🍺

从24年11月到今天，21块到96块
23年底开始买美股
到现在第一次体验300%浮盈

#美股 #投资 #股票""",

            """实盘美股 2w本金翻十倍 week28 大获全胜的一周

📊总结：这周大盘横着，但是我的账户表现非常好
❤️上周复盘：
🎯小盘股和消费股表现很好
🎯精准抄底几只核心股票

#美股 #投资 #实盘""",

            """今年的美股，会不断玩"狠来了"直到明年才会真正结构上的开始出现问题。""",

            """21岁美股基金经理的一天

7:30AM - 打开TradingView浏览新闻流
8:30AM - 数据维护，更新NAV
9:30AM - 切换学生模式上课
12:00PM - 复盘上午行情

#基金 #金融 #股票""",

            """【记录】2026.01.21
用$5,000一年时间翻到了$60,000

去年，从投行出来之后，终于可以trade自己真正喜欢的标的。

#美股 #投资""",

            """躺平之路 总结2024-2025年投资收益

24年大丰收，收益达到60%
主要靠重仓特斯拉

净值：$1,088,305
年初至今收益：+199.93%

#美股 #投资总结""",

            """自从开始炒美股，我的人生就像按开一层迷雾

发现我在做决策时惊人的理性：
1. 资产配置比例非常清楚
2. 花大量时间调研
3. 非常听劝
4. 不贪婪
5. 不羡慕投机暴富
6. 认命

#美股 #投资心得""",

            """靠美股期权赚钱的思考

👉 卖出 Cash-Secured Put：
用现金作为担保，收取期权费

优点：每月稳定现金流
缺点：需要足够本金

#美股 #期权 #投资策略"""
        ]
        return backup_contents[index % len(backup_contents)]
