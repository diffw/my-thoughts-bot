import requests
import json
import os
from datetime import datetime
from pytz import timezone

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
POSTS_FILE = "posts.json"

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
central_tz = timezone("America/Chicago")  # 🕘 达拉斯时间 CST/CDT 自动转换

def load_posts():
    try:
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

def fetch_messages():
    posts = load_posts()
    seen_ids = {p.get("id") for p in posts if "id" in p}

    res = requests.get(API_URL).json()
    updates = res.get("result", [])
    new_posts = []

    for update in updates:
        print("📦 update 原始内容:", json.dumps(update, ensure_ascii=False), flush=True)

        msg = update.get("message")
        if not msg:
            continue

        message_id = msg.get("message_id")
        user_id = str(msg.get("from", {}).get("id"))
        text = msg.get("text")
        timestamp = datetime.fromtimestamp(msg["date"], tz=central_tz).strftime("%Y-%m-%d")

        print("🔍 收到来自用户 ID 的消息:", user_id, text, flush=True)

        if text and message_id not in seen_ids:
            post = {"id": message_id, "timestamp": timestamp, "text": text}
            new_posts.append(post)

    if new_posts:
        posts.extend(new_posts)
        # ✅ 使用 fallback 的方式排序，避免老数据没有 id 报错
        posts.sort(key=lambda x: (x["timestamp"], x.get("id", 0)), reverse=True)
        save_posts(posts)

    print(f"✅ 新增 {len(new_posts)} 条消息", flush=True)

if __name__ == "__main__":
    fetch_messages()
