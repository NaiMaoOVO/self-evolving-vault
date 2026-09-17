---
title: 游戏内容运营AI工作台
type: project
status: active
created: 2026-08-23
updated: 2026-09-18
source: 多轮开发会话（2026-08-23 全天）
confidence: high
sensitivity: 内部
---

# 游戏内容运营 AI 工作台

## 项目定位

面向游戏内容运营岗位的一站式本地分析工作台，最初为简历/面试演示项目，**当前正在向"每天真实使用的长期工具"转型**。零 npm 依赖（Node 内置能力 + 浏览器原生 API）是核心卖点。

- 唯一源码目录：`/Users/chenzixun/Documents/Codex/2026-05-22/new-chat`
- GitHub：`NaiMaoOVO/chengzi-game-ai-workbench`（main=源码，gh-pages=在线演示）
- 网页入口必须用本地文件 `file://…/new-chat/index.html`；GitHub 线上版无法控制本机服务（CORS 白名单有意不放行外部站点）
- 持久交接文档：项目根目录 `HANDOFF.md`（唯一交接依据）；内部评审 `OPTIMIZATION.md`（均已 gitignore）

## 架构速记

| 服务 | 端口 | 职责 |
| --- | --- | --- |
| hotspot | 8790 | B站/平台热点 |
| comment | 8791 | 评论抓取 |
| ocr | 8787 | 截图识别（macOS Vision / remote） |
| llm | 8794 | LLM 增强网关（DeepSeek 默认，LLM_JSON_MODE 兼容开关） |
| archive | 8796 | **新增**：node:sqlite 持久化（~/.gameops/archive.db，ARCHIVE_DB_PATH 可覆盖） |
| xhs-bridge | 8805 | 小红书 MCP 桥接（可选） |
| controller | 8793 | 本地控制进程 + gameops:// URL Scheme |

前端 app.js 单文件约 5400 行、八模块 + 总览简报面板。Launcher 机制：源码 → `npm run launcher:install` 同步到 Application Support runtime 快照 → 网页按钮经 gameops:// 唤起重启。

## 已完成里程碑（截至 2026-08-23）

1. **P0 安全与功能修复**：畸形 Host 头防崩（safe-request-url）；KOL 效果回填真实参与评分；导出报告样例数据水印；Nginx 屏蔽 /probe。
2. **服务层加固**：共享限流（不信任 XFF、定期清理、key 上限）；LLM 缓存 single-flight + 稳定序列化 + 容量上限；OCR 子进程 TERM→KILL 两级终止 + 输出上限 + 总截止时间；评论分页死循环保护。
3. **第四轮弹性优化**：B站会话 Cookie 24h 刷新；上游重试预算（≤3 次）+ 尊重 Retry-After；OCR readiness 每 60s 自愈；RUNTIME_FILES 抽取为 lib/runtime-manifest.js 单一来源。
4. **长期使用转型第一阶段**：
   - archive-server.js 存档服务（node:sqlite 零依赖）
   - 总览页「今日运营简报」面板：生成/存档/最近 7 份回看
   - 热点与舆情分析自动落快照（保留 real/sample 来源标记）
   - 近 14 天趋势柱状图 + 周环比自动结论（负向占比、热点条数）
   - 定时晨报抓取：MORNING_SCHEDULE/MORNING_GAMES 配置，每日自动抓今日热点入库
5. **测试体系**：42 项通过，含四个服务的真实启动冒烟测试（临时端口 + /health 身份断言）、runtime 清单回归、http-guards 单测。

## 关键教训（勿重蹈）

- **清单漂移**：新增文件必须同步 lib/runtime-manifest.js——已有回归测试锁定，安装器与检查脚本共用同一清单。
- **CORS 是浏览器行为**：curl 验证正常 ≠ 页面可用。file:// 页面依赖 Origin:null 放行；四服务已统一额外接受 null 来源；控制器仅回显 null 与 localhost 白名单。
- **语法检查发现不了运行时缺失**：丢函数/缺模块只有真正启动才暴露。已有启动冒烟测试兜底。
- **升级必须走完整流程**：改源码后 `launcher:install` → 网页「重启本地服务」。直接换控制器而遗留旧子服务时，监督器会复用旧代码进程（端口占用即跳过），导致新修复不生效。
- **区分两个入口**：GitHub 在线演示页无法遥控本机；本地页有「运行环境」标识徽章可辨别。

## 待办路线图

- [ ] SSE 流式输出（LLM 长文案首字 ~2s）
- [ ] 多游戏项目档案持久化与一键切换
- [ ] 发布台账 + BV 号效果回流（AI 输出验证闭环）
- [ ] AI 输出引用溯源（quote_id 回跳原评论）
- [ ] 静态资源指纹缓存（?v=hash）
- [ ] 小红书 MCP 本机安装登录注册验证
- [ ] 热点榜单键盘可达性、CSS 三套系统收敛

## 2026-09-17 同步记录

- 本轮完成：每日工作台接入晨报运行状态（成功时间、失败原因、服务不可用提示）；手动待办按逾期/今日/计划日期排序并显示状态标签；存档备份增加 SHA-256 校验文件与 `ARCHIVE_BACKUP_KEEP` 保留策略。
- 验证结果：`npm run check`、`npm run build:public`、`npm run check:public`、`npm test` 全部通过，当前 145/145。
- 源码 GitHub：`NaiMaoOVO/chengzi-game-ai-workbench`，本轮已整理本地提交，推送待确认目标分支。
- 同步规则：每完成 3 个已验证功能同步一次；P0、安全和数据完整性修复立即同步。

## 2026-09-18 优化记录

- 新增：每日工作台日期标题统一使用 Asia/Shanghai；待办队列在晨报接口异常时保留核心数据；备份增加独立完整性验证命令 `npm run archive:verify`。
- 本批验证：相关契约测试、`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码本地提交：`473da9b`、`b3c7454`、`0f6f91e`；GitHub 推送待确认目标分支后执行。

## 2026-09-18 优化记录（二）

- 新增：后台热点/评论快照写入状态可见（保存中、已保存编号、失败原因），不再静默吞错。
- 新增：热点与评论快照使用按业务日和内容生成的幂等键，重复渲染不会污染历史记录。
- 修复：趋势周环比边界改用 Asia/Shanghai 业务日，避免 UTC 跨日造成误分组。
- 本批验证：`npm test` 149/149 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码本地提交：`bed5d81`、`4478132`、`c6fe3e1`；GitHub 推送待确认目标分支后执行。

## 2026-09-18 优化记录（三）

- 修复：评论、热点、版本、分层、达人库和完整报告等导出文件名统一使用 Asia/Shanghai 业务日。
- 修复：热点更新时间、发布台账日期和历史热点日期统一使用业务时区，跨设备显示一致。
- 本批验证：`npm test` 154/154 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码本地提交：`c7f3020`、`0070b1d`、`3318848`；GitHub 推送待确认目标分支后执行。

## 2026-09-18 优化记录（四）

- 新增：后台存档失败时提供“重试存档”按钮，复用最近快照请求，不必重新运行分析。
- 修复：侧边导航同步 `aria-current="page"`，辅助技术可识别当前模块。
- 修复：创作者个人库“最近更新”日期使用共享业务日期格式化器。
- 本批验证：契约测试、`npm run check`、`npm run build:public`、`npm run check:public` 均通过；此前完整测试 154/154 通过。
- 代码本地提交：`8e42018`、`3be8363`、`0f90d99`；GitHub 推送待确认目标分支后执行。

## 2026-09-18 优化记录（五）

- 修复：每日待办创建请求加入稳定幂等键，网络重试不会产生重复任务。
- 修复：晨报最近运行时间统一使用 Asia/Shanghai。
- 修复：每日工作台读取待办上限从 50 提升到服务端允许的 200，全部项目范围不再静默漏项。
- 本批验证：`npm test` 159/159 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`e5ca583`、`b0f8959`、`3d7459a` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（六）

- 新增：开放待办支持一键延期到下一个业务日，减少临时调整的操作成本。
- 新增：每日队列增加“逾期”和“今日到期”快捷筛选，优先处理真正需要关注的事项。
- 修复：每日汇总读取风险工单与发布回流的上限统一提升到 200，避免长期积累后只展示前 50 条。
- 本批验证：`npm test` 162/162 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码提交：`98ecaa5`、`53053bf`、`1bda769`；待同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（七）

- 修复：每日队列改为按数据源部分降级；风险工单或发布回流接口异常时，手动待办仍继续显示。
- 修复：不可用的风险/回流统计显示为“—”并明确提示来源，避免把接口故障误报成 0 条。
- 本批验证：`npm test` 163/163 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码提交：`51a5694`；待同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 关联

- 项目内评审详情：OPTIMIZATION.md（含第一至第四轮全部建议与进度标记）
- 会话中曾求助的子智能体模式：三路并行深读评审（前端/后端/产品）→ 合并去重 → 分批落地
