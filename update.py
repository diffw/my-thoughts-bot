import json

POSTS_FILE = "posts.json"
EXCLUDED_TEXTS = {"定时添加：你好！"}  # 可以继续加入其他想屏蔽的内容

# 读取现有内容
with open(POSTS_FILE, "r", encoding="utf-8") as f:
    posts = json.load(f)

# 去重（后出现的覆盖前面的）
unique = {}
for post in posts:
    if post["text"] not in EXCLUDED_TEXTS:
        unique[post["id"]] = post

# 重新排序（按日期降序）
sorted_posts = sorted(unique.values(), key=lambda x: x["timestamp"], reverse=True)

# 写入
with open(POSTS_FILE, "w", encoding="utf-8") as f:
    json.dump(sorted_posts, f, indent=2, ensure_ascii=False)

print(f"✅ 清理完成，当前共 {len(sorted_posts)} 条消息。")
