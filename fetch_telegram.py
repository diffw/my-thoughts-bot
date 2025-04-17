import requests
import json
import os
from datetime import datetime
from pytz import timezone

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
POSTS_FILE = "posts.json"
SEEN_FILE = "seen_update_ids.txt"  # 每个 update_id 只处理一次

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
central_tz = timezone("America/Chicago")

def load_posts():
    try:
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

def load_seen_ids():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(map(int, f.read().splitlines()))
    except:
        return set()

def save_seen_ids(seen_ids):
    with open(SEEN_FILE, "w") as f:
        f.write("\n".join(map(str, sorted(seen_ids))))

def fetch_messages():
    posts = load_posts()
    seen_message_ids = {p["id"] for p in posts}
    seen_update_ids = load_seen_ids()

    res = requests.get(API_URL).json()
    updates = res.get("result", [])
    new_posts = []

    for update in updates:
        update_id = update.get("update_id")
        if update_id in seen_update_ids:
            continue  # 已处理过

        msg = update.get("message")
        if not msg:
            seen_update_ids.add(update_id)
            continue

        message_id = msg.get("message_id")
        user_id = str(msg.get("from", {}).get("id"))
        text = msg.get("text")
        timestamp = datetime.fromtimestamp(msg["date"], tz=central_tz).strftime("%Y-%m-%d")

        print("📦 收到消息:", json.dumps(update, ensure_ascii=False), flush=True)

        if text and message_id not in seen_message_ids:
            post = {"id": message_id, "timestamp": timestamp, "text": text}
            new_posts.append(post)

        seen_update_ids.add(update_id)  # 无论是否录用，都记为已处理

    if new_posts:
        posts.extend(new_posts)
        posts.sort(key=lambda x: (x["timestamp"], x["id"]), reverse=True)
        save_posts(posts)

    save_seen_ids(seen_update_ids)

    print(f"✅ 本次新增 {len(new_posts)} 条消息", flush=True)

if __name__ == "__main__":
    fetch_messages()
