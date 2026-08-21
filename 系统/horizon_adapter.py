#!/usr/bin/env python3
"""Horizon 日报 → Obsidian vault 适配器（第03章）。

输入：<data-dir>/summaries/horizon-YYYY-MM-DD-<lang>.md（默认取 zh，避免双语重复入库）
输出：<vault>/00_资源库/外部知识/<日期>-<slug>.md 知识卡
      <vault>/04_系统维护/运行记录/Horizon-运行-<timestamp>.md 运行报告
运行：cd ~/horizon && uv run python 系统/horizon_adapter.py [--data-dir D] [--vault V] [--dry-run]
"""

import argparse
import asyncio
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import trafilatura

DEFAULT_DATA_DIR = os.environ.get("HORIZON_DATA_DIR", str(Path.home() / "horizon" / "data"))
DEFAULT_VAULT = os.environ.get(
    "VAULT_ROOT", "/Users/chenzixun/Documents/自进化知识库/vault"
)
DEFAULT_PROXY = os.environ.get("HORIZON_ADAPTER_PROXY", "http://127.0.0.1:7897")
DEFAULT_TIMEOUT = 15
EXCERPT_CHARS = 2000
SENSITIVITY = "公开"

SOURCE_TYPES = (
    "hackernews",
    "rss",
    "github",
    "reddit",
    "telegram",
    "twitter",
    "openbb",
    "ossinsight",
    "gdelt",
    "google_news",
)

HEADLINE_RE = re.compile(
    r"^###\s+\[(?P<title>.+)\]\((?P<url>https?://[^)\s]+)\)\s*[⭐️]*\s*(?P<score>[\d.]+|\?)/10\s*$"
)
SOURCE_LINE_RE = re.compile(
    r"^(?P<stype>" + "|".join(SOURCE_TYPES) + r")\s*(?: · (?P<rest>.*))?\s*$"
)
ZH_TIME_RE = re.compile(r"^(?P<month>\d{1,2})月(?P<day>\d{1,2})日 (?P<hh>\d{1,2}):(?P<mm>\d{2})$")
EN_TIME_RE = re.compile(r"^(?P<mon>[A-Za-z]{3}) (?P<day>\d{1,2}), (?P<hh>\d{1,2}):(?P<mm>\d{2})$")
EN_MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
DISCUSSION_RE = re.compile(r"\[(?:社区讨论|Discussion)\]\((https?://[^)\s]+)\)")
TAGS_RE = re.compile(r"^\*\*(?:标签|Tags)\*\*:\s*(?P<tags>.+)$")
REPORT_DATE_RE = re.compile(r"^horizon-(\d{4}-\d{2}-\d{2})-(\w+)\.md$")
EXTRA_BLOCK_RE = re.compile(r"^\*\*「.+」\*\*")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def unescape_daily(text: str) -> str:
    if not text:
        return text
    text = html.unescape(text)
    return re.sub(r"\\(.)", r"\1", text)


def slugify(title: str, limit: int = 40) -> str:
    slug = unescape_daily(title).strip()
    slug = re.sub(r"[\s/\\:]+", "-", slug)
    slug = re.sub(r"[^\w\u4e00-\u9fff-]", "", slug, flags=re.UNICODE)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    if len(slug) > limit:
        slug = slug[:limit].rstrip("-")
    return slug or "untitled"


def derive_source(url: str) -> tuple[str, str]:
    host = urlsplit(url).netloc.lower()
    if host.endswith("news.ycombinator.com"):
        return "hackernews", "Hacker News"
    if host.endswith("github.com"):
        parts = [p for p in urlsplit(url).path.split("/") if p]
        if len(parts) >= 2 and ("releases" in parts or "releases" in url):
            return "github-release", f"{parts[0]}/{parts[1]}"
        return "github", f"{parts[0]}/{parts[1]}" if len(parts) >= 2 else "GitHub"
    return "rss", host


def parse_published(token: str, report_date: dt.date) -> str:
    token = token.strip()
    m = ZH_TIME_RE.match(token)
    month = day = None
    hh = mm = ""
    if m:
        month, day = int(m["month"]), int(m["day"])
        hh, mm = m["hh"], m["mm"]
    else:
        m = EN_TIME_RE.match(token)
        if m:
            month, day = EN_MONTHS.get(m["mon"].title(), 0), int(m["day"])
            hh, mm = m["hh"], m["mm"]
    if not month:
        return ""
    year = report_date.year
    if month > report_date.month + 6:
        year -= 1
    return f"{year:04d}-{month:02d}-{day:02d} {hh.zfill(2)}:{mm}"


def parse_item_block(block: str, report_date: dt.date) -> dict | None:
    lines = block.splitlines()
    headline = HEADLINE_RE.match(lines[0].strip())
    if not headline:
        return None
    title = unescape_daily(headline["title"])
    url = headline["url"]
    score = headline["score"]

    summary_lines = []
    source_type = source_name = author = published = discussion = ""
    tags: list[str] = []
    in_details = False
    for line in lines[1:]:
        stripped = line.strip()
        if stripped.startswith("<a id="):
            continue
        if stripped.startswith("<details"):
            in_details = True
            continue
        if in_details:
            if "</details>" in stripped:
                in_details = False
            continue
        if stripped == "---":
            break
        if not source_type:
            m = SOURCE_LINE_RE.match(stripped)
            if m and stripped not in ("---",):
                source_type = m["stype"]
                rest = m["rest"] or ""
                parts = [p.strip() for p in rest.split(" · ") if p.strip()]
                time_part = ""
                for p in parts:
                    dm = DISCUSSION_RE.search(p)
                    if dm:
                        discussion = dm.group(1)
                    elif ZH_TIME_RE.match(p) or EN_TIME_RE.match(p):
                        time_part = p
                    elif not source_name:
                        source_name = unescape_daily(p)
                published = parse_published(time_part, report_date) if time_part else ""
                continue
        tm = TAGS_RE.match(stripped)
        if tm:
            tags = [t.strip().strip("`#") for t in tm["tags"].split(",") if t.strip()]
            continue
        if EXTRA_BLOCK_RE.match(stripped):
            summary_lines.append(unescape_daily(stripped))
            continue
        if stripped:
            summary_lines.append(unescape_daily(stripped))

    fallback_type, fallback_name = derive_source(url)
    if not source_type:
        source_type = fallback_type
    elif source_type == "github" and "/releases" in url:
        source_type = "github-release"
    if not source_name:
        source_name = fallback_name
    if source_type == "hackernews" and not discussion:
        discussion = url if "news.ycombinator.com" in url else ""
    author = source_name if source_type == "rss" else (source_name or "")

    return {
        "title": title,
        "url": url,
        "score": score,
        "ai_summary": "\n\n".join(s for s in summary_lines if s).strip(),
        "source_type": source_type,
        "source_name": source_name,
        "author": author,
        "published": published or f"未知(日报日期：{report_date.isoformat()})",
        "discussion": discussion,
        "tags": tags,
        "report_date": report_date.isoformat(),
    }


def parse_daily_report(path: Path) -> list[dict]:
    m = REPORT_DATE_RE.match(path.name)
    if not m:
        return []
    report_date = dt.date.fromisoformat(m.group(1))
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    items = []
    current: list[str] = []
    for line in lines:
        if HEADLINE_RE.match(line.strip()):
            if current:
                parsed = parse_item_block("\n".join(current), report_date)
                if parsed:
                    items.append(parsed)
            current = [line]
        elif current:
            current.append(line)
    if current:
        parsed = parse_item_block("\n".join(current), report_date)
        if parsed:
            items.append(parsed)
    seen = set()
    unique = []
    for item in items:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)
    return unique


def item_id(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]


def card_filename(item: dict) -> str:
    return f"{item['report_date']}-{slugify(item['title'])}.md"


def load_existing_ids(cards_dir: Path) -> set[str]:
    ids = set()
    if not cards_dir.exists():
        return ids
    for f in cards_dir.glob("*.md"):
        head = f.read_text(encoding="utf-8", errors="replace")[:2000]
        m = re.search(r"^id:\s*(\S+)", head, re.MULTILINE)
        if m:
            ids.add(m.group(1))
    return ids


def render_card(item: dict, card_id: str, excerpt: str, fetched_at: str, report_name: str) -> str:
    tags = item["tags"]
    fm = [
        "---",
        f"id: \"{card_id}\"",
        f"title: \"{item['title'].replace(chr(34), '″')}\"",
        f"author: \"{item['author'].replace(chr(34), '″') or '未知'}\"",
        f"published: \"{item['published']}\"",
        f"url: {item['url']}",
        f"source_type: {item['source_type']}",
        f"source_name: \"{item['source_name']}\"",
        f"fetched_at: {fetched_at}",
        f"score: \"{item['score']}/10\"",
        f"tags: [{', '.join(t for t in tags if t)}]",
        "sensitivity: 公开",
        f"source_report: {report_name}",
        "---",
        "",
    ]
    body = [
        f"# {item['title']}",
        "",
        "## AI 摘要（Horizon 日报）",
        "",
        item["ai_summary"] or "（日报未提供摘要）",
        "",
        "## 原文 excerpt",
        "",
        excerpt,
        "",
        "## 来源信息",
        "",
        f"- 来源类型：{item['source_type']}（{item['source_name']}）",
        f"- 发布时间：{item['published']}",
        f"- 原始 URL：{item['url']}",
    ]
    if item["discussion"]:
        body.append(f"- 社区讨论：{item['discussion']}")
    body.append(f"- 抓取时间：{fetched_at}")
    body.append(f"- 敏感等级：{SENSITIVITY}（外部公开源）")
    body.append("")
    return "\n".join(fm) + "\n".join(body)


async def fetch_excerpt(urls: list[str], proxy: str, timeout: int) -> dict[str, str]:
    results: dict[str, str] = {}

    async def one(client: httpx.AsyncClient, url: str):
        try:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()
            text = trafilatura.extract(resp.text, include_comments=False) or ""
            if not text.strip():
                return url, "抓取失败：正文提取为空（trafilatura 无正文输出）"
            return url, text.strip()[:EXCERPT_CHARS]
        except Exception as e:
            return url, f"抓取失败：{type(e).__name__}: {e}"

    async with httpx.AsyncClient(
        proxy=proxy,
        timeout=timeout,
        trust_env=False,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    ) as proxied:
        tasks = [one(proxied, u) for u in urls]
        for u, text in await asyncio.gather(*tasks):
            results[u] = text

    retry = [u for u, t in results.items() if t.startswith("抓取失败") and ("ProxyError" in t or "ConnectError" in t)]
    if retry:
        async with httpx.AsyncClient(
            timeout=timeout,
            trust_env=False,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        ) as direct:
            got = await asyncio.gather(*[one(direct, u) for u in retry])
            for u, text in got:
                results[u] = text
    return results


def render_report(run: dict) -> str:
    lines = [
        "# Horizon 适配器运行报告",
        "",
        f"- 运行时间：{run['started_at']}",
        f"- 模式：{'dry-run（未写入任何文件）' if run['dry_run'] else '真实写入'}",
        f"- 输入日报：{run['report_files']}",
        f"- 卡片目录：{run['cards_dir']}",
        f"- 本报告目录：{run['reports_dir']}",
        "",
        "## 各源统计",
        "",
        "| 来源 | 日报条目数 | 新入库 | 跳过(已存在) | 原文抓取失败 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, st in sorted(run["by_source"].items()):
        lines.append(
            f"| {name} | {st['total']} | {st['new']} | {st['skipped']} | {st['fetch_fail']} |"
        )
    totals = run["totals"]
    lines += [
        "",
        f"合计：日报条目 {totals['total']}，新入库 {totals['new']}，"
        f"跳过 {totals['skipped']}，原文抓取失败 {totals['fetch_fail']}。",
        "",
        "## 输出文件",
        "",
    ]
    lines += [f"- {p}" for p in run["outputs"]] or ["-（无新文件）"]
    if run["failures"]:
        lines += ["", "## 失败明细", ""]
        lines += [f"- {f}" for f in run["failures"]]
    lines.append("")
    return "\n".join(lines)


async def main() -> int:
    ap = argparse.ArgumentParser(description="Horizon daily report → Obsidian vault adapter")
    ap.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    ap.add_argument("--vault", default=DEFAULT_VAULT)
    ap.add_argument("--cards-dir", default=None)
    ap.add_argument("--reports-dir", default=None)
    ap.add_argument("--lang", default="zh")
    ap.add_argument("--proxy", default=DEFAULT_PROXY)
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data_dir = Path(args.data_dir).expanduser()
    summaries = sorted((data_dir / "summaries").glob(f"horizon-*-{args.lang}.md"))
    if not summaries:
        print(f"未找到日报：{data_dir / 'summaries'}" f"/horizon-*-{args.lang}.md", file=sys.stderr)
        return 2

    vault = Path(args.vault).expanduser()
    cards_dir = Path(args.cards_dir).expanduser() if args.cards_dir else vault / "00_资源库" / "外部知识"
    reports_dir = (
        Path(args.reports_dir).expanduser() if args.reports_dir else vault / "04_系统维护" / "运行记录"
    )

    now = dt.datetime.now()
    fetched_at = now.strftime("%Y-%m-%d %H:%M:%S")
    run = {
        "started_at": fetched_at,
        "dry_run": args.dry_run,
        "report_files": [str(p) for p in summaries],
        "cards_dir": str(cards_dir),
        "reports_dir": str(reports_dir),
        "by_source": {},
        "totals": {"total": 0, "new": 0, "skipped": 0, "fetch_fail": 0},
        "outputs": [],
        "failures": [],
    }

    items = []
    for path in summaries:
        items.extend(parse_daily_report(path))

    existing_ids = load_existing_ids(cards_dir)
    pending = []
    for item in items:
        card_id = item_id(item["url"])
        st = run["by_source"].setdefault(
            item["source_name"],
            {"total": 0, "new": 0, "skipped": 0, "fetch_fail": 0},
        )
        st["total"] += 1
        run["totals"]["total"] += 1
        fname = card_filename(item)
        target = cards_dir / fname
        if card_id in existing_ids or target.exists():
            st["skipped"] += 1
            run["totals"]["skipped"] += 1
            continue
        existing_ids.add(card_id)
        pending.append((item, card_id, target))

    excerpts: dict[str, str] = {}
    if pending and not args.no_fetch:
        urls = [it["url"] for it, _, _ in pending]
        excerpts = await fetch_excerpt(urls, args.proxy, args.timeout)
    elif pending:
        excerpts = {it["url"]: "抓取失败：本次运行禁用网络抓取（--no-fetch）" for it, _, _ in pending}

    if not args.dry_run:
        cards_dir.mkdir(parents=True, exist_ok=True)
        reports_dir.mkdir(parents=True, exist_ok=True)

    for item, card_id, target in pending:
        st = run["by_source"][item["source_name"]]
        excerpt = excerpts.get(item["url"], "抓取失败：未知原因")
        if excerpt.startswith("抓取失败"):
            st["fetch_fail"] += 1
            run["totals"]["fetch_fail"] += 1
            run["failures"].append(f"{item['source_name']} | {item['title']} | {excerpt}")
        if target.exists():
            target = cards_dir / f"{target.stem}-{card_id[:6]}.md"
        content = render_card(item, card_id, excerpt, fetched_at, Path(summaries[-1]).name)
        if args.dry_run:
            run["outputs"].append(f"[dry-run] {target}")
            print(f"[dry-run] 将写入: {target}")
        else:
            target.write_text(content, encoding="utf-8")
            run["outputs"].append(str(target))
        st["new"] += 1
        run["totals"]["new"] += 1

    report = render_report(run)
    report_path = reports_dir / f"Horizon-运行-{now.strftime('%Y%m%d-%H%M%S')}.md"
    if args.dry_run:
        print(f"[dry-run] 运行报告将写入: {report_path}")
        print("\n" + report)
    else:
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(f"运行报告: {report_path}")
        print(
            f"合计: 条目 {run['totals']['total']} | 新入库 {run['totals']['new']} | "
            f"跳过 {run['totals']['skipped']} | 抓取失败 {run['totals']['fetch_fail']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
