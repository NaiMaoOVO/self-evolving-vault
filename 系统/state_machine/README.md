# 第08章 自动运行状态机 — README

> 施工依据：`教程/08-自动运行状态机与故障恢复.md`
> 设计文档：`系统/state_machine/DESIGN.md`
> 主代码：`系统/state_machine/runner.py`（纯标准库，py3.9+ 兼容）

## 需求编号表

| 编号 | 需求 | 实现状态 |
| --- | --- | --- |
| R1 | 调度每日一轮，目标日=自然日 Asia/Shanghai；支持 `--date YYYY-MM-DD` 补跑 | ✅ `compute_window()` + `--date` 参数 |
| R2 | 单实例文件锁，第二实例退出 | ✅ flock `LOCK_EX\|LOCK_NB`，退出码 3 |
| R3 | 启动写 run_id(UTC+随机)、目标日、输入清单sha256、恢复点 | ✅ `start_run()` 冻结清单+hash+stage_progress |
| R4 | 各阶段幂等，重跑无副本 | ✅ 适配器 frontmatter id 判重 + stage_progress 跳过 |
| R5 | 中断后 resume 从恢复点续，不从头 | ✅ `run_stages(reset_attempts=True)` 跳过已完成阶段 |
| R6 | 关机/agent未开只记"待补跑"不判故障；合并错过天数为单轮 | ✅ `compute_window()` gap≥2 → 补跑，窗口=hours+2，日志"非故障" |
| R7 | 24h内同目标日已有合法结案则 skip | ✅ `find_closure()` + `should_skip()` |
| R8 | 最大运行时长30分钟、每阶段重试≤2次、停止条件明确 | ✅ `budget_deadline` + `attempts<3` + 停止条件枚举 |
| R9 | 日志按 网络/权限/运行时/依赖/上游/数据/规则冲突 分类 | ✅ `Log(cat, msg)` 七类故障 + 过程标签 |
| R10 | 状态机文件 + AGENTS健康块 + 运行记录 + 主结案 四方一致 | ✅ `sync_health()` 原子写三视图 + verify 检查结案 |
| R11 | 自动轮只做机械阶段，mechanical_ok 后停；不外发不删除不高成本 | ✅ 白名单：horizon+adapter+gbrain import --no-embed |
| R12 | 命令：run/resume/status/pause/uninstall/force --date | ✅ argparse 子命令 |
| R13 | 实现前备份；测试用隔离样本 | ✅ `backup_before_install()` + 隔离测试目录 |
| R14 | 通过标准：同一输入最多一个结案；中断不重复；滞后≠故障；mechanical_ok≠正式成功 | ✅ 全部故障注入测试通过 |

## 状态转移图

```
                    ┌─────────────────────────── agent/用户接力（不自动） ──────────────────────────┐
                    │                                                                          │
 idle ──run/resume──▶ running ──机械阶段全ok──▶ mechanical_ok ──agent蒸馏──▶ draft_pending ──用户审──▶ promoted
   ▲                  │   ▲                        │                        │
   │                  │   └── resume（从恢复点）     ├─规则升级+对照测试──────▶ evolved
   │                  ▼                            │                        ▼
   └──uninstall/归档── failed（带分类与恢复点）        └────────── 结案 ──▶ closed_knowledge / closed_drop
```

- **自动层**只驱动 `idle → running → mechanical_ok | failed`，以及 failed 的 resume。
- `draft_pending / promoted / closed_* / evolved` 由 agent/用户推进，状态机文件记录但不自动触发。
- `paused` 是布尔标志（非教程状态），true 时拒绝新自动 run，force 可越过。

## 命令手册

```bash
# 每日轮（目标日=今天 Asia/Shanghai）
python3 系统/state_machine/runner.py run

# 指定日期补跑
python3 系统/state_machine/runner.py run --date 2026-08-20

# 强制轮（越过 paused；R7 仍生效）
python3 系统/state_machine/runner.py force --date 2026-08-22

# 显式越过 R7 结案跳过（需用户授权）
python3 系统/state_machine/runner.py force --date 2026-08-22 --allow-closed

# 从恢复点续跑（failed/running 残留自动触发）
python3 系统/state_machine/runner.py resume

# 查看状态
python3 系统/state_machine/runner.py status

# 暂停（拒绝新自动轮；force 可越过）
python3 系统/state_machine/runner.py pause

# 卸载（只删 状态机.json/锁/健康块/托管行；日志与其它文件保留）
python3 系统/state_machine/runner.py uninstall
```

### 退出码

| 码 | 含义 |
| --- | --- |
| 0 | 成功 / 跳过 / mechanical_ok |
| 2 | 阶段失败（failed，可 resume） |
| 3 | 单实例锁拒绝 |
| 4 | 已暂停（paused） |
| 5 | 用法错误 |

### 环境变量（隔离测试用）

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `SM_PROJECT` | runner.py 上上两级 | 工程根 |
| `SM_VAULT` | `$SM_PROJECT/vault` | vault 路径 |
| `SM_HORIZON_DIR` | `~/horizon` | Horizon 工作目录（adapter 的 venv 来源） |
| `SM_DATA_DIR` | `$SM_HORIZON_DIR/data` | Horizon 数据目录 |
| `SM_HORIZON_CONFIG` | （空=默认） | Horizon 配置文件路径 |
| `SM_HORIZON_CMD` | （空=`uv run horizon`） | 自定义 horizon 命令 |
| `SM_ADAPTER` | `$SM_PROJECT/系统/horizon_adapter.py` | 适配器路径 |
| `SM_ADAPTER_ARGS` | （空） | 适配器额外参数（如 `--no-fetch`） |
| `SM_GBRAIN_CMD` | （空=`gbrain`） | 自定义 gbrain 命令 |
| `SM_PROXY` | `http://127.0.0.1:7897` | 代理地址 |
| `SM_MAX_RUNTIME` | `1800`（30分钟） | 最大运行时长（秒） |
| `SM_NOW_ISO` | （空=当前时间） | 固定时间（测试用） |
| `SM_CRASH_POINT` | （空） | 崩溃注入点（测试用） |

## 调度策略

**不安装 cron/launchd 常驻调度器。**

本库语义是"agent 打开才补跑"（R6）：电脑不常开时，常驻调度器只会堆积"错过计划"噪音。推荐方式：

1. **手动触发**：用户打开 agent 会话时执行 `runner.py run`
2. **agent 会话触发**：agent 启动时检查状态，自动调用 `run`
3. **可选 crontab**（用户自行安装）：

```crontab
# 每天 09:00 尝试运行（电脑关机则跳过，下次自动补跑）
0 9 * * * cd /Users/chenzixun/Documents/自进化知识库 && /usr/bin/python3 系统/state_machine/runner.py run >> vault/04_系统维护/运行记录/cron.log 2>&1
```

## 机械阶段（自动轮）

| 阶段 | 动作 | 幂等依据 | 失败分类 |
| --- | --- | --- | --- |
| ingest | Horizon 抓取（窗口=距上次成功h+2缓冲）→ 适配器入库 | Horizon 回溯窗口可重跑；适配器 frontmatter id 判重 | 上游/网络/运行时 |
| dedup | 扫 id 重复、核对 frozen_batch 卡片存在；只报告不删除 | 只读扫描 | 数据 |
| brain_refresh | `gbrain import <vault> --no-embed` | import 幂等 | 依赖 |
| verify | 卡片存在性、无重复 id、日志在写、结案一致性 | 只读 | 数据/规则冲突 |

全部 ok → `mechanical_ok`：状态.md 写"待 agent 蒸馏接力"，停。**不做蒸馏/路由/结案**。

## 文件布局

| 文件 | 角色 |
| --- | --- |
| `系统/state_machine/runner.py` | 主入口（纯标准库） |
| `系统/state_machine/DESIGN.md` | 设计文档 |
| `系统/state_machine/README.md` | 本文件 |
| `vault/04_系统维护/状态机.json` | 状态机文件（机器读，schema v1） |
| `vault/04_系统维护/状态.md` | 人读状态（托管行由状态机维护） |
| `vault/04_系统维护/.run.lock` | 单实例锁（flock） |
| `vault/04_系统维护/运行记录/状态机-<date>-<run_id>.log` | 分类日志 |
| `vault/AGENTS.md` 末尾 `<!-- SM-HEALTH v1 -->` | 健康块（幂等替换） |

## 测试

故障注入测试 A-F + R4 幂等性，全部在隔离环境（`/var/folders/.../T/opencode/sm-test/`）执行，不碰真实 vault。详见最终报告。
