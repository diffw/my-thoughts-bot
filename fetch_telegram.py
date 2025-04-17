import requests
import json
from datetime import datetime

BOT_TOKEN = "8086705781:AAHZNKjhaJv6f02G2Wiq5OZHjql9u978MXk"
TELEGRAM_USER_ID = 5090028387
POSTS_FILE = "posts.json"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

def load_posts():
    try:
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

def fetch_messages():
    posts = load_posts()
    seen = {(p['timestamp'], p['text']) for p in posts}

    res = requests.get(API_URL).json()
    new_posts = []

    for update in res.get("result", []):
        msg = update.get("message")
        if not msg:
            continue
        user_id = msg.get("from", {}).get("id")
        text = msg.get("text")
        if user_id == TELEGRAM_USER_ID and text:
            timestamp = datetime.utcfromtimestamp(msg["date"]).strftime("%Y-%m-%d %H:%M:%S")
            post = {"timestamp": timestamp, "text": text}
            if (timestamp, text) not in seen:
                new_posts.append(post)

    if new_posts:
        posts.extend(new_posts)
        posts.sort(key=lambda x: x["timestamp"], reverse=True)
        save_posts(posts)

if __name__ == "__main__":
    fetch_messages()
