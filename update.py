import json
from datetime import datetime

# 模拟新消息
new_message = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "text": "定时添加：你好！"
}

# 加载旧内容
with open("posts.json", "r", encoding="utf-8") as f:
    posts = json.load(f)

posts.append(new_message)

with open("posts.json", "w", encoding="utf-8") as f:
    json.dump(posts, f, indent=2, ensure_ascii=False)
