#!/usr/bin/env python3
"""黄金运行 B1 前置：在【工作区内的隔离配置副本】上新增 4 个游戏行业源 + 1 个故意坏源。
背景：直接写 ~/horizon/data/config.json 被文件沙箱拒绝（PermissionError, 一次即止不重试），
改用 Horizon 官方支持的 -d/--data-dir + 隔离副本（runner 的 SM_HORIZON_CONFIG 同机制）。
同时为隔离场景禁用 hackernews/github（黄金运行聚焦游戏市场运营输入），提升 AI 并发以控制时长。
只改副本，不改原配置；幂等。"""
import json, pathlib

cfg_path = pathlib.Path("/Users/chenzixun/Documents/自进化知识库/vault/04_系统维护/运行记录/黄金运行-2026-08-22/horizon-run/data/config.json")
cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
# 隔离：关闭聚合类大源，聚焦游戏行业源
if isinstance(cfg["sources"].get("hackernews"), dict):
    cfg["sources"]["hackernews"]["enabled"] = False
if isinstance(cfg["sources"].get("github"), list):
    for g in cfg["sources"]["github"]:
        g["enabled"] = False
# AI 并发（仅影响本次隔离运行速度）
cfg.setdefault("ai", {})["analysis_concurrency"] = 4
cfg.setdefault("ai", {})["enrichment_concurrency"] = 4

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
