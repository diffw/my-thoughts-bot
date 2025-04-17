import requests
import json
import os
from datetime import datetime
from pytz import timezone

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
POSTS_FILE = "posts.json"
OFFSET_FILE = "offset.txt"  # 用于记录上一次处理到哪个 update_id

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
central_tz = timezone("America/Chicago")  # 达拉斯时间 CST/CDT 自动转换

def load_posts():
    try:
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

def load_offset():
    try:
        with open(OFFSET_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0

def save_offset(offset):
    with open(OFFSET_FILE, "w") as f:
        f.write(str(offset))

def fetch_messages():
    posts = load_posts()
    seen_ids = {p.get("id") for p in posts if "id" in p}
    offset = load_offset()

    # 每次只获取从 offset 之后的消息
    res = requests.get(API_URL, params={"offset": offset + 1}).json()
    updates = res.get("result", [])
    new_posts = []

    for update in updates:
        print("📦 update 原始内容:", json.dumps(update, ensure_ascii=False), flush=True)

        msg = update.get("message")
        if not msg:
            continue

        message_id = msg.get("message_id")
        update_id = update.get("update_id")
        user_id = str(msg.get("from", {}).get("id"))
        text = msg.get("text")
        timestamp = datetime.fromtimestamp(msg["date"], tz=central_tz).strftime("%Y-%m-%d")

        print("🔍 收到来自用户 ID 的消息:", user_id, text, flush=True)

        if text and message_id not in seen_ids:
            post = {"id": message_id, "timestamp": timestamp, "text": text}
            new_posts.append(post)

        # 更新 offset，即使没有新消息也要记录 update_id，避免重复拉取
        offset = max(offset, update_id)

    if new_posts:
        posts.extend(new_posts)
        posts.sort(key=lambda x: (x["timestamp"], x["id"]), reverse=True)
        save_posts(posts)

    save_offset(offset)

    print(f"✅ 新增 {len(new_posts)} 条消息", flush=True)

if __name__ == "__main__":
    fetch_messages()
