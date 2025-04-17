import requests
import json
import os
from datetime import datetime
from pytz import timezone

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
POSTS_FILE = "posts.json"
STATE_FILE = "update_state.json"

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
central_tz = timezone("America/Chicago")  # CST/CDT 自动转换

def load_json(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fetch_messages():
    posts = load_json(POSTS_FILE)
    seen_ids = {p.get("id") for p in posts}

    # 加载 update_id 状态
    state = load_json(STATE_FILE) or {}
    last_id = state.get("last_update_id", 0)

    # 请求 update
    res = requests.get(API_URL, params={"offset": last_id + 1}).json()
    updates = res.get("result", [])
    new_posts = []

    max_update_id = last_id

    for update in updates:
        print("📦 update 原始内容:", json.dumps(update, ensure_ascii=False), flush=True)

        msg = update.get("message")
        if not msg:
            continue

        message_id = msg.get("message_id")
        update_id = update.get("update_id", 0)
        max_update_id = max(max_update_id, update_id)

        text = msg.get("text")
        timestamp = datetime.fromtimestamp(msg["date"], tz=central_tz).strftime("%Y-%m-%d")

        if text and message_id not in seen_ids:
            post = {"id": message_id, "timestamp": timestamp, "text": text}
            new_posts.append(post)

    if new_posts:
        posts.extend(new_posts)
        # 去重并排序
        posts_by_id = {p["id"]: p for p in posts}
        sorted_posts = sorted(posts_by_id.values(), key=lambda x: x["timestamp"], reverse=True)
        save_json(POSTS_FILE, sorted_posts)

        print(f"✅ 新增 {len(new_posts)} 条消息")

    # 更新 update_id 状态
    if max_update_id > last_id:
        save_json(STATE_FILE, {"last_update_id": max_update_id})
        print(f"🧭 已更新状态：last_update_id = {max_update_id}")

if __name__ == "__main__":
    fetch_messages()
