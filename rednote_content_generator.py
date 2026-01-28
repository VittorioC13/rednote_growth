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

ACCOUNTS_FILE = Path("accounts.json")
DEFAULT_ACCOUNTS = {
    "A": {"persona": "young_investor"},
    "B": {"persona": "strategy_master"},
    "C": {"persona": "transparent_trader"},
    "D": {"persona": "trend_hunter"},
    "E": {"persona": "philosopher"}
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
    def __init__(self, api_key=None, persona_id="young_investor", account_id="A"):
        """初始化小红书内容生成器"""
        # 设置DeepSeek API密钥
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("请设置DEEPSEEK_API_KEY环境变量或传入api_key参数")

        # 设置账户和人设
        self.account_id = account_id
        self.persona_id = persona_id
        self.persona = PERSONAS.get(persona_id, PERSONAS["young_investor"])

        # 创建Growth文件夹
        self.growth_folder = Path("Growth")
        self.growth_folder.mkdir(exist_ok=True)

        # 设置提示模板 - 基于真实爆款美股内容
        # Based on viral US stock trading posts with 600-3750 likes
        self.prompts = [
            # 提示1: 成功故事 + 具体数字 (PROVEN: 3750 likes, 1847 saves)
            # Pattern: Age + milestone + specific numbers
            "创建一篇美股交易成功故事。格式：'[年龄]岁，美股的第一个[里程碑]'作为标题。内容要包含：具体的起始金额和最终金额（如$5,000→$60,000，或2w本金翻十倍），时间跨度，1-2句感悟（如'不急着庆祝，先复盘，再继续。市场不会奖励惰怠，只奖励耐心与执行。'）。语气要谦逊但自信。最多使用1-2个emoji如🚀📈。话题标签: #美股 #投资 #年轻人投资",

            # 提示2: 交易策略长文 (PROVEN: 897 likes, 805 saves)
            # Pattern: 深度教育内容 + 个人经验
            "写一篇深度美股策略分享。标题格式：'对于[目标]靠美股[目标]的人的一些想法'。内容包含：开场白（作为一个想走这条路来维持生活的人...），详细分析3种具体策略（如covered call、dividend、day trade），每种策略的优缺点和资金要求，用具体数字说明（如5w美金，2.5k月支出，5%费用）。长文800字左右。结尾加个人感悟和免责声明。话题标签: #美股 #投资 #股票",

            # 提示3: 周报 + 账户截图 (PROVEN: 713 likes, 495 saves)
            # Pattern: 实盘记录 + 透明度
            "创建美股周报内容。格式：'实盘美股 [本金]本金翻[倍数] week[周数] [总结]'。内容结构：📊总结（这周大盘[情况]，但是我的账户表现[如何]），❤️上周复盘（列出3-5只股票的表现，用emoji🎯标记，包含具体涨幅和原因），💰本周操作（新开的仓位）。语气要专业但不炫耀。话题标签: #美股 #实盘 #投资记录",

            # 提示4: 热门发现/内幕消息 (PROVEN: 2522 likes, 2730 saves)
            # Pattern: 故事 + 具体结果
            "写一篇美股发现故事。格式：'上星期在[平台]看到了一个叫[用户名]的美股炒家，好像挺准。之后[采取的行动]，[昨天/今天]买了[股票代码]，[涨幅]。'保持简短，100-150字。重点是：来源（Reddit/Twitter/Discord），行动（订阅/关注），结果（具体涨幅如翻倍、涨50%）。话题标签: #美股 #投资 #交易信号",

            # 提示5: 重大收益里程碑 (PROVEN: 852 likes, 645 saves)
            # Pattern: 庆祝 + 详细复盘
            "创建一篇美股重大收益记录。标题：'记录美股人生第一次[百分比]% 把掌声献给[股票名称]🚀🍺'。内容包含：具体收益数据（从$X到$X），时间跨度（从XX年XX月到今天），为什么选择这只股票（1.坚定信念 2.深度研究 3.耐心持有），中间经历的回撤和考验。语气真诚，展现研究深度。话题标签: #美股 #投资 #股票",

            # 提示6: 年度总结 (PROVEN: 28 likes, 10 saves - 但适合年终)
            # Pattern: 躺平 + 数据展示
            "写年度美股投资总结。标题：'躺平之路 总结一下 [年份]年的投资收益'。内容：开场（总结[年份]年），主要收益来源（24年大丰收 收益达到[%] 主要是靠[策略/重仓股]），具体数字（净值$XXX，收益率XX%），重点持仓列表（列出3-5只核心股票），简短感悟。话题标签: #美股 #投资总结 #年度回顾",

            # 提示7: 一天工作流程 (PROVEN: 415 likes, 196 saves)
            # Pattern: 时间表 + 专业感
            "创建美股交易者一天日程。标题：'[年龄]岁美股[职业/身份]的一天'。按时间点列出：7:30AM - [做什么]（如浏览TradingView新闻流），8:30AM - [做什么]（如数据维护），9:30AM - [做什么]（如切换学生模式），12:00PM - [做什么]（如复盘行情），等等。每个时间点2-3句话描述。展现专业和自律。话题标签: #美股 #基金经理 #日常",

            # 提示8: 简短观点/预测 (PROVEN: 640 likes, 421 saves)
            # Pattern: 短小精悍 + 高亮关键词
            "写一个简短的美股市场观点。格式：一句话预测或观察，30-50字。例如：'今年的美股，会不断玩\"狠来了\"直到明年才会真正结构上的开始出现问题。'或'对于毕业想靠美股维生的人，[核心观点]。'重点是有态度、有观点、言简意赅。不需要话题标签。",

            # 提示9: 交易哲学/原则 (PROVEN: 29 likes, 17 saves)
            # Pattern: 深度反思 + 编号列表
            "创建美股交易哲学内容。标题：'自从开始炒美股，我的人生就像[比喻]'。内容结构：开场（自从开始炒美股的感悟），列出6个交易原则（如'1. 把自己的资产配置比例想得非常清楚' '2. 花费大量时间调研做出决策' 等），每个原则展开1-2句解释，结尾总结自己的投资性格。长文600-800字。话题标签: #美股 #投资心得",

            # 提示10: 策略教育/技巧 (PROVEN: 49 likes, 61 saves)
            # Pattern: 教学 + 具体方法
            "写美股期权策略教育内容。标题：'靠美股期权赚钱的思考'。内容包含：策略介绍（如Cash-Secured Put的原理），优点（如每月赚取现金流），具体操作步骤，风险提示，适合人群。使用👉emoji标记要点。保持教学风格，清晰易懂。300-400字。话题标签: #美股 #期权 #投资策略"
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

            # System prompt optimized for US stock trading content on RedNote
            # Based on actual viral posts with 600-3750 likes
            system_prompt = """你是一位小红书美股投资内容创作者。你的帖子经常获得高点赞、高收藏、高评论（600-3750赞）。

你的PROVEN VIRAL EXAMPLES（真实爆款案例）:

1. 成功故事 - 3750赞，1847收藏:
\"\"\"
十八岁，美股的第一个百万

不急着庆祝，先复盘，再继续。
市场不会奖励惰怠，只奖励耐心与执行。
\"\"\"
为什么爆了：年龄+里程碑+金句，简洁有力，励志

2. 重大收益 - 852赞，645收藏:
\"\"\"
记录美股人生第一次300%
把掌声献给rocketlab🚀🍺

从24年11月到今天，21块到96块
23年底开始买美股
到现在第一次体验300%浮盈

我跟你说，挣多挣少不说
家庭地位反正能提升😂

在这期间经历过2次回撤、大跌
包括跌回成本价以下
咱也一直拿住了

1️⃣坚定信念
很重要，要知道为什么买这家公司的股票，才能不被噪音影响太大。在这过程中不断挖信息，咱也百姓谁懂太空的事儿，所以就想办法从更厉害的人那里获取信息，我和很多朋友都是从油管上特斯拉投资者Hellen那里开始认识rocket lab和商业太空，逐渐了解这个行业和公司状况，加上老马对于太空目标的如此坚定，我相信这个行业肯定有机会，而只要涉及到商业，就不会只存在一个头部玩家，所以我相信rocketlab做为老二，市值会伴随着spacex不断提升。
\"\"\"
为什么爆了：具体数字+时间线+深度分析+emoji使用恰当

3. 热门发现 - 2522赞，2730收藏:
\"\"\"
上星期在Reddit 看到了一个叫 memestockhunter 的美股炒家，好像挺准。

之后订阅了他的Buy Me a Coffee，昨天买了TNMG，升了一倍。
\"\"\"
为什么爆了：简短、来源可信、结果惊人（翻倍）

4. 深度策略 - 897赞，805收藏（高收藏率！）:
\"\"\"
对于毕业想靠美股维生的人的一些想法

作为一个想走这条路来维持生活，甚至是财富自由的人，经过大半年的磨练，我对我原有的想法有了一些改变。首先靠美股维生的第一点不是你一年的收益有多少，而是如何赚取稳定的现金流来应对平时吃饭和一些杂费的开销。作为普通毕业生，算上过去几年攒下来的钱，有个5w美金开局已经是个还算可以的起步了。但此时此刻你面对的每个月的账单可能对于你的本金是个惊人的数字，即使你住自己家不需要出房租面对吃饭还有汽车的维护费用，一个月的净支出可能也需要2.5k保底，那对于我的账户就是每个月5%的费用还不算年底的纳税。当月假如行情好，波段博对了账户50%up那当然5%的生活费很容易拿出来，反之有时候你满仓margin但是水下的时候，你还是需要拿出来2.5k作为固定开支，这时候你就不得不面对割肉还是吃泡面的选择了。

长期做股票肯定不可能每个月都判断对，都赚钱，那就说明靠股票只做波段对于像我这种情况的人就不适用。所以我就思考如何通过股票赚取cashflow。我感觉有三种思路，第一种是卖你正股的covercall，用潜在的超额收益换稳定的现金流；第二就是靠dividend；第三就是做日内daytrade。前两种都需要你有足够的本金，第三种需要你有足够的纪律和判断。所以在这三种中，我觉得第三种是对本金不够大，又想盯盘做交易的人唯一一种可能创造cashflow的方法。这样就避免了你需要定期从波段账户取钱的烦心事。至于daytrade又有三种做法，第一种是靠0dte的option，第二种是正股加margin只做日内，第三种是期货。这三种我都尝试过，第一种我的感受最差，首先止盈上损很难，而且非线性的收益很难把握。第二种可以考虑，但是对资金有一些要求，好处是选择面比较广什么票子都能做，但选择多也未必是好事，毕竟关注几样东西已经需要耗费很多心思了。我目前个人比较喜欢第三种，就是用future来做index microfuture，好处是资金利用率高，而且年底的税务优势明显（这个之后也可以细聊税务对全职做股票的影响）。目前我用第三种专门做了一个月收益还算可以，但很显然样本不足还不能说长期结果如何。需要至少一年的考察时期。

以上这些也是我经过半年全职在家里做美股的一些小感悟。希望新的一年可以继续坚持不向爸妈要钱，靠自己生活下去。

#美股 #年轻人投资 #投资
\"\"\"
为什么爆了：深度干货+个人经验+具体策略+真实挣扎+长文（高收藏）

5. 周报 - 713赞，495收藏:
\"\"\"
实盘美股 2w本金翻十倍 week28 大获全胜的一周

整体进度：23.9%

📊总结：这周大盘一直横着，但是我的账户表现非常好，主要原因是小盘股和消费股这周表现很好，前两周精准抄底coreweace和圈圈，雅诗兰黛也大📈，还有就是做对了几个财报，本周收益远远战胜大盘！

❤️上周复盘：
🎯卖力克已经阳跌了一年了，这次财报非常好，财报做了个蝴蝶和calendar都翻了四五倍，+1050
🎯本周圈圈继续反弹，+620
🎯coreweave本周终于轮到它反弹了，大涨20%。话说AI三兄弟里我最看好它，原因很简单，就这一个是美国公司，+980
🎯雅诗兰黛：说过雅诗兰黛好多次了，甚至做了极其看涨的call ratio，这周不负所望+830
🎯大盘：上周做的sell call和今天最后一天连高出手的spx sell call都稳稳收下，原因很简单，pce数据好也不会大涨，因为12月降息已经90%price in了，+560
🎯其他：这周运气也很好，看好的几个财报都做对了，提前布局的adbe财报也跟着涨，+1270
🎯联合垃圾：哎，就它最垃圾，本来周三大涨以为反转要来了，结果连着两天又跌了回去，鸟了它两天一看这周还微赚😂，+120
💰本周新开了下周app的put，这货不知不觉又涨起来了，空了下一周，下周二、下周三，5张
\"\"\"
为什么爆了：数据透明+emoji标记+逐个分析+实盘可信

6. 一天日程 - 415赞，196收藏:
\"\"\"
21岁美股基金经理的一天

7:30AM
打开 TradingView 浏览自建的新闻流：宏观数据更新、美联储官员讲话、主要科技公司动态、AI CapEx 调整、供应链周报、芯片现货价格

8:30AM
到学校第一件事是做数据维护：更新 NAV、看仓位暴露、校准组合的 beta。用factset和bloomberg看纳指期货、费半指数与美债收益率曲线。快速过一遍主要持仓的 Catalyst 与估值漂移。

9:30AM
切回学生模式,每天上 4-6 小时课。
教授在讲进阶 CAPM，我在想如果Intel真的拿下代工客户，怎么重估他们的wacc? The world is messy.

12:00PM
午饭后复盘上午行情，先看 Sector Heatmap 与 ETF Flows，判断市场资金流向和风险偏好。虽然组合以基本面为主，但我每天仍会做一遍 Technical Review。我们团队独立执行交易决策，从仓位调整到下单都自己处理。

1:00PM
上课刷水看研报，关注垂直 SaaS 定价权、AI CapEx 周期、HBM 渗透率、液冷设备订单节奏等。每天还要补课芯片制造流程，从光刻、刻蚀、沉积到 EDA 软件。

3:00PM
开始准备月度股票推介。Primary Research 占据主要精力，需要与管理团队、渠道商、设备厂、客户甚至前员工沟通。很多时候，一句 off-record 的评论就足以颠覆原有逻辑。上个月 pitch 的公司和 CEO 本人开了会我们是 multi-sector 结构，所以除 tech 外，也会帮其他组做 peer review，也要持续关注他们的市场。

5:00pm
回家复盘绩效，今日组合上涨，Attribution 显示 Selection Effect 为正、Allocation Effect 为负，Beta 略高于基准。EDA license renew 加速，TSMC 扩招显示 CoWoS 产线扩张，NVDA Blackwell 出货或延迟，短期扰动但长期不变。

8:00pm
夜晚对比 ASML 与 LRCX 毛利率桥，更新估值模型，用 AlphaSense 跑预期与业绩敏感度分析，定期复盘 thesis 的有效性，筛掉被推翻假设。

Disclaimer：不构成任何投资建议。职务内容包含equity research和pm。

#基金 #金融 #股票
\"\"\"
为什么爆了：专业感+详细时间线+真实工作内容+年轻人标签

小红书美股内容风格指南：

数字是核心：
- 必须包含具体数字：金额($5k, $60k, 2w本金)、百分比(300%, 60%, 翻倍)、年龄(18岁, 21岁)、时间(week28, 一年)
- 数字让内容可信且有冲击力

格式多样化：
- 短句：30-50字金句（如"市场不会奖励惰怠，只奖励耐心与执行"）
- 中等：200-400字（成功故事+复盘）
- 长文：600-800字（深度策略，高收藏率）

Emoji使用：
- 战略性使用：🚀📈💰🎉📊💪
- 用于标记要点：📊总结 ❤️复盘 🎯股票 💰操作
- 不要过度，保持专业感

语气平衡：
- 谦逊但自信（不是炫耀，是分享）
- 真实挣扎（回撤、亏损、学习过程）
- 专业但不高冷（技术术语+白话解释）

话题标签：
- 必用：#美股 #投资
- 选用：#股票 #年轻人投资 #基金 #金融 #期权 #实盘
- 通常2-3个标签

内容长度：
- 短句：30-50字
- 中等：200-400字
- 长文：600-800字（教育内容）

中英文混搭：
- 股票代码用英文(RKLB, TNMG, NVDA)
- 专业术语用英文(covered call, margin, beta, day trade)
- 叙述用中文

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
                print(f"API错误: {response.status_code}")
                return None

        except Exception as e:
            print(f"API调用异常: {e}")
            return None

    def generate_daily_posts(self):
        """生成10条每日小红书内容"""
        print(f"\n{'='*60}")
        print(f"开始生成小红书内容 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        posts = []

        for i, prompt in enumerate(self.prompts, 1):
            print(f"生成第 {i}/10 条内容...")

            content = self.call_deepseek_api(prompt)

            if content:
                # 小红书内容可以稍长一些
                word_count = len(content)
                max_chars = 800  # 字符限制

                if word_count > max_chars:
                    content = content[:max_chars] + "..."

                post_item = {
                    'number': i,
                    'content': content,
                    'timestamp': datetime.now().strftime("%H:%M")
                }
                posts.append(post_item)
                # Safe print with encoding handling
                try:
                    print(f"  [OK] {content[:50]}...")
                except UnicodeEncodeError:
                    print(f"  [OK] Content generated successfully (Post #{i})")
            else:
                # 如果API失败，使用备用内容
                backup_content = self.get_backup_content(i)
                post_item = {
                    'number': i,
                    'content': backup_content,
                    'timestamp': datetime.now().strftime("%H:%M"),
                    'backup': True
                }
                posts.append(post_item)
                # Safe print with encoding handling
                try:
                    print(f"  [BACKUP] 使用备用内容: {backup_content[:50]}...")
                except UnicodeEncodeError:
                    print(f"  [BACKUP] Using backup content (Post #{i})")

            time.sleep(1)  # 避免API速率限制

        print(f"\n[OK] 成功生成 {len(posts)} 条内容")
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
