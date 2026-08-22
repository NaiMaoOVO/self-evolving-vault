#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第09章 质量闸门检查器（教程/09）。

子命令：check [--vault VAULT] [--target DIR]
纯标准库实现（py3.9+ 兼容）。设计见 系统/第09章-质量闸门说明.md。

对 vault 跑 15 项检查覆盖教材 14 条闸门（来源/日期拆分两项；新增⑮用户目标质量高于技术通过，教材第12条闸门落位于此），
每项独立函数，输出 PASS/FAIL/WARN/N/A + 证据。
退出码：全部 PASS/WARN/N/A → 0；任一 FAIL → 1。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")


def env(k, d=""):
    return os.environ.get(k, d)


PROJECT_ROOT = Path(env("QG_PROJECT", str(Path(__file__).resolve().parents[1])))
DEFAULT_VAULT = Path(env("QG_VAULT", str(PROJECT_ROOT / "vault")))


def now_iso():
    return dt.datetime.now(TZ).isoformat(timespec="seconds")


def parse_frontmatter(text: str):
    """返回 (dict, body)。无 frontmatter 返回 ({}, text)。"""
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


def iter_md(root: Path):
    if not root.exists():
        return
    for p in root.rglob("*.md"):
        if ".obsidian" in p.parts:
            continue
        yield p


def find_in_vault(vault: Path, link_target: str):
    """解析 Obsidian wikilink 目标。link_target 已去掉 [[]] 和 |alias。"""
    lt = link_target.strip()
    if not lt:
        return None
    if "|" in lt:
        lt = lt.split("|", 1)[0].strip()
    cand = vault / lt
    if cand.is_file():
        return cand
    if not lt.endswith(".md") and (cand.with_suffix(".md")).is_file():
        return cand.with_suffix(".md")
    base = Path(lt).name
    base_md = base if base.endswith(".md") else base + ".md"
    for p in iter_md(vault):
        if p.name == base_md:
            return p
    return None


WIKILINK_RE = re.compile(r"\[\[([^\]]+?)\]\]")


def extract_wikilinks(text: str):
    return [m.group(1) for m in WIKILINK_RE.finditer(text)]


class R:
    def __init__(self, idx, name, status, evidence):
        self.idx = idx
        self.name = name
        self.status = status
        self.evidence = evidence

    def fmt(self):
        ev = self.evidence
        if isinstance(ev, list):
            ev = "\n    ".join(ev)
        return f"[{self.status}] {self.idx:02d} {self.name}\n    {ev}"


# ---------- 15 项检查（覆盖教材 14 条闸门） ----------

def check_01_resource_no_overwrite(vault: Path) -> R:
    """①资源层零覆盖：git diff 00_资源库 为空（已跟踪文件无修改/删除；新文件允许）。"""
    res_dir = vault / "00_资源库"
    if not res_dir.exists():
        return R(1, "资源层零覆盖", "N/A", "00_资源库 不存在")
    repo = vault
    while repo != repo.parent:
        if (repo / ".git").exists():
            break
        repo = repo.parent
    if not (repo / ".git").exists():
        return R(1, "资源层零覆盖", "N/A",
                 f"{vault} 不在 git 仓库内，git diff 不可用")
    try:
        out = subprocess.run(
            ["git", "diff", "--name-status", "HEAD", "--", "vault/00_资源库"],
            cwd=str(repo), capture_output=True, text=True, timeout=15,
        )
    except Exception as e:
        return R(1, "资源层零覆盖", "N/A", f"git 调用失败：{e}")
    lines = [l for l in out.stdout.splitlines() if l.strip()]
    bad = [l for l in lines if l.startswith(("M", "D", "R", "C", "T"))]
    if bad:
        return R(1, "资源层零覆盖", "FAIL",
                 "00_资源库 已跟踪文件被改动/删除：\n    " + "\n    ".join(bad))
    return R(1, "资源层零覆盖", "PASS",
             "git diff HEAD -- vault/00_资源库 为空（已跟踪文件无修改/删除）")


SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?:api[_-]?key|apikey)\s*[=:]\s*['\"]?[A-Za-z0-9_-]{16,}['\"]?", re.I),
    re.compile(r"password\s*[=:]\s*['\"]?[A-Za-z0-9_!@#$%^&*.-]{8,}['\"]?", re.I),
    re.compile(r"token\s*[=:]\s*['\"]?[A-Za-z0-9_-]{16,}['\"]?", re.I),
]
PLACEHOLDER_HINTS = ["<", ">", "YOUR_", "your_", "xxx", "占位", "示例", "example",
                     "placeholder", "REPLACE", "填入", "必填", "模板", "字段名",
                     "field name", "字段说明"]


def check_02_secret_scan(vault: Path) -> R:
    """②secret扫描：grep sk-/api_key=/password=/token=，排除占位与字段名。"""
    hits = []
    seen = set()

    def scan(text, label):
        for i, line in enumerate(text.splitlines(), 1):
            for pat in SECRET_PATTERNS:
                if not pat.search(line):
                    continue
                if any(h in line for h in PLACEHOLDER_HINTS):
                    continue
                if re.match(r"^\s*[A-Za-z_]+\s*:\s*<.+>\s*$", line):
                    continue
                key = (label, i)
                if key in seen:
                    continue
                seen.add(key)
                hits.append(f"{label}:{i}: {line.strip()}")

    for p in iter_md(vault):
        scan(read_text(p) or "", str(p.relative_to(vault)))
    sys_dir = vault.parent / "系统"
    if sys_dir.exists():
        for p in sys_dir.rglob("*.py"):
            scan(p.read_text(encoding="utf-8", errors="ignore"), f"系统/{p.name}")
    if hits:
        return R(2, "secret扫描", "FAIL",
                 f"发现疑似硬编码 secret {len(hits)} 处：\n    " + "\n    ".join(hits[:10]))
    return R(2, "secret扫描", "PASS", "未发现硬编码 secret（已排除占位与字段名）")


def check_03_source_exists(vault: Path) -> R:
    """③来源存在：知识卡 [[wikilink]] 目标文件存在。"""
    wiki = vault / "01_主题Wiki"
    if not wiki.exists():
        return R(3, "来源存在", "N/A", "01_主题Wiki 不存在")
    broken = []
    checked = 0
    for p in iter_md(wiki):
        text = read_text(p) or ""
        for link in extract_wikilinks(text):
            target = link.split("|", 1)[0].strip()
            if not target or target.startswith("#"):
                continue
            target = target.split("#", 1)[0].strip()
            checked += 1
            if find_in_vault(vault, target) is None:
                broken.append(f"{p.relative_to(vault)} → [[{link}]]")
    if broken:
        return R(3, "来源存在", "FAIL",
                 f"{len(broken)} 条 wikilink 目标不存在：\n    " + "\n    ".join(broken[:10]))
    return R(3, "来源存在", "PASS", f"知识卡 {checked} 条 wikilink 目标全部存在")


ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?([+-]\d{2}:\d{2})?)?$")


def check_04_date_valid(vault: Path) -> R:
    """④日期有效：frontmatter created/updated 为 ISO 格式。"""
    bad = []
    checked = 0
    for p in iter_md(vault):
        fm, _ = parse_frontmatter(read_text(p) or "")
        for key in ("created", "updated"):
            if key not in fm:
                continue
            val = fm[key]
            if "<" in val or ">" in val:  # 模板占位符跳过
                continue
            checked += 1
            if not ISO_DATE_RE.match(val):
                bad.append(f"{p.relative_to(vault)} {key}={val!r} 非合法 ISO")
    if bad:
        return R(4, "日期有效", "FAIL",
                 f"{len(bad)} 处日期非法：\n    " + "\n    ".join(bad[:10]))
    return R(4, "日期有效", "PASS", f"{checked} 处 created/updated 均为合法 ISO 日期")


def check_05_fact_judgment_separation(vault: Path) -> R:
    """⑤事实判断分离：知识卡含 '## 事实' 与 '## 判断' 分区标记。"""
    wiki = vault / "01_主题Wiki"
    if not wiki.exists():
        return R(5, "事实判断分离", "N/A", "01_主题Wiki 不存在")
    missing = []
    total = 0
    for p in iter_md(wiki):
        fm, body = parse_frontmatter(read_text(p) or "")
        if fm.get("type") not in (None, "knowledge"):
            continue
        total += 1
        has_fact = bool(re.search(r"^##\s*事实\b", body, re.M))
        has_judge = bool(re.search(r"^##\s*判断\b", body, re.M))
        if not (has_fact and has_judge):
            miss = ([x for x, ok in [("事实", has_fact), ("判断", has_judge)] if not ok])
            missing.append(f"{p.relative_to(vault)} 缺 {'/'.join(miss)} 区")
    if missing:
        return R(5, "事实判断分离", "FAIL",
                 f"{len(missing)} 张知识卡缺分区标记：\n    " + "\n    ".join(missing[:10]))
    return R(5, "事实判断分离", "PASS", f"{total} 张知识卡均含 ## 事实 与 ## 判断 分区")


CLAIM_RE = re.compile(r"(实测|亲测|我做过|亲自测试|亲历|我亲自)")


def check_06_no_fabricated_claim(vault: Path) -> R:
    """⑥不虚构实测/经历/引用：含 '实测/亲测/我做过' 等且无来源支撑(wikilink/URL)则 FAIL。"""
    wiki = vault / "01_主题Wiki"
    if not wiki.exists():
        return R(6, "不虚构实测/经历/引用", "N/A", "01_主题Wiki 不存在")
    bad = []
    for p in iter_md(wiki):
        _, body = parse_frontmatter(read_text(p) or "")
        has_source = bool(re.search(r"\[\[.+?\]\]", body)) or bool(re.search(r"https?://\S+", body))
        for m in CLAIM_RE.finditer(body):
            if has_source:
                continue
            start = max(0, m.start() - 40)
            ctx = body[start:m.start() + 40].replace("\n", " ")
            bad.append(f"{p.relative_to(vault)}: …{ctx}… （全卡无 wikilink/URL 来源）")
    if bad:
        return R(6, "不虚构实测/经历/引用", "FAIL",
                 f"{len(bad)} 处无来源支撑的实测/经历声明：\n    " + "\n    ".join(bad[:10]))
    return R(6, "不虚构实测/经历/引用", "PASS",
             "知识卡中实测/经历类声明均附来源（或无此类声明）")


def check_07_no_duplicate_output(vault: Path) -> R:
    """⑦不重复生产旧成果：03_输出库 成果标题查重。"""
    out_dir = vault / "03_输出库"
    if not out_dir.exists():
        return R(7, "不重复生产旧成果", "N/A", "03_输出库 不存在")
    titles = {}
    for p in iter_md(out_dir):
        fm, _ = parse_frontmatter(read_text(p) or "")
        t = fm.get("title") or p.stem
        titles.setdefault(t, []).append(str(p.relative_to(vault)))
    dup = {t: v for t, v in titles.items() if len(v) > 1}
    if dup:
        ev = [f"标题「{t}」×{len(v)}：" + " / ".join(v) for t, v in dup.items()]
        return R(7, "不重复生产旧成果", "FAIL",
                 f"{len(dup)} 个重复标题：\n    " + "\n    ".join(ev[:10]))
    n = sum(len(v) for v in titles.values())
    return R(7, "不重复生产旧成果", "PASS", f"03_输出库 {n} 个成果标题唯一")


CLOSURE_RE = re.compile(r"结案-(\d{4}-\d{2}-\d{2})-轮次(\d+)")


def check_08_unique_closure(vault: Path) -> R:
    """⑧每轮唯一结案：蒸馏与结案目录同期(同日同轮)closure 数 ≤ 1。"""
    cd = vault / "04_系统维护" / "蒸馏与结案"
    if not cd.exists():
        return R(8, "每轮唯一结案", "N/A", "蒸馏与结案目录不存在")
    groups = {}
    for p in cd.glob("结案-*.md"):
        m = CLOSURE_RE.match(p.name)
        if m:
            groups.setdefault((m.group(1), m.group(2)), []).append(p.name)
    dup = {k: v for k, v in groups.items() if len(v) > 1}
    if dup:
        ev = [f"{k[0]} 轮次{k[1]} ×{len(v)}：" + " / ".join(v) for k, v in dup.items()]
        return R(8, "每轮唯一结案", "FAIL",
                 f"{len(dup)} 组重复结案：\n    " + "\n    ".join(ev[:10]))
    return R(8, "每轮唯一结案", "PASS",
             f"蒸馏与结案目录 {len(groups)} 组(日,轮)均唯一，无重复结案")


def check_09_fetch_fail_not_no_new(vault: Path) -> R:
    """⑨抓取失败不等于无新增：运行报告含'抓取失败'时不应同时声称无新增且成功入库0。"""
    run_dir = vault / "04_系统维护" / "运行记录"
    if not run_dir.exists():
        return R(9, "抓取失败≠无新增", "N/A", "运行记录目录不存在")
    bad = []
    ok = []
    for p in sorted(run_dir.glob("Horizon-运行-*.md")):
        text = read_text(p) or ""
        if "抓取失败" not in text:
            continue
        m = re.search(r"新入库\s*(\d+)", text)
        new_n = int(m.group(1)) if m else None
        m2 = re.search(r"入库\s*(\d+)", text)
        in_n = int(m2.group(1)) if m2 else None
        claims_no_new = ("无新增" in text) or (new_n == 0) or (in_n == 0)
        claims_success = ("成功" in text) or (new_n is not None and new_n > 0)
        if claims_no_new and not claims_success:
            bad.append(f"{p.name}：含抓取失败且声称无新增/入库0，却宣告成功")
        else:
            ok.append(f"{p.name}：抓取失败存在但新入库 {new_n if new_n is not None else in_n}（未掩盖）")
    if bad:
        return R(9, "抓取失败≠无新增", "FAIL",
                 f"{len(bad)} 份报告掩盖抓取失败：\n    " + "\n    ".join(bad[:10]))
    if not ok:
        return R(9, "抓取失败≠无新增", "PASS",
                 "无运行报告含'抓取失败'，本项无触发场景")
    return R(9, "抓取失败≠无新增", "PASS",
             f"{len(ok)} 份含'抓取失败'的报告均如实记录新增数，未掩盖：\n    " + "\n    ".join(ok[:5]))


def probe_gbrain_cli():
    """探测 gbrain CLI 是否可用（绝不 kill 任何进程）。

    已知环境事实：gbrain serve(MCP) 持 PGLite 锁时 CLI 子命令被拒绝。
    返回 (available: bool, evidence: str)，证据含 serve 进程与退出码。
    """
    ev = []
    try:
        pg = subprocess.run(["pgrep", "-fl", "gbrain"], capture_output=True,
                            text=True, timeout=5)
        ev.append(f"pgrep -fl gbrain (exit={pg.returncode}): {pg.stdout.strip() or '(无进程)'}")
    except Exception as e:  # noqa: BLE001
        ev.append(f"pgrep 调用失败: {e}")
    try:
        out = subprocess.run(["gbrain", "status"], capture_output=True,
                             text=True, timeout=15)
        blob = (out.stdout + out.stderr).strip()
        head = " | ".join(blob.splitlines()[:3])[:300]
        ev.append(f"gbrain status (exit={out.returncode}): {head}")
        lock_markers = ("pglite", "cannot open", "already open", "lock")
        if any(m in blob.lower() for m in lock_markers):
            return False, "\n    ".join(ev)
        return True, "\n    ".join(ev)
    except Exception as e:  # noqa: BLE001
        ev.append(f"gbrain status 调用失败: {e}")
        return False, "\n    ".join(ev)


def check_10_gbrain_consistency(vault: Path) -> R:
    """⑩GBrain一致性（三维度：页面/索引/embedding）。

    页面数：vault 实际 .md 数 vs 状态.md vault_md_count/brain_pages（静态可验）。
    索引/embedding：需 gbrain CLI；serve(MCP) 持 PGLite 锁期间 CLI 被拒 → 该两维度
    N/A，附 serve 进程 + 退出码 + stderr 摘录证据（绝不 kill 进程）。
    """
    msgs = []
    # 维度1：页面数（静态对比）
    actual = sum(1 for _ in iter_md(vault))
    state_md = vault / "04_系统维护" / "状态.md"
    vmc = bp = None
    if state_md.exists():
        text = read_text(state_md) or ""
        m1 = re.search(r"vault_md_count:\s*(\d+)", text)
        m2 = re.search(r"brain_pages:\s*(\d+)", text)
        vmc = int(m1.group(1)) if m1 else None
        bp = int(m2.group(1)) if m2 else None
    msgs.append(f"页面数: vault 实际 .md = {actual}, 状态.md vault_md_count = {vmc}, "
                f"brain_pages = {bp}")
    page_status = "PASS"
    if vmc is None or bp is None:
        page_status = "WARN"
        msgs.append("页面数: 状态.md 缺少 vault_md_count/brain_pages，无法比对")
    elif vmc != bp:
        page_status = "FAIL"
        msgs.append(f"页面数: vault_md_count({vmc}) ≠ brain_pages({bp})")
    else:
        diff = abs(actual - vmc)
        if diff > 2:
            page_status = "WARN"
            msgs.append(f"页面数: 状态计数({vmc}) 与实际({actual}) 差异 {diff}（待刷新）")
        else:
            msgs.append(f"页面数: 一致（差异 {diff}）")
    # 维度2/3：索引与 embedding（需 CLI；锁拒绝 → N/A + 证据）
    ok, ev = probe_gbrain_cli()
    if ok:
        msgs.append("索引/embedding: gbrain CLI 可用，但纯标准库不解析其索引与 "
                    "embedding 计数 → N/A（精确核对请走 gbrain serve 的 MCP 工具）")
    else:
        msgs.append("索引: N/A —— gbrain serve(MCP) 持 PGLite 锁，CLI 被拒绝；证据:\n    " + ev)
        msgs.append("embedding: N/A —— 同上（锁拒绝，无法核验 embedding 状态）")
    overall = "FAIL" if page_status == "FAIL" else ("WARN" if page_status == "WARN" else "PASS")
    return R(10, "GBrain一致性(页面/索引/embedding)", overall, "\n    ".join(msgs))


def check_11_state_file_consistency(vault: Path) -> R:
    """⑪状态文件一致：状态机.json.state vs 状态.md 状态机: vs AGENTS.md SM-HEALTH 状态字段。"""
    sj = vault / "04_系统维护" / "状态机.json"
    state_md = vault / "04_系统维护" / "状态.md"
    agents = vault / "AGENTS.md"
    json_state = None
    if sj.exists():
        try:
            json_state = json.loads(read_text(sj) or "{}").get("state")
        except Exception as e:
            return R(11, "状态文件一致", "FAIL", f"状态机.json 解析失败：{e}")
    md_state = None
    if state_md.exists():
        m = re.search(r"^- 状态机:\s*([A-Za-z_]+)", read_text(state_md) or "", re.M)
        md_state = m.group(1) if m else None
    agents_state = None
    if agents.exists():
        m = re.search(r"^状态机:\s*([A-Za-z_]+)", read_text(agents) or "", re.M)
        agents_state = m.group(1) if m else None
    msgs = [f"状态机.json.state = {json_state!r}",
            f"状态.md 状态机: = {md_state!r}",
            f"AGENTS.md SM-HEALTH = {agents_state!r}"]
    states = [s for s in (json_state, md_state, agents_state) if s is not None]
    if len(states) < 2:
        return R(11, "状态文件一致", "WARN",
                 "状态字段样本不足，无法三方比对；\n    " + "\n    ".join(msgs))
    if len(set(states)) > 1:
        return R(11, "状态文件一致", "FAIL",
                 "状态字段不一致；\n    " + "\n    ".join(msgs))
    return R(11, "状态文件一致", "PASS", "三方状态字段一致；\n    " + "\n    ".join(msgs))


def check_12_no_draft_as_output(vault: Path) -> R:
    """⑫中间页不冒充成果：03_输出库 文件 frontmatter status 非 draft。"""
    out_dir = vault / "03_输出库"
    if not out_dir.exists():
        return R(12, "中间页不冒充成果", "N/A", "03_输出库 不存在")
    drafts = []
    total = 0
    for p in iter_md(out_dir):
        total += 1
        fm, _ = parse_frontmatter(read_text(p) or "")
        if fm.get("status", "").strip().lower() == "draft":
            drafts.append(f"{p.relative_to(vault)} status=draft")
    if drafts:
        return R(12, "中间页不冒充成果", "FAIL",
                 f"{len(drafts)} 个 draft 状态文件混入 03_输出库：\n    " + "\n    ".join(drafts[:10]))
    if total == 0:
        return R(12, "中间页不冒充成果", "PASS", "03_输出库 暂无成果文件（无 draft 冒充）")
    return R(12, "中间页不冒充成果", "PASS",
             f"03_输出库 {total} 个文件 status 均非 draft")


def check_13_pause_on_repeat_reject(vault: Path) -> R:
    """⑬连续低分或重复否决触发暂停扩量：≥2 连续否决/dismissed 应触发 paused。"""
    fb_dir = vault / "04_系统维护" / "反馈与进化" / "反馈卡"
    if not fb_dir.exists():
        return R(13, "重复否决触发暂停", "PASS", "反馈卡目录不存在，无触发条件")
    cards = []
    for p in sorted(fb_dir.glob("*.md")):
        if p.name == "README.md":
            continue
        text = read_text(p) or ""
        fm, _ = parse_frontmatter(text)
        action = ""
        m = re.search(r"^##\s*动作\s*$\n(.*?)(?=^##\s|\Z)", text, re.M | re.S)
        if m:
            action = m.group(1).strip()
        cards.append({"file": p.name, "created": fm.get("created", ""),
                      "status": fm.get("status", "").lower(), "action": action,
                      "text": text})

    low_score_re = re.compile(r"(?:满意度|评分|score|rating)\s*[=:：]\s*(\d+)", re.I)

    def is_negative(c):
        if c["status"] == "dismissed":
            return True
        if any(k in c["action"] for k in ("否决", "忽略", "拒绝", "reject")):
            return True
        m = low_score_re.search(c["text"])
        if m and int(m.group(1)) <= 2:
            return True
        return False

    rejects = [c for c in cards if is_negative(c)]
    sj = vault / "04_系统维护" / "状态机.json"
    paused = False
    if sj.exists():
        try:
            paused = bool(json.loads(read_text(sj) or "{}").get("paused", False))
        except Exception:
            paused = False
    if len(rejects) >= 2 and not paused:
        return R(13, "重复否决触发暂停", "FAIL",
                 f"否决/忽略/低分信号 {len(rejects)} 条但状态机 paused=false（未触发暂停扩量）：\n    "
                 + "\n    ".join(c["file"] for c in rejects[:5]))
    if len(rejects) >= 2 and paused:
        return R(13, "重复否决触发暂停", "PASS",
                 f"否决/忽略/低分 {len(rejects)} 条，状态机已 paused（暂停扩量已生效）")
    return R(13, "重复否决触发暂停", "PASS",
             f"反馈卡 {len(cards)} 条，否决/忽略/低分 {len(rejects)} 条（未达 ≥2 阈值，无需暂停）")


def check_14_profile_staleness_audit(vault: Path) -> R:
    """⑭画像长期无更新触发审计：职业包文件 updated 距今 >30 天 → WARN（不 FAIL）。"""
    cp = vault / "04_系统维护" / "职业包"
    if not cp.exists():
        return R(14, "画像长期无更新审计", "N/A", "职业包目录不存在")
    today_d = dt.date.today()
    stale = []
    total = 0
    for p in cp.rglob("*.md"):
        if ".obsidian" in p.parts:
            continue
        fm, _ = parse_frontmatter(read_text(p) or "")
        upd = fm.get("updated", "")
        if not upd:
            continue
        total += 1
        try:
            d = dt.date.fromisoformat(upd[:10])
        except Exception:
            stale.append(f"{p.relative_to(vault)} updated={upd!r} 无法解析")
            continue
        age = (today_d - d).days
        if age > 30:
            stale.append(f"{p.relative_to(vault)} updated={upd} 距今 {age} 天（>30，建议审计）")
    if stale:
        return R(14, "画像长期无更新审计", "WARN",
                 f"{len(stale)} 个职业包文件长期未更新（WARN 不 FAIL，触发审计而非伪升级）：\n    "
                 + "\n    ".join(stale[:10]))
    return R(14, "画像长期无更新审计", "PASS",
             f"职业包 {total} 个文件 updated 均在 30 天内")


USER_GOAL_RE = re.compile(
    r"(用户目标|用户问题|用户要什么|用户确认|用户验收|用户认可|用户满意|验收人)")
TECH_PASS_RE = re.compile(
    r"(技术通过|测试通过|检查通过|闸门.{0,6}PASS|全部PASS|技术验收通过)")


def check_15_user_goal_over_technical(vault: Path) -> R:
    """⑮用户目标质量高于技术通过：正式成果不得仅凭技术通过宣告达成。

    对象：结案类型=A(正式成果) 的结案文件 + 03_输出库 全部成果文件。
    FAIL：含技术通过声明但全篇无用户目标/用户确认证据（技术通过冒充用户目标达成）。
    WARN：正式成果缺用户目标/用户确认字段（触发审计，不强制伪升级）。
    """
    targets = []
    cd = vault / "04_系统维护" / "蒸馏与结案"
    if cd.exists():
        for p in sorted(cd.glob("结案-*.md")):
            text = read_text(p) or ""
            m = re.search(r"结案类型[：:]\s*\**\s*([ABC])", text)
            if m and m.group(1) == "A":
                targets.append((str(p.relative_to(vault)), text))
    out_dir = vault / "03_输出库"
    if out_dir.exists():
        for p in iter_md(out_dir):
            targets.append((str(p.relative_to(vault)), read_text(p) or ""))
    if not targets:
        return R(15, "用户目标高于技术通过", "PASS",
                 "当前无正式成果类结案与成果文件，无触发对象")
    fails, warns, oks = [], [], []
    for label, text in targets:
        has_goal = bool(USER_GOAL_RE.search(text))
        has_tech = bool(TECH_PASS_RE.search(text))
        if has_tech and not has_goal:
            fails.append(f"{label}：含技术通过声明但全篇无用户目标/用户确认证据"
                         "（技术通过冒充用户目标达成）")
        elif not has_goal:
            warns.append(f"{label}：缺用户目标/用户确认字段（WARN 审计，不强制）")
        else:
            oks.append(label)
    if fails:
        return R(15, "用户目标高于技术通过", "FAIL",
                 f"{len(fails)} 处技术通过冒充用户目标：\n    " + "\n    ".join(fails[:10]))
    if warns:
        return R(15, "用户目标高于技术通过", "WARN",
                 f"{len(warns)} 个正式成果缺用户目标证据（触发审计）：\n    "
                 + "\n    ".join(warns[:10]))
    return R(15, "用户目标高于技术通过", "PASS",
             f"{len(oks)} 个正式成果均含用户目标/用户确认证据")


CHECKS = [
    check_01_resource_no_overwrite,
    check_02_secret_scan,
    check_03_source_exists,
    check_04_date_valid,
    check_05_fact_judgment_separation,
    check_06_no_fabricated_claim,
    check_07_no_duplicate_output,
    check_08_unique_closure,
    check_09_fetch_fail_not_no_new,
    check_10_gbrain_consistency,
    check_11_state_file_consistency,
    check_12_no_draft_as_output,
    check_13_pause_on_repeat_reject,
    check_14_profile_staleness_audit,
    check_15_user_goal_over_technical,
]


def run_all(vault: Path):
    results = [fn(vault) for fn in CHECKS]
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(prog="quality_gate.py", description="第09章 质量闸门检查器")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="对 vault 跑 15 项检查（覆盖教材 14 条闸门）")
    c.add_argument("--vault", default=str(DEFAULT_VAULT), help="vault 根路径（默认 工程/vault）")
    c.add_argument("--target", default=None, help="隔离测试目标目录（替代 --vault）")
    args = ap.parse_args(argv)

    if args.cmd == "check":
        target = Path(args.target) if args.target else Path(args.vault)
        print(f"# 质量闸门检查报告")
        print(f"# vault: {target}")
        print(f"# 时间: {now_iso()}")
        print(f"# 项数: {len(CHECKS)}")
        print()
        results = run_all(target)
        cnt = {"PASS": 0, "FAIL": 0, "WARN": 0, "N/A": 0}
        for r in results:
            print(r.fmt())
            print()
            cnt[r.status] += 1
        print(f"# 汇总: PASS={cnt['PASS']} FAIL={cnt['FAIL']} WARN={cnt['WARN']} N/A={cnt['N/A']}")
        print(f"# 退出码: {'1' if cnt['FAIL'] else '0'}")
        return 1 if cnt['FAIL'] else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
