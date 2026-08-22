#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第09章 周进化协议执行器（教程/09）。

子命令：
  review                          读近 7 天反馈卡，按 对象+范围 聚类，输出候选信号表；
                                  强度判定：单次=只记录/候选，≥2 重复或有结果数据=可提稳定规则；
                                  无合格信号输出"本周无可验证进化"。
  apply <proposal-file> --approved
                                  用户批准后增量更新对应规则文件 version+1；
                                  不自动改全局；仅更新提案 status=accepted 并改对应规则文件版本号。

纯标准库实现（py3.9+ 兼容）。设计见 系统/第09章-质量闸门说明.md。
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")


def env(k, d=""):
    return os.environ.get(k, d)


PROJECT_ROOT = Path(env("WE_PROJECT", str(Path(__file__).resolve().parents[1])))
DEFAULT_VAULT = Path(env("WE_VAULT", str(PROJECT_ROOT / "vault")))
FB_DIR = DEFAULT_VAULT / "04_系统维护" / "反馈与进化" / "反馈卡"
PROP_DIR = DEFAULT_VAULT / "04_系统维护" / "反馈与进化" / "进化提案"
RULES_DIR = DEFAULT_VAULT / "04_系统维护" / "规则与画像"


def now_iso():
    return dt.datetime.now(TZ).isoformat(timespec="seconds")


def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_raw = text[3:end].strip()
    body = text[end + 4:]
    fm = {}
    for line in fm_raw.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, body


def read_text(p: Path):
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return None


def section(text: str, title: str):
    """提取 ## title 小节正文（到下一个 ## 或文末）。"""
    m = re.search(rf"^##\s*{re.escape(title)}\s*$\n(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


# 结果数据 = 可量化数字证据：百分比 / 键值数字 / 计数(次|人次|倍|单|天|小时) / 变动词+数字。
# 仅出现"结果数据""提升"等字样不触发（防"无可量化结果数据"类否定句误判，T3 教训）。
QUANT_RE = re.compile(
    r"\d+(?:\.\d+)?\s*%"
    r"|[=:：]\s*-?\d+(?:\.\d+)?"
    r"|\d+(?:\.\d+)?\s*(?:次|人次|倍|单|天|小时)"
    r"|(?:提升|下降|增长|降低|升到|降至)\s*[\d.]+",
    re.I,
)


# ---------- review ----------

def collect_feedback_cards(days: int = 7, fb_dir: Path = FB_DIR):
    """收集 days 天内 created 的反馈卡。返回 list[dict]。"""
    if not fb_dir.exists():
        return []
    cutoff = dt.date.today() - dt.timedelta(days=days)
    cards = []
    for p in sorted(fb_dir.glob("*.md")):
        text = read_text(p) or ""
        fm, body = parse_frontmatter(text)
        created = fm.get("created", "")
        try:
            d = dt.date.fromisoformat(created[:10])
        except Exception:
            continue
        if d < cutoff:
            continue
        cards.append({
            "file": p.name,
            "path": p,
            "fm": fm,
            "body": body,
            "text": text,
            "对象": section(body, "对象"),
            "范围": section(body, "范围"),
            "强度": section(body, "强度"),
            "原话": section(body, "原话"),
            "事实": section(body, "事实"),
            "判断": section(body, "判断"),
            "结果数据": "",  # 从原话/事实里探测"结果数据"关键词
        })
        joined = cards[-1]["原话"] + cards[-1]["事实"]
        if QUANT_RE.search(joined):
            cards[-1]["结果数据"] = "yes"
    return cards


def cluster_signals(cards):
    """按 (对象, 范围) 聚类。返回 dict[(对象,范围)] -> list[card]。"""
    groups = {}
    for c in cards:
        obj = (c["对象"] or "未标注").split("\n")[0].strip("- ").strip()
        scope = (c["范围"] or "未标注").split("\n")[0].strip("- ").strip()
        key = (obj, scope)
        groups.setdefault(key, []).append(c)
    return groups


def strength_label(group):
    """强度判定：单次=只记录/候选；≥2 重复 或 任一含结果数据 = 可提稳定规则。"""
    n = len(group)
    has_data = any(c["结果数据"] == "yes" for c in group)
    if n >= 2 or has_data:
        return "可提稳定规则"
    return "只记录/候选"


def cmd_review(args):
    days = int(getattr(args, "days", 7))
    fb_dir = Path(getattr(args, "fb_dir", None) or FB_DIR)
    cards = collect_feedback_cards(days=days, fb_dir=fb_dir)
    print(f"# 周进化 review 报告")
    print(f"# 反馈卡目录: {fb_dir}")
    print(f"# 窗口: 近 {days} 天")
    print(f"# 时间: {now_iso()}")
    print(f"# 命中反馈卡: {len(cards)} 张")
    print()

    if not cards:
        print("## 结论")
        print()
        print("本周无可验证进化（反馈卡目录无近 7 天反馈或为空）。")
        print()
        print("## 依据")
        print()
        print("- 教程第09章铁律：无合格信号就写\"本周无可验证进化\"，不伪进化。")
        print("- 单次反馈不得直接改全局规则（进化协议.md 铁律一）。")
        return 0

    groups = cluster_signals(cards)
    print("## 候选信号表")
    print()
    print("| # | 对象 | 范围 | 重复次数 | 结果数据 | 强度判定 | 来源卡 |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    rows = []
    idx = 1
    for (obj, scope), grp in sorted(groups.items()):
        label = strength_label(grp)
        has_data = "是" if any(c["结果数据"] == "yes" for c in grp) else "否"
        files = ", ".join(c["file"] for c in grp)
        print(f"| {idx} | {obj} | {scope} | {len(grp)} | {has_data} | {label} | {files} |")
        rows.append({"对象": obj, "范围": scope, "n": len(grp), "强度": label,
                     "来源": grp, "结果数据": has_data})
        idx += 1
    print()

    stable = [r for r in rows if r["强度"] == "可提稳定规则"]
    cand = [r for r in rows if r["强度"] == "只记录/候选"]
    print("## 结论")
    print()
    if stable:
        print(f"可提稳定规则信号 {len(stable)} 条（≥2 重复或有结果数据）：")
        for r in stable:
            print(f"- 对象「{r['对象']}」范围「{r['范围']}」（n={r['n']}，结果数据={r['结果数据']}）→ 建议生成进化提案待用户批准")
        print()
        print("注：用户批准前不修改任何规则文件（铁律一）。")
    else:
        print("本周无可验证进化：仅单次反馈/候选信号，未达 ≥2 重复或结果数据阈值。")
    print()
    if cand:
        print("## 仅记录/候选（不升级全局）")
        print()
        for r in cand:
            print(f"- 对象「{r['对象']}」范围「{r['范围']}」（n={r['n']}，单次意见）→ 只记录，不改全局规则")
        print()
    print("## 铁律核对")
    print()
    print("- 单次反馈不改全局：✓（本次 review 未对任何规则文件写入）")
    print(f"- ≥2 重复或结果数据才升级：✓（稳定信号 {len(stable)} 条均满足）")
    print("- 无行为差异不标 evolved：✓（本报告仅产出候选，未标 evolved）")
    if not stable:
        print("- 无信号写\"本周无进化\"：✓")
    return 0


# ---------- apply ----------

VERSION_RE = re.compile(r"^version:\s*(\d+)\s*$", re.M)


def find_rule_file(rules_dir: Path, proposal_body: str):
    """从提案正文 ## 影响 / ## 新规则 推断目标规则文件名关键词。"""
    # 优先：提案 frontmatter 或正文里出现的目标文件 wikilink
    m = re.search(r"\[\[([^\]]+?)\]\]", proposal_body)
    if m:
        name = m.group(1).split("|", 1)[0].strip()
        cand = rules_dir / name
        if cand.is_file():
            return cand
        if not name.endswith(".md") and (cand.with_suffix(".md")).is_file():
            return cand.with_suffix(".md")
    # 退化：按 ## 影响 区提到的关键词在 rules_dir 搜文件名
    impact = section(proposal_body, "影响") + section(proposal_body, "新规则")
    for p in rules_dir.rglob("*.md"):
        if ".obsidian" in p.parts:
            continue
        if p.name == "进化协议.md":
            continue
        for kw in re.findall(r"[\u4e00-\u9fa5A-Za-z]{2,}", impact):
            if kw in p.stem or kw in p.name:
                return p
    return None


def bump_version(rule_file: Path):
    text = rule_file.read_text(encoding="utf-8")
    m = VERSION_RE.search(text)
    if m:
        old = int(m.group(1))
        new = old + 1
        text = VERSION_RE.sub(f"version: {new}", text, count=1)
        rule_file.write_text(text, encoding="utf-8")
        return old, new
    # 无 version 字段 → 在 frontmatter 末尾插入 version: 1
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[:end] + f"\nversion: 1" + text[end:]
            rule_file.write_text(text, encoding="utf-8")
            return None, 1
    return None, None


def cmd_apply(args):
    proposal = Path(args.proposal)
    if not proposal.is_file():
        print(f"FAIL: 提案文件不存在: {proposal}", file=sys.stderr)
        return 2
    if not args.approved:
        print("FAIL: 未带 --approved，不执行任何修改（用户批准前不改规则）。", file=sys.stderr)
        return 2
    text = proposal.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if fm.get("status", "").lower() not in ("open", "accepted"):
        print(f"FAIL: 提案 status={fm.get('status')!r}，仅 open 可经 --approved 升为 accepted。",
              file=sys.stderr)
        return 2

    rules_dir = Path(getattr(args, "rules_dir", None) or RULES_DIR)
    rule_file = find_rule_file(rules_dir, body)
    if rule_file is None:
        print(f"FAIL: 未能从提案定位目标规则文件（rules_dir={rules_dir}）。", file=sys.stderr)
        print("请人工确认目标规则文件后手动 version+1。", file=sys.stderr)
        return 3

    old_v, new_v = bump_version(rule_file)
    # 同步提案 status -> accepted
    if fm.get("status", "").lower() == "open":
        text = proposal.read_text(encoding="utf-8")
        text = re.sub(r"^status:\s*\S+\s*$", "status: accepted", text, count=1, flags=re.M)
        # 同步正文 ## 状态
        text = re.sub(r"(^##\s*状态\s*$\n- )(\S+)", lambda m: m.group(1) + "accepted", text,
                      count=1, flags=re.M)
        # 刷新 updated
        today = dt.date.today().isoformat()
        text = re.sub(r"^updated:\s*\S+\s*$", f"updated: {today}", text, count=1, flags=re.M)
        proposal.write_text(text, encoding="utf-8")

    print(f"# 进化 apply 报告")
    print(f"# 提案: {proposal}")
    print(f"# 目标规则文件: {rule_file}")
    if old_v is None:
        print(f"# version: 无 → 新增 version: 1")
    else:
        print(f"# version: {old_v} → {new_v}（增量 +1，未改全局）")
    print(f"# 提案 status: {fm.get('status', 'open')} → accepted")
    print(f"# 时间: {now_iso()}")
    print()
    print("## 铁律核对")
    print("- 仅增量 version+1，未触碰其他规则文件：✓")
    print("- 用户已显式批准（--approved）：✓")
    print("- 未自动改全局：✓（只改命中的单条规则文件）")
    print("- 待办：version+1 后须用同类旧任务/新任务做前后对照，有行为差异方可标 evolved（铁律三）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="weekly_evolution.py", description="第09章 周进化协议执行器")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("review", help="读近7天反馈，聚类输出候选信号表")
    r.add_argument("--days", default="7", help="窗口天数（默认7）")
    r.add_argument("--fb-dir", default=None, help="反馈卡目录（隔离测试用）")
    r.set_defaults(func=cmd_review)
    a = sub.add_parser("apply", help="用户批准后增量更新规则文件 version+1")
    a.add_argument("proposal", help="提案文件路径")
    a.add_argument("--approved", action="store_true", help="用户已批准标志")
    a.add_argument("--rules-dir", default=None, help="规则与画像目录（隔离测试用）")
    a.set_defaults(func=cmd_apply)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
