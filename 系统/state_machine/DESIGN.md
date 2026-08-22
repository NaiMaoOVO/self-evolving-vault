# 第08章 自动运行状态机 — 设计文档

> 施工依据：教程/08-自动运行状态机与故障恢复.md。本文档先于代码写成（教程要求"先写需求、设计和测试，不直接编码"）。
> 状态：已定稿（实现期间如偏差，在文末"偏差记录"登记）。

## 1. 需求（从教程施工提示词14条提取，编号 R1–R14）

| 编号 | 需求 | 来源 |
| --- | --- | --- |
| R1 | 调度：默认每日一轮，目标日=自然日，时区 Asia/Shanghai；支持手动指定日期补跑 | 第1条 |
| R2 | 单实例文件锁：第二实例启动即退出并报告 | 第2条 |
| R3 | 启动即写 run_id（UTC时间戳+随机后缀）、目标日、输入清单hash、恢复点 | 第3条 |
| R4 | 每阶段幂等，重跑不产生副本 | 第4条 |
| R5 | 进程中断后 resume 从恢复点继续，不从头重跑 | 第5条 |
| R6 | 错过计划时间只记"待补跑"，不判系统故障；下次运行合并错过的天数为一轮，只补一次（窗口=距上次成功的小时数+缓冲） | 第6、7条 |
| R7 | 24h 内已有合法结案（同目标日）则跳过 | 第8条 |
| R8 | 最大运行时长 30 分钟；每阶段重试 ≤2 次；停止条件明确 | 第9条 |
| R9 | 日志分类：网络/权限/运行时/依赖/上游/数据/规则冲突 | 第10条 |
| R10 | 状态一致性：状态机文件、AGENTS健康块、运行记录、主结案四方一致 | 第11条 |
| R11 | 自动任务只做已授权动作：不外发、不删除、不高成本模型调用；蒸馏/结案不自动执行，自动轮只做机械阶段（摄取/去重/入库/检索刷新），完成即 mechanical_ok 等 agent/用户接力 | 第12条 |
| R12 | 暂停/恢复/卸载/手动强制运行命令 | 第13条 |
| R13 | 实现前备份；测试用隔离样本 | 第14条 |
| R14 | 通过标准：同一输入最多一个合法结案；中断恢复不重复；时间滞后与真实失败分开；mechanical_ok 不冒充正式成功 | 通过标准节 |

## 2. 设计

### 2.1 状态机（教程9状态，本层驱动至 mechanical_ok 为止）

```
                    ┌──────────────────────────── agent/用户接力（不自动） ───────────────────────────┐
                    │                                                                             │
 idle ──run/resume──▶ running ──机械阶段全ok──▶ mechanical_ok ──agent蒸馏──▶ draft_pending ──用户审──▶ promoted
   ▲                  │   ▲                        │                        │
   │                  │   └── resume（从恢复点）     ├─规则升级+对照测试──────▶ evolved
   │                  ▼                            │                        ▼
   └──uninstall/归档── failed（带分类与恢复点）        └────────── 结案 ──▶ closed_knowledge / closed_drop
```

- 自动层只驱动 `idle → running → mechanical_ok | failed`，以及 failed 的 resume。
- `draft_pending/promoted/closed_*/evolved` 由 agent/用户推进，状态机文件记录但不自动触发。
- `paused` 不是教程状态，实现为 状态机.json 内布尔标志（true 时拒绝新的自动 run，force 可越过）。

### 2.2 文件布局

| 文件 | 角色 |
| --- | --- |
| `系统/state_machine/runner.py` | 主入口，纯标准库（兼容 py3.9+/3.12），无第三方依赖 |
| `vault/04_系统维护/状态机.json` | 状态机文件（机器读，schema v1） |
| `vault/04_系统维护/状态.md` | 人读状态（结构固定不动，只追加/替换一行托管 bullet） |
| `vault/04_系统维护/.run.lock` | 单实例锁（pid+时间戳，死锁可检测可接管） |
| `vault/04_系统维护/运行记录/状态机-<date>-<run_id>.log` | 分类日志 |
| `vault/04_系统维护/运行记录/状态机-备份-<date>-<run_id>/` | 首次运行前对 AGENTS.md/状态.md 的备份（R13） |
| `vault/AGENTS.md` 末尾 `<!-- SM-HEALTH v1 -->…<!-- /SM-HEALTH -->` | 健康块（幂等替换） |

### 2.3 状态机.json schema v1（要点）

```json
{
  "schema": 1, "state": "idle", "paused": false, "updated_at": "…+08:00",
  "install": {"backups_done": true},
  "run": {
    "run_id": "sm-20260822T073000Z-a1b2",
    "target_date": "2026-08-22", "window_hours": 26,
    "attempt_of": null,
    "input_manifest_hash": "sha256:…",
    "input_manifest": {"pre_vault": {"md_count": 68, "listing_sha256": "…"},
                        "horizon": {"config": "…", "data_dir": "…"}},
    "frozen_batch": {"cards": ["2026-08-22-x.md"], "ids": ["ab12…"], "summaries": ["horizon-…-zh.md"]},
    "stage_progress": {
      "ingest":       {"status": "ok|failed|pending", "attempts": 1, "detail": "…"},
      "dedup":        {…}, "brain_refresh": {…}, "verify": {…}
    },
    "started_at": "…", "log_file": "…", "budget_deadline_unix": 1234567890
  },
  "last_success": {"run_id": "…", "target_date": "…", "finished_at": "…"},
  "pending_backfill": null,
  "history": [/* 归档轮次，cap 20 */]
}
```

- 恢复点 = `run.stage_progress`（每阶段完成即落盘）+ `frozen_batch`。
- 输入清单hash = 启动时冻结的 `{目标日, 窗口, 运行前 vault 清单 sha256}` 的 sha256；ingest 完成后追加冻结批次（frozen_batch，供 resume 复用、不再重扫）。

### 2.4 阶段（自动轮=机械阶段，R11）

| 阶段 | 动作 | 幂等依据 | 失败分类 |
| --- | --- | --- | --- |
| ingest | Horizon 抓取（窗口=距上次成功小时数+2h缓冲）→ 适配器入库（含去重） | Horizon 回溯窗口可重跑；适配器按 frontmatter id 判重（已修复） | 上游（单源失败不致命）/网络/运行时 |
| dedup | 扫 `00_资源库/外部知识` id 重复、核对 frozen_batch 卡片存在；只报告不删除 | 只读扫描 | 数据 |
| brain_refresh | `gbrain import <vault> --no-embed` | import 幂等 | 依赖 |
| verify | 卡片存在性、无重复 id、日志在写、（若同目标日已有结案）四方一致检查 | 只读 | 数据/规则冲突 |

- 全部 ok → `mechanical_ok`：更新 状态.md 托管 bullet（"待 agent 蒸馏接力"）、AGENTS 健康块、日志收尾。**不做蒸馏/路由/结案**。
- 单源抓取失败：日志 `[上游]` 记录，不判整体 failed（第03章已验证此行为）。
- Horizon AI 失败（占位日报）：判 ingest failed（分类 上游），不假成功；Horizon 窗口为回溯式，恢复后加大窗口重跑可补回（第03章移交的运行契约）。

### 2.5 锁（R2）

- `.run.lock` = JSON `{pid, run_id, created_unix, host}`，`O_CREAT|O_EXCL` 原子创建。
- 已存在时：pid 存活 且 未超 `最大运行时长+10min` → 立即退出（退出码 3）。
- pid 已死（kill -9 残留）或超时 → 接管（日志记明原因），`os.replace` 原子换锁。

### 2.6 补跑与跳过（R6/R7）

- run 开始：`gap_days = today − last_success.target_date`。
  - gap ≥ 2 → 本轮为补跑：`window_hours = 距上次成功完成的小时数 + 2`，**合并为一轮**，日志 `[调度] 补跑`；不写任何"故障"字样。
  - gap ≤ 1 → 常规轮，`window_hours = max(26, 距上次成功小时数+2)`。
- R7 跳过：`蒸馏与结案/结案-<目标日>-*.md` 存在且 frontmatter `status: closed` 且 24h 内 → 跳过本轮（状态回到 idle/保持 closed_*，日志 `[调度] 24h内已有合法结案`）。force 不越过 R7（另设 `--allow-closed` 显式越过）。
- 同目标日已达 mechanical_ok 且无新输入 → 再次 run 报"等待 agent 接力"并退出。

### 2.7 预算与重试（R8）

- 总预算 `SM_MAX_RUNTIME`（默认 1800s），run 启动时记 `budget_deadline`；每个子进程 timeout=剩余预算，阶段间检查超预算 → failed（运行时/超时，保留恢复点）。
- 每阶段初始尝试 + 至多 2 次重试（`attempts` 记录在 stage_progress）；重试仅对可重试分类（网络/运行时/依赖）；上游 AI 认证类失败重试 1 次后停止（再试无意义）。
- 停止条件枚举：阶段重试耗尽 / 预算耗尽 / 上游致命（AI认证失败且重试确认）/ 数据不一致（verify）。

### 2.8 日志（R9）

行格式：`<ISO8601+08:00> [分类] 消息`。分类集合：
- 故障7类：`网络` `权限` `运行时` `依赖` `上游` `数据` `规则冲突`
- 过程标签：`调度` `阶段` `锁` `状态` `恢复`

### 2.9 一致性（R10）

- 每阶段结束与终态迁移时执行 `sync_health()`：原子写 状态机.json → 替换 AGENTS.md 健康块 → 替换 状态.md 托管 bullet（同一条信息的三个视图 + 日志流）。
- 主结案一致性：verify/终态时若同目标日存在结案文件，核对 状态.md `last_closure` 与之相符，结果记入 json 与日志。
- 状态.md 结构固定不动：只在 `下一步` 节维护一行 `- 状态机: …`（存在则替换），不改任何固定键值。

### 2.10 命令（R12）

```
python3 系统/state_machine/runner.py run                 # 每日轮（目标日=今天）
python3 系统/state_machine/runner.py run --date YYYY-MM-DD
python3 系统/state_machine/runner.py force --date YYYY-MM-DD [--allow-closed]  # 越过 paused；R7 仍生效
python3 系统/state_machine/runner.py resume              # 从恢复点续跑
python3 系统/state_machine/runner.py status              # 查看状态/锁/最后日志
python3 系统/state_machine/runner.py pause               # 暂停（拒绝新自动轮）
python3 系统/state_machine/runner.py uninstall           # 删 状态机.json/锁/自身标记；日志与其它文件不动
```

### 2.11 授权边界（R11，逐条核对）

- 自动轮动作白名单：Horizon 抓取（第03章已验收，DeepSeek 直连摘要属既有授权）、适配器入库（幂等）、gbrain import --no-embed（本地）、文件读写（授权路径内）。
- 不做：删除、外发、embedding、蒸馏 LLM 调用、结案（留给 agent/用户）。
- 所有路径可被环境变量重定向（隔离测试用）：`SM_VAULT / SM_HORIZON_DIR / SM_HORIZON_CONFIG / SM_HORIZON_CMD / SM_DATA_DIR / SM_ADAPTER / SM_ADAPTER_ARGS / SM_GBRAIN_CMD / SM_PROXY / SM_NOW_ISO / SM_MAX_RUNTIME / SM_CRASH_POINT`。

### 2.12 调度建议（写实）

不安装 cron/launchd：本库语义是"agent 打开才补跑"（R6），常驻调度器在电脑不常开的前提下只会堆积"错过计划"噪音；推荐用户手动或让 agent 会话中触发 `run`。README 保留 crontab 示例供用户自选。

## 3. 测试计划（故障注入 A–F，全部隔离样本）

隔离根：`/var/folders/…/T/opencode/sm-test/`（vault 副本 + 假 horizon 数据/命令 + 假 gbrain；适配器用真实代码 + `--no-fetch` 离线）。

| 用例 | 注入方法 | 判定 |
| --- | --- | --- |
| A Horizon 单源失败 | 真实 horizon + 隔离 config（追加无效源）+ 隔离 data/vault，跑一轮 | 日志记 `[上游]`，非整体 failed，其它源正常入库 |
| B gbrain 刷新失败 | PATH 注入假 gbrain（exit 1） | brain_refresh failed 分类 `依赖`；恢复点保留；resume 跳过已成功阶段 |
| C 运行中终止 | kill -9 运行中进程（ingest 中） | 锁残留 → 下次运行检测死 pid 接管 → resume 从恢复点续跑不重复（卡片数不翻倍） |
| D 双实例互斥 | 同时启动两个实例 | 第二个立即退出（码 3）并报告 |
| E 状态写后成果写前中断 | `SM_CRASH_POINT=before_health_write` 在状态落盘与 状态.md/AGENTS 写入间 os._exit(97) | resume 后仅一份结案视图/无第二份产物；健康块与状态一致 |
| F 错过计划时间 | 隔离 json 伪造 last_success=前天；目标日=今天 | 识别为补跑，窗口自动覆盖 gap+2h，只补一次；无"故障"记录 |

每例记录五项：不重复 / 不丢输入 / 不假成功 / 有恢复点 / 状态一致。
通过后真实冒烟：`force --date 今天` → 预期 R7 命中（结案-2026-08-22-轮次1.md）→ skip。此冒烟会写真实 状态机.json 与日志（预期写入）。

## 4. 偏差记录

| 偏差 | 说明 | 影响 |
| --- | --- | --- |
| 锁实现改用 flock | 设计文写 `O_CREAT\|O_EXCL`，实现用 `fcntl.flock(LOCK_EX\|LOCK_NB)` | 正向偏差：flock 内核级互斥，进程死亡自动释放，无 TOCTOU 竞态 |
| 测试 A 用假 horizon | 设计文写"真实 horizon + 隔离 config"，实际用假 horizon 脚本（stderr 输出源失败信息） | 隔离测试不依赖网络/API key；仍验证 runner 日志分类逻辑（[上游]不致命→不整体 failed） |
| 测试适配器用真实 venv | 隔离测试中 `SM_HORIZON_DIR` 指向真实 `~/horizon`（获取 httpx/trafilatura venv），`SM_DATA_DIR`/`SM_VAULT` 指向隔离目录 | 适配器代码真实，仅数据/vault 隔离；不碰真实 vault |
