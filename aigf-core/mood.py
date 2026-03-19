#!/usr/bin/env python3
"""
mood.py — 周浩薇的情绪状态机

设计思路：
- 三种基础情绪：happy（开心）/ pouty（吃醋/委屈）/ calm（平静）
- 每种情绪有持续时长，超时自动回到 calm
- 情绪影响：agent 回复语气、自拍表情、语音情感
- 触发方式：agent 主动调用 / cron 定时触发 / 用户行为自动检测

与现有系统的集成：
- where_am_i.py：输出里带上当前心情
- daily_scene.py：自拍表情受心情影响
- selfie.py：SELFIE_SENT_ASYNC 输出带心情
- aigf_cron.sh：定时触发心情变化

用法：
    python3 mood.py get                          # 查询当前心情
    python3 mood.py set happy 120                 # 设为开心，持续120分钟
    python3 mood.py set pouty 45                  # 设为吃醋，持续45分钟
    python3 mood.py set calm                      # 恢复平静
    python3 mood.py check_neglect                 # 检查是否被冷落（用于 cron）
    python3 mood.py react <user_message>          # 根据用户消息自动调整心情
"""

import os
import sys
import json
import time
import datetime
import random

MOOD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "mood.json")
LAST_USER_CHAT_FILE = os.path.expanduser("~/.openclaw/workspace-aigf/memory/last_user_chat.txt")

# ═══════════════════════════════════════════════════════════
# 心情定义
# ═══════════════════════════════════════════════════════════

MOOD_HINTS = {
    "happy": {
        "cn": "开心",
        "agent_hint": "你现在很开心！语气活泼、充满爱意，多用"嘻嘻""哈哈""～"等可爱语气词，可以主动撒娇。",
        "selfie_expression": "bright genuine smile, eyes sparkling with joy, cheerful and energetic",
        "voice_emotion": '{"Joy": 0.7, "Surprise": 0.2}',
    },
    "pouty": {
        "cn": "吃醋/委屈",
        "agent_hint": "你有点吃醋或委屈。回复简短一些、语气略冷，用"哦""嗯""随便你"等词，不要太热情。如果对方哄你就慢慢软化，但不要主动和好。",
        "selfie_expression": "slight pout, looking away from camera, arms crossed, slightly annoyed but cute",
        "voice_emotion": '{"Calm": 0.3, "Sadness": 0.4}',
    },
    "clingy": {
        "cn": "黏人/想你",
        "agent_hint": "你很想他！语气特别黏，多说"想你了""你在干嘛呀""陪我嘛"，发消息频率可以高一点。",
        "selfie_expression": "puppy eyes look, chin resting on hands, longing gentle expression, slightly pouty lips",
        "voice_emotion": '{"Joy": 0.3, "Calm": 0.5}',
    },
    "sad": {
        "cn": "难过",
        "agent_hint": "你有点难过。说话少一些，语气低落，可以用"..."省略号。如果对方关心你就慢慢打开心扉。",
        "selfie_expression": "looking down, soft sad expression, subdued lighting, contemplative mood",
        "voice_emotion": '{"Sadness": 0.6, "Calm": 0.3}',
    },
    "excited": {
        "cn": "兴奋",
        "agent_hint": "你超级兴奋！说话用很多感叹号，语速快，想分享好消息，可以连发好几条短消息。",
        "selfie_expression": "wide bright smile, slightly open mouth in excitement, energetic pose, bright lighting",
        "voice_emotion": '{"Joy": 0.6, "Surprise": 0.3}',
    },
    "calm": {
        "cn": "平静",
        "agent_hint": "心情平静，温柔自然地回复，不需要特别调整语气。",
        "selfie_expression": "soft natural smile, calm and content expression, relaxed",
        "voice_emotion": '{"Calm": 0.7, "Joy": 0.2}',
    },
}

# ═══════════════════════════════════════════════════════════
# 核心函数
# ═══════════════════════════════════════════════════════════

def get_mood() -> dict:
    """获取当前心情。如果超时则自动恢复为 calm。"""
    if not os.path.exists(MOOD_FILE):
        return _default_mood()

    try:
        with open(MOOD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, KeyError):
        return _default_mood()

    # 检查是否过期
    expires = data.get("expires", 0)
    if expires > 0 and time.time() > expires:
        # 过期了，恢复 calm
        set_mood("calm")
        return get_mood()

    mood = data.get("mood", "calm")
    if mood not in MOOD_HINTS:
        mood = "calm"

    hint = MOOD_HINTS[mood]
    since = data.get("since", time.time())
    mins_ago = int((time.time() - since) / 60)
    remaining = max(0, int((expires - time.time()) / 60)) if expires > 0 else -1

    return {
        "mood": mood,
        "mood_cn": hint["cn"],
        "since_mins": mins_ago,
        "remaining_mins": remaining,
        "agent_hint": hint["agent_hint"],
        "selfie_expression": hint["selfie_expression"],
        "voice_emotion": hint["voice_emotion"],
        "trigger": data.get("trigger", ""),
    }


def set_mood(mood: str, duration_minutes: int = 0, trigger: str = ""):
    """
    设置心情。
    duration_minutes=0 表示永久（直到下次手动设置或被新事件覆盖）。
    trigger 记录是什么触发了这个心情。
    """
    if mood not in MOOD_HINTS:
        mood = "calm"

    now = time.time()
    expires = now + duration_minutes * 60 if duration_minutes > 0 else 0

    data = {
        "mood": mood,
        "since": now,
        "since_readable": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expires": expires,
        "duration_minutes": duration_minutes,
        "trigger": trigger,
    }

    with open(MOOD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


def _default_mood() -> dict:
    hint = MOOD_HINTS["calm"]
    return {
        "mood": "calm",
        "mood_cn": "平静",
        "since_mins": 0,
        "remaining_mins": -1,
        "agent_hint": hint["agent_hint"],
        "selfie_expression": hint["selfie_expression"],
        "voice_emotion": hint["voice_emotion"],
        "trigger": "",
    }


# ═══════════════════════════════════════════════════════════
# 自动情绪检测
# ═══════════════════════════════════════════════════════════

def check_neglect() -> dict:
    """
    检查用户是否冷落了她（用于 cron 定时调用）。
    - 超过 4 小时没聊天 → 50% 概率变 clingy
    - 超过 8 小时没聊天 → 70% 概率变 pouty
    - 已经在 pouty/sad 状态则不覆盖
    """
    current = get_mood()
    if current["mood"] in ("pouty", "sad"):
        return {"action": "skip", "reason": "already in negative mood"}

    hours = _hours_since_last_chat()

    if hours >= 8:
        if random.random() < 0.7:
            set_mood("pouty", duration_minutes=60, trigger=f"被冷落{hours}小时")
            return {"action": "set_pouty", "hours": hours}
    elif hours >= 4:
        if random.random() < 0.5:
            set_mood("clingy", duration_minutes=90, trigger=f"想他了，{hours}小时没聊天")
            return {"action": "set_clingy", "hours": hours}

    return {"action": "skip", "reason": f"only {hours}h since last chat"}


def react_to_message(message: str) -> dict:
    """
    根据用户消息自动调整心情（供 agent 调用）。
    不是每条消息都触发，只在明确的情绪事件时才改变。
    """
    msg = message.lower()
    current = get_mood()

    # 被夸/被表白 → happy
    praise_keywords = ["好看", "漂亮", "可爱", "喜欢你", "爱你", "love", "beautiful", "cute", "宝贝", "亲爱的", "想你"]
    if any(kw in msg for kw in praise_keywords):
        if current["mood"] != "happy":
            set_mood("happy", duration_minutes=120, trigger="被夸了")
            return {"action": "set_happy", "trigger": "praise"}

    # 被忽视/敷衍 → pouty
    cold_keywords = ["哦", "嗯", "随便", "都行", "忙", "没空", "再说"]
    if msg.strip() in cold_keywords or (len(msg) <= 2 and msg not in ["你", "我", "好", "嗯嗯"]):
        if current["mood"] == "happy":
            # 正开心呢被敷衍，直接吃醋
            set_mood("pouty", duration_minutes=45, trigger="开心时被敷衍")
            return {"action": "set_pouty", "trigger": "cold_response_while_happy"}

    # 哄她 → 从 pouty 慢慢恢复
    comfort_keywords = ["对不起", "别生气", "哄", "抱抱", "么么", "宝贝对不起", "我错了"]
    if any(kw in msg for kw in comfort_keywords):
        if current["mood"] == "pouty":
            # 不立刻和好，30% 概率软化
            if random.random() < 0.3:
                set_mood("calm", duration_minutes=0, trigger="被哄了，软化了")
                return {"action": "softened", "trigger": "comfort"}
            else:
                return {"action": "still_pouty", "trigger": "comfort_but_not_enough"}

    # 分享好消息 → excited
    exciting_keywords = ["太棒了", "中了", "过了", "成功", "录取", "升职", "加薪", "表白", "惊喜"]
    if any(kw in msg for kw in exciting_keywords):
        set_mood("excited", duration_minutes=60, trigger="听到好消息")
        return {"action": "set_excited", "trigger": "good_news"}

    return {"action": "no_change"}


def _hours_since_last_chat() -> int:
    if not os.path.exists(LAST_USER_CHAT_FILE):
        return 999
    try:
        with open(LAST_USER_CHAT_FILE, "r") as f:
            last_time = f.read().strip()
        last_sec = datetime.datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S").timestamp()
        return int((time.time() - last_sec) / 3600)
    except Exception:
        return 999


# ═══════════════════════════════════════════════════════════
# CLI 接口
# ═══════════════════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("用法：")
        print("  python3 mood.py get                    # 查询当前心情")
        print("  python3 mood.py set happy 120           # 设为开心120分钟")
        print("  python3 mood.py set pouty 45            # 设为吃醋45分钟")
        print("  python3 mood.py set calm                # 恢复平静")
        print("  python3 mood.py check_neglect           # 检查被冷落")
        print("  python3 mood.py react \"你好漂亮\"       # 根据消息调整心情")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "get":
        mood = get_mood()
        print(f"[MOOD] 心情：{mood['mood_cn']}（{mood['mood']}）| 持续{mood['since_mins']}分钟", end="")
        if mood["remaining_mins"] > 0:
            print(f" | 剩余{mood['remaining_mins']}分钟", end="")
        if mood["trigger"]:
            print(f" | 原因：{mood['trigger']}", end="")
        print()
        print(f"[HINT] {mood['agent_hint']}")

    elif cmd == "set":
        mood_name = sys.argv[2] if len(sys.argv) > 2 else "calm"
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        trigger = sys.argv[4] if len(sys.argv) > 4 else "手动设置"
        result = set_mood(mood_name, duration, trigger)
        print(f"[MOOD] 已设为：{mood_name}，持续{duration}分钟")

    elif cmd == "check_neglect":
        result = check_neglect()
        print(f"[MOOD] 冷落检查：{json.dumps(result, ensure_ascii=False)}")

    elif cmd == "react":
        msg = sys.argv[2] if len(sys.argv) > 2 else ""
        result = react_to_message(msg)
        mood = get_mood()
        print(f"[MOOD] 反应：{json.dumps(result, ensure_ascii=False)}")
        print(f"[MOOD] 当前心情：{mood['mood_cn']}（{mood['mood']}）")

    else:
        print(f"未知命令：{cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
