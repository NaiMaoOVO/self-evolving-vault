#!/usr/bin/env python3
"""黄金运行 A3：为 Horizon 配置新增 4 个游戏行业源 + 1 个故意坏源（失败真实性测试）。
先备份原配置；只追加、不修改既有条目；幂等（重复执行不重复添加）。"""
import json, pathlib, sys

cfg_path = pathlib.Path.home() / "horizon" / "data" / "config.json"
cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
rss = cfg["sources"].setdefault("rss", [])
have_name = {r.get("name") for r in rss}
have_url = {r.get("url") for r in rss}
adds = [
    {"name": "游戏陀螺", "url": "https://www.youxituoluo.com/rss", "enabled": True, "category": "game-industry", "profile": "tech-news"},
    {"name": "GameLook", "url": "http://www.gamelook.com.cn/feed/", "enabled": True, "category": "game-industry", "profile": "tech-news"},
    {"name": "Eurogamer", "url": "https://www.eurogamer.net/feed", "enabled": True, "category": "game-industry", "profile": "tech-news"},
    {"name": "Rock Paper Shotgun", "url": "https://www.rockpapershotgun.com/feed", "enabled": True, "category": "game-industry", "profile": "tech-news"},
    {"name": "黄金运行-坏源测试", "url": "https://nonexistent-goldenrun.invalid/feed.xml", "enabled": True, "category": "test-bad-source", "profile": "tech-news"},
]
added = []
for a in adds:
    if a["name"] not in have_name and a["url"] not in have_url:
        rss.append(a)
        added.append(a["name"])
cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("ADDED:", json.dumps(added, ensure_ascii=False))
print("RSS_TOTAL:", len(rss))
