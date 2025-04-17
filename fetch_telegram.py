import requests
import json
import os
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN", "8086705781:AAHZNKjhaJv6f02G2Wiq5OZHjql9u978MXk")
TELEGRAM_USER_ID = "5090028387"
POSTS_FILE = "posts.json"
OFFSET_FILE = "last_update_id.txt"

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

def load_offset():
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, "r") as f:
            return int(f.read().strip())
    return None

def save_offset(offset):
    with open(OFFSET_FILE, "w") as f:
        f.write(str(offset))

def load_posts():
    try:
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

def fetch_messages():
    posts = load_posts()
    seen = {(p["timestamp"], p["text"]) for p in posts}

    offset = load_offset()
    params = {"offset": offset + 1} if offset else {}

    res = requests.get(API_URL, params=params).json()
    updates = res.get("result", [])
    new_posts = []

    max_update_id = offset or 0

    for update in updates:
        msg = update.get("message")
        if not msg:
            continue

        user_id = str(msg.get("from", {}).get("id"))
        text = msg.get("text")
        timestamp = datetime.utcfromtimestamp(msg["date"]).strftime("%Y-%m-%d %H:%M:%S")
        update_id = update["update_id"]
        max_update_id = max(max_update_id, update_id)

        if user_id == TELEGRAM_USER_ID and text:
            item = {"timestamp": timestamp, "text": text}
            if (timestamp, text) not in seen:
                new_posts.append(item)

    if new_posts:
        posts.extend(new_posts)
        posts.sort(key=lambda x: x["timestamp"], reverse=True)
        save_posts(posts)

    save_offset(max_update_id)

if __name__ == "__main__":
    fetch_messages()
