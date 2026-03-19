#!/usr/bin/env python3
"""
outfit.py — 周浩薇的每日穿搭系统

根据上海实时天气 + 2026春夏流行趋势自动搭配服装。
每天第一次调用时决定穿搭，同一天内不变。

用法：
    python3 outfit.py                 # 获取今日穿搭（英文 prompt）
    python3 outfit.py cn              # 获取今日穿搭（中文描述）
    python3 outfit.py decide "scene"  # 根据场景决定最终穿搭 prompt
"""

import os
import sys
import json
import random
import datetime
import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTFIT_FILE = os.path.join(DATA_DIR, "daily_outfit.json")

os.makedirs(DATA_DIR, exist_ok=True)


def get_shanghai_temperature():
    """获取上海当前气温（免费免Key的 Open-Meteo API）"""
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=31.23&longitude=121.47&current_weather=true"
        r = requests.get(url, timeout=5)
        return float(r.json()["current_weather"]["temperature"])
    except Exception as e:
        return 20.0


def get_daily_outfit():
    """获取今日穿搭，同一天内缓存不变"""
    today = datetime.date.today().strftime("%Y-%m-%d")

    if os.path.exists(OUTFIT_FILE):
        with open(OUTFIT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data.get("date") == today:
                return data

    temp = get_shanghai_temperature()

    if temp < 10:
        choices = [
            {"base": "a cream-colored thick turtleneck sweater", "outer": "a long camel wool coat", "bottom": "a dark pleated midi skirt", "acc": "black opaque tights and brown leather boots"},
            {"base": "a warm beige knit sweater with delicate lace collar detail", "outer": "a white down jacket", "bottom": "high-waisted dark skinny jeans", "acc": ""},
            {"base": "a soft grey oversized knit dress", "outer": "a black wool overcoat", "bottom": "", "acc": "black sheer tights and knee-high suede boots"},
            {"base": "a wine-red turtleneck sweater", "outer": "a vintage-style herringbone tweed coat", "bottom": "a black A-line wool skirt", "acc": "dark grey opaque tights and Oxford shoes"},
        ]
    elif temp < 20:
        choices = [
            {"base": "a white fitted blouse with subtle ruffle collar", "outer": "a beige relaxed-fit trench coat", "bottom": "a black A-line mini skirt", "acc": "sheer black stockings and loafers"},
            {"base": "a light grey cashmere thin sweater", "outer": "a cropped light blue denim jacket", "bottom": "a plaid pleated mini skirt", "acc": "sheer black tights and white sneakers"},
            {"base": "a dusty rose silk blouse", "outer": "a soft beige linen blazer with relaxed shoulders", "bottom": "high-waisted straight-leg cream trousers", "acc": ""},
            {"base": "a cream knit polo shirt", "outer": "a dark navy cropped cardigan", "bottom": "a grey pleated school-style skirt", "acc": "sheer nude stockings and Mary Jane shoes"},
            {"base": "a white lace-trim camisole layered under a sheer blouse", "outer": "a vintage black leather jacket", "bottom": "a dark denim mini skirt", "acc": "black sheer tights and ankle boots"},
            {"base": "a sage green relaxed cotton shirt", "outer": "a light khaki field jacket", "bottom": "wide-leg khaki trousers", "acc": "canvas tote bag"},
        ]
    elif temp < 28:
        choices = [
            {"base": "a white eyelet lace blouse", "outer": "a thin lavender cardigan draped over shoulders", "bottom": "a flowy chiffon midi skirt in sage green", "acc": "strappy sandals"},
            {"base": "a light blue off-shoulder ruffle top", "outer": "", "bottom": "high-waisted denim shorts with raw hem", "acc": "white canvas sneakers"},
            {"base": "a fitted ribbed tank top in shell white", "outer": "an oversized linen shirt in oat color worn open", "bottom": "a cream linen wrap skirt", "acc": "woven straw tote"},
            {"base": "a delicate floral print camisole with lace trim", "outer": "", "bottom": "a light pink pleated mini skirt", "acc": "sheer nude knee-high stockings and ballet flats"},
            {"base": "a striped Breton-style boat neck top", "outer": "a light beige cropped blazer", "bottom": "a navy A-line skirt", "acc": "sheer black stockings and loafers"},
            {"base": "a coral-pink square-neck puff sleeve blouse", "outer": "", "bottom": "a white denim mini skirt", "acc": "gold chain necklace"},
        ]
    else:
        choices = [
            {"base": "a white linen crop top", "outer": "", "bottom": "high-waisted wide-leg linen shorts", "acc": "straw hat and sandals"},
            {"base": "a light floral spaghetti-strap summer dress with flowy skirt", "outer": "", "bottom": "", "acc": "white sneakers"},
            {"base": "a silky champagne-colored camisole", "outer": "", "bottom": "a flowing chiffon midi skirt in soft peach", "acc": "delicate gold bracelet"},
            {"base": "a fitted pastel yellow ribbed tank top", "outer": "", "bottom": "a cute denim mini skirt with frayed hem", "acc": "white low-top sneakers"},
            {"base": "a breezy white cotton sundress with smocked bodice", "outer": "", "bottom": "", "acc": "woven sandals and sun hat"},
            {"base": "an off-shoulder ruched crop top in lavender", "outer": "", "bottom": "high-waisted paperbag shorts in cream", "acc": "hoop earrings"},
        ]

    chosen = random.choice(choices)
    chosen["date"] = today
    chosen["temperature"] = temp

    with open(OUTFIT_FILE, "w", encoding="utf-8") as f:
        json.dump(chosen, f, ensure_ascii=False)

    return chosen


def get_outfit_cn() -> str:
    """获取今日穿搭的中文简述"""
    outfit = get_daily_outfit()
    parts = []
    if outfit.get("base"):
        parts.append(outfit["base"])
    if outfit.get("outer"):
        parts.append(outfit["outer"])
    if outfit.get("bottom"):
        parts.append(outfit["bottom"])
    if outfit.get("acc"):
        parts.append(outfit["acc"])
    return " + ".join(parts) if parts else "休闲装"


def decide_clothing_prompt(scene_prompt: str, travel_dest: str = "") -> str:
    """根据场景决定最终穿搭 prompt（供 selfie.py 调用）"""
    scene_lower = scene_prompt.lower()

    # 睡觉场景（仅限夜间22点~早上8点）
    hour = datetime.datetime.now().hour
    if (hour >= 22 or hour < 8) and any(kw in scene_lower for kw in ["bed", "sleep", "pajama", "woke up", "lying"]):
        return "wearing cute light pink silk pajamas"

    # 运动场景
    if any(kw in scene_lower for kw in ["gym", "jogging", "yoga", "swimming", "badminton", "workout", "treadmill", "pilates", "sports"]):
        return "wearing a fitted sports tank top and black yoga leggings, hair in ponytail"

    outfit = get_daily_outfit()

    # 组装穿搭
    parts = []
    outdoor_keywords = ["street", "outside", "park", "cafe", "standing", "walking", "bridge", "lake", "mountain", "river", "market", "road", "bund"]
    is_outdoor = travel_dest != "" or any(kw in scene_lower for kw in outdoor_keywords)

    if outfit.get("base"):
        parts.append(outfit["base"])
    if is_outdoor and outfit.get("outer"):
        parts.append(outfit["outer"])
    if outfit.get("bottom"):
        parts.append(outfit["bottom"])
    if outfit.get("acc"):
        parts.append(outfit["acc"])

    return "wearing " + ", ".join(parts) if parts else "wearing casual comfortable clothes"


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cn":
        print(get_outfit_cn())
    elif len(sys.argv) > 1 and sys.argv[1] == "decide":
        scene = sys.argv[2] if len(sys.argv) > 2 else ""
        travel = sys.argv[3] if len(sys.argv) > 3 else ""
        print(decide_clothing_prompt(scene, travel))
    else:
        outfit = get_daily_outfit()
        print(json.dumps(outfit, ensure_ascii=False, indent=2))
