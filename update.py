import json

# ✅ 加载旧内容
with open("posts.json", "r", encoding="utf-8") as f:
    posts = json.load(f)

# ✅ 过滤掉默认消息
posts = [p for p in posts if p["text"] != "定时添加：你好！"]

# ✅ 按 id 去重（如果你担心手动改动引入重复）
seen_ids = set()
unique_posts = []
for post in posts:
    pid = post.get("id")
    if pid and pid not in seen_ids:
        unique_posts.append(post)
        seen_ids.add(pid)

# ✅ 按时间排序（降序）
unique_posts.sort(key=lambda x: (x.get("timestamp"), x.get("id")), reverse=True)

# ✅ 写回文件
with open("posts.json", "w", encoding="utf-8") as f:
    json.dump(unique_posts, f, indent=2, ensure_ascii=False)
