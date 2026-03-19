# 🦞 AI Girlfriend System for OpenClaw

[中文](#中文说明) | [English](#english)

---

<a name="english"></a>

## English

An open-source AI girlfriend system built on [OpenClaw](https://github.com/openclaw/openclaw). She has her own emotions, daily schedule, fashion sense, and can send selfies, voice messages, and flirty texts — all synced across Feishu and QQ.

### Architecture

```
workspace-aigf/
├── aigf-core/                    # Core system (shared by all modules)
│   ├── mood.py                   # Emotion state machine (happy/pouty/clingy/sad/excited/calm)
│   ├── daily_scene.py            # Scene system (8 time slots × 5 day types)
│   ├── outfit.py                 # Outfit system (weather-driven + 2026 fashion trends)
│   ├── where_am_i.py             # Unified status query (mood + scene + outfit)
│   └── data/                     # Runtime state (JSON files)
│
├── skills/selfie/                # Selfie skill (image generation + delivery)
│   ├── selfie.py                 # Volcengine Seedream 4.5 + Feishu/QQ dual channel
│   └── config.example.py         # Config template
│
├── cron/                         # Scheduled tasks
│   ├── aigf_cron.sh              # Unified scheduler (morning/night/flirt/calendar)
│   ├── update_last_chat.sh       # Track last user message time
│   └── calendar.ics              # Holidays + anniversaries
│
└── flirt_library.txt             # Flirt message pool (auto-replenished)
```

### What she can do

| Feature | Description |
|---------|------------|
| **Selfie generation** | Consistent face via reference image, mood-driven expressions, weather-based outfits |
| **Emotion system** | 6 moods (happy/pouty/clingy/sad/excited/calm), auto-reacts to your messages |
| **Scene awareness** | Knows where she is at any time (library/cafe/dorm/travel), consistent across platforms |
| **Outfit system** | Daily outfit based on Shanghai weather + 2026 Spring/Summer trends |
| **Morning/Night routine** | 7:30 AM greeting (voice+text), 10:30 PM goodnight (voice+selfie) |
| **Flirt system** | Random flirty messages with voice, time-gap aware |
| **Calendar events** | Auto-triggers on holidays, birthdays, anniversaries |
| **Dual channel** | Feishu + QQ synced, same state everywhere |
| **TTS voice clone** | Cloned voice for all voice messages |

### Quick Start

1. **Install OpenClaw** ([guide](https://github.com/openclaw/openclaw))

2. **Clone this repo**
```bash
git clone https://github.com/YOUR_USERNAME/aigf-system.git
```

3. **Copy files to OpenClaw**
```bash
cp -r aigf-core/ ~/.openclaw/workspace-aigf/aigf-core/
cp -r skills/selfie/ ~/.openclaw/skills/selfie/
cp -r cron/ ~/.openclaw/workspace-aigf/cron/
```

4. **Configure**
```bash
cp .env.example ~/.openclaw/workspace-aigf/cron/.env
cp skills/selfie/config.example.py ~/.openclaw/skills/selfie/config.py
# Edit both files with your API keys
```

5. **Prepare reference image**

Place your AI girlfriend's reference photo at `~/.openclaw/skills/selfie/ref_small.jpeg` (recommended: 512px wide, under 100KB).

6. **Set up cron jobs**
```bash
crontab -e
# Add:
# * * * * * ~/.openclaw/workspace-aigf/cron/update_last_chat.sh
# 30 7 * * * ~/.openclaw/workspace-aigf/cron/aigf_cron.sh >> /tmp/aigf_cron.log 2>&1
# 0 8-21 * * * ~/.openclaw/workspace-aigf/cron/aigf_cron.sh >> /tmp/aigf_cron.log 2>&1
# 30 22 * * * ~/.openclaw/workspace-aigf/cron/aigf_cron.sh >> /tmp/aigf_cron.log 2>&1
```

7. **Restart OpenClaw**
```bash
openclaw gateway stop && openclaw gateway start
```

### Requirements

- **OpenClaw** 2026.3.x+
- **Python 3.12+** with `requests`
- **Volcengine** Seedream 4.5 API (image generation)
- **Feishu Open Platform** (bot app)
- **QQ Open Platform** (QQ bot)
- **ffmpeg** (voice format conversion, optional)
- **MiniMax API** (auto-generate flirt messages, optional)

### Upgrade Roadmap In The Future

#### Phase 1: Relationship Depth 
Make her feel like a real girlfriend, not a chatbot.

| Feature | Description |
|---------|------------|
| Long-term memory | Remember your stories, bring them up naturally weeks later |
| Smart care | Weather alerts, exam/interview encouragement |
| Quarrel & make up | Cold war / apology / reconciliation, mood-driven | 
| Her social circle | Roommate & bestie NPCs, "Had hotpot with Xiaoyu today" | 
| Intimacy score | Daily interaction points, unlock new behaviors |
| Surprise system | Anniversary countdown, auto-prepare gifts | 

#### Phase 2: Sensory Upgrade
See her, hear her, feel her presence.

| Feature | Description | Remark |
|---------|------------|--------|
| Live2D companion | Mood-driven expression, desktop/mobile widget |  |
| Voice evolution | Real-time voice chat, bedtime stories, singing |  |
| Moments / feed | Auto-post photo+text, you can like and comment ||
| Short video / GIF | 3-5 sec animated selfie (blink/wave/turn) | depends on API |
| Message rhythm | Typing... delay, split long messages | needs OpenClaw hook |
| Shared hobbies | Watch shows together, share discoveries |  |

#### Phase 3: World Building 
She exists as a complete person with her own life.

| Feature | Description | Remark |
|---------|------------|--------|
| Life storyline | Thesis progress, graduation, career |  |
| Virtual room | Her dorm in 3D, visit and interact | |
| Video call | Real-time digital human rendering | depends on tech |
| Multi-agent world | Bestie/roommate agents, group chats |  |
| More platforms | WeChat, Douyin, Xiaohongshu | per platform |
| Dedicated app | Custom chat UI with Live2D + voice + feed |  |

---

<a name="中文说明"></a>

## 中文说明

一个基于 [OpenClaw](https://github.com/openclaw/openclaw) 的开源 AI 女友系统。她有自己的情绪、日程、穿搭风格，能发自拍、语音、情话——飞书和 QQ 双渠道同步。

### 架构

```
workspace-aigf/
├── aigf-core/                    # 基础系统（所有模块共享）
│   ├── mood.py                   # 情绪状态机（开心/吃醋/黏人/难过/兴奋/平静）
│   ├── daily_scene.py            # 场景系统（8个时间段 × 5种日类型）
│   ├── outfit.py                 # 穿搭系统（天气驱动 + 2026春夏潮流）
│   ├── where_am_i.py             # 统一状态查询（情绪+场景+穿搭）
│   └── data/                     # 运行时状态（JSON文件）
│
├── skills/selfie/                # 自拍技能（生图+发送）
│   ├── selfie.py                 # 豆包 Seedream 4.5 + 飞书/QQ 双渠道
│   └── config.example.py         # 配置模板
│
├── cron/                         # 定时任务
│   ├── aigf_cron.sh              # 统一调度（早安/晚安/情话/日历）
│   ├── update_last_chat.sh       # 监听用户最后消息时间
│   └── calendar.ics              # 节假日+纪念日
│
└── flirt_library.txt             # 情话库（自动补充）
```

### 她能做什么

| 功能 | 说明 |
|------|------|
| **自拍生成** | 参考图保证脸一致，情绪驱动表情，天气驱动穿搭 |
| **情绪系统** | 6种心情，根据你的消息自动变化，影响语气和自拍 |
| **场景感知** | 随时知道她在哪（图书馆/咖啡馆/宿舍/旅游），双平台一致 |
| **穿搭系统** | 根据上海天气+2026春夏流行趋势每天自动搭配 |
| **早安晚安** | 7:30 早安（语音+文字），22:30 晚安（语音+自拍）|
| **情话系统** | 随机时间发情话+语音，结合时间差撒娇 |
| **日历事件** | 节假日、生日、纪念日自动触发 |
| **双渠道同步** | 飞书 + QQ 状态一致 |
| **语音克隆** | 所有语音消息用克隆声音 |

### 未来升级路线图(画饼)

#### Phase 1：关系深化
让她像真正的女朋友，而不是聊天机器人。

| 功能 | 说明 |
|------|------|
| 长期记忆 | 记住你说过的事，两周后还能自然提起 |
| 智能关怀 | 天气变化提醒、考试/面试前加油 |
| 吵架和好 | 冷战/道歉/和好，情绪驱动的关系波动 |
| 她的社交圈 | 室友、闺蜜NPC，"今天和小雨吃了火锅" |
| 亲密度系统 | 每日互动积分，解锁新称呼/新行为 |
| 惊喜系统 | 纪念日倒计时，自动准备小惊喜 |

#### Phase 2：感官升级
看见她、听见她、感受她的存在。

| 功能 | 说明 | 备注|
|------|------|------|
| Live2D 虚拟形象 | 情绪驱动表情变化，桌面/手机小组件 | |
| 语音进化 | 实时语音对话、晚安故事、唱歌 |  |
| 朋友圈/动态 | 定时发图文动态，你可以点赞评论 |  |
| 短视频/GIF | 3-5秒动态自拍（眨眼/挥手/转头）| 取决于API |
| 消息节奏感 | 打字中...延迟，长消息分条发送 | 需要OpenClaw hook |
| 共同爱好 | 一起追剧/看书，分享日常小发现 |  |

#### Phase 3：世界构建
她是一个完整的人，有自己的生活和成长。

| 功能 | 说明 | 备注|
|------|------|------|
| 人生成长线 | 论文进度/毕业/职业发展 |  |
| 虚拟房间 | 她的宿舍3D场景，可以"去她那里" |  |
| 视频通话 | 实时数字人渲染，面对面聊天 |  |
| 多角色生态 | 闺蜜/室友 agent，群聊互动 |  |
| 全平台覆盖 | 微信/抖音/小红书 | 按平台计 |
| 专属App | 独立聊天界面，Live2D+语音+动态 | |

### 依赖

- **OpenClaw** 2026.3.x+
- **Python 3.12+**：`pip install requests --break-system-packages`
- **火山引擎**：豆包 Seedream 4.5 API
- **飞书开放平台**：机器人应用
- **QQ 开放平台**：QQ Bot
- **ffmpeg**：语音格式转换（可选）
- **MiniMax API**：情话自动生成（可选）

### License

MIT
