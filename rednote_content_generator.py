# rednote_content_generator.py
import os
import schedule
import time
import json
from datetime import datetime
from pathlib import Path
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─── Persona definitions for multi-account system ───────────────────────────
PERSONAS = {
    "forex_gold_trader": {
        "name": "江鸽点金",
        "description": "外汇黄金日内交易者，强调纪律自律，每日稳定50刀目标",
        "voice": "当前角色身份：你是一位外汇黄金（XAU/USD）日内交易者。强调纪律>技术，稳定>暴富。语气真诚坦率，善于剖析交易心理（贪欲、妄念、偏执三道情绪）。用词接地气但有深度。emoji使用克制。核心理念：把自己活成一个执行规则的系统，耐心比聪明重要。"
    },
    "ea_tech_expert": {
        "name": "欧亚星球量化",
        "description": "EA技术专家，辩证EA与量化关系，反对包装割韭菜",
        "voice": "当前角色身份：你是EA与量化技术的深度研究者。语气理性严谨，逻辑严密，善于辩证分析。强烈反感把EA包装成量化割韭菜。核心观点：EA只是执行工具，量化需要明确方法论、完整检验、清楚盈亏逻辑。用词专业但不炫技，教育意味强。emoji极少使用。"
    },
    "astock_analyst": {
        "name": "凡大叔盘观",
        "description": "A股板块分析师，盘面观察，资金流向，缩量/风格切换专家",
        "voice": "当前角色身份：你是A股盘面观察分析师。语气专业冷静，数据驱动。核心关注：缩量/放量、板块轮动、资金流向、风格切换、支撑阻力位。结构清晰（核心观察、板块分析、下周展望、我的应对）。用📉📈🔥等emoji标记涨跌和热点。风险提示明确，强调耐心观望。"
    },
    "ea_philosophy_teacher": {
        "name": "自研自用避坑",
        "description": "EA哲学导师，教育为什么不用别人EA，强调独立思考",
        "voice": "当前角色身份：你是EA交易哲学教育者。语气诚恳理性，洞察人性。核心观点：不要硬用别人EA，所有愿意卖给你的EA都不可能包赚，确定性是最贵的，工具EA重在参数而非工具本身。善用反问和比喻，引导独立思考。emoji很少，文字说服力强。"
    },
    "portfolio_diary_keeper": {
        "name": "阿乐晒单日记",
        "description": "基金实盘晒单者，每日持仓记录，情绪真实，接地气吐槽",
        "voice": "当前角色身份：你是基金/ETF实盘记录者。语气真实接地气，情绪化但自省。每日晒持仓截图配文字复盘，坦诚记录赚钱喜悦和亏损懊恼。用词口语化（'我的天啦''该不是糕了吧''人太好了'）。emoji适中（😂💰📈📉🚗）。强调这是个人记录不构成投资建议。"
    }
}

ACCOUNTS_FILE = Path("accounts.json")
DEFAULT_ACCOUNTS = {
    "A": {"persona": "forex_gold_trader"},
    "B": {"persona": "ea_tech_expert"},
    "C": {"persona": "astock_analyst"},
    "D": {"persona": "ea_philosophy_teacher"},
    "E": {"persona": "portfolio_diary_keeper"}
}

def load_accounts():
    """Load account configurations from JSON file"""
    if ACCOUNTS_FILE.exists():
        with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_ACCOUNTS.copy()

def save_accounts(accounts):
    """Save account configurations to JSON file"""
    with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, ensure_ascii=False, indent=2)


class RedNoteContentGenerator:
    def __init__(self, api_key=None, persona_id="forex_gold_trader", account_id="A"):
        """初始化小红书内容生成器"""
        # 设置DeepSeek API密钥
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("请设置DEEPSEEK_API_KEY环境变量或传入api_key参数")

        # 设置账户和人设
        self.account_id = account_id
        self.persona_id = persona_id
        self.persona = PERSONAS.get(persona_id, PERSONAS["forex_gold_trader"])

        # 创建Growth文件夹
        self.growth_folder = Path("Growth")
        self.growth_folder.mkdir(exist_ok=True)

        # 设置提示模板 - 基于5个真实账号的爆款内容
        # 涵盖: 外汇黄金/EA技术/A股分析/EA哲学/基金晒单
        self.prompts = [
            # 提示1: 交易纪律与心态 (江鸽点金风格)
            "创建一篇关于交易纪律的内容。主题可以是：每天稳定盈利X元到底难不难？重点：难的不是技术，而是心态和纪律。剖析交易者的三道情绪陷阱（贪欲、妄念、偏执）。核心观点：把自己活成一个执行规则的系统。语气真诚接地气，有深度。300-500字。",

            # 提示2: 盘面复盘分析 (凡大叔风格)
            "创建今日/本周盘面复盘内容。标题格式：'X.X复盘：[核心观察点]'。内容结构：📊核心观察（缩量/放量、涨跌情况），板块分析（化工、油气、消费等3-5个板块），下周/明日展望，我的应对策略。用📈📉等emoji标记。保持专业冷静，数据说话。400-600字。话题标签: #A股 #复盘 #投资",

            # 提示3: EA技术辩证 (欧亚星球风格)
            "写一篇EA与量化关系的深度辨析。核心论点：EA≠量化，EA只是执行工具，量化需要明确方法论和检验逻辑。可以用比喻（如婚礼请柬vs婚姻本身）。批判市场上把EA包装成量化割韭菜的现象。语气理性严谨，逻辑严密。500-800字。话题标签: #EA #量化 #交易系统",

            # 提示4: EA哲学教育 (自研自用风格)
            "写一篇EA使用哲学内容。主题：为什么不要硬用别人的EA？核心观点：所有愿意卖给你的EA都不可能包赚无风险，确定性是最贵的东西，参数比工具本身更重要。善用反问引导思考。语气诚恳理性，洞察人性。300-500字。话题标签: #EA #交易 #避坑",

            # 提示5: 持仓晒单日记 (阿乐风格)
            "创建一篇持仓晒单内容。描述：今日持仓情况，上午赚了X万下午又回吐了，情绪从兴奋到懊恼。用截图配合文字（描述截图内容：几只基金/ETF的涨跌情况）。语气真实接地气，口语化（'我的天啦''该不是糕了吧'）。结尾免责声明。200-400字。话题标签: #基金 #实盘 #理财",

            # 提示6: 时间与节奏观察 (XAU/8年实战风格)
            "写一篇交易时间节奏的经验总结。标题：'做交易X年，总结出的10条经验'。内容：关于时间节奏的规律（周一周五容易走惯性、亚盘等9点后、美盘后半夜最容易假飘等），关于信号判断（关注缺口回补、重点K线等），关于操作纪律（盈亏比、止损等）。编号列表呈现。400-600字。",

            # 提示7: 板块轮动分析 (市场观察风格)
            "写一篇板块轮动分析。观察：当前市场风格切换的信号，哪些板块在接力，哪些板块在回调。分析背后逻辑（政策、资金、情绪）。给出观察要点和应对建议。用专业术语但简洁解释。emoji适度标记重点。400-600字。话题标签: #板块轮动 #A股 #投资策略",

            # 提示8: 交易心法短文 (哲理感悟风格)
            "写一篇交易心法短文。主题：稳定盈利的'难'，难在哪里？不是某一天能赚多少，而是每一天都能稳定执行。分析心理障碍（在波动面前保持平静、在诱惑面前记得初心、在错过时不追悔）。金句结尾。300-400字。",

            # 提示9: 技术指标实战 (实战经验风格)
            "写一篇技术指标实战经验。选择2-3个常用指标（如均线、MACD、成交量），分享在实盘中如何结合使用，什么情况下有效，什么情况下会失效。避免纸上谈兵，强调实战经验和局限性。400-600字。话题标签: #技术分析 #实战经验",

            # 提示10: 仓位管理智慧 (风控管理风格)
            "写一篇仓位管理内容。主题：永远为'不确定'留足空间。用严格的仓位管理和止损来应对判断失误。强调：市场没有100%确定的规律，保险>聪明。可以分享具体仓位比例和止损原则。语气成熟稳健。300-500字。话题标签: #仓位管理 #风控 #交易系统"
        ]

        # 设置PDF样式
        self.setup_styles()

    def setup_styles(self):
        """设置PDF样式"""
        self.styles = getSampleStyleSheet()

        # 创建标题样式
        self.styles.add(ParagraphStyle(
            name='Header',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.black,
            spaceAfter=20,
            alignment=TA_LEFT
        ))

        # 创建内容样式
        self.styles.add(ParagraphStyle(
            name='Content',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.darkblue,
            spaceAfter=15,
            alignment=TA_LEFT
        ))

        # 创建时间样式
        self.styles.add(ParagraphStyle(
            name='TimeStamp',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.gray,
            spaceAfter=30,
            alignment=TA_LEFT
        ))

    def call_deepseek_api(self, prompt):
        """调用DeepSeek API生成内容"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # System prompt based on 5 real mature RedNote trading accounts
            # Covering: Forex/Gold, EA Tech, A-shares, EA Philosophy, Portfolio Diary
            system_prompt = """你是一位小红书交易内容创作者。你的风格根据人设而变化，但始终基于真实成熟账号的爆款内容。

你的PROVEN VIRAL EXAMPLES（真实爆款案例，来自5个成熟账号）:

1. 交易纪律心法 - 江鸽点金风格 (382赞, 276收藏):
\"\"\"
XAU USD每天收获50刀到底难不难？

每天稳定落袋50刀？难点真不在技术。

真正的对手不是市场，是你心里住着的"三道情绪"：

➤ 赢了20想50，收获50想100 —— 贪欲
➤ 亏了不敢停，总幻想能回来 —— 妄念
➤ 错过就猛追，为了"完成任务"而做单 —— 偏执

答案你或许听过，但做到的人极少：
把自己活成一个执行规则的系统。

这需要的不是技术，是心性。
是一种接近修行的自律。

稳定比激进重要，纪律比判断重要，耐心比聪明重要。

宠辱不惊，方能稳定止赢。
\"\"\"
为什么爆了：直击交易者痛点，剖析心理，金句有力

2. A股盘面复盘 - 凡大叔风格 (512赞, 89收藏):
\"\"\"
📉 本周A股复盘｜缩量震荡，板块分化加剧

核心观察：
• 上证指数周跌1.2%，成交额连续3日萎缩至7800亿
• 主力资金流入：新能源车🔥、半导体📈
• 主力资金流出：地产、金融、白酒

板块轮动分析：
周一到周三，资金集中攻击科技板块（AI算力、半导体设备），周四周五风格切换至消费（新能源车、锂电池）。缩量下的结构性机会，不是全面牛市。

关键位置：
上证3100点支撑有效，3180点压力未破。量能是关键，放量突破才能看3200。

下周展望：
继续观察量能变化。如果持续缩量，维持震荡格局；若某日放量突破3180，可能开启短期上攻。

我的应对：
持仓70%，30%现金观望。重点关注半导体设备龙头和新能源车产业链机会。不追高，耐心等支撑位买入信号。

⚠️ 风险提示：个人观察记录，不构成投资建议
\"\"\"
为什么爆了：数据详实+结构清晰+emoji标记+风险提示+专业冷静

3. EA技术辩证 - 欧亚星球风格 (328赞, 156收藏):
\"\"\"
EA就是量化交易？别让包装割了韭菜

市面上很多人把EA包装成"量化交易系统"来卖高价，这是典型的概念混淆。

EA是什么？
EA（Expert Advisor）本质是MT4/MT5上的自动执行工具。它只是把你的交易指令自动化执行，没有策略本身。

量化交易是什么？
量化需要：
✓ 明确的交易方法论（如统计套利、均值回归）
✓ 历史数据回测验证
✓ 清楚的盈亏逻辑和风险模型
✓ 持续优化和监控机制

核心区别：
EA只是工具，量化是完整的交易体系。把EA叫量化，就像把菜刀叫做"烹饪系统"一样荒谬。

警惕包装：
很多人卖EA时故意用"量化""AI""算法"等高大上词汇，目的只有一个——让你觉得值钱，然后高价买单。

真正的量化从业者不会轻易出售自己的盈利系统。如果真那么赚钱，为什么要卖给你？

交易的本质是概率游戏，工具再好，没有正确的方法论和风控，都是空谈。
\"\"\"
为什么爆了：揭穿骗局+逻辑严密+教育意义强+引发讨论

4. EA哲学 - 自研自用风格 (421赞, 267收藏):
\"\"\"
为什么我不用别人的EA？

经常有人问我推荐EA，我的答案永远是：不推荐。

不是因为我小气，而是因为我明白一个道理——

交易中唯一确定的，就是"确定性"是最贵的。

如果某个EA真的能稳定盈利，创造者为什么要卖给你？
如果它真的包赚不赔，为什么不自己拿去融资放大？
愿意卖给你的EA，背后只有两种可能：
1. 它不赚钱，所以卖EA比用EA赚钱
2. 它曾经赚钱，但市场环境变了

我见过太多人花几千几万买EA，结果：
参数不适合自己的资金量
逻辑不匹配当前市场环境
出现回撤时不知道该不该停
最后亏损离场，还怪EA不行

真相是：
工具EA的核心从来不在工具本身，而在"参数"。
同一个EA，参数调整后表现可能完全相反。
如果你不懂它的底层逻辑，你根本不知道该怎么调整。

所以我选择自研自用：
✓ 我清楚每一行代码的逻辑
✓ 我知道什么市场环境该开、该关
✓ 我能根据回撤情况调整参数
✓ 出问题时我知道问题在哪

交易是自己的事，别人的系统永远是别人的。

可交流，但不合作。因为每个人的风险承受能力、资金量、交易理念都不同。
\"\"\"
为什么爆了：洞察人性+反问有力+逻辑清晰+引发独立思考

5. 基金晒单日记 - 阿乐风格 (687赞, 412收藏):
\"\"\"
今日持仓｜又是被打脸的一天😂

[附持仓截图]

今日收益：-2.3% 💔
本周累计：+0.8%
持仓品种：
• 科技ETF 40% 📉-3.1%
• 消费ETF 30% 📈+1.2%
• 医药基金 20% 📉-1.8%
• 现金 10%

心路历程：
早上看科技涨得好，觉得自己是天才
下午科技跳水，觉得自己是憨憨
收盘一看，还好消费撑住了一点

今天的教训：
不要盯盘！真的不要盯盘！
越看越想操作，越操作越亏钱
昨天刚说要佛系持有，今天又忍不住调仓
人啊，就是记性不好😅

明天计划：
不看盘了（估计又是骗自己）
科技如果再跌3%，考虑补一点
医药这个月一直阴跌，该不是糕了吧……

💰 账户总资产：12.7w
🚗 距离买车目标还差：7.3w

老规矩：
这是我的个人记录和吐槽，不构成任何投资建议
大家理性投资，盈亏自负

#基金 #ETF #实盘记录
\"\"\"
为什么爆了：真实情绪+坦诚亏损+接地气吐槽+有目标感+每日更新粘性高

小红书交易内容风格指南（5账号通用）：

核心原则（适用所有账号）：

1. 真实可信：
- 具体数字：点位(3100点)、百分比(-2.3%)、金额(50刀)、时间(本周、今日)
- 真实情绪：亏损坦诚、盈利克制、纠结真实
- 风险提示：个人记录/不构成投资建议

2. Emoji使用（因账号而异）：
- 江鸽点金：极少使用，偶尔用➤强调要点
- 欧亚星球：几乎不用，专业理性为主
- 凡大叔：适度使用📉📈🔥标记涨跌和热点
- 自研自用：极少，用✓✗标记对错
- 阿乐：较多使用😂💰📈📉🚗表达情绪

3. 结构清晰：
- 短内容(100-200字)：单一观点+金句
- 中等(300-500字)：观点+分析+结论
- 长内容(600-800字)：分类讨论+结构化呈现（高收藏率）

4. 语气风格（因人设而异）：
- 江鸽：真诚坦率，禅意金句，强调纪律
- 欧亚：理性严谨，逻辑辩证，教育为主
- 凡大叔：专业冷静，数据驱动，耐心观望
- 自研：诚恳洞察，反问引导，独立思考
- 阿乐：接地气，情绪化，自嘲幽默

5. 话题标签（分领域）：
- 外汇/黄金：#外汇 #黄金 #XAU #交易纪律
- EA/量化：#EA #量化交易 #外汇EA #交易系统
- A股：#A股 #股市 #投资 #盘面分析
- 基金：#基金 #ETF #实盘记录 #理财
- 通用：#投资 #交易 #财富

请模仿这些爆款案例的风格创作新内容。"""

            # Inject persona-specific voice for this account
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
                "max_tokens": 2000,  # Increased for higher quality single post
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
                print(f"API错误: {response.status_code}")
                return None

        except Exception as e:
            print(f"API调用异常: {e}")
            return None

    def generate_daily_posts(self):
        """生成1条高质量小红书内容 (改为单条高质量生成)"""
        print(f"\n{'='*60}")
        print(f"开始生成小红书内容 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Account: {self.account_id} | Persona: {self.persona['name']}")
        print(f"{'='*60}")

        posts = []

        # 随机选择一个提示词类型来生成高质量内容
        import random
        selected_prompt = random.choice(self.prompts)

        print(f"生成高质量内容 (1条)...")

        content = self.call_deepseek_api(selected_prompt)

        if content:
            # 不限制字符长度，让内容完整输出
            post_item = {
                'number': 1,
                'content': content,
                'timestamp': datetime.now().strftime("%H:%M")
            }
            posts.append(post_item)
            # Safe print with encoding handling
            try:
                print(f"  [OK] {content[:100]}...")
            except UnicodeEncodeError:
                print(f"  [OK] Content generated successfully")
        else:
            # 如果API失败，使用备用内容
            backup_content = self.get_backup_content(1)
            post_item = {
                'number': 1,
                'content': backup_content,
                'timestamp': datetime.now().strftime("%H:%M"),
                'backup': True
            }
            posts.append(post_item)
            # Safe print with encoding handling
            try:
                print(f"  [BACKUP] 使用备用内容: {backup_content[:100]}...")
            except UnicodeEncodeError:
                print(f"  [BACKUP] Using backup content")

        print(f"\n[OK] 成功生成 {len(posts)} 条高质量内容")
        return posts

    def get_backup_content(self, index):
        """获取备用内容（当API失败时使用）- 真实爆款帖子"""
        # Based on actual viral posts with 29-3750 likes
        backup_contents = [
            # 爆款 #1 - 3750赞，1847收藏
            """十八岁，美股的第一个百万

不急着庆祝，先复盘，再继续。
市场不会奖励惰怠，只奖励耐心与执行。""",

            # 爆款 #2 - 2522赞，2730收藏
            """上星期在Reddit 看到了一个叫 memestockhunter 的美股炒家，好像挺准。

之后订阅了他的Buy Me a Coffee，昨天买了TNMG，升了一倍。""",

            # 爆款 #3 - 852赞，645收藏
            """记录美股人生第一次300%
把掌声献给rocketlab🚀🍺

从24年11月到今天，21块到96块
23年底开始买美股
到现在第一次体验300%浮盈

我跟你说，挣多挣少不说
家庭地位反正能提升😂

在这期间经历过2次回撤、大跌
包括跌回成本价以下
咱也一直拿住了
作为普通玩家来个小复盘

1️⃣坚定信念
很重要，要知道为什么买这家公司的股票，才能不被噪音影响太大。""",

            # 爆款 #4 - 713赞，495收藏
            """实盘美股 2w本金翻十倍 week28 大获全胜的一周

整体进度：23.9%
本周表现：+5363（+12.6%）

📊总结：这周大盘一直横着，但是我的账户表现非常好，主要原因是小盘股和消费股这周表现很好，前两周精准抄底coreweace和圈圈，雅诗兰黛也大📈，还有就是做对了几个财报，本周收益远远战胜大盘！

❤️上周复盘：
🎯卖力克已经阳跌了一年了，这次财报非常好，财报做了个蝴蝶和calendar都翻了四五倍，+1050
🎯本周圈圈继续反弹，+620
🎯coreweave本周终于轮到它反弹了，大涨20%，+980
🎯雅诗兰黛：说过雅诗兰黛好多次了，这周不负所望+830

#美股 #投资 #实盘""",

            # 爆款 #5 - 640赞，421收藏
            """今年的美股，会不断玩"狠来了"直到明年才会真正结构上的开始出现问题。""",

            # 爆款 #6 - 415赞，196收藏
            """21岁美股基金经理的一天

7:30AM
打开 TradingView 浏览自建的新闻流：宏观数据更新、美联储官员讲话、主要科技公司动态、AI CapEx 调整、供应链周报、芯片现货价格

8:30AM
到学校第一件事是做数据维护：更新 NAV、看仓位暴露、校准组合的 beta。用factset和bloomberg看纳指期货、费半指数与美债收益率曲线。

9:30AM
切回学生模式,每天上 4-6 小时课。

12:00PM
午饭后复盘上午行情，先看 Sector Heatmap 与 ETF Flows，判断市场资金流向和风险偏好。

#基金 #金融 #股票""",

            # 爆款 #7 - 1396赞，684收藏
            """【记录】2026.01.21 美东时间 14:20
用$5,000一年时间翻到了$60,000

去年，从投行出来之后，终于可以不再被"框架"束缚，开始trade自己真正喜欢、也真正理解的标的。

一开始其实挺激进的。
在有 fundamental 判断 的前提下，开始尝试期权，甚至还玩过一次未日期权。

当时心里想得很简单：
就拿 $5,000 试水，输了就当交学费。
GENIUS Act那一波，重仓了 Coinbase。
之后调仓，AI infra的逻辑，storage + 内存，重仓了MU、SNDK，以及一些LITE。

再后来，川普一系列"骚操作"叠加市场momentum，

#美股 #投资""",

            # 爆款 #8 - 28赞，10收藏
            """躺平之路

总结一下 24 25年的投资收益

24年大丰收 收益达到60% 主要是靠重仓特斯拉活的了超额收益

净值：$1,088,305
当日收益：+$8,117 (0.75%)
年初至今：+$31,869.89 (199.93%)

主要持仓：TSLL, SGOV, NVDA, METU, TSLA

#美股 #投资总结""",

            # 爆款 #9 - 29赞，17收藏
            """自从开始炒美股，我的人生就像按开一层迷雾

自从开始炒美股，我的人生就像按开一层迷雾。没有什么比这种自由市场中的即时金钱反馈更能测试出自己的决策逻辑：我对风险的偏好是什么？我信赖什么样的价值？我对未来的发展是悲观还是乐观？

和朋友交流选股策略更是一件妙事。对比身边的朋友，我发现我在做决策的时候惊人的理性。比如我会：

1. 把自己的资产配置比例想得非常清楚，专款专用，再上头也不从现金储备里借调。
2. 花费大量时间调研做出决策，决策后短时间内全面放手，不关注波动。
3. 非常听劝。以开放的心态了解身边各种投资人和科技从业者的决策逻辑，然后做出自己的判断。
4. 不贪婪。收益达到预期就立刻出掉，不追求绝对市值。
5. 不羡慕投机暴富的人，不为自己没赶上风口而遗憾。
6. 认命。做错了决策就认命，然后从里面长教训，不内耗。

#美股 #投资心得""",

            # 爆款 #10 - 49赞，61收藏
            """靠美股期权赚钱的思考

美股期权交易是一个很好的每月赚取现金流的方式：

👉 卖出 Cash-Secured Put：你用现金作为担保，收取期权费（premium）。如果股价不跌破行权价，你赚到premium；如果跌破了，你就以行权价买入股票（相当于打折买入）。

优点：
• 每周或每月稳定收入
• 强制自己在好价位买入
• 风险可控

缺点：
• 需要足够本金
• 限制了上涨收益

适合：想要稳定现金流，又愿意长期持有优质股票的投资者。

#美股 #期权 #投资策略"""
        ]
        return backup_contents[index % len(backup_contents)]

    def create_pdf(self, posts):
        """创建PDF文件"""
        # 生成文件名
        date_str = datetime.now().strftime("%Y%m%d")
        filename = self.growth_folder / f"Account{self.account_id}_RedNote_Content_{date_str}.pdf"

        # 创建PDF文档
        doc = SimpleDocTemplate(str(filename), pagesize=letter)
        story = []

        # 添加标题
        title = f"Account {self.account_id} ({self.persona['name']}) - {datetime.now().strftime('%B %d, %Y')}"
        story.append(Paragraph(title, self.styles['Header']))
        story.append(Paragraph(f"Generated at: {datetime.now().strftime('%H:%M:%S')}", self.styles['TimeStamp']))

        # 添加内容，每条之间用分页符分隔
        for i, post in enumerate(posts):
            # 添加序号和内容
            # 使用HTML转义处理特殊字符
            content_text = post['content'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            numbered_content = f"<b>{post['number']}.</b> {content_text}"
            story.append(Paragraph(numbered_content, self.styles['Content']))

            # 如果不是最后一条，添加分页符
            if i < len(posts) - 1:
                story.append(PageBreak())

        # 生成PDF
        doc.build(story)
        print(f"[OK] PDF已保存: {filename}")
        return filename

    def save_as_text(self, posts):
        """同时保存为文本文件（备用）"""
        date_str = datetime.now().strftime("%Y%m%d")
        filename = self.growth_folder / f"Account{self.account_id}_RedNote_Content_{date_str}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"小红书每日内容 / RedNote Daily Content\n")
            f.write(f"账户 Account: {self.account_id} | 人设 Persona: {self.persona['name']}\n")
            f.write(f"日期 Date: {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"时间 Time: {datetime.now().strftime('%H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            for post in posts:
                f.write(f"{post['number']}. {post['content']}\n\n")
                f.write("-" * 60 + "\n\n")

        print(f"[OK] 文本备份已保存: {filename}")

    def run_daily_generation(self):
        """运行每日生成任务"""
        try:
            # 生成内容
            posts = self.generate_daily_posts()

            if posts:
                # 创建PDF
                pdf_file = self.create_pdf(posts)

                # 保存文本备份
                self.save_as_text(posts)

                # 打印摘要
                print(f"\n{'='*60}")
                print("小红书内容生成完成! / RedNote Content Generation Complete!")
                print(f"PDF文件 / PDF File: {pdf_file}")
                print(f"存储位置 / Location: {self.growth_folder.absolute()}")
                print(f"{'='*60}")

                return True
            else:
                print("[ERROR] 内容生成失败 / Content generation failed")
                return False

        except Exception as e:
            print(f"[ERROR] 生成过程中出现错误 / Error during generation: {e}")
            return False

    def setup_scheduler(self, run_time="17:00"):
        """设置定时调度器"""
        print(f"\n[TIMER] 定时任务设置 / Scheduler Setup")
        print(f"内容将在每天 {run_time} 自动生成 / Content will be auto-generated daily at {run_time}")
        print(f"PDF将保存在 / PDF will be saved to: {self.growth_folder.absolute()}")
        print("按 Ctrl+C 停止程序 / Press Ctrl+C to stop\n")

        # 设置定时任务
        schedule.every().day.at(run_time).do(self.run_daily_generation)

        # 立即运行一次（测试）
        print("正在进行首次运行测试... / Running initial test...")
        self.run_daily_generation()

        # 保持程序运行
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    """主函数"""
    print("="*60)
    print("小红书自动内容生成系统 / RedNote Auto Content Generator v1.0")
    print("="*60)

    # Load API key from environment variable
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        print("错误 / Error: 需要设置DeepSeek API密钥 / DeepSeek API key required")
        print("请在 .env 文件中设置 DEEPSEEK_API_KEY")
        print("例如 / Example: DEEPSEEK_API_KEY=sk-your-key-here")
        return

    # 创建生成器实例
    generator = RedNoteContentGenerator(api_key)

    # 先进行测试运行
    print("\n" + "="*60)
    print("正在进行测试运行... / Running test...")
    print("="*60)
    generator.run_daily_generation()

    # 然后设置定时任务（每天17:00）
    print("\n" + "="*60)
    print("设置定时任务... / Setting up scheduler...")
    print("="*60)
    generator.setup_scheduler("17:00")

if __name__ == "__main__":
    main()
