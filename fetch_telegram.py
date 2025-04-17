import requests
import json
import os
from datetime import datetime
from pytz import timezone

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
POSTS_FILE = "posts.json"
SEEN_FILE = "seen_update_ids.txt"

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

def load_seen_update_ids():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(map(int, f.read().splitlines()))
    except:
        return set()

def save_seen_update_ids(ids):
    with open(SEEN_FILE, "w") as f:
        f.write("\n".join(map(str, sorted(ids))))

def fetch_messages():
    posts = load_posts()
    seen_message_ids = {p["id"] for p in posts}
    seen_update_ids = load_seen_update_ids()

    res = requests.get(API_URL).json()
    updates = res.get("result", [])
    new_posts = []
    new_seen_ids = set()

    for update in updates:
        update_id = update["update_id"]
        if update_id in seen_update_ids:
            continue

        msg = update.get("message")
        if not msg:
            new_seen_ids.add(update_id)
            continue

        message_id = msg.get("message_id")
        text = msg.get("text")
        timestamp = datetime.fromtimestamp(msg["date"], tz=central_tz).strftime("%Y-%m-%d")

        if text and message_id not in seen_message_ids:
            print(f"📥 收到新
