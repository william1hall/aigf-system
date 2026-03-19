#!/usr/bin/env python3
"""
where_am_i.py — 查询周浩薇当前的完整状态

统一查询入口：情绪 + 场景 + 穿搭，供 agent / cron / selfie 等所有模块调用。

用法：
    python3 where_am_i.py

输出示例：
    [STATUS] 时间：15:30 | 时间段：下午活动 | 今日类型：工作日上课 | 当前在：学校图书馆 | 穿搭：white blouse + trench coat... | 心情：开心
    [MOOD_HINT] 你现在很开心！语气活泼、充满爱意...
"""

import sys
import os
import datetime

# 确保同目录下的模块可以被导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daily_scene import get_daily_plan, get_current_scene
from mood import get_mood
from outfit import get_outfit_cn

SLOT_NAMES = {
    "sleeping": "睡觉中",
    "morning_routine": "刚起床",
    "morning_activity": "上午活动",
    "lunch_break": "午饭/午休",
    "afternoon_activity": "下午活动",
    "dinner_time": "晚饭时间",
    "evening_activity": "晚上活动",
    "night_relaxing": "睡前放松",
}

DAY_TYPE_NAMES = {
    "normal": "工作日上课",
    "travel": "出去旅游",
    "shanghai_local": "逛上海",
    "home": "宅家休息",
    "sport": "运动日",
}


def get_full_status() -> dict:
    """返回完整状态字典，供其他 Python 模块调用"""
    now = datetime.datetime.now()
    plan = get_daily_plan()
    scene = get_current_scene()
    outfit_cn = get_outfit_cn()
    mood_info = get_mood()

    return {
        "time": now.strftime("%H:%M"),
        "slot": scene["slot"],
        "slot_cn": SLOT_NAMES.get(scene["slot"], scene["slot"]),
        "day_type": plan["day_type"],
        "day_type_cn": DAY_TYPE_NAMES.get(plan["day_type"], plan["day_type"]),
        "location_cn": scene["location_cn"],
        "scene_en": scene["scene_en"],
        "travel_dest": plan.get("travel_dest", ""),
        "outfit_cn": outfit_cn,
        "mood": mood_info["mood"],
        "mood_cn": mood_info["mood_cn"],
        "mood_hint": mood_info["agent_hint"],
        "selfie_expression": mood_info["selfie_expression"],
        "voice_emotion": mood_info["voice_emotion"],
    }


def main():
    status = get_full_status()

    output = f"[STATUS] 时间：{status['time']} | 时间段：{status['slot_cn']} | 今日类型：{status['day_type_cn']}"
    if status["travel_dest"]:
        output += f" | 旅游目的地：{status['travel_dest']}"
    output += f" | 当前在：{status['location_cn']} | 穿搭：{status['outfit_cn']} | 心情：{status['mood_cn']}"
    print(output)
    print(f"[MOOD_HINT] {status['mood_hint']}")


if __name__ == "__main__":
    main()
