#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第08章 自动运行状态机 runner（教程/08）。

子命令：run / force / resume / status / pause / uninstall
纯标准库实现（py3.9+ 兼容）。设计见 系统/state_machine/DESIGN.md。

路径可用环境变量整体重定向（隔离测试用）：
SM_PROJECT SM_VAULT SM_HORIZON_DIR SM_HORIZON_CONFIG SM_DATA_DIR SM_ADAPTER
SM_ADAPTER_ARGS SM_HORIZON_CMD SM_GBRAIN_CMD SM_PROXY SM_NOW_ISO
SM_MAX_RUNTIME SM_CRASH_POINT
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import random
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")


def env(k, d=""):
    return os.environ.get(k, d)


PROJECT_ROOT = Path(env("SM_PROJECT", str(Path(__file__).resolve().parents[2])))
VAULT = Path(env("SM_VAULT", str(PROJECT_ROOT / "vault")))
HORIZON_DIR = Path(env("SM_HORIZON_DIR", str(Path.home() / "horizon")))
DATA_DIR = Path(env("SM_DATA_DIR", str(HORIZON_DIR / "data")))
HORIZON_CONFIG = env("SM_HORIZON_CONFIG", "")
ADAPTER = Path(env("SM_ADAPTER", str(PROJECT_ROOT / "系统" / "horizon_adapter.py")))
ADAPTER_ARGS = env("SM_ADAPTER_ARGS", "")
HORIZON_CMD = env("SM_HORIZON_CMD", "")
GBRAIN_CMD = env("SM_GBRAIN_CMD", "")
PROXY = env("SM_PROXY", "http://127.0.0.1:7897")
MAX_RUNTIME = int(env("SM_MAX_RUNTIME", "1800"))
NOW_ISO = env("SM_NOW_ISO", "")
CRASH_POINT = env("SM_CRASH_POINT", "")

MAINT = VAULT / "04_系统维护"
STATE_FILE = MAINT / "状态机.json"
LOCK_FILE = MAINT / ".run.lock"
LOG_DIR = MAINT / "运行记录"
MD_STATE = MAINT / "状态.md"
AGENTS_MD = VAULT / "AGENTS.md"
CARDS_DIR = VAULT / "00_资源库" / "外部知识"
CLOSURE_DIR = MAINT / "蒸馏与结案"

HEALTH_A = "<!-- SM-HEALTH v1 -->"
HEALTH_B = "<!-- /SM-HEALTH -->"
MD_BULLET_PREFIX = "- 状态机: "
STAGES = ("ingest", "dedup", "brain_refresh", "verify")
EXIT_OK, EXIT_FAILED, EXIT_LOCKED, EXIT_PAUSED, EXIT_USAGE = 0, 2, 3, 4, 5

CATS_FATAL_NORETRY = {"权限"}


def now_dt() -> dt.datetime:
    if NOW_ISO:
        base = dt.datetime.fromisoformat(NOW_ISO)
        return base if base.tzinfo else base.replace(tzinfo=TZ)
    return dt.datetime.now(TZ)


def iso(x: dt.datetime) -> str:
    return x.isoformat(timespec="seconds")


def rand4() -> str:
    return "%04x" % random.randrange(1 << 16)


def new_run_id() -> str:
    u = dt.datetime.now(dt.timezone.utc)
    return "sm-%s-%s" % (u.strftime("%Y%m%dT%H%M%SZ"), rand4())


def crash_point(name: str):
    if CRASH_POINT == name:
        sys.stderr.write("[CRASH-注入] %s\n" % name)
        sys.stderr.flush()
        os._exit(97)


def atomic_write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp-" + rand4())
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def sha256_text(s: str) -> str:
    return "sha256:" + hashlib.sha256(s.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- 日志

class Log:
    def __init__(self, path: Path):
        self.path = path
        self.f = None

    def open(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.f = open(self.path, "a", encoding="utf-8")

    def __call__(self, cat: str, msg: str):
        line = "%s [%s] %s" % (iso(now_dt()), cat, msg)
        if self.f:
            self.f.write(line + "\n")
            self.f.flush()
        print(line, flush=True)


# ---------------------------------------------------------------- 状态机文件

def fresh_state() -> dict:
    return {
        "schema": 1,
        "state": "idle",
        "paused": False,
        "updated_at": iso(now_dt()),
        "install": {"backups_done": False},
        "run": None,
        "last_success": None,
        "pending_backfill": None,
        "history": [],
    }


def load_state() -> dict:
    try:
        st = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return fresh_state()
    except Exception:
        return fresh_state()
    base = fresh_state()
    for k, v in base.items():
        st.setdefault(k, v)
    return st


def save_state(st: dict):
    st["updated_at"] = iso(now_dt())
    atomic_write(STATE_FILE, json.dumps(st, ensure_ascii=False, indent=1))


def vault_md_listing() -> list:
    out = []
    if VAULT.exists():
        for p in sorted(VAULT.rglob("*.md")):
            out.append(str(p.relative_to(VAULT)))
    return out


def cards_listing() -> list:
    out = []
    if CARDS_DIR.exists():
        for p in sorted(CARDS_DIR.glob("*.md")):
            out.append(p.name)
    return out


def card_id_of(path: Path):
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:2000]
        m = re.search(r"^id:\s*(\S+)", head, re.M)
        return m.group(1).strip("\"'") if m else None
    except Exception:
        return None


def scan_card_ids() -> dict:
    ids = {}
    if CARDS_DIR.exists():
        for p in sorted(CARDS_DIR.glob("*.md")):
            cid = card_id_of(p)
            if cid:
                ids.setdefault(cid, []).append(p.name)
    return ids


def find_closure(target_date: str):
    """R7：同目标日合法结案（status: closed）。今日结案还需 24h 内。"""
    if not CLOSURE_DIR.exists():
        return None
    today = now_dt().date().isoformat()
    best = None
    for p in sorted(CLOSURE_DIR.glob("结案-%s-*.md" % target_date)):
        try:
            head = p.read_text(encoding="utf-8", errors="replace")[:800]
        except Exception:
            continue
        m = re.search(r"""^status:\s*["']?([A-Za-z_]+)["']?""", head, re.M)
        if not m or m.group(1) != "closed":
            continue
        if target_date == today and time.time() - p.stat().st_mtime > 86400:
            continue
        best = p
    return best


# ---------------------------------------------------------------- 健康块与 状态.md

def render_health(st: dict) -> str:
    run = st.get("run") or {}
    if run:
        prog = run.get("stage_progress") or {}
        stages = " ".join(
            "%s=%s" % (k, (prog.get(k) or {}).get("status", "-")) for k in STAGES
        )
        core = (
            "状态机: %s | run: %s | 目标日: %s | 窗口: %sh\n"
            "阶段: %s\n最后成功: %s\n更新: %s | 日志: 04_系统维护/运行记录/%s"
            % (
                st["state"], run.get("run_id", "-"), run.get("target_date", "-"),
                run.get("window_hours", "-"), stages,
                (st.get("last_success") or {}).get("target_date", "无"),
                st["updated_at"], Path(str(run.get("log_file", "-"))).name,
            )
        )
    else:
        core = (
            "状态机: %s | 最后成功: %s\n更新: %s"
            % (st["state"], (st.get("last_success") or {}).get("target_date", "无"),
               st["updated_at"])
        )
    return "%s\n%s\n%s" % (HEALTH_A, core, HEALTH_B)


def write_health_block(st: dict):
    if not AGENTS_MD.exists():
        AGENTS_MD.parent.mkdir(parents=True, exist_ok=True)
        AGENTS_MD.write_text("", encoding="utf-8")
    text = AGENTS_MD.read_text(encoding="utf-8")
    block = render_health(st)
    pat = re.compile(re.escape(HEALTH_A) + r".*?" + re.escape(HEALTH_B), re.S)
    if pat.search(text):
        text = pat.sub(lambda _: block, text, count=1)
    else:
        text = text.rstrip("\n") + "\n\n" + block + "\n"
    atomic_write(AGENTS_MD, text)


def strip_health_block():
    if not AGENTS_MD.exists():
        return
    text = AGENTS_MD.read_text(encoding="utf-8")
    pat = re.compile(re.escape(HEALTH_A) + r".*?" + re.escape(HEALTH_B) + r"\n?", re.S)
    text = pat.sub("", text, count=1)
    atomic_write(AGENTS_MD, text.rstrip("\n") + "\n")


def render_md_bullet(st: dict) -> str:
    run = st.get("run") or {}
    if not run:
        return "%sidle（无活动轮次）" % MD_BULLET_PREFIX
    tail = ""
    if st["state"] == "mechanical_ok":
        tail = " 待 agent 蒸馏接力（不自动执行）"
    elif st["state"] == "failed":
        tail = " 待 resume（恢复点已保留）"
    return "%s%s（run_id=%s, 目标日=%s）%s；日志 04_系统维护/运行记录/%s" % (
        MD_BULLET_PREFIX, st["state"], run.get("run_id", "-"),
        run.get("target_date", "-"), tail, Path(str(run.get("log_file", "-"))).name,
    )


def write_md_bullet(st: dict):
    if not MD_STATE.exists():
        return
    lines = MD_STATE.read_text(encoding="utf-8").splitlines()
    bullet = render_md_bullet(st)
    out, replaced = [], False
    for ln in lines:
        if ln.startswith(MD_BULLET_PREFIX):
            out.append(bullet)
            replaced = True
        else:
            out.append(ln)
    if not replaced:
        for i, ln in enumerate(out):
            if ln.strip() == "## 下一步":
                out.insert(i + 1, bullet)
                replaced = True
                break
        if not replaced:
            out.append("")
            out.append(bullet)
    atomic_write(MD_STATE, "\n".join(out) + "\n")


def strip_md_bullet():
    if not MD_STATE.exists():
        return
    lines = MD_STATE.read_text(encoding="utf-8").splitlines()
    out = [ln for ln in lines if not ln.startswith(MD_BULLET_PREFIX)]
    atomic_write(MD_STATE, "\n".join(out) + "\n")


def sync_health(st: dict, log: Log):
    save_state(st)
    try:
        write_health_block(st)
        write_md_bullet(st)
    except PermissionError:
        log("权限", "健康块/状态.md 写入被拒绝")
        raise


# ---------------------------------------------------------------- 锁

def pid_alive(pid) -> bool:
    try:
        os.kill(int(pid), 0)
        return True
    except (ProcessLookupError, TypeError, ValueError):
        return False
    except PermissionError:
        return True


def lock_payload(run_id: str) -> str:
    return json.dumps({
        "pid": os.getpid(), "run_id": run_id,
        "created_unix": int(time.time()), "host": os.uname().nodename,
    })


def acquire_lock(run_id: str, log: Log):
    """flock 内核级单实例锁（R2）。返回：
    - dict{fd, payload}：持锁成功
    - str：忙（对方信息，立即退出）
    进程死亡（kill -9）时内核自动释放 flock——残留锁文件可被直接接管，无 TOCTOU 竞态。
    存活但超时的持有者不抢（flock 语义）：报告并退出，由用户/agent 处理僵死进程。
    """
    import fcntl
    MAINT.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        try:
            os.lseek(fd, 0, 0)
            cur = json.loads(os.read(fd, 65536).decode("utf-8") or "{}")
        except Exception:
            cur = {}
        os.close(fd)
        return "另一实例运行中：run_id=%s pid=%s（flock 持有中；若确认僵死可 kill 后重试）" % (
            cur.get("run_id", "?"), cur.get("pid", "?"))
    try:
        os.lseek(fd, 0, 0)
        old = json.loads(os.read(fd, 65536).decode("utf-8") or "{}")
        if old and not pid_alive(old.get("pid")):
            log("锁", "接管残留锁：前持有 pid=%s（run_id=%s）已退出，flock 已随进程释放"
                % (old.get("pid"), old.get("run_id")))
    except Exception:
        pass
    payload = lock_payload(run_id)
    os.ftruncate(fd, 0)
    os.lseek(fd, 0, 0)
    os.write(fd, payload.encode("utf-8"))
    return {"fd": fd, "payload": payload}


def release_lock(holder, run_id: str, log: Log):
    import fcntl
    if not isinstance(holder, dict):
        return
    try:
        fcntl.flock(holder["fd"], fcntl.LOCK_UN)
    except Exception:
        pass
    try:
        os.close(holder["fd"])
    except Exception:
        pass
    try:
        cur = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
        if cur.get("run_id") == run_id:
            LOCK_FILE.unlink()
            log("锁", "已释放（run_id=%s）" % run_id)
        else:
            log("锁", "锁已被其它实例持有（%s），仅释放 flock 不删文件" % cur.get("run_id"))
    except FileNotFoundError:
        pass
    except Exception as e:
        log("锁", "释放收尾异常：%s" % e)


# ---------------------------------------------------------------- 备份（R13）

def backup_before_install(run_id: str, log: Log):
    bdir = LOG_DIR / ("状态机-备份-%s-%s" % (now_dt().date().isoformat(), run_id))
    bdir.mkdir(parents=True, exist_ok=True)
    for src in (AGENTS_MD, MD_STATE):
        if src.exists():
            dst = bdir / src.name
            if not dst.exists():
                dst.write_bytes(src.read_bytes())
    log("调度", "实现前备份完成：%s" % bdir.name)
    return bdir


# ---------------------------------------------------------------- 阶段实现

def budget_left(deadline: float) -> float:
    return deadline - time.time()


def classify_exception(e: Exception) -> str:
    if isinstance(e, PermissionError):
        return "权限"
    if isinstance(e, subprocess.TimeoutExpired):
        return "运行时"
    if isinstance(e, FileNotFoundError):
        return "依赖"
    return "运行时"


def hardened_env() -> dict:
    """PATH 前缀 ~/.bun/bin 与 ~/.local/bin（gbrain/uv 在用户级 bin）。"""
    env2 = os.environ.copy()
    extra = [str(Path.home() / ".bun" / "bin"), str(Path.home() / ".local" / "bin")]
    env2["PATH"] = os.pathsep.join(extra + [env2.get("PATH", "")])
    return env2


def run_horizon(window_hours: int, deadline: float, log: Log):
    """返回 (ok, classification, detail)。单源失败=上游告警不致命；AI失败=致命上游。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "summaries").mkdir(parents=True, exist_ok=True)
    if HORIZON_CMD:
        cmd = shlex.split(HORIZON_CMD)
    else:
        cmd = ["uv", "run", "horizon"]
    cmd += ["--hours", str(window_hours), "-d", str(DATA_DIR), "-l", "INFO"]
    if HORIZON_CONFIG:
        cmd += ["-c", HORIZON_CONFIG]
    env2 = hardened_env()
    for k in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"):
        env2.setdefault(k, PROXY)
    for k in ("NO_PROXY", "no_proxy"):
        env2.setdefault(k, "api.deepseek.com,localhost,127.0.0.1")
    log("阶段", "horizon 抓取：--hours=%d%s" % (window_hours, (" -c " + HORIZON_CONFIG) if HORIZON_CONFIG else ""))
    left = max(30, budget_left(deadline))
    try:
        pr = subprocess.run(
            cmd, cwd=str(HORIZON_DIR), env=env2, capture_output=True,
            text=True, timeout=left)
    except subprocess.TimeoutExpired:
        return False, "运行时", "horizon 超时（剩余预算 %.0fs 耗尽）" % left
    except FileNotFoundError as e:
        return False, "依赖", "horizon 命令不存在：%s" % e
    except PermissionError as e:
        return False, "权限", "horizon 启动被拒：%s" % e
    err = (pr.stderr or "") + "\n" + (pr.stdout or "")
    ai_fail = False
    for ln in err.splitlines():
        if "Error fetching" in ln or "不可达" in ln or "403" in ln:
            log("上游", "源失败（不致命）：%s" % ln.strip()[:200])
        if re.search(r"(AuthenticationError|api[_ ]?key|ApiKey)", ln, re.I) and "ERROR" in ln:
            log("上游", "AI 调用失败（致命，不假成功）：%s" % ln.strip()[:200])
            ai_fail = True
        if re.search(r"(ProxyError|ConnectError|SSLError|timeout)", ln, re.I) and ("WARNING" in ln or "ERROR" in ln):
            log("网络", "网络类告警：%s" % ln.strip()[:200])
    if pr.returncode != 0:
        return False, "运行时", "horizon 退出码 %d" % pr.returncode
    if ai_fail:
        return False, "上游", "Horizon AI 摘要失败（占位日报不冒充成功；窗口可回溯，恢复后重跑补回）"
    return True, "-", "horizon 完成（窗口 %dh）" % window_hours


def run_adapter(deadline: float, log: Log):
    cmd = ["uv", "run", "python", str(ADAPTER),
           "--data-dir", str(DATA_DIR), "--vault", str(VAULT)]
    if ADAPTER_ARGS:
        cmd += shlex.split(ADAPTER_ARGS)
    left = max(30, budget_left(deadline))
    log("阶段", "适配器入库（幂等判重：frontmatter id）")
    try:
        pr = subprocess.run(cmd, cwd=str(HORIZON_DIR), env=hardened_env(),
                            capture_output=True, text=True, timeout=left)
    except subprocess.TimeoutExpired:
        return False, "运行时", "适配器超时（剩余预算 %.0fs 耗尽）" % left
    except FileNotFoundError as e:
        return False, "依赖", "适配器/uv 不存在：%s" % e
    for ln in (pr.stdout or "").splitlines():
        if ln.startswith("合计:"):
            log("阶段", "适配器：%s" % ln.strip())
    if pr.returncode != 0:
        detail = (pr.stderr or pr.stdout or "").strip().splitlines()
        return False, "运行时" if pr.returncode == 1 else "数据", \
            "适配器退出码 %d：%s" % (pr.returncode, detail[-1][:200] if detail else "")
    return True, "-", "适配器完成"


def stage_ingest(st: dict, deadline: float, log: Log):
    ok, cls, detail = run_horizon(st["run"]["window_hours"], deadline, log)
    if not ok:
        return ok, cls, detail
    ok, cls, detail = run_adapter(deadline, log)
    if not ok:
        return ok, cls, detail
    run = st["run"]
    pre = set(run["input_manifest"]["pre_cards"])
    cur = cards_listing()
    new_cards = [c for c in cur if c not in pre]
    ids = []
    for c in new_cards:
        cid = card_id_of(CARDS_DIR / c)
        if cid:
            ids.append(cid)
    summaries = sorted(p.name for p in (DATA_DIR / "summaries").glob("horizon-*-zh.md"))
    run["frozen_batch"] = {"cards": new_cards, "ids": ids, "summaries": summaries}
    log("阶段", "ingest 完成：本轮新卡 %d 张（幂等判重后）" % len(new_cards))
    return True, "-", "新卡 %d" % len(new_cards)


def stage_dedup(st: dict, deadline: float, log: Log):
    ids = scan_card_ids()
    dups = {k: v for k, v in ids.items() if len(v) > 1}
    if dups:
        for k, v in list(dups.items())[:10]:
            log("数据", "重复 id 告警（只报告不删除，留 agent 裁决）：%s → %s" % (k, v))
    missing = [c for c in st["run"]["frozen_batch"]["cards"] if not (CARDS_DIR / c).exists()]
    if missing:
        return False, "数据", "冻结清单卡片缺失：%s" % missing[:5]
    log("阶段", "dedup 完成：id 总数 %d，重复 %d 组" % (len(ids), len(dups)))
    return True, "-", "重复 %d 组" % len(dups)


def gbrain_env() -> dict:
    return hardened_env()


def stage_brain_refresh(st: dict, deadline: float, log: Log):
    if GBRAIN_CMD:
        cmd = shlex.split(GBRAIN_CMD) + ["import", str(VAULT), "--no-embed"]
    else:
        cmd = ["gbrain", "import", str(VAULT), "--no-embed"]
    left = max(30, budget_left(deadline))
    log("阶段", "gbrain import --no-embed（本地，无 embedding）")
    try:
        pr = subprocess.run(cmd, env=gbrain_env(), capture_output=True, text=True,
                            timeout=left)
    except subprocess.TimeoutExpired:
        return False, "运行时", "gbrain 超时（剩余预算 %.0fs 耗尽）" % left
    except FileNotFoundError:
        return False, "依赖", "gbrain 命令不存在（PATH 需含 ~/.bun/bin 或设 SM_GBRAIN_CMD）"
    except PermissionError as e:
        return False, "权限", "gbrain 启动被拒：%s" % e
    if pr.returncode != 0:
        tail = (pr.stderr or pr.stdout or "").strip().splitlines()
        return False, "依赖", "gbrain 退出码 %d：%s" % (
            pr.returncode, tail[-1][:200] if tail else "")
    for ln in (pr.stdout or "").splitlines():
        if re.search(r"\b\d+/\d+\b", ln):
            log("阶段", "gbrain：%s" % ln.strip()[:160])
            break
    return True, "-", "gbrain import 完成"


def stage_verify(st: dict, deadline: float, log: Log):
    run = st["run"]
    missing = [c for c in run["frozen_batch"]["cards"] if not (CARDS_DIR / c).exists()]
    if missing:
        return False, "数据", "verify：卡片缺失 %s" % missing[:5]
    ids = scan_card_ids()
    dups = [k for k, v in ids.items() if len(v) > 1]
    if dups:
        log("数据", "verify：存量重复 id %d 组（历史遗留，登记不阻断）" % len(dups))
    log_file = Path(run["log_file"])
    if not log_file.exists():
        return False, "数据", "verify：日志文件缺失"
    closure = find_closure(run["target_date"])
    if closure:
        if MD_STATE.exists():
            text = MD_STATE.read_text(encoding="utf-8")
            m = re.search(r"^- last_closure:\s*(\S+)", text, re.M)
            rel = "04_系统维护/蒸馏与结案/" + closure.name
            if m and m.group(1).strip() != rel:
                log("规则冲突", "状态.md last_closure(%s) 与结案文件(%s)不一致，登记待 agent 核对"
                    % (m.group(1), rel))
            else:
                log("状态", "四方一致：同目标日合法结案 %s 与 状态.md 相符" % closure.name)
    log("阶段", "verify 完成（卡片/日志/结案一致性检查通过）")
    return True, "-", "verify ok"


STAGE_FUNCS = {
    "ingest": stage_ingest,
    "dedup": stage_dedup,
    "brain_refresh": stage_brain_refresh,
    "verify": stage_verify,
}

RETRYABLE = {"网络", "运行时", "依赖", "上游"}


def run_stages(st: dict, deadline: float, log: Log, reset_attempts=False) -> bool:
    run = st["run"]
    for name in STAGES:
        prog = run["stage_progress"][name]
        if prog["status"] == "ok":
            log("恢复", "阶段 %s 已完成，跳过（恢复点生效）" % name)
            continue
        if reset_attempts:
            prog["attempts"] = 0
            log("恢复", "阶段 %s 尝试计数重置（新一轮 attempt）" % name)
        log("阶段", "开始 %s（第 %d 次尝试）" % (name, prog["attempts"] + 1))
        while prog["attempts"] < 3:  # 初始1 + 重试≤2
            prog["attempts"] += 1
            try:
                ok, cls, detail = STAGE_FUNCS[name](st, deadline, log)
            except Exception as e:  # noqa: BLE001
                ok, cls, detail = False, classify_exception(e), "%s: %s" % (type(e).__name__, e)
            if ok:
                prog.update({"status": "ok", "class": "-", "detail": detail})
                save_state(st)
                log("阶段", "%s ok：%s" % (name, detail))
                break
            prog.update({"status": "failed", "class": cls, "detail": detail})
            save_state(st)
            log(cls, "阶段 %s 失败（第 %d 次）：%s" % (name, prog["attempts"], detail))
            if cls not in RETRYABLE or prog["attempts"] >= 3:
                break
            if budget_left(deadline) < 60:
                log("运行时", "剩余预算不足 60s，停止重试")
                break
            log("阶段", "%s 将重试（重试≤2 次）" % name)
        if prog["status"] != "ok":
            run["stage_progress"]["__failed__"] = {"stage": name, "class": prog["class"]}
            return False
        if budget_left(deadline) < 30:
            nxt = STAGES[STAGES.index(name) + 1] if name != "verify" else None
            if nxt:
                log("运行时", "预算耗尽，停在恢复点 %s 之后" % name)
                run["stage_progress"]["__failed__"] = {"stage": nxt, "class": "运行时", "detail": "预算耗尽"}
                return False
    return True


# ---------------------------------------------------------------- 轮次调度决策

def compute_window(st: dict, log: Log) -> tuple:
    """返回 (window_hours, is_backfill, gap_days)。R1/R6。"""
    ls = st.get("last_success")
    today = now_dt().date()
    if not ls or not ls.get("target_date"):
        log("调度", "无上次成功记录，窗口取默认 26h")
        return 26, False, None
    try:
        last_day = dt.date.fromisoformat(ls["target_date"])
    except Exception:
        return 26, False, None
    gap = (today - last_day).days
    try:
        fin = dt.datetime.fromisoformat(ls["finished_at"])
        hours_since = max(1, (now_dt() - fin).total_seconds() / 3600.0)
    except Exception:
        hours_since = 26.0
    if gap >= 2:
        w = int(hours_since) + 2
        log("调度", "补跑：距上次成功(%s) %d 天，合并错过的天数为一轮，窗口=%.0f+2=%dh（只补一次，非故障）"
            % (ls["target_date"], gap, hours_since, w))
        return w, True, gap
    w = max(26, int(hours_since) + 2)
    log("调度", "常规轮：距上次成功 %.1fh，窗口=%dh" % (hours_since, w))
    return w, False, gap


def should_skip(st: dict, target_date: str, log: Log):
    """返回 (skip, reason)。R7 + 同日接力检查。"""
    closure = find_closure(target_date)
    if closure:
        return True, "24h内同目标日已有合法结案：%s（R7 跳过）" % closure.name
    run = st.get("run")
    if run and run.get("target_date") == target_date and st["state"] == "mechanical_ok":
        return True, "今日机械轮已完成（mechanical_ok），待 agent 蒸馏接力，不重复开轮"
    ls = st.get("last_success")
    if ls and ls.get("target_date") == target_date and st["state"] in (
            "mechanical_ok", "closed_knowledge", "closed_drop", "evolved", "promoted", "draft_pending"):
        return True, "目标日 %s 已有成功轮次（状态 %s）" % (target_date, st["state"])
    return False, ""


def archive_stale_run(st: dict, log: Log):
    run = st.get("run")
    if not run:
        return
    log("调度", "归档上一轮（%s, 目标日 %s，状态 %s）：冻结批次 %d 张卡保留在 00_资源库，agent 可继续接力"
        % (run.get("run_id"), run.get("target_date"), st["state"], len((run.get("frozen_batch") or {}).get("cards", []))))
    st["history"].insert(0, {
        "run_id": run.get("run_id"), "target_date": run.get("target_date"),
        "state": st["state"], "archived_at": iso(now_dt()),
        "cards": (run.get("frozen_batch") or {}).get("cards", []),
    })
    del st["history"][20:]
    st["run"] = None


def start_run(st: dict, target_date: str, run_id: str, deadline: float, log: Log,
              window_hours: int = None, resume_from: dict = None):
    if resume_from:
        st["run"] = resume_from
        st["run"]["attempt_of"] = resume_from.get("run_id")
        st["run"]["run_id"] = run_id
        st["run"]["log_file"] = str(log.path)
        st["run"]["budget_deadline_unix"] = int(deadline)
        log("恢复", "resume：沿用原输入清单 hash=%s（不重新冻结）与恢复点 %s"
            % (st["run"]["input_manifest_hash"][:19],
               {k: st["run"]["stage_progress"].get(k, {}).get("status") for k in STAGES}))
    else:
        listing = vault_md_listing()
        pre_cards = cards_listing()
        manifest = {
            "target_date": target_date,
            "window_hours": window_hours,
            "pre_md_count": len(listing),
            "pre_listing_sha256": sha256_text("\n".join(listing)),
            "pre_cards": pre_cards,
            "horizon_config": Path(HORIZON_CONFIG).name if HORIZON_CONFIG else "default",
            "data_dir": str(DATA_DIR),
        }
        st["run"] = {
            "run_id": run_id,
            "target_date": target_date,
            "window_hours": window_hours,
            "attempt_of": None,
            "input_manifest_hash": sha256_text(json.dumps(manifest, sort_keys=True, ensure_ascii=False)),
            "input_manifest": manifest,
            "frozen_batch": {"cards": [], "ids": [], "summaries": []},
            "stage_progress": {k: {"status": "pending", "attempts": 0} for k in STAGES},
            "started_at": iso(now_dt()),
            "log_file": str(log.path),
            "budget_deadline_unix": int(deadline),
        }
        log("调度", "冻结输入清单：目标日=%s 窗口=%dh 运行前 md=%d 清单hash=%s"
            % (target_date, window_hours, manifest["pre_md_count"],
               st["run"]["input_manifest_hash"][:19]))
    st["state"] = "running"
    save_state(st)


def finalize_ok(st: dict, log: Log):
    run = st["run"]
    st["state"] = "mechanical_ok"
    run["finished_at"] = iso(now_dt())
    st["last_success"] = {
        "run_id": run["run_id"], "target_date": run["target_date"],
        "finished_at": run["finished_at"], "kind": "mechanical",
    }
    save_state(st)
    crash_point("before_mechanical_health")
    try:
        write_health_block(st)
        write_md_bullet(st)
    except PermissionError:
        log("权限", "mechanical_ok 收尾写入被拒绝")
        raise
    log("状态", "mechanical_ok：机械阶段完成，待 agent 蒸馏接力（不自动蒸馏/结案，不冒充正式成功）")


def finalize_failed(st: dict, log: Log):
    st["state"] = "failed"
    f = (st["run"].get("stage_progress") or {}).get("__failed__") or {}
    log("状态", "failed：阶段=%s 分类=%s；恢复点已保留，可 resume" % (
        f.get("stage", "-"), f.get("class", "-")))
    save_state(st)
    try:
        write_health_block(st)
        write_md_bullet(st)
    except PermissionError:
        log("权限", "failed 收尾写入被拒绝")


# ---------------------------------------------------------------- 子命令

def cmd_run(st, log_factory, target_date, force, allow_closed, resume_mode=False):
    today = now_dt().date().isoformat()
    if not target_date:
        target_date = today
    if st.get("paused") and not force:
        print("已暂停（paused=true）。恢复请用 resume，或 force 强制。")
        return EXIT_PAUSED

    run_id = new_run_id()
    log = log_factory(target_date, run_id)
    log.open()
    holder = acquire_lock(run_id, log)
    if isinstance(holder, str):
        log("锁", "拒绝启动：%s" % holder)
        print("单实例锁：%s" % holder)
        return EXIT_LOCKED

    try:
        if not st["install"]["backups_done"]:
            bdir = backup_before_install(run_id, log)
            st["install"]["backups_done"] = True
            st["install"]["backup_dir"] = str(bdir)
            save_state(st)

        prev = st.get("run")
        prev_state = st["state"]

        # resume 三种入口：显式 resume / 同日 failed 自动续 / 同日 running 残留（配合锁接管）
        same_day_pending = prev and prev.get("target_date") == target_date and prev_state in ("failed", "running")
        if (resume_mode or same_day_pending) and prev:
            if prev_state == "mechanical_ok":
                log("恢复", "已是 mechanical_ok，仅补齐一致性视图（幂等，不产生第二份）")
                write_health_block(st)
                write_md_bullet(st)
                return EXIT_OK
            log("恢复", "从恢复点续跑：前次 %s（run_id=%s）→ 新 attempt %s"
                % (prev_state, prev.get("run_id"), run_id))
            deadline = time.time() + MAX_RUNTIME
            start_run(st, target_date, run_id, deadline, log, resume_from=prev)
            ok = run_stages(st, deadline, log, reset_attempts=True)
            if ok:
                finalize_ok(st, log)
            else:
                finalize_failed(st, log)
            return EXIT_OK if ok else EXIT_FAILED
        if resume_mode and not prev:
            log("恢复", "无可恢复轮次（run=null），按新轮次执行")

        skip, reason = should_skip(st, target_date, log)
        if skip:
            if allow_closed and "合法结案" in reason:
                log("调度", "--allow-closed：越过 R7 结案跳过（用户显式授权重跑）")
            else:
                log("调度", "跳过：%s" % reason)
                st["pending_backfill"] = None
                save_state(st)
                try:
                    write_health_block(st)
                    write_md_bullet(st)
                except PermissionError:
                    log("权限", "健康块写入被拒")
                return EXIT_OK

        if prev and prev.get("target_date") != target_date:
            archive_stale_run(st, log)

        window, is_backfill, gap = compute_window(st, log)
        st["pending_backfill"] = {"merged_days": gap} if is_backfill else None
        deadline = time.time() + MAX_RUNTIME
        start_run(st, target_date, run_id, deadline, log, window_hours=window)
        ok = run_stages(st, deadline, log)
        if ok:
            finalize_ok(st, log)
        else:
            finalize_failed(st, log)
        return EXIT_OK if ok else EXIT_FAILED
    finally:
        release_lock(holder, run_id, log)


def cmd_status(st):
    run = st.get("run") or {}
    print("状态机: %s%s" % (st["state"], "（paused）" if st.get("paused") else ""))
    print("更新: %s" % st["updated_at"])
    if run:
        print("run_id: %s  目标日: %s  窗口: %sh" % (
            run.get("run_id"), run.get("target_date"), run.get("window_hours")))
        print("输入清单hash: %s" % run.get("input_manifest_hash"))
        print("冻结批次: %d 张卡" % len((run.get("frozen_batch") or {}).get("cards", [])))
        for k in STAGES:
            p = (run.get("stage_progress") or {}).get(k) or {}
            print("  %-13s %-7s 尝试%d %s" % (k, p.get("status", "-"), p.get("attempts", 0),
                                              p.get("detail", "")[:80]))
        print("日志: %s" % run.get("log_file"))
    ls = st.get("last_success")
    if ls:
        print("上次成功: %s（%s, %s）" % (ls.get("target_date"), ls.get("kind"), ls.get("finished_at")))
    lk = None
    try:
        lk = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    print("锁: %s" % (("run_id=%s pid=%s alive=%s" % (lk.get("run_id"), lk.get("pid"),
                                                      pid_alive(lk.get("pid")))) if lk else "无"))
    return EXIT_OK


def cmd_pause(st):
    st["paused"] = True
    save_state(st)
    print("已暂停：新的 run 将被拒绝（force 可越过；resume 解除）。")
    return EXIT_OK


def cmd_uninstall(st, log_blank):
    made = []
    if AGENTS_MD.exists():
        strip_health_block()
        made.append("vault/AGENTS.md 健康块已移除")
    if MD_STATE.exists():
        strip_md_bullet()
        made.append("状态.md 托管行已移除")
    if STATE_FILE.exists():
        bdir = LOG_DIR / ("状态机-卸载备份-%s" % now_dt().strftime("%Y%m%d-%H%M%S"))
        bdir.mkdir(parents=True, exist_ok=True)
        (bdir / "状态机.json").write_text(STATE_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        STATE_FILE.unlink()
        made.append("状态机.json 已删除（卸载前快照存 运行记录/%s）" % bdir.name)
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()
        made.append(".run.lock 已删除")
    for m in made:
        print("- %s" % m)
    print("卸载完成：运行日志（运行记录/状态机-*.log）与其它文件一律保留。")
    return EXIT_OK


def main():
    ap = argparse.ArgumentParser(description="第08章 自动运行状态机")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run", help="每日轮（目标日=今天，Asia/Shanghai）")
    p_run.add_argument("--date", dest="date", default=None, help="目标日 YYYY-MM-DD（补跑）")
    p_force = sub.add_parser("force", help="强制轮（越过 paused；R7 仍生效）")
    p_force.add_argument("--date", dest="date", default=None)
    p_force.add_argument("--allow-closed", dest="allow_closed", action="store_true",
                         help="显式越过 R7 结案跳过")
    p_res = sub.add_parser("resume", help="从恢复点续跑")
    p_res.add_argument("--date", dest="date", default=None)
    sub.add_parser("status", help="查看状态")
    sub.add_parser("pause", help="暂停")
    sub.add_parser("uninstall", help="卸载（只删自身文件与标记）")
    args = ap.parse_args()

    st = load_state()

    if args.cmd == "status":
        return cmd_status(st)
    if args.cmd == "pause":
        return cmd_pause(st)
    if args.cmd == "uninstall":
        return cmd_uninstall(st, None)

    def log_factory(target_date, run_id):
        return Log(LOG_DIR / ("状态机-%s-%s.log" % (target_date, run_id)))

    if args.cmd == "resume":
        return cmd_run(st, log_factory, args.date, force=True,
                       allow_closed=False, resume_mode=True)
    if args.cmd == "run":
        return cmd_run(st, log_factory, args.date, force=False, allow_closed=False)
    return cmd_run(st, log_factory, args.date, force=True,
                   allow_closed=args.allow_closed)


if __name__ == "__main__":
    sys.exit(main())
