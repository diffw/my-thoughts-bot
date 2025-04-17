import json
from datetime import datetime

# ✅ 不再添加默认消息

# 加载旧内容
with open("posts.json", "r", encoding="utf-8") as f:
    posts = json.load(f)

# ✅ 过滤掉所有默认消息
posts = [p for p in posts if p["text"] != "定时添加：你好！"]

# 写回去
with open("posts.json", "w", encoding="utf-8") as f:
    json.dump(posts, f, indent=2, ensure_ascii=False)
