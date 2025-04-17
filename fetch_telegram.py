import requests
import json
import os
from datetime import datetime
from pytz import timezone

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
POSTS_FILE = "posts.json"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

central_tz = timezone("America/Chicago")  # 自动处理 CST/CDT 时间

def load_posts():
    try:
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

def fetch_messages():
    posts = load_posts()
    seen_ids = {p.get("id") for p in posts if "id" in p}

    res = requests.get(API_URL)
    updates = res.json().get("result", [])
    new_posts = []

    for update in updates:
        print("📦 update 原始内容:", json.dumps(update, ensure_ascii=False), flush=True)

        msg = update.get("message")
        if not msg:
            continue

        message_id = msg.get("message_id")
        text = msg.get("text")
        if not text or message_id in seen_ids:
            continue

        timestamp = datetime.fromtimestamp(
            msg.get("date", 0), tz=central_tz
        ).strftime("%Y-%m-%d")

        print(f"📥 收到新消息 {message_id}：{text}", flush=True)

        post = {
            "id": message_id,
            "timestamp": timestamp,
            "text": text
        }
        new_posts.append(post)

    if new_posts:
        # 使用 dict 去重：id 最新优先，保持降序
        unique = {p["id"]: p for p in sorted(new_posts + posts, key=lambda x: x["id"], reverse=True)}
        sorted_posts = sorted(unique.values(), key=lambda x: x["timestamp"], reverse=True)
        save_posts(sorted_posts)

    print(f"✅ 新增 {len(new_posts)} 条消息", flush=True)

if __name__ == "__main__":
    fetch_messages()
