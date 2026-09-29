---
title: 游戏内容运营AI工作台
type: project
status: active
created: 2026-08-23
updated: 2026-09-29
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

## 2026-09-18 优化记录（八）

- 修复：项目总览“保存当前项目”在浏览器存储不可用时不再抛出未处理异常，改为显示可理解的失败状态。
- 修复：KOL/KOC 个人库导入会确认 `localStorage` 写入结果；空间不足时明确提示导入失败，避免刷新后数据悄然丢失。
- 本批验证：`npm test` 165/165 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码提交：`bb6bb71`、`88f076f`；待同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（九）

- 修复：晨报运行记录加入 `owner_key`，认证模式下按账号过滤，避免跨账号暴露游戏与抓取状态。
- 修复：兼容旧版 `morning_runs` 表并将 `default` 记录迁移到管理员 owner；定时任务写入和更新同时带 owner。
- 本批验证：认证隔离测试、`npm test` 165/165、`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码提交：`11e6a91`；待同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（十）

- 修复：服务端趋势统计按 Asia/Shanghai 业务日分组，与前端周环比和导出日期保持一致，避免凌晨快照错归前一天。
- 本批验证：`npm test` 166/166 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码提交：`543d3eb`；待同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（十一）

- 修复：热点服务“今天”范围使用 Asia/Shanghai 业务日零点，不再依赖服务器本地时区，部署到 UTC 环境时也不会错抓日期。
- 本批验证：`npm test` 167/167 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码提交：`9cc9ce2`；待同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（十二）

- 修复：发布台账和风险工单管理列表的请求上限从 20 提升到服务端允许的 200，长期积累的历史不再过早从界面消失。
- 新增：列表读取接口返回 `total` 时，界面明确显示“已加载最近 X/总数条”；未截断时显示已加载条数，避免静默截断和误把部分数据当成全部数据。
- 本批验证：`npm test` 168/168 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`165a6b2` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（十三）

- 修复：晨报运行记录主键改为 `(owner_key, run_date, game, platform)`，避免多账号同日运行同一游戏时互相覆盖或抢占。
- 新增：启动时兼容迁移旧版 `morning_runs` 表，保留既有记录并重建账号隔离主键；调度器冲突更新同步使用复合键。
- 本批验证：`npm test` 168/168 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过，并覆盖旧表迁移及两个账号同日同游戏记录共存。
- 代码已推送：`0d83982` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（十四）

- 修复：存档服务 `POST /snapshots` 对 `null` 或数组请求体增加对象校验，统一返回 400，不再因直接访问 `body.kind` 引发未处理异常。
- 新增：回归测试确认非法请求后 `/health` 仍正常，避免单次坏请求影响后续个人工作台存档。
- 本批验证：`npm test` 168/168 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`b77e6cc` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（十五）

- 修复：KOL/KOC 效果回填写入个人库时不再静默吞掉浏览器存储失败，回填函数返回持久化结果。
- 新增：若部分回填无法写入个人库，页面仍完成当前评分，但明确提示失败人数和检查存储空间，避免刷新后历史合作数据消失却无人知晓。
- 本批验证：`npm test` 169/169 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`f8befb5` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（十六）

- 修复：抖音/小红书外部提供器的 `today` 过滤改用 Asia/Shanghai 业务日零点，部署到 UTC 主机时不再错分凌晨内容。
- 新增：跨时区回归测试在 UTC 环境验证上海零点边界，并保留 24 小时等其他范围逻辑不变。
- 本批验证：`npm test` 170/170 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`6db374d` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（十七）

- 修复：版本包装助手的口径说明在写入弹窗前统一转义动态文本，仅保留换行转换，避免后续接入可编辑或外部数据时产生 HTML 注入。
- 新增：静态回归测试锁定 `openCaliberPanel` 的安全渲染约束，防止后续重构回退到直接拼接原文。
- 本批验证：`npm test` 171/171 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`9c78c70` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（十八）

- 修复：晨报生成时间、历史简报时间和项目档案更新时间统一按 Asia/Shanghai 显示，避免浏览器或设备时区不同导致日期前后跳变。
- 新增：引入统一的业务时间格式化函数，并将复制到飞书/企微的晨报日期也改为业务日期。
- 本批验证：`npm test` 172/172 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`e26793a` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（十九）

- 修复：每日工作台在风险、回流或手动待办超过接口加载上限时，不再把截断结果当成完整队列。
- 新增：状态栏和进度摘要展示服务端总数与当前加载数，明确提示“仅展示最近 X/Y 条”，方便及时进入管理列表继续处理。
- 本批验证：`npm test` 173/173 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`d0faf20` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（二十）

- 修复：发布台账写入和评论风险转工单请求增加稳定幂等键，重复点击或网络重试不会重复创建记录。
- 新增：幂等键由当日业务日期与本次表单/风险事件内容生成，内容变更后仍可创建新的合法记录。
- 本批验证：`npm test` 174/174 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`9fe0153` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（二十一）

- 修复：每日工作台“待回流”判断不再只识别 B 站，已纳入小红书，并按渠道分别检查 `view` 或 `likes` 指标是否缺失。
- 新增：小红书实际互动数据现在会进入每日回流提醒，完成回流后 0 值也会正确视为已记录。
- 本批验证：`npm test` 175/175 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`e927d21` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（二十二）

- 修复：每日工作台读取风险、回流、待办和晨报接口时，统一将 `null`、数组等非对象 JSON 归一化为空对象，避免读取 `.ok` 抛错后把手动待办整体误判为加载失败。
- 新增：回归测试覆盖非对象响应体，确保可选接口异常时仍保留手动待办和可用的降级提示。
- 本批验证：`npm test` 176/176 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`9a9dc65` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（二十三）

- 修复：项目档案接口不再直接解析数据库 JSON；历史损坏记录会降级为空对象并标记 `invalid`，`/profiles` 与 `/profile` 均能保持 200 响应，避免单条坏数据拖垮存档服务。
- 新增：档案列表会显示“档案损坏，请重新保存”，读取接口异常也会在页面状态栏提示，不再静默清空下拉框。
- 本批验证：`npm test` 177/177 通过，覆盖认证服务下的损坏档案；`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`71c4c55` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（二十四）

- 修复：快照列表、最新快照和统计接口不再因单条损坏 JSON 直接失败；无效记录会降级为空对象并标记 `invalid`，统计保留记录数并计入无效计数。
- 新增：认证服务回归用例覆盖损坏快照的列表、最新记录和统计读取，确保存档服务继续可用。
- 本批验证：`npm test` 177/177 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`8fe9ed4` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（二十五）

- 修复：简报历史读取现在校验 HTTP 与业务状态，服务异常不会再被误显示为空列表；页面状态栏会说明读取失败原因。
- 新增：损坏的历史简报显示为“数据损坏”并禁用查看，提示重新生成，避免把空对象当成正常工作日志。
- 本批验证：`npm test` 178/178 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`27cd5e5` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（二十六）

- 修复：项目档案写入接口拒绝数组类型，避免 API 自身继续制造后续读取时被标记为损坏的档案。
- 新增：存档服务冒烟契约现在真正执行扩展读写检查，并覆盖数组档案返回 400。
- 本批验证：`npm test` 178/178 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`608d2d9` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（二十七）

- 修复：每日队列刷新接入 generation guard，初始化、切换项目、操作待办和定时刷新并发时，旧响应不会覆盖最新状态，旧请求失败也不会误报全局错误。
- 新增：前端静态回归检查锁定队列刷新必须使用 generation guard。
- 本批验证：`npm test` 179/179 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`8c7a964` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（二十八）

- 修复：项目档案下拉项被标记为损坏后，载入操作会明确阻断并提示重新保存，不再误报“已恢复”或用空对象覆盖当前内容。
- 新增：静态回归检查锁定损坏档案的载入保护。
- 本批验证：`npm test` 180/180 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`07572a4` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（二十九）

- 修复：每日队列对风险、回流、手动待办、已完成待办和晨报的 `items` 做数组校验，错误响应按来源降级或进入明确错误态，不再因字符串等异常形状触发 `.map/.filter` 类型错误。
- 新增：异常可选响应不会伪造数量，风险统计在不可用时显示为 0/不可用状态。
- 本批验证：`npm test` 181/181 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`fd7e6ba` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（三十）

- 修复：发布台账与风险工单列表读取失败时，状态栏会显示具体错误，不再保留旧的“已加载”状态造成误判；列表仍保留服务不可用提示。
- 新增：静态回归检查锁定两个列表 catch 分支必须更新各自状态栏。
- 本批验证：`npm test` 182/182 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`40123c8` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（三十一）

- 修复：发布台账和风险工单列表不再把对象、字符串等异常 `items` 当作“暂无记录”，会进入明确的读取失败状态并保留重试提示。
- 新增：静态回归检查锁定两个管理列表必须校验 `items` 为数组。
- 本批验证：`npm test` 183/183 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`6ccc248` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（三十二）

- 修复：发布台账和风险工单的刷新、写入后自动加载等并发请求接入独立 generation guard，旧成功或失败响应不会覆盖最新列表与状态。
- 新增：静态回归检查锁定两个管理列表的请求代次校验。
- 本批验证：`npm test` 184/184 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`364a76a` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（三十三）

- 修复：风险工单按工单 ID 进行写入串行化，同一工单快速点击状态流转或删除时只会保留一个进行中的请求，避免并行写入和旧响应覆盖。
- 新增：重复操作会收到明确的“正在处理中”提示，异常路径也会释放锁，后续仍可重试。
- 本批验证：`npm test` 185/185 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`9e99aa2` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（三十四）

- 修复：历史简报即使 JSON 本身合法、但 `topics`、待办建议、舆情或环比字段形状异常，也会归一化为安全的空值，不再在“查看存档”时触发前端渲染异常。
- 新增：动态回归用例直接执行简报渲染，覆盖字段为字符串、对象或空值的损坏情形。
- 本批验证：`npm test` 186/186 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`37d033a`（RED）与 `3ff3966`（修复）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（三十五）

- 修复：远端创作者库出现损坏 JSON 时，接口会明确返回 `invalid`，并拒绝后续同步覆盖写入；不再把损坏库静默伪装为空库而丢失原始数据。
- 新增：前端同步在发现远端损坏时会停止写入，提示恢复备份或确认后重新保存；后端与前端均有回归测试。
- 本批验证：`npm test` 188/188 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`34a6ac5`、`ddf49fd`（RED）与 `f8533e9`（修复）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（三十六）

- 修复：手动“存档本次简报”现在携带稳定幂等键；网络重试或页面恢复对同一份简报不会重复创建工作日志。
- 新增：回归检查锁定手动简报存档必须复用快照幂等键。
- 本批验证：`npm test` 189/189 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`7357fd2`（RED）与 `17b2c15`（修复）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

- 本轮额度检查：五小时窗口已用 37%，仍在 50% 上限内。

- 浏览器端到端检查仍受 Codex In-app Browser 对本机回环地址的 `ERR_BLOCKED_BY_CLIENT` 限制；本批以完整测试与发布产物校验代替，未把它当作浏览器验收成功。

## 2026-09-18 优化记录（三十七）

- 修复：每日待办的截止日期不再只校验字符串格式；`2026-02-30`、月份越界等不存在的日历日期会被接口拒绝，避免无效任务进入时间线。
- 新增：接口回归用例覆盖“格式正确但日期不存在”的输入。
- 本批验证：`npm test` 189/189 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`308308f`（RED）与 `da753fc`（修复）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。
- 本轮额度复查：五小时窗口已用 43%，为避免越过 50% 上限，本批后停止新增代码。

## 2026-09-18 优化记录（三十八）

- 修复：编辑每日待办时，传入 `null` 或空字符串可以清空截止日期；省略 `due_date` 仍会保留原值，避免延期和取消截止时间时产生歧义。
- 新增：接口回归用例覆盖截止日期清空路径。
- 本批验证：`npm test` 189/189 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`b4c9814`（RED）与 `8da27af`（修复）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。
- 本轮额度复查：五小时窗口已用 45%，当周窗口已用 61%，仍保留超过 20% 的当周额度。

## 2026-09-18 优化记录（三十九）

- 修复：每日待办接口显式提供 `due_date` 时，只接受字符串日期、`null` 或空字符串；数字、对象等错误类型不再被静默忽略。
- 新增：回归用例覆盖非字符串截止日期输入。
- 本批验证：`npm test` 189/189 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`630bc1a`（RED）与 `e9f5669`（修复）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。
- 本轮额度复查：当周窗口已用 61%，仍保留 39%，高于预留的 20%。

## 2026-09-18 优化记录（四十）

- 修复：每日工作台前端对历史损坏日期增加日历真实性校验；无效日期统一按“未设日期”处理，不会误显示为逾期或计划事项。
- 新增：回归检查锁定 `dueState` 必须使用真实日历日期判断。
- 本批验证：`npm test` 189/189 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`feb8ae9`（RED）与 `d917b41`（修复）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。
- 本轮额度复查：当周窗口已用 61%，剩余 39%，仍保留超过 20% 的预算。

## 2026-09-18 优化记录（四十一）

- 修复：备份校验程序除了 SHA-256 外，还会以只读模式打开 SQLite 并执行 `PRAGMA integrity_check`；校验和匹配但不是有效 SQLite 的文件会被拒绝。
- 新增：回归用例覆盖“校验文件匹配但数据库内容不是 SQLite”的情况。
- 本批验证：`npm test` 190/190 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`24df907`（RED）与 `db2c6dc`（修复）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-18 优化记录（四十二）

- 修复：备份脚本每次运行都会将备份目录权限收紧为 `0700`；即使目录之前已存在且权限过宽，也不会继续暴露备份文件。
- 新增：回归用例覆盖已有备份目录的权限收紧。
- 本批验证：`npm test` 191/191 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`16f6067`（RED）与 `1aa86c2`（修复）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。
- 本轮额度复查：五小时窗口已用 49%，当周窗口仍剩 39%。

## 2026-09-18 优化记录（四十三）

- 修复：备份校验现在要求 `.sha256` 中声明的文件名必须与实际目标文件一致，避免把一个备份的校验值误配到另一个文件。
- 新增：回归用例覆盖校验和正确但文件名不匹配的情况。
- 本批验证：`npm test` 192/192 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`e9e65bc`（RED）与 `5a7e034`（修复）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。
- 本轮额度复查：当周窗口已用 62%，剩余 38%，距离 20% 停止线仍有余量。

## 2026-09-18 优化记录（四十四）

- 修复：创作者效果回填不再按重名直接猜测；当回填记录重复或当前名单存在同名达人时会跳过写入，并明确提示补充账号 ID 或拆分名单。
- 保留：唯一姓名或已有账号 ID/主页的创作者仍按原流程更新评分、实际成本和合作历史。
- 本批验证：`npm test` 193/193 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`93b4701`（RED）与 `da8796c`（修复）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。
- 本轮额度复查：当周窗口已用 62%，剩余 38%，仍高于 20% 停止线。

## 2026-09-18 优化记录（四十五）

- 修复：个人库同步合并前会根据创作者平台、账号 ID 或主页统一生成稳定键；旧“平台+姓名”记录与新稳定身份记录会合并，不再因同步产生重复档案。
- 保留：合作历史按记录 ID 去重，并按更新时间保留较新的档案字段。
- 本批验证：`npm test` 194/194 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`31dbf2e`、`4e1f68c`（测试）与 `12be01a`（修复）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。
- 本轮额度复查：当周窗口已用 62%，剩余 38%，仍高于 20% 停止线。

## 2026-09-18 优化记录（四十六）

- 修复：个人库同步发现缺少姓名或平台等结构损坏记录时，会阻止覆盖写入并提示恢复或修复；不再静默丢弃坏记录。
- 新增：前端回归检查覆盖本地、远端结构损坏记录的同步保护。
- 本批验证：`npm test` 195/195 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。
- 代码已推送：`93d9ea2`（RED）与 `f3c5079`（修复）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。
- 本轮额度复查：当周窗口已用 62%，剩余 38%，仍高于 20% 停止线。

## 2026-09-18 优化记录（四十七）

- 前端重构：每日工作台改为克制、高密度的运营决策台，统一为浅灰画布、白色工作面、细边框与低阴影，移除大面积渐变和玻璃拟态。
- 导航与效率：侧栏按“工作区 / 内容洞察 / 内容生产 / 增长运营”分组；新增可搜索的 `⌘ K` 命令面板，支持直达模块、新建待办与刷新队列。
- 决策呈现：首屏改为紧凑四指标（待办、风险、回流、晨报运行）；行动队列以“事项—来源—优先级或状态—操作”结构呈现；AI 洞察仅根据实际风险、回流和待办生成建议，不伪造热点或版本数据。
- 本批验证：静态界面契约测试通过；完整 `npm test` 196/196 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过；Safari 已实际验证分组导航、命令面板和“新建今日待办”焦点跳转。
- 代码已推送：`a987666`（RED）与 `1df228b`（实现）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。
- 说明：初次沙箱测试因禁止监听 `127.0.0.1` 报 `EPERM`；允许本机回环端口后完整服务测试通过。

## 2026-09-19 优化记录（四十八）

- 参考真实运营仪表台的信息结构，调整每日工作台首屏为“项目上下文 → 四项工作量 → 行动队列与 AI 洞察并列”。
- 新增：项目 Banner 从当前游戏与版本主题字段实时读取；只有游戏匹配时才展示主题，否则提示“尚未为当前项目配置版本主题”，不使用虚构版本、活动或素材。
- 新增：Banner 的“版本包装”和“项目档案”入口直达原有功能；Safari 已验证版本入口可用。
- 本批验证：`npm test` 197/197 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过；Safari 已验证项目上下文、桌面双栏布局与跨模块跳转。
- 代码已推送：`2798b5a`（RED）与 `db2c351`（实现）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（四十九）

- 首屏层级：每日页改为“标题与目标说明 → 当前项目 Banner → 四项工作量 → 行动队列与 AI 洞察”；全局链路与存档错误不再占据每日页第一屏，但连接状态仍在工作台内明确可见。
- 视觉细节：四项指标补充来源明确的工作语义、低饱和状态图形和紧凑信息层级；项目 Banner 使用纯 CSS 的深色项目上下文，不伪造角色图、版本主题或活动数据。
- 真实性：本机服务未连接时保持空队列与连接说明，不为了匹配样稿而写入虚构任务、趋势或告警。
- 本批验证：每日页面契约测试 61/61 通过；完整 `npm test` 198/198 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过；Edge 强制刷新后已实际核对标题、Banner、指标卡和首屏错误信息收纳。
- 代码已推送：`fcef6d5`（RED）与 `0c4d62b`（实现）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（五十）

- 下半区重构：今日简报增加“汇总信号 → 确认下一步 → 存档并同步”的可见工作流；发布台账与风险工单由两块空的折叠栏改为并列的“内容回流 / 风险处置”行动卡。
- 操作收纳：日常先用“刷新台账 / 查询工单”处理；录入发布和筛选工单字段收进二级展开项，减少空数据时的表单噪音，同时保留全部原有字段和接口。
- 错误体验：本机存档服务未连接时只显示可行动的说明，不再把 `Failed to fetch` 暴露给用户，也不重复显示同一故障。
- 本批验证：每日页面契约测试 62/62 通过；完整 `npm test` 199/199 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过；Edge 已实际验证两张行动卡和“登记一条发布”的展开字段。
- 代码已推送：`6ccb988`、`69f1dda`（RED）与 `14893b4`（实现）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（五十一）

- 修复：没有生成或载入简报时，“存档本次简报”和“复制为飞书/企微消息”默认禁用，并通过提示说明需要先生成简报；不再允许用户触发必然失败的后续操作。
- 保留：查看历史简报始终可用；生成新简报或载入一份历史简报后，存档与复制会自动恢复可用。
- 本批验证：新增行为回归用例；每日页面契约测试 63/63 通过，完整 `npm test` 200/200 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过；Edge 已实际验证初始禁用状态与辅助提示。
- 代码已推送：`763200f`（RED）与 `aa644d8`（实现）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（五十二）

- 修复：简报存档、历史读取、发布台账和风险工单统一使用本机服务不可用判定；每日工作台不再暴露 `Failed to fetch`、`NetworkError` 等传输细节。
- 恢复路径：连接故障明确提示启动本机服务；非连接类异常仅提示稍后重试，避免把数据异常误说成服务未启动。
- 本批验证：每日页面契约测试 64/64 通过；完整 `npm test` 201/201 通过，`npm run check`、`npm run build:public`、`npm run check:public` 均通过。浏览器验证因 Mac 锁屏无法执行，待解锁后补测。
- 代码已推送：`682b8ba`（RED）与 `f1ddd89`（实现）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（五十三）

- 修复：个人待办在新增、完成、改期或放弃时遇到本机服务断开，不再暴露网络报错；统一提示“启动服务后重试”。
- 区分：只有连接类失败才引导启动本机服务，其他写入异常仅提示稍后重试，避免错误恢复路径。
- 本批验证：每日页面契约测试 65/65 通过，完整 `npm test` 202/202 通过（使用本机回环端口运行临时服务），`npm run check`、`npm run build:public`、`npm run check:public` 均通过。浏览器验证仍受 Mac 锁屏阻断，待解锁后补测。
- 代码已推送：`8ec498e`（RED）与 `71a4199`（实现）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（五十四）

- 防误触：删除发布台账或风险工单前，会明确显示删除对象并提示“此操作无法恢复”；取消确认不会发送删除请求。
- 范围：仅为已有的两类日常记录删除动作增加保护，不改变现有记录、筛选和回流接口。
- 本批验证：每日页面契约测试 66/66 通过，完整 `npm test` 203/203 通过（使用本机回环端口运行临时服务），`npm run check`、`npm run build:public`、`npm run check:public` 均通过。浏览器验证仍受 Mac 锁屏阻断，待解锁后补测。
- 代码已推送：`e273406`（RED）与 `8524b57`（实现）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（五十五）

- 修复：记录发布、回流效果、删除发布记录、更新工单状态和删除风险工单统一输出业务动作与恢复路径，不再暴露底层传输错误。
- 区分：本机存档服务断开时提示启动服务后重试；非连接类写入异常只提示稍后重试。
- 本批验证：每日页面契约测试 67/67 通过，完整 `npm test` 204/204 通过（使用本机回环端口运行临时服务），`npm run check`、`npm run build:public`、`npm run check:public` 均通过。浏览器验证仍受 Mac 锁屏阻断，待解锁后补测。
- 代码已推送：`f14f7f8`（RED）与 `eb98e6c`（实现）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（五十六）

- 修复：项目档案的读取和保存也统一为可行动的恢复说明；本机服务断开时提示启动后重试，非连接类异常提示稍后重试。
- 保留：数据损坏仍明确要求重新保存，不把结构问题误提示为服务问题。
- 本批验证：每日页面契约测试 68/68 通过，完整 `npm test` 205/205 通过（使用本机回环端口运行临时服务），`npm run check`、`npm run build:public`、`npm run check:public` 均通过。浏览器验证仍受 Mac 锁屏阻断，待解锁后补测。
- 代码已推送：`33167e9`（RED）与 `bc9ac59`（实现）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（五十七）

- 视觉统一：竞品、评论、复盘、热点、版本、分层和 KOL/KOC 等工作区的输入面、结果区、指标卡、表单控件与状态卡收敛为每日工作台一致的冷静、高密度产品风格；保留各模块原有业务结构。
- 新增：每日工作台 AI 洞察可在用户主动点击后，仅基于当前待办、开放风险和待回流内容调用已配置模型，输出摘要、最多 3 条优先动作与最多 2 条观察项；没有真实信号时入口禁用，模型不可用时保留规则归纳。
- 数据边界：服务端 `daily-insight` 任务明确禁止虚构外部数据、热点、版本、玩家反馈或执行结果，且前端仅发送当前动作队列的有限字段。
- 本批验证：页面契约测试 70/70、AI 服务定向联调 7/7 和完整 `npm test` 均通过；`npm run check`、`npm run build:public`、`npm run check:public` 均通过。浏览器验收仍受 Mac 锁屏阻断，待解锁后补测。
- 代码已推送：`9513cd2`（契约）与 `5c07dd5`（实现）已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（五十八）

- 修复：非流式 LLM 调用现在正确继承各任务的温度和输出长度配置；上游不支持 `response_format` 时，自动降级会真正移除 JSON 模式参数后重试。
- 影响：新增的每日 AI 洞察以及既有评论、版本文案等非流式任务，在 OpenAI 兼容性不完整的网关中不再因同一参数重复失败。
- 本批验证：新增回归覆盖“每日洞察保留任务限制并降级 JSON 模式”，定向 LLM 服务测试 8/8、完整 `npm test`、`npm run build:public`、`npm run check:public` 与差异检查均通过。
- 代码已推送：`81d92e8` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（五十九）

- 修复：项目总览原本有两个同名 `overview-view`，导航只会激活项目控制区，服务状态、运营闭环、演示路线和案例区无法显示。
- 处理：保留两个内容区及其全部已有控制项，但将它们归入同一“项目总览”路由并移除重复 ID；进入项目总览时两个区块都会显示。
- 本批验证：新增重复 ID 与多区块路由契约；页面契约测试 71/71、完整 `npm test`、`npm run check`、`npm run build:public` 与 `npm run check:public` 均通过。浏览器验收仍受 Mac 锁屏阻断，待解锁后补测。
- 代码已推送：`7297f00` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（六十）

- 视觉统一：项目总览也收敛到每日工作台和各工具页的安静、高密度工作台体系；Hero 去除装饰性网格，服务状态、运营流程、案例和路线卡统一使用白底、细边框和低阴影层级。
- 保留：未改动项目控制、服务状态、案例载入和运营流程的信息结构，只调整视觉层级。
- 本批验证：扩展跨工作区视觉契约；页面契约测试 71/71、完整 `npm test`、`npm run check`、`npm run build:public` 与 `npm run check:public` 均通过。浏览器验收仍受 Mac 锁屏阻断，待解锁后补测。
- 代码已推送：`bc88284` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（六十一）

- 安全修复：LLM 网关不再将上游代理、供应商或网络异常的原始错误回传页面；浏览器统一得到可行动的通用错误，原始信息仅记入本机服务日志。
- 覆盖范围：普通 JSON 请求和版本文案的流式 SSE 请求使用相同的错误边界。
- 本批验证：新增上游内部错误不泄漏到浏览器的回归；定向 LLM 测试 9/9、完整 `npm test`、`npm run build:public`、`npm run check:public` 与差异检查均通过。
- 代码已推送：`9b3aee6` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（六十二）

- 无障碍：每日 AI 洞察进入生成状态时，原生 `disabled` 与 `aria-disabled` 同步，避免读屏用户将忙碌中的入口误解为可操作。
- 交互修复：热点卡片的“查看分析”改为独立按钮，“原帖”改为独立外链；不再在互动控件中嵌套链接，方向键选择不拦截外链的 Enter 打开行为。
- 本批验证：新增热点语义与键盘边界契约；页面契约测试 72/72、完整 `npm test`、`npm run check`、`npm run build:public` 与 `npm run check:public` 均通过。
- 代码已推送：`3f3e816` 与 `161314a` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 2026-09-19 优化记录（六十三）

- 无障碍：全局命令面板补齐 Tab / Shift+Tab 焦点圈闭，与 `aria-modal` 一致；Escape、遮罩关闭和触发器焦点回退保持原行为。
- 验证：命令面板结构契约扩展，页面契约测试 72/72、完整 `npm test`、语法检查与 public 构建校验均通过。
- 代码已推送：`cc70f23` 已同步至 `NaiMaoOVO/chengzi-game-ai-workbench:main`。

## 关联

- 项目内评审详情：OPTIMIZATION.md（含第一至第四轮全部建议与进度标记）
- 会话中曾求助的子智能体模式：三路并行深读评审（前端/后端/产品）→ 合并去重 → 分批落地

## 2026-09-27 优化记录（六十四）

- 数据可靠性：每日工作台异步读取/存档绑定账号会话，写入增加超时与幂等保护；CORS 放行幂等请求头，避免重试产生重复记录。
- 备份恢复：SQLite 备份校验采用流式 SHA-256；恢复前校验 SQLite 完整性，替换时保留数据库及 sidecar，并通过原子化流程降低误覆盖风险。
- 输入与资源上限：创作者 CSV/XLSX 导入限制行数、输入体积与解压体积；截图 OCR 限制单图、批次、队列和保留行数，删除时释放临时 URL、队列槽位并中止活动请求。
- 发布产物：public 构建会生成必需的 inert launcher 状态资源，校验脚本确认页面本地资源完整且内容指纹有效。
- 异步正确性：评论 AI 分析绑定服务模式代次；切换本地/线上模式后，迟到结果不再覆盖当前页面，并提示重新分析。
- 本批验证：离线回归 282/282 通过；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 通过。`tests/archive-auth.test.js` 在获批的本机回环环境下 2/2 通过。
- 验收边界：本轮未完成浏览器端到端操作验证；回环服务测试仅运行了上述定向认证测试，其余依赖监听的服务测试未纳入 282 项离线结果。
- 同步状态：本条记录已写入本地 Obsidian vault；GitHub 当前连接未列出可访问仓库或安装，源码仍是 `main` ahead 21 且有未提交改动，因此本轮没有远程推送。vault 中原有未跟踪文件未改动。

## 2026-09-27 优化记录（六十五）

- 异步正确性：评论抓取采用 latest-request-wins；切换平台、服务模式或输入链接后，迟到的旧响应不会覆盖当前结果。
- 输入健壮性：新增安全 URI 解码，损坏的本地文件路径保留可读回退，损坏的路由 hash 回到每日工作台，小红书 token 编码错误给出重新复制链接的提示。
- 服务契约：B站评论服务与小红书桥接响应校验顶层对象和评论数组；格式错误显示重启/刷新服务提示，畸形记录被安全跳过，不再暴露 `.map is not a function` 等内部异常。
- 本批验证：完整 `npm test` 341/341 通过（含需本机回环监听的集成测试）；`npm run check`、`npm run build:public`、`npm run check:public` 通过。未完成浏览器端到端验证。
- 同步状态：本地项目源码仍有既存未提交改动，当前 Codex GitHub 连接返回 0 个账号、0 个安装和 0 个可见仓库，未推送 GitHub。此优化记录已写入本地 Obsidian；未推送 vault 远端，未改动原有未跟踪文件。

## 2026-09-27 优化记录（六十六）

- 本地项目恢复：将“尚未保存”“浏览器存储不可用”“快照 JSON 损坏”“快照字段不兼容”分开提示，替代统一失败和原样暴露解析器异常。
- 数据保护：加载失败时不写回或清理本机快照；提示先备份再恢复，避免用户误以为数据被覆盖。
- 本批验证：完整 `npm test` 345/345 通过（含本机回环服务集成测试）；`npm run check`、`npm run build:public`、`npm run check:public` 通过。未进行浏览器端到端验收。
- 同步状态：本记录仅写入本地 Obsidian vault；GitHub 连接仍无可见账号、安装或仓库，因此未推送代码或 vault 远端。既存未提交源码与 vault 未跟踪文件均保留。

## 2026-09-27 优化记录（六十七）

- 数据保护：创作者个人库检测到结构合法但档案字段或合作历史损坏时，改为只读并阻止普通保存、删除回写和云端同步覆盖；页面明确提示档案损坏，不再静默当作空库。
- 恢复路径：只有用户选取有效备份并确认后才能替换损坏库；恢复从干净库合并备份，且恢复目标仍须通过结构校验。
- 本批验证：新增嵌套档案/历史损坏、无效恢复目标和确认顺序回归；完整 `npm test` 353/353 通过，`npm run check`、`npm run build:public`、`npm run check:public` 与 `git diff --check` 通过。未做浏览器端到端验收。
- 同步状态：本地 Obsidian 记录已更新。当前 GitHub connector 读到 0 个已安装账号、0 个安装和 0 个可访问仓库；Codex UI 自动化被安全策略拒绝，需用户本人完成 OAuth/仓库授权后再复查。未推送源码或 vault 远端。

## 2026-09-27 优化记录（六十八）

- 服务端数据边界：`/creator-library` PUT 拒绝非档案对象、错误类型的名称/平台字段，以及非数组或含非对象记录的合作历史；返回稳定错误码 `creator_library_invalid_payload`，不改动现有档案。
- 兼容性：姓名或平台字段缺失的旧迁移档案仍可读写；只拒绝字段类型错误，避免破坏既有版本数据。
- 本批验证：服务端创作者库定向测试 2/2、认证/损坏数据测试 2/2、完整 `npm test` 354/354；`npm run check`、`npm run build:public`、`npm run check:public` 与项目/vault 差异检查通过。
- 同步状态：此条已写入本地 Obsidian；GitHub 连接检查仍为 0 个已安装账号、0 个 installation、0 个可访问仓库，未推送源码或 vault 远端。

## 2026-09-27 优化记录（六十九）

- 远端数据保护：创作者库 GET 会把结构合法但档案/合作历史形状错误的数据标为 `invalid`；后续 PUT 沿用 409 冲突保护，不能用一份新的有效库覆盖旧坏数据。
- 回归覆盖：在隔离 SQLite 中直接注入损坏合作历史，验证 GET 标记、PUT 拒绝并且内容和更新时间不变。
- 本批验证：创作者库及认证定向测试 5/5、完整 `npm test` 355/355、`npm run check`、public 构建/完整性检查和项目/vault 差异检查通过。
- 同步状态：本地 Obsidian 已更新；GitHub connector 仍返回 0 个账号、0 个 installation、0 个可访问仓库，未进行远程推送。

## 2026-09-27 优化记录（七十）

- 备份配置安全：备份脚本在创建目录或修改权限前规范化目标路径及符号链接，拒绝文件系统根目录、系统一级目录和用户主目录及其上级目录，避免误配置导致广泛目录被改为 `0700`。
- 回归覆盖：验证根目录、用户主目录上级及指向根目录的符号链接被拒绝，安全嵌套目录仍可用。
- 本批验证：备份测试 10/10；完整 `npm test` 356/356；`npm run check`、`npm run check:public`、`git diff --check` 通过。本机回环集成测试在获准本地监听后通过。
- 同步状态：源码提交 `d07c77f` 已推送到 GameOps `main`；本条记录随本次 Obsidian 项目笔记同步提交。

## 2026-09-27 优化记录（七十一）

- 创作者个人库并发恢复保护：损坏库的备份导入会先记录原始存储快照；确认期间若其他标签页已写入新数据，则取消旧备份恢复、保留新数据并提示重新读取，避免覆盖有效更新。
- 回归覆盖：模拟确认后另一标签页修复并更新个人库，验证旧快照恢复被拒绝、更新数据未被覆盖且损坏状态刷新。
- 本批验证：完整 `npm test` 357/357；`npm run check`、`npm run check:public` 与 `git diff --check` 通过。未做浏览器端到端验收。
- 同步状态：源码提交 `abe25d3` 已推送到 GameOps `main`；用户已将 GitHub Connector 授权范围改为所有仓库。本记录仅更新此项目笔记。

## 2026-09-27 优化记录（七十二）

- 创作者云同步并发保护：开始同步时固定本机数据快照；远端读取期间若本机数据变化，则取消旧快照上传；远端写入期间若本机数据变化，则拒绝把旧同步结果写回本机，并提示保留本机新内容后再次同步。
- 回归覆盖：分别模拟远端 GET 和 PUT 等待期间另一标签页更新档案，验证 GET 阶段不上传旧数据、PUT 阶段不覆盖本机更新；底层存储写入器也验证快照不匹配会拒绝写入。
- 本批验证：完整 `npm test` 360/360；`npm run check`、`npm run build:public`、`npm run check:public` 与 `git diff --check` 通过。未进行浏览器端到端验收。
- 同步状态：源码提交 `cf6cadb` 已推送到 GameOps `main`；本记录只写入本 Obsidian 项目笔记。

## 2026-09-27 优化记录（七十三）

- 项目槽位数据保护：本机槽位 JSON 或单个槽位结构损坏时，启动清理不会把槽位误写成空列表；读取会提示问题，保存/载入会停止，保留原始损坏数据。
- 安全兼容：若槽位列表中混有损坏记录，只清除可识别槽位中残留的存档登录凭据，损坏项原样保留；避免数据恢复保护造成凭据净化失效。
- 回归覆盖：验证损坏 JSON、损坏条目均不会被启动清理或保存覆盖；混合数据会保留损坏条目并清理有效槽位凭据。
- 本批验证：完整 `npm test` 363/363；`npm run check`、`npm run build:public`、`npm run check:public` 与 `git diff --check` 通过。浏览器端检查受策略阻止：`file://` 页面 URL 不可访问；未尝试绕过，未完成浏览器端到端验收。
- 同步状态：源码提交 `321b9d9` 已推送到 GameOps `main`；本条仅更新此项目笔记。

## 2026-09-27 优化记录（七十四）

- 本机项目快照保护：保存前先读取并检查现有快照；若 JSON 或必需结构已损坏，必须明确确认后才能覆盖，取消时保留原始数据。若无法读取存储，也会停止保存。
- 回归覆盖：验证损坏快照取消覆盖、明确确认后替换、可读快照正常无额外确认，以及读取失败时不写入。
- 本批验证：定向测试 8/8，完整 `npm test` 367/367；`npm run check`、`npm run build:public`、`npm run check:public` 与 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `b3fa9c5` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（七十五）

- 跨标签页并发保护：损坏快照覆盖确认框关闭后，会再次读取本机快照并与确认前的原始内容比对；若另一标签页在等待期间已更新，取消本次旧页面覆盖并提示重新载入。
- 回归覆盖：模拟用户在确认期间切换到另一标签页并写入有效快照，验证旧页面不会覆盖新数据。
- 本批验证：定向测试 9/9，完整 `npm test` 368/368；`npm run check`、`npm run build:public`、`npm run check:public` 与 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `32f8ebc` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（七十六）

- 项目快照恢复校验：恢复前统一预检必需的 `controls` 结构，以及可选创作者/热点数组中的记录形状。损坏的数组项会在恢复逻辑运行前被拒绝，避免表单先被部分改写后才报错。
- 回归覆盖：创作者和热点数组包含 `null` 时，均验证恢复函数不会被调用，页面状态保持未应用。
- 本批验证：定向测试 11/11，完整 `npm test` 370/370；`npm run check`、`npm run build:public`、`npm run check:public` 与 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `48ca9e2` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（七十七）

- 项目槽位覆盖保护：保存到已有槽位前要求明确确认；用户取消时不写入。确认框期间若任一标签页更新了槽位列表，会检测到快照变化并取消旧页面覆盖。
- 回归覆盖：覆盖取消、确认后替换，以及确认期间另一标签页更新三种路径。
- 本批验证：槽位定向测试 3/3，完整 `npm test` 373/373；`npm run check`、`npm run build:public`、`npm run check:public` 与 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `ee9e1bc` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（七十八）

- 项目槽位载入一致性：槽位载入现在复用项目快照结构预检，拒绝含损坏创作者/热点条目的状态，并在恢复前说明未应用任何项目内容；空槽位提示保持不变。
- 回归覆盖：模拟已保存槽位包含 `streamers: [null]`，验证恢复函数未执行且原槽位不变。
- 本批验证：槽位定向测试 4/4，完整 `npm test` 374/374；`npm run check`、`npm run build:public`、`npm run check:public` 与 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `7d60ab9` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（七十九）

- 多标签页状态同步：项目槽位订阅浏览器 `storage` 事件；同源标签页修改槽位或清空本机存储时，当前页自动刷新槽位名称与占用状态，避免列表继续显示旧数据。
- 回归覆盖：项目槽位 key 和 `localStorage.clear()` 事件会刷新；无关 key 被忽略。
- 本批验证：槽位定向测试 5/5，完整 `npm test` 375/375；`npm run check`、`npm run build:public`、`npm run check:public` 与 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `6414950` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（八十）

- 运维文档纠偏：本机 `HANDOFF.md` 原记录“2026-09-01 已同步”已过期，现更新为 2026-09-27 只读检查结果，准确列出 5 个过期运行时文件、重装目标目录与需授权的安装步骤。
- 验证：重新运行 `npm run launcher:check`，输出与手册列出的 5 个文件一致并以非零状态提示需要同步；未执行安装器。`HANDOFF.md` 被项目 `.gitignore` 排除，因此保留为本机说明，不强行加入源码提交。
- 同步状态：本条 Obsidian 项目笔记更新；未产生新的 GameOps 源码提交。

## 2026-09-27 优化记录（八十一）

- 项目快照跨标签页防覆盖：记录页面打开/载入时的快照版本；若另一标签页已更新，旧页面保存会取消并提示先保留当前未保存内容。写入前再核对一次，正常保存成功后更新本页基线。
- 回归覆盖：旧页面不能覆盖新快照；载入最新快照后可继续保存；在实际写入前发生更新也会拦截；启动时无法读取基线则采取失败关闭。
- 本批验证：新增回归后完整 `npm test` 380/380；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收；`localStorage` 仍是本机存储，并非事务型跨设备同步。
- 同步状态：源码提交 `1e82829` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（八十二）

- 启动隐私清理的并发保护：清除项目快照/项目槽位中的旧敏感字段前，重新核对原始存储值；清洗过程中若另一标签页已提交新值，则跳过旧值写回，保护较新的项目数据。
- 回归覆盖：分别模拟清理项目快照和槽位时另一标签页更新，验证新值保留且清理流程不执行覆盖写入；既有损坏数据保护用例仍通过。
- 本批验证：完整 `npm test` 381/381；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `635a715` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（八十三）

- 项目槽位最终写入保护：保存前重新读取槽位原始值；若页面状态收集期间其他标签页修改了任一槽位，则取消整次写入，避免空槽保存时丢掉其他标签页新增的槽位。
- 回归覆盖：覆盖已有槽位与保存到空槽两种竞争场景；两个用例均先复现静默覆盖，再验证更新后能保留新数据。
- 本批验证：完整 `npm test` 383/383；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `2d391b4` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（八十四）

- 启动数据清理隔离：项目快照与项目槽位现在分别清理、分别处理异常。损坏的快照不会再中断有效槽位中的敏感字段清理；损坏的槽位也不会阻断项目快照清理。
- 回归覆盖：同时构造损坏项目快照与包含旧密码字段的有效槽位，确认损坏快照原文保留、槽位独立完成清理。
- 本批验证：完整 `npm test` 383/383；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `fbd792c` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（八十五）

- LLM 请求体类型校验：`/generate` 在读取任务字段前强制校验顶层是 JSON 对象；此前合法 JSON `null` 会抛出未捕获异常并终止 LLM 服务，现在 `null` 和数组均返回 400，服务继续运行。
- 回归覆盖：契约测试发送 `null`、数组、非法 JSON、未知任务和样本不足请求，并验证限流响应仍正常。
- 本批验证：完整 `npm test` 383/383；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `4b5f569` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（八十六）

- LLM 上游响应限额：非流式成功/错误响应和 SSE 响应统一限制为 1 MiB；超限时中止上游读取，浏览器侧只收到通用错误，避免兼容服务异常响应无限占用本机内存。
- 回归覆盖：用超过 1 MiB 的有效 JSON 结果分别测试非流式与 SSE，确认非流式返回通用 502、SSE 发出 error 而不发 done。
- 本批验证：完整 `npm test` 384/384；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `27d3f23` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（八十七）

- LLM 输出结构校验：上游虽要求 JSON，但 `null`、字符串和数组曾被当作成功解析结果返回。现在解析器只接受 JSON 对象；非对象结果在普通请求中返回通用 502，在 SSE 中发出错误事件且不伪报完成。
- 回归覆盖：使用真实本地假上游分别验证 `null` 的非流式和流式响应；确认调用方收到可恢复错误，SSE 不产生 `done`。
- 本批验证：完整 `npm test` 385/385；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `7e6e42c` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（八十八）

- SSE 正常结束校验：流式网关此前只要收到可解析文本就会发送成功事件，即使上游没有发 OpenAI 兼容协议的 `[DONE]` 结束标记。现在缺少该标记会作为上游中断处理，向前端发出错误而不伪报完成。
- 回归覆盖：构造“内容本身是有效 JSON，但 SSE 缺少 `[DONE]`”的上游响应；先复现旧逻辑错误发出 `done`，再验证修复后只发出 `error`。正常结束标记的既有流式用例继续通过。
- 本批验证：LLM 流式专项 12/12、完整 `npm test` 386/386；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `37b2388` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（八十九）

- AI 任务必需字段校验：即便上游返回合法 JSON 对象，`{}` 也曾被作为成功结果返回并缓存。现在评论分析/日报必须带非空 `summary`，版本包装必须带非空 `announcement`；缺失时 JSON 返回通用 502、SSE 发出错误事件，不写入缓存。
- 回归覆盖：三类任务分别用空对象覆盖 JSON 与 SSE 路径；额外重复一次相同失败请求，确认再次访问上游而不是命中错误缓存。同步更新日报成功响应的测试夹具。
- 本批验证：完整 `npm test` 387/387；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `fbdd633` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（九十）

- 发布台账输入校验：发布时间现在只接受有效的 `YYYY-MM-DD` 或 ISO 日期时间；非法日期和非字符串输入返回 400，无效更新不会覆盖已有值。创建时对超长字段统一捕获并返回 400，避免验证异常逃出 HTTP 回调导致存档服务退出；历史脏日期在未修改时保持原样。
- 回归覆盖：拒绝自然语言日期、无效闰日、非字符串日期和超长标题；逐项确认服务仍可健康响应；接受有效日期和既有 ISO 时间戳，并验证非法更新保留旧值。
- 本批验证：完整 `npm test` 388/388；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `4504822` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（九十一）

- 存档文本字段类型校验：共享的 `textValue` 现在只在字段缺省时回退默认/旧值；显式提交数字、对象或其他非字符串类型会返回 400，不再以 200 静默忽略。覆盖发布台账与每日待办的更新接口。
- 回归覆盖：非法标题/链接类型均返回 400；读取记录确认原值未被误改，字段缺省的部分更新仍由既有用例覆盖。
- 本批验证：完整 `npm test` 390/390；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `5b90486` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（九十二）

- 风险工单与快照输入异常边界：风险工单创建/更新及快照写入此前直接调用严格文本校验，非字符串字段可能抛出未捕获异常并终止存档服务。现在统一返回 400；无效更新不改变原记录，服务仍可健康响应。
- 回归覆盖：为风险工单创建、更新分别提交数字/对象字段，并对快照写入提交非字符串项目名；逐项断言 400、原记录保留或健康端点持续可用。
- 本批验证：完整 `npm test` 391/391；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `718e404` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（九十三）

- 存档枚举字段类型校验：待办优先级/状态、风险工单级别/状态以及待办的 `link_view` 若显式提交非字符串，此前会被当成缺省值并返回成功。现在创建和更新路径拒绝该输入并返回 400；缺省字段仍按既有默认值处理。
- 回归覆盖：覆盖待办创建的 priority/status/link_view、待办更新的 priority/status，以及风险工单创建的 level/status；用数字、对象和数组验证不再静默成功。
- 本批验证：完整 `npm test` 393/393；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `36fb394` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（九十四）

- 快照来源口径校验：`POST /snapshots` 过去把任何非 `real` 值（包括数字和拼写错误）都静默记为 `sample`。现在显式来源只接受 `real`/`sample` 并拒绝其他值；省略来源仍兼容默认 `sample`。
- 回归覆盖：真实 HTTP 服务测试验证数字和未知来源值返回 400；验证省略值默认保存为 sample、显式 real 保留为 real，服务仍可继续响应。
- 本批验证：完整 `npm test` 393/393；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `c45e640` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（九十五）

- 并行后台快照重试：多个自动存档请求重叠时，较晚成功响应此前会隐藏较早失败的提示；重试也可能重发最新尝试而非失败快照。现在失败快照按幂等键保存在待重试队列，后续成功不会清除其他失败项，重试逐项使用原始数据；切换账号会清空旧账号队列。
- 回归覆盖：用延迟请求模拟反馈快照先失败、热点快照后成功；确认重试状态仍显示，并验证按钮重发反馈快照而非热点快照。
- 本批验证：完整 `npm test` 394/394；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `7c81b96` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（九十六）

- 快照明确拒绝反馈：后台存档收到 HTTP 400/422 时，过去会显示“状态未知”并将同一无效数据放入重试队列。现在明确显示本次未保存，要求修正后重新生成；其他待重试快照仍保留，超时/断连继续按结果不确定处理。
- 回归覆盖：模拟失败快照重试收到 HTTP 400，确认提示“本次数据未保存”且不再重复展示该项重试按钮；并保留并发快照失败队列的覆盖。
- 本批验证：完整 `npm test` 394/394；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `21cd18f` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（九十七）

- 存档失败恢复文案：重试内容只保存在页面内存，旧提示却建议“刷新确认后重试”，刷新会丢失当前待重试队列。现改为留在当前页点击重试，并说明同一幂等键可避免重复新增；并发失败时也给出当前页重试入口。
- 回归覆盖：实际执行存档状态回调，断言服务中断后保留待重试数量、明确提示留在当前页，并且不再建议刷新。
- 本批验证：完整 `npm test` 394/394；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `8ea8157` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（九十八）

- 存档删除异常保护：发布台账、每日待办、风险工单的删除 SQL 遇到数据库错误时，过去会让未捕获异常终止存档服务。现在各接口返回明确的 500 JSON 提示，不暴露 SQLite 内部错误；失败删除不会改变记录。
- 回归覆盖：用 SQLite `BEFORE DELETE` 触发器模拟三类删除失败，逐项断言 500、安全错误文案、记录仍存在，并在每次失败后确认 `/health` 仍可用。用例先在旧实现上复现了连接重置，再于修复后通过。
- 本批验证：完整 `npm test` 395/395；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。`npm run launcher:check` 仍报告用户级安装的桌面启动器运行时过期；因安装器会改动 `~/Applications`、`~/Library/Application Support` 并注册 `gameops://`，尚未获得本轮安装授权，未执行。未做浏览器端到端验收。
- 同步状态：源码提交 `7664682` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（九十九）

- 项目档案写入错误分类：`PUT /profile` 此前将 SQLite 写入错误和请求校验错误放进同一个捕获分支，数据库故障会误报 400 并把底层错误文本回给浏览器。现在输入仍按 400 处理，存储失败返回不含内部细节的通用 500 提示。
- 回归覆盖：用数据库触发器拒绝项目档案写入，先验证旧实现返回 400，再验证修复后返回预期 500 JSON、响应中不含数据库错误内容，且健康检查仍成功。
- 本批验证：完整 `npm test` 396/396；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `c20951e` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百）

- 项目档案读取故障隔离：`GET /profiles` 与 `GET /profile` 之前直接查询 SQLite，底层表不可用时异常会逃出请求回调并终止存档服务。现在两路由返回统一的 500 恢复提示，不泄露 SQLite 细节；缺少 `game` 参数依旧返回 400。
- 回归覆盖：在隔离临时库中重命名档案表，验证两个读取接口都返回 500，错误体不含内部表名/SQLite 信息，并且服务健康检查持续成功。用例先在旧实现上复现 socket hang up，再于修复后通过。
- 本批验证：完整 `npm test` 397/397；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `7f9108e` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百零一）

- 风险工单创建存储异常：幂等创建过去在数据库插入失败后查询幂等记录；若查询无结果（或查询本身失败），异常会逃出请求回调并终止服务。现在先校验文本字段，再分别保护幂等查询/插入/结果确认；确认不了时返回通用 500，不伪报成功也不泄露数据库错误。
- 回归覆盖：用 `BEFORE INSERT` 触发器拒绝带幂等键的工单创建，确认返回 500、响应无内部错误、无记录残留且服务健康；原有非字符串文本校验仍返回 400。
- 本批验证：完整 `npm test` 398/398；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `31b0d40` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百零二）

- 发布台账创建故障保护：幂等键查询失败或 SQLite 插入失败此前可能从请求回调逸出；创建字段 `url`/关联话题的文本校验也混在写入分支中。现在校验错误按 400 返回，幂等查询、插入及插入结果确认失败按通用 500 返回；确认存在同幂等键记录时仍返回已有记录，写入后暂时无法读取时明确告知结果。
- 回归覆盖：以非字符串 URL 验证输入仍是 400；用 SQLite 触发器拒绝发布记录写入，确认 500 不暴露内部错误、没有残留记录且服务健康；既有幂等重试回归仍通过。
- 本批验证：完整 `npm test` 399/399；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `caee2fd` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百零三）

- 每日待办创建故障分类：待办 POST 过去会把幂等查找/SQLite 写入错误交给输入校验总捕获，向界面返回 400 和数据库细节。现将来源字段校验移到写入前，并保护幂等查找、写入结果确认及新建后读取；存储异常返回安全 500，无法确认结果时不猜测成功。
- 回归覆盖：以 SQLite 插入触发器模拟待办存储故障，确认 500、无 SQLite 错误泄漏、无记录残留且服务健康；待办正常幂等重试、枚举和既有输入验证回归通过。
- 本批验证：完整 `npm test` 400/400；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `d24ebfc` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百零四）

- 每日待办更新错误分类：`PUT /daily-todos/:id` 此前将 SQLite 查询/更新异常当作字段校验失败，返回 400 并可能暴露数据库错误。现在解析与业务字段错误仍返回 400，查找/更新失败返回安全 500；更新成功后若无法重新读取，会明确说明数据已更新但暂不可见。
- 回归覆盖：用 `BEFORE UPDATE` 触发器拒绝状态更新，确认接口 500、不泄露内部错误、原待办仍为 open 且服务健康；原有非字符串字段和幂等创建验证继续通过。
- 本批验证：完整 `npm test` 401/401；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `f9732fa` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百零五）

- 风险工单更新故障分类：更新路由此前未保护初始数据库读取，写入异常又被当成字段错误返回 400；读写故障可能泄露内部细节或终止服务。现在数据库读取、更新和更新后回读分别返回受控 500；文本/枚举校验错误仍是 400。
- 回归覆盖：用 `BEFORE UPDATE` 触发器拒绝工单状态变更，确认 500、不泄露数据库错误、原状态仍为 open 且健康检查成功；旧实现实际误报 400。
- 本批验证：完整 `npm test` 402/402；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `cf52f0a` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百零六）

- 发布台账更新故障分类：`PUT /publications/:id` 此前把 SQLite 查询、更新和回读异常与请求字段校验一起返回 400。现在存储读取/更新问题返回不含内部错误的 500，成功更新但回读失败会明确说明；非法字段和日期仍返回 400。
- 回归覆盖：通过 `BEFORE UPDATE` 触发器拒绝台账更新，确认 500、内部错误不泄露、标题保留原值且服务健康；既有非字符串字段、日期与指标校验回归通过。
- 本批验证：完整 `npm test` 403/403；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `96de29d` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百零七）

- 快照存档失败隔离：`POST /snapshots` 的幂等键查找或写入失败此前会逃出请求回调并终止归档服务。现在查找/写入异常返回不泄露 SQLite 细节的 500；无法查明写入结果时不假报成功，同键已存在时仍返回原快照。
- 回归覆盖：以 `BEFORE INSERT` 触发器拒绝快照写入，确认 500、响应不含内部错误、无快照残留且服务健康。
- 本批验证：完整 `npm test` 404/404；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `2341489` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百零八）

- KOL/KOC 个人库同步错误分类：`PUT /creator-library` 此前把远端 SQLite 查询/保存失败与档案格式错误共用一个捕获分支，数据库错误会返回 400 并暴露底层文本。现在无效个人库仍返回 400，远端读取/保存失败返回安全 500；冲突和损坏保护语义不变。
- 回归覆盖：用数据库触发器拒绝远端库写入，确认 500、不泄露内部错误、健康检查成功，并验证失败前后的远端 `library` 与 `updated_at` 完全一致；既有登录、CSRF、冲突、无效档案回归通过。
- 本批验证：完整 `npm test` 405/405；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `61a2aee` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百零九）

- KOL/KOC 个人库读取故障保护：`GET /creator-library` 此前直接查询 SQLite，表不可用时未捕获异常会让请求连接重置。现在返回统一的安全 500 提示，不暴露 SQLite/表结构信息，服务进程保持可用。
- 回归覆盖：在隔离临时数据库中重命名个人库表，验证旧实现先复现 `socket hang up`；修复后接口返回预期 500，随后 `/health` 仍为 200。
- 本批验证：完整 `npm test` 406/406；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `7ff1b98` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百一十）

- 每日待办列表存储故障分类：`GET /daily-todos` 此前把 SQLite 查询失败返回为 400，并把底层数据库错误带给前端。现在返回固定的安全 500 提示；常规待办列表/筛选行为不变。
- 回归覆盖：在隔离临时数据库中重命名待办表，旧实现返回 400（并泄漏表错误），修复后返回预期 500，响应不含 SQLite/表名，且 `/health` 仍为 200。
- 本批验证：完整 `npm test` 407/407；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `154c6c2` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百一十一）

- 风险工单列表存储故障分类：`GET /risk-events` 此前把 SQLite 查询失败误报为 400，并将数据库异常文本回给调用方。现在统一返回安全 500 提示；工单列表筛选与正常读取逻辑不变。
- 回归覆盖：在隔离临时数据库中重命名风险表，确认旧实现返回 400；修复后返回固定 500、不含表名或 SQLite 错误，且 `/health` 仍为 200。
- 本批验证：完整 `npm test` 408/408；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `98523d4` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百一十二）

- 发布台账列表存储故障分类：`GET /publications` 此前把 SQLite 查询故障误报成 400，并将内部数据库错误文本返回给前端。现在固定返回安全 500 提示，正常列表筛选/分页逻辑保持不变。
- 回归覆盖：隔离临时数据库重命名发布表，验证旧实现返回 400；修复后为 500、不含表名/SQLite 细节，且 `/health` 仍为 200。
- 本批验证：完整 `npm test` 409/409；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `0a9a440` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百一十三）

- 快照列表/最近快照读取故障隔离：`GET /snapshots` 与 `GET /latest` 之前把 SQLite 读取异常返回为 400 并泄露内部文本。现在非法 `kind` 在访问数据库前仍返回 400；存储异常则统一为安全 500，损坏 JSON 的无效标记行为保持不变。
- 回归覆盖：先验证非法 kind 保持 400，再于隔离临时库重命名快照表，验证两路由返回固定 500、不含 SQLite/表名且服务健康检查仍为 200。
- 本批验证：完整 `npm test` 410/410；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `ee857ad` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百一十四）

- 仪表盘只读存储故障隔离：`GET /stats` 与 `GET /morning-runs` 此前会把查询异常返回为 400 并回传 SQLite 文本。现在统一返回安全 500 提示；正常统计和晨报历史查询保持原样。
- 回归覆盖：临时重命名快照表验证统计接口返回固定 500、不泄漏数据库细节；重命名晨报表验证运行记录接口同样受控；两类故障期间健康检查均保持 200。快照非法 kind 仍返回 400。
- 本批验证：完整 `npm test` 411/411；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `41093a6` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百一十五）

- 登录会话读取故障保护：归档服务在进入任一受保护路由前都会查询会话；认证表故障过去会让请求连接重置。现在会话验证异常返回固定 500，不泄漏数据库信息，也不会伪装为未登录；服务继续响应健康检查。
- 回归覆盖：先登录获取有效会话，再于隔离认证库重命名用户表，验证 `/auth/session` 返回安全 500、无 SQLite/表名信息，且 `/health` 仍为 200；用例先在旧实现上复现 `socket hang up`。
- 本批验证：完整 `npm test` 412/412；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。既有登录、CSRF、管理员权限及账号隔离用例通过。未做浏览器端到端验收。
- 同步状态：源码提交 `4a6f90a` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百一十六）

- 管理员用户列表读取保护：`GET /auth/users` 查询失败过去会从请求处理器逸出并重置连接。现在管理员列表读取错误返回固定 500，不泄露数据库信息；会话认证与管理权限判断仍在原位。
- 回归覆盖：使用有效管理员会话，临时改名用户表中的非认证时间字段以只破坏列表查询，验证固定 500、服务健康；恢复 schema 后确认同一会话仍有效，未影响后续会话故障用例。
- 本批验证：完整 `npm test` 413/413；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。管理员权限、CSRF 与账号隔离回归通过。未做浏览器端到端验收。
- 同步状态：源码提交 `b0c4f36` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百一十七）

- 管理员新增账号故障分类：账号输入校验、角色/密码规则与重名仍返回 400；认证模块的用户查找、插入或写后读取遇到数据库异常时，改为带内部错误码交给路由映射成安全 500。
- 回归覆盖：SQLite `BEFORE INSERT` 触发器拒绝新成员账号，验证 500、不暴露触发器/SQLite 文本、账号未落库、服务健康；认证专项正常账号创建、登录与隔离回归继续通过。
- 本批验证：完整 `npm test` 414/414；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `7a8118c` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百一十八）

- 登录存储错误分类：正确凭据遇到用户查询、过期会话清理或会话插入故障时，过去会误报为 401“用户名或密码错误”。现在认证存储异常使用内部错误码转为不泄露细节的 500；真实凭据错误仍保持 401。
- 回归覆盖：SQLite 触发器拒绝有效管理员会话写入，确认安全 500；移除触发器后同一凭据登录成功。认证集成测试进程单独提高限流阈值以隔离多个登录故障用例，生产默认限流不变。
- 本批验证：完整 `npm test` 415/415；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `d2e0d41` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百一十九）

- 账号私有响应禁用缓存：归档服务所有 JSON 响应现在都设置 `Cache-Control: no-store`，避免认证状态、待办、项目档案、创作者库等私有内容留在浏览器或中间层缓存；业务响应数据不变。
- 回归覆盖：使用已认证会话检查 `/auth/session`、`/daily-todos`、`/creator-library` 与 `/profile` 均返回 `no-store`。
- 本批验证：完整 `npm test` 416/416；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `13debcb` 已推送到 GameOps `main`；本条为 Obsidian 项目笔记更新。

## 2026-09-27 优化记录（一百二十）

- 退出登录的存储故障恢复：数据库删除会话失败时，接口现在返回固定 500 提示且不清除仍有效的 cookie；数据库恢复后，同一会话可重试退出。修复了路由将 SQLite 预编译语句误当函数调用的接口问题，并将会话删除封装为认证模块方法。
- 回归覆盖：通过 SQLite 触发器模拟一次删除失败，验证会话仍有效、响应不设置清除 cookie；解除故障后重试返回成功、清除 cookie，旧会话随即无效。
- 本批验证：完整 `npm test` 417/417；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `9a51ecf` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百二十一）

- 前端登录态抗瞬时故障：`/auth/session` 返回 500 或网络请求失败时，不再把当前已确认账号误判为未登录，也不清掉 CSRF 状态；只有明确 401 才清理账号并展示需要登录。
- 回归覆盖：在已登录会话下分别模拟 500、fetch 拒绝，确认用户与 CSRF 保留；模拟 401，确认用户与 CSRF 被清理。
- 本批验证：完整 `npm test` 420/420；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `6ab6b30` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百二十二）

- 会话刷新竞态保护：认证刷新现在采用代次校验，迟到的旧刷新不能覆盖后续登录/登出或较新的刷新；切换本地/线上服务会清理上一服务的账号与 CSRF 状态，再按新服务重新验证。
- 回归覆盖：退出完成后释放迟到的已认证响应、让较旧并发刷新晚于新刷新返回，以及服务模式切换后释放旧模式响应，三种情况下旧账号都不能被重新应用；401 仍明确清理用户和 CSRF。
- 本批验证：完整 `npm test` 423/423；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `d14a30c` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百二十三）

- 登录/登出响应上下文保护：认证变更请求现在绑定当前登录上下文；请求期间切换服务或开始另一项认证变更后，旧响应不会覆盖新服务的身份状态，并会显示可重试提示。
- 回归覆盖：模拟旧服务的登录和登出请求在切换到线上模式后才返回，确认账号与 CSRF 保持新模式的空状态；正常成功登录、登出仍正确应用会话。
- 本批验证：完整 `npm test` 426/426；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做浏览器端到端验收。
- 同步状态：源码提交 `f5d8aeb` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百二十四）

- 跨标签页账号隔离：登录或登出成功后只广播随机状态标记，不写用户名、密码、session 或 CSRF；其他标签收到后重新向服务端核验，让账号切换事件触发既有旧账号数据清理。服务模式跨标签更改时也会同步端点、清理旧身份并重新验证。
- 回归覆盖：模拟另一个标签切换到新账号、退出登录、本地/线上模式切换，确认本标签读取正确 session、旧 CSRF 不残留；另验证广播不包含账号/token 文本。
- 本批验证：完整 `npm test` 429/429；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未做真实浏览器多标签端到端验收。
- 同步状态：源码提交 `75c347f` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百二十五）

- 部署检查诊断：将 `deploy:check` 的内联 Node 异常改为独立检查脚本；配置不完整时保留非零退出和原校验，改为一行可行动错误，不展示调用栈；有效 HTTPS 配置仍通过。
- 凭据保护回归：用无效管理员口令哨兵验证部署错误输出不包含口令；占位域名提示保持单行，避免泄露无关环境细节。
- 本批验证：完整 `npm test` 432/432；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。`npm run deploy:check` 在当前环境按预期因未设置正式 `ALLOWED_ORIGIN` 退出；未部署、未代填域名。
- 同步状态：源码提交 `1f3ebe7` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百二十六）

- 线上来源白名单校验：`ALLOWED_ORIGIN` 现在逐项要求规范 HTTPS origin，拒绝 malformed URL、HTTP、路径、localhost 和 IPv4/IPv6 回环地址；仍支持逗号分隔的多个 HTTPS origin。
- 占位域名判定收紧：仅拦截 `example.com` 与其子域，不再误拒绝名称中包含该字符串的其他域名。
- 回归覆盖：格式错误、HTTP、本机地址、IPv6 回环、附带路径与混合不安全列表均被拒绝；多域名 HTTPS 列表和 `notexample.com` 可通过。
- 本批验证：完整 `npm test` 433/433；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。正式 `ALLOWED_ORIGIN` 仍需部署者填写真实站点，未部署。
- 同步状态：源码提交 `0eb1c04` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百二十七）

- PM2 认证配置传递：archive 服务的 ecosystem `env` 显式携带认证开关、管理员用户名/口令、Secure Cookie 和会话时长；否则部署检查虽读到并验证 `.env`，archive 应用清单本身没有这些条目。
- 回归覆盖：从隔离子进程加载 ecosystem 配置，仅核对口令是否匹配的布尔值（不打印口令），并验证认证开关、用户名、安全 Cookie 与会话时长均注入 archive 进程配置。
- 本批验证：完整 `npm test` 434/434；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未在本机重启 PM2 实例做运行时验收。
- 同步状态：源码提交 `1cb795a` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百二十八）

- PM2 生产安全门：线上 archive 部署现在必须启用认证，管理员名符合 3-40 位格式、口令长度为 12-200 位，并保持 Secure Cookie；不安全配置会在 PM2 启动前失败。`start-demo.js` 本机演示模式不受影响。
- 回归覆盖：分别验证认证关闭、无效用户名、超长口令、关闭 Secure Cookie 会被拒绝；有效 HTTPS 与认证配置通过，短口令错误不回显口令内容。
- 本批验证：完整 `npm test` 436/436；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未在本机运行 PM2 服务端到端验收。
- 同步状态：源码提交 `fbe5ae1` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百二十九）

- PM2 最小权限回归：扩展部署配置测试，确认管理员口令和认证开关只注入 archive 应用，不进入热点、评论、OCR 或 LLM 的进程环境。
- 凭据处理：测试只比较配置值是否匹配的布尔结果，并断言测试口令不出现在任何标准输出中。
- 本批验证：完整 `npm test` 436/436；`npm run check` 和 `git diff --check` 通过。
- 同步状态：源码提交 `3a144d8` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百三十）

- 管理员占位口令拦截：生产检查现在拒绝 README 示例句、`change-me`、`changeme`、`password`、`admin123` 等明显占位口令，避免照抄文档后仅凭长度检查误通过。
- 回归覆盖：示例句与常见占位值均被拒绝；长度不在 12-200 的值也被拒绝；诊断不回显口令。
- 本批验证：完整 `npm test` 436/436；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。
- 同步状态：源码提交 `6a3b222` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百三十一）

- GitHub 持续集成：新增 push/PR 检查，在 Node 24 上执行语法检查、完整测试、public 构建、指纹校验，并要求构建不改写已提交 public 文件。
- 安全边界：workflow 仅有 `contents: read`，不部署、不读取 secrets；checkout/setup-node 均固定到官方不可变提交。
- 本批验证：本机 YAML 语法解析通过；按 workflow 顺序执行 `npm run check`、完整 `npm test` 436/436、`npm run build:public`、`npm run check:public`、`git diff --exit-code -- public` 和 `git diff --check` 均通过。GitHub 远端 Actions 运行结果尚未读取（当前环境无 `gh` CLI）。
- 同步状态：源码提交 `eda7730` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百三十二）

- CI 凭据收敛：checkout 显式设置 `persist-credentials: false`；该测试/构建工作流不执行 Git 写操作，无需把仓库令牌保留在 checkout 中。
- 本批验证：workflow YAML 语法解析与 `git diff --check` 通过。应用代码未改动；完整回归最近一次为 436/436，CI 远端运行结果仍待可读渠道确认。
- 同步状态：源码提交 `7fd1b71` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百三十三）

- PM2 子进程环境补齐：显式把 LLM Key/模式、远程 OCR Key、平台提供器令牌、B站 Cookie/API URL、晨报计划与游戏范围、热点来源和归档限流配置传给实际消费它们的 worker，避免线上静默退回规则模式或默认计划。
- 最小权限：B站 Cookie 只进热点/评论服务；LLM Key 只进 LLM；OCR Key 只进 OCR；抖音/小红书提供器令牌只进热点。测试仅校验布尔匹配，不输出凭据。
- 本批验证：完整 `npm test` 437/437；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。未运行真实 PM2 worker 做部署端到端验收。
- 同步状态：源码提交 `f7a4f87` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百三十四）

- 线上来源校验补强：规范化域名尾随点后再判断 loopback，避免 `localhost.`、`127.0.0.1.` 绕过部署 origin 检查。
- 回归覆盖：新增两个带尾随点的本机来源拒绝用例；标准公网 HTTPS 来源仍由此前用例覆盖。
- 本批验证：完整 `npm test` 437/437；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。
- 同步状态：源码提交 `d45a39a` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百三十五）

- 远程 OCR 部署预检：仅接受 HTTP/HTTPS URL；公网 HTTP 必须显式设置 `OCR_ALLOW_INSECURE_REMOTE=true`，环回 HTTP 与 HTTPS 可用。
- 运行时边界对齐：就绪检查和实际 OCR 请求共用 URL 校验，避免启用不安全开关后把 `ftp://` 误报为可用服务。
- 本批验证：新增预检配置用例和服务 `/ready` 回归用例；完整 `npm test` 439/439，`npm run check`、`npm run build:public`、`npm run check:public`、构建文件无差异检查和 `git diff --check` 均通过。未执行真实远端 OCR 或线上部署。
- 同步状态：源码提交 `766e9b6` 已推送到 GameOps `main`；本条记录已推送到 Obsidian `main`（提交 `d10f823`）。

## 2026-09-27 优化记录（一百三十六）

- OCR 占位域名判断改为解析主机名后精确匹配 `example.com` 及其子域，忽略主机名大小写和尾随 DNS 点；不再因 URL 路径包含 `example.com` 或真实域名 `notexample.com` 误报。
- 回归覆盖：占位主机及尾随点形式拒绝；`notexample.com`、合法域名的路径包含示例字符串、`example.com.evil.test` 均正常接受。
- 本批验证：部署检查专项 9/9；完整 `npm test` 439/439；语法检查、public 构建与一致性检查、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `91a757c` 已推送到 GameOps `main`；本条记录已推送到 Obsidian `main`（提交 `5d5e9aa`）。

## 2026-09-27 优化记录（一百三十七）

- OCR 部署模式校验：仅允许 `macos` / `remote`；对大小写和首尾空白做标准化，远程模式的 URL 预检不再被 `REMOTE` 或 ` REMOTE ` 绕过，PM2 收到规范值。
- 回归覆盖：未知 provider 拒绝、远程模式缺少 URL 时拒绝、空白/大小写变体成功标准化且 PM2 配置值为 `remote`。
- 本批验证：部署检查专项 10/10；完整 `npm test` 440/440；语法检查、public 构建与一致性、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `a91a79a` 已推送到 GameOps `main`；本条记录已推送到 Obsidian `main`（提交 `827b616`）。

## 2026-09-27 优化记录（一百三十八）

- 本地 OCR 启动一致性：服务入口也对 `OCR_PROVIDER` 去除首尾空白并转小写，和 PM2 部署预检的规范化行为一致。
- 回归覆盖：以 `" REMOTE "` 启动真实 OCR 子进程，验证 `/ready` 返回 200、provider 为 `remote` 且配置就绪。
- 本批验证：HTTP 合约专项 19/19；完整 `npm test` 441/441；语法检查、public 构建与一致性、public 无差异检查和 `git diff --check` 均通过。仅验证本机 loopback 配置，不调用真实远端 OCR。
- 同步状态：源码提交 `e688a1c` 与本条项目记录已推送到各自仓库 `main`。

## 2026-09-27 优化记录（一百三十九）

- 限流 fail-closed：共享限流器拒绝 `NaN`、无穷大、零、负数及非整数的窗口/上限/键数，避免非法参数使窗口永不清理或配额比较始终放行。
- 部署预检：对通用、归档、归档登录、OCR、LLM 的限流变量检查正安全整数；错误只显示变量名，不回显输入内容。
- 回归覆盖：代表性非数字、`NaN`、零、分数、无穷大、超安全整数均被拒绝；合法默认配置通过。
- 本批验证：专项 15/15；完整 `npm test` 443/443；语法检查、public 构建与一致性、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `303fb8a` 与本条项目记录已推送到各自仓库 `main`。

## 2026-09-27 优化记录（一百四十）

- 晨报时刻 fail-fast：新增共享 `HH:mm` 24 小时格式校验；部署预检与本机 archive 服务共用，确保错误配置不会让每天晨报静默失效。
- 标准化：有效配置会去除首尾空白，并将规范值传给 PM2 worker。
- 回归覆盖：`00:00`、`09:00`、`23:59` 接受；`9:00`、`24:00`、`12:60` 等拒绝；本机 archive 子进程在建库/监听前退出并给出配置提示。
- 本批验证：相关专项 35/35；完整 `npm test` 446/446；语法检查、public 构建与一致性、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `04d0ae9` 与本条项目记录已推送到各自仓库 `main`。

## 2026-09-27 优化记录（一百四十一）

- 晨报平台配置 fail-fast：晨报定时任务使用的平台现在与热点模块共用同一份平台白名单；拼写错误或不支持的平台会在服务启动前被拒绝，避免定时任务反复失败。
- 标准化与覆盖：有效平台去除首尾空白；测试覆盖未知平台拒绝、PM2 收到规范值，以及本机 archive 服务在建库/监听前退出。
- 本批验证：专项 40/40；完整 `npm test` 448/448；`npm run check`、public 构建与一致性检查、public 无差异检查和 `git diff --check` 均通过。未运行线上 PM2 worker。
- 同步状态：源码提交 `3dfddc2` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百四十二）

- 运行参数 fail-fast：热点和评论服务的上游超时、重试次数、缓存时长改为严格整数解析；无效的 `NaN` 不再造成请求循环不执行或缓存永不过期。
- 部署预检与本机启动对齐：上游超时限制为 1000–2147483647 毫秒，重试为 0–3 次，缓存时长为非负整数（0 可关闭缓存）；错误信息只报告配置项，不回显输入值。
- 回归覆盖：非法数值在部署预检和两个服务监听前均被拒绝；`UPSTREAM_RETRIES=0`、`CACHE_TTL_MS=0` 可通过。
- 本批验证：专项 51/51；完整 `npm test` 452/452；`npm run check`、改动库语法检查、public 构建及一致性检查、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `dd61a44` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百四十三）

- OCR/LLM 资源配置 fail-fast：请求超时、OCR 就绪检查时限、并发上限和 LLM 缓存 TTL 均改为安全整数解析；负超时、`NaN`、`Infinity` 等值在启动前拒绝。
- 缓存行为：`LLM_CACHE_TTL_MS=0` 现在可明确关闭缓存；有效配置在部署预检和服务本机启动中采用一致边界。
- 回归覆盖：坏配置在部署预检及 OCR/LLM 服务监听前均被拒绝；关闭缓存配置通过。
- 本批验证：专项 3/3；完整 `npm test` 453/453；`npm run check`、改动库语法检查、public 构建及一致性检查、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `a8df6ff` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百四十四）

- 平台请求时限：`PLATFORM_PROVIDER_TIMEOUT_MS` 现在要求 1000–2147483647 毫秒的安全整数；`Infinity` 等无效值会在部署预检和热点服务启动时被拒绝，不再拖到实际抓取时报错。
- 管理员会话时长：部署预检和本机 archive 服务统一校验 1–744 小时，与认证模块原有 31 天上限一致。
- 回归覆盖：越界/非有限值在预检和服务监听前拒绝；缓存关闭、最短提供器超时和最长会话边界通过。
- 本批验证：专项 3/3；完整 `npm test` 453/453；`npm run check`、public 构建与一致性、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `3fe26e7` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百四十五）

- 服务端口 fail-fast：热点、评论、OCR、LLM、归档和小红书桥接服务统一校验 1–65535 整数；部署预检拒绝无效 API 端口，本机服务也在监听前给出明确变量名。
- 归档安全：无效归档端口会在打开/迁移 SQLite 之前被拒绝，避免配置错误时先触碰数据文件。
- OCR 端口一致性：本地启动器、OCR 服务和 PM2 都优先使用 `OCR_PORT`，并保留 `PORT` 兼容回退；示例环境文件补充端口约束说明。
- 回归覆盖：6 个服务的越界端口拒绝；无效归档端口不创建 DB；启动器用自定义 `OCR_PORT` 拉起并监测 OCR 服务。
- 本批验证：端口专项 8/8；完整 `npm test` 455/455；`npm run check`、public 构建及一致性、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `a10f53c` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百四十六）

- 小红书桥接子进程超时改为安全整数解析，限制 1000–2147483647 毫秒；`Infinity`、`NaN`、负数及超范围配置在桥接服务启动前拒绝，避免 Node 定时器溢出后几乎立即杀死子进程。
- 部署预检也会报告该配置项；示例环境文件补充默认值 125000 毫秒。
- 本批验证：专项 2/2；完整 `npm test` 456/456；`npm run check`、public 构建与一致性、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `3ebdb76` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百四十七）

- 重启脚本统一校验 `CONTROLLER_PORT`，与本地启动器共用 1–65535 安全边界；错误端口不再被静默替换为默认值。
- 将重启入口置于 `require.main` 守卫后，使配置可被无副作用地检查；新增导入级回归测试，确认非法端口不会触发服务重启。
- 本批验证：专项 1/1；完整 `npm test` 457/457；`npm run check`、public 构建与一致性、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `e69687e` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百四十八）

- 限流配置统一 fail-fast：热点、评论、OCR、LLM、归档服务对限流次数采用严格正整数解析；`RATE_LIMIT_WINDOW_MS` 统一限制为 1000–2147483647 毫秒，避免 `0`、小数、`NaN` 或超大值被静默替换成默认策略。
- 部署预检与本机启动采用相同边界，并明确报告配置项；归档服务的普通请求限流和登录限流均在打开 SQLite 前验证。
- 回归覆盖：部署预检拒绝非法值并接受 1000ms 边界；各服务在监听/打开数据库前拒绝非法限流配置。
- 本批验证：完整 `npm test` 457/457；`npm run check`、public 构建与一致性检查、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `732c047` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百四十九）

- 归档列表查询参数改为完整安全整数校验：覆盖快照、晨报记录、发布台账、每日待办、风险工单和统计天数，拒绝 `12abc`、小数及超出安全整数范围的参数，不再部分解析或意外回到第一页。
- 错误响应统一为 400 并指出参数名；合法数值仍保留既有默认值与边界截断，服务端数据库异常继续返回原有安全 500 提示。
- 回归覆盖：6 类接口非法查询参数均被拒绝，随后健康检查仍通过；已有分页/列表集成用例保持通过。
- 本批验证：完整 `npm test` 458/458；`npm run check`、public 构建与一致性检查、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `39fad59` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百五十）

- 趋势时间窗口与产品口径统一：统计接口不再按请求时刻回溯 N×24 小时，而从最早纳入的上海自然日 00:00 起算，确保“近 14 天”稳定覆盖 14 个业务日，与工作台按自然日划分的两周比较一致。
- 新增共享 `businessDateStart`，并保留上海时区边界处理；统计仍按原有权限、游戏和类型筛选，不改已有存档。
- 回归覆盖：固定时间的上海午夜/窗口边界单测；归档 HTTP 集成验证窗口外快照被排除、窗口内与当日快照保留。
- 本批验证：完整 `npm test` 460/460；`npm run check`、public 构建与一致性检查、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `b64a9c8` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百五十一）

- 趋势查询索引：为按游戏筛选的历史快照查询增加 `(owner_key, kind, game, created_at)` 复合索引；保留不筛选游戏时使用的 `(owner_key, kind, created_at)` 索引。
- 启动迁移会创建新索引并移除被替代的前缀索引，不改动快照内容，避免重复索引长期增加写入和磁盘开销。
- 回归覆盖：从含旧索引的数据库启动并验证迁移；`EXPLAIN QUERY PLAN` 确认两种统计查询命中各自的范围索引，游戏筛选查询无临时排序。
- 本批验证：完整 `npm test` 461/461；`npm run check`、public 构建与一致性检查、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `a5b32de` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百五十二）

- 修复共享 single-flight 缓存的过期请求竞争：只有仍登记在缓存中的那一代 Promise 才能写入成功结果或清理失败项；容量淘汰后的旧请求仍可返回给原调用方，但不会复活缓存、覆盖新请求或删除新请求。
- 回归覆盖：容量为 1 时旧请求完成后条目数仍受限；同 key 的旧成功与旧失败均不能污染后续新请求；仍只调用一次当前 producer。
- 本批验证：完整 `npm test` 464/464；`npm run check`、public 构建与一致性检查、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `01ee265` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百五十三）

- 前端安全回归：审计简报存档字段到 HTML 的渲染路径，确认 `dataIssues` 在最终输出阶段已有 `escapeHtml`；未发现可利用的 XSS 路径。新增恶意存档字段用例，锁定其只能作为文本显示。
- 备份留存 fail-fast：`ARCHIVE_BACKUP_KEEP` 严格接受 1–100 的整数，拒绝 `1junk`、0、101、小数、`NaN` 和 `Infinity`，并在创建备份/清理旧副本前退出，避免配置误解析为 1 后静默删减恢复点；边界测试确认 1 与 100 可用。
- 文档同步：README 明确无效保留份数配置会在备份与清理前被拒绝。
- 本批验证：完整 `npm test` 466/466；备份专项 11/11；`npm run check`、public 构建及一致性、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `746d3ca`、`4df8c06`、`824b11e` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百五十四）

- 部署预检补齐备份策略：`deploy:check` 与实际备份脚本共用 `ARCHIVE_BACKUP_KEEP` 校验器；无效值在部署检查阶段即失败，避免上线后才在定时备份时暴露配置问题。
- 回归覆盖：预检拒绝 `1junk`、0、101、小数、`NaN`、`Infinity`；1 和 100 的边界通过；备份脚本继续复用同一校验结果。
- 本批验证：完整 `npm test` 467/467；`npm run check`、public 构建及一致性、public 无差异检查和 `git diff --check` 均通过。
- 同步状态：源码提交 `c9b7219` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-27 优化记录（一百五十五）

- 小红书桥接错误脱敏：不再把 mcporter 子进程 stderr 或 MCP 错误原文回传浏览器；stderr 仅排空、不缓存，避免签名 `xsec_token`、请求参数或提供器内部细节随失败响应泄露。
- 可操作提示：对外错误按超时、输出超限、mcporter 未安装及登录态失效给出稳定提示；其他错误统一指引检查登录态与桥接服务。
- 回归覆盖：用临时 mcporter 进程模拟 stderr 回显假签名 token，验证 HTTP 502 响应不含 token；错误分类单测验证不会反射提供器详情。
- 本批验证：完整 `npm test` 469/469；`npm run check`、`npm run check:public` 与 `git diff --check` 均通过。
- 同步状态：源码提交 `e56bccd` 已推送到 GameOps `main`；本条记录已随 Obsidian 提交 `eef81f8` 推送。

## 2026-09-27 优化记录（一百五十六）

- LLM 网关日志脱敏：上游 HTTP 错误正文不再写入服务日志，保留受控错误类型、错误码与 HTTP 状态，避免可配置上游回显 `Authorization` 假 Key 时把凭据写入 stderr/PM2 日志。
- 浏览器错误继续使用稳定业务提示；日志回归覆盖普通 JSON 与 SSE 错误处理路径，并确认本地假上游确实收到 Bearer 假 Key、但日志不包含该 Key。
- 本批验证：LLM 专项 13/13；完整 `npm test` 469/469；`npm run check`、`npm run check:public` 与 `git diff --check` 均通过。
- 同步状态：源码提交 `547afd8` 已推送到 GameOps `main`；本条记录已随 Obsidian 提交 `8952c51` 推送。

## 2026-09-27 优化记录（一百五十七）

- 交接文档纠偏：本地 `HANDOFF.md` 与 `OPTIMIZATION.md` 顶部仍残留 106/106 测试数、旧工作区状态和“HTTP 契约测试受 listen EPERM 阻断”等过期描述；已在本地刷新为最近 469/469、Launcher runtime 过期、服务状态未确认，并标注长篇旧内容为历史记录。
- 边界：两份文档被项目 `.gitignore` 明确排除，未强制加入源码仓库；项目笔记在此记录最新状态。Launcher 安装仍待用户授权，浏览器登录 Cookie 的手动验证待用户反馈。
- 验证：重新运行 `npm run launcher:check`，确认 runtime 过期及差异文件；完整源码测试此前 469/469，通过 `npm run check`、`npm run check:public`、`git diff --check`。
- 同步状态：源码最近提交 `547afd8` 已在 GameOps `main`；本条记录已随 Obsidian 提交 `046dba6` 推送到 `main`。

## 2026-09-27 优化记录（一百五十八）

- B 站凭据目标校验：评论服务会将 `BILIBILI_COOKIE` 发给 `BILIBILI_VIDEO_INFO_URL`。生产配置现只接受 `https://api.bilibili.com`，并拒绝 URL 内嵌账号密码、查询参数或片段，避免 Cookie 被误发到自定义主机；本地开发仍支持 loopback HTTP 假上游。
- 校验在服务启动与 PM2 部署配置中共用，`.env.example` 已说明生产限制；当前本机 `.env` 未配置自定义视频接口，不受行为变更影响。
- 回归覆盖：默认官方地址、伪装域名、内嵌凭据、固定查询参数、非 loopback HTTP、生产服务拒绝任意主机，以及本地 loopback 假上游继续可用。
- 本批验证：完整 `npm test` 475/475；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `0819b78` 已推送到 GameOps `main`；本条记录已随 Obsidian 提交 `5a90e95` 推送到 `main`。

## 2026-09-27 优化记录（一百五十九）

- 热点提供器容错：归一化外部平台数据时跳过 `null`、数组等无效行，不再因一条坏记录丢弃整份结果；超出 JavaScript 日期范围的时间戳降级为空时间，不再让 `toISOString()` 抛错中断整个列表。
- 回归用例混合无效行、超范围时间戳与有效热点，确认坏数据被隔离且有效结果仍返回。
- 本批验证：完整 `npm test` 476/476；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `79ee062` 已推送到 GameOps `main`；本条记录已随 Obsidian 提交 `1dba86d` 推送到 `main`。

## 2026-09-27 优化记录（一百六十）

- 外部热点提供器响应上限：请求时长有限但此前 JSON 响应体无大小上限，异常提供器可能造成不必要的内存占用。现在通过流式读取最多接收 2 MiB，超限即取消上游流并返回稳定错误；合法流式 JSON 仍正常归一化。
- 回归覆盖：超限 3 MiB 响应在解析前被拒绝，合法原生 `Response` 流成功解析；旧的坏行/无效时间戳隔离仍通过。
- 本批验证：完整 `npm test` 478/478；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `392308f` 已推送到 GameOps `main`；本条已随 Obsidian 提交 `10147b4` 推送到 `main`。

## 2026-09-27 优化记录（一百六十一）

- Nginx 代理 IP 信任链校正：两个部署模板在 `include proxy_params` 后再次设置 `X-Forwarded-For`；若发行版 include 同时设置该头，Nginx 会把重复配置都发给上游，应用取首个地址时可能采用客户端伪造值。改为显式发送唯一的 XFF（`$remote_addr`），并显式保留 Host、X-Real-IP、X-Forwarded-Proto。
- 回归覆盖：两个模板的全部五个 API location 均必须只有一条可信 XFF，且不再依赖发行版 `proxy_params`；测试先在旧配置失败，修复后通过。
- 本批验证：完整 `npm test` 480/480；`npm run check`、`npm run check:public` 和 `git diff --check` 均通过。未安装 Nginx，未执行实际 `nginx -t`。
- 同步状态：源码提交 `9ed1f86` 已推送到 GameOps `main`；本条已随 Obsidian 提交 `6023f86` 推送到 `main`。

## 2026-09-27 优化记录（一百六十二）

- LLM 网关超时边界：此前将上游模型等待时长 `LLM_TIMEOUT_MS` 加 5 秒后同时用于 Node HTTP 入站 `requestTimeout`，慢模型配置可能把未完成的客户端请求体连接延长到数分钟。现将入站完整请求限制固定为 60 秒、请求头限制为 10 秒；上游模型调用仍使用独立的 `LLM_TIMEOUT_MS`。
- 回归覆盖：运行时将模型超时设为 600 秒，确认服务器入站超时仍是 60/10 秒；旧实现复现为 605/60 秒。
- 本批验证：完整 `npm test` 481/481；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `349f03c` 已推送到 GameOps `main`；本条已随 Obsidian 提交 `56c5781` 推送到 `main`。

## 2026-09-27 优化记录（一百六十三）

- 多服务入站请求防护：热点、评论服务此前随 `UPSTREAM_TIMEOUT_MS` 延长客户端收包期限；OCR 服务也将入站请求体/请求头限制绑定到远端识别超时。现在热点、评论与 LLM 固定为请求体 60 秒/请求头 10 秒，OCR 固定为请求体 120 秒/请求头 10 秒（为较大图片上传保留时间）；各上游调用仍受其独立超时控制。
- 回归覆盖：运行时探针把各服务上游超时设为 600 秒，逐个读取真实 HTTP Server 配置，确认入站限制不变；历史配置对热点、评论、OCR 探针均失败。
- 本批验证：完整 `npm test` 484/484；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `6344983` 已推送到 GameOps `main`；本条已随 Obsidian 提交 `71d9433` 推送到 `main`。

## 2026-09-27 优化记录（一百六十四）

- LLM 流式体验：LLM 网关已发出 SSE 增量事件，但两份 Nginx 模板只关闭请求体缓冲、响应仍使用默认缓冲，线上可能攒住事件直到生成完成。现只在 `/api/llm/` 代理 location 增加 `proxy_buffering off`，同时保留 `proxy_request_buffering off`。
- 回归覆盖：两份模板均检查 LLM location 独立具备请求与响应缓冲关闭指令；旧模板测试失败，修复后通过。该环境未安装 Nginx，未执行 `nginx -t` 或真实反代浏览器验收。
- 本批验证：完整 `npm test` 486/486；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `41f6231` 已推送到 GameOps `main`；本条已随 Obsidian 提交 `e5da6ed` 推送到 `main`。

## 2026-09-27 优化记录（一百六十五）

- 登录密码校验短路：账号密码长度策略为 12–200 位，但登录此前会先对任意长度的密码执行同步 `scrypt`，超长输入可无意义占用 CPU。现在非字符串或长度越界会在哈希计算前直接拒绝。
- 回归覆盖：用内存 SQLite 和 `scrypt` 调用计数确认 11 位、201 位密码零次哈希且拒绝；有效密码仍只执行一次哈希并可登录。
- 本批验证：完整 `npm test` 487/487；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `24179af` 已推送到 GameOps `main`；本条记录已随 Obsidian 提交 `6c84802` 推送到 `main`。

## 2026-09-27 优化记录（一百六十六）

- 登录限流合同测试：存档服务已有独立登录速率限制，但缺少针对真实 `/auth/login` HTTP 路由的回归覆盖。新增隔离服务测试，以配置上限 2 次验证前两次错误凭据返回 401、第三次返回 429，并带有效 `Retry-After`；未改变生产限流策略。
- 验证：新增专项测试通过；完整 `npm test` 488/488；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `43f0e99` 已推送到 GameOps `main`；本条记录已随 Obsidian 提交 `d1b8aac` 推送到 `main`。

## 2026-09-27 优化记录（一百六十七）

- 登录请求体上限：认证登录此前复用存档 API 的通用 5 MiB JSON 上限，少量登录字段也可触发大体积请求的缓冲与解析。现只为 `/auth/login` 设 4 KiB 上限，其他存档 API 保持原有 5 MiB 上限，超限返回 413 并标明上限。
- 回归覆盖：约 5 KiB 登录请求在旧逻辑返回 401（进入认证），修复后返回 413；普通正确凭据仍返回 200，后续失败登录及超过配置尝试数后的 429/`Retry-After` 仍符合预期。错误响应明确标注 4 KiB 上限。
- 本批验证：完整 `npm test` 488/488；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `54166f6`（限额实现）和 `acd787c`（补齐成功登录回归覆盖）均已推送到 GameOps `main`；本条记录随 Obsidian 笔记后续更新一并推送。

## 2026-09-28 优化记录（一百六十八）

- 存档磁盘权限：现场权限元数据确认默认 `~/.gameops` 目录为 `0755`、SQLite 主库为 `0644`、进程 umask 为 `0022`，同机其他账号可能绕过应用层隔离直接读取账号哈希和私人运营数据。服务启动改用保留既有更严限制的 `umask | 0077`，把新建目录设为 `0700`，并在打开数据库前将已有主库及 `-journal/-wal/-shm` 侧文件收紧至 `0600`；不修改已有父目录权限，自定义路径父目录由部署方管理。
- 回归覆盖：新建数据库以 `0600` 创建；预先设为 `0644` 的旧数据库在服务启动时被收紧到 `0600`。本机存档服务未运行，主库内容未读取或改写，仅将当前 `~/.gameops/archive.db` 文件权限从 `0644` 调整到 `0600`。
- 本批验证：完整 `npm test` 489/489；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `d400b4e` 已推送到 GameOps `main`；本条记录已随 Obsidian 提交 `8dbe31e` 推送到 `main`。

## 2026-09-28 优化记录（一百六十九）

- 创作者档案身份键：主页 URL 曾整体转小写，可能把抖音等大小写敏感路径中的不同账号合并，导致合作历史串档。现在用 URL 解析规范化主机名、去除查询参数/片段和尾斜杠，同时保留路径大小写；稳定账号 ID 仍优先。
- 回归覆盖：主机名大小写、追踪参数与尾斜杠归一为同一档案；仅路径大小写不同的主页保持为两个身份。新增测试在旧逻辑下失败，修复后通过。
- 本批验证：完整 Node 测试套件退出码 0（在此前 489 项基础上新增 1 项）；`npm run check`、`npm run check:public`、`git diff --check` 均通过，公共构建已刷新。
- 同步状态：源码提交 `9af158c` 已推送到 GameOps `main`；本条记录已随优化记录（一百七十七）一并推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百七十）

- SQLite 备份轮换安全：此前脚本生成并写入校验和后即按保留数量删除旧备份，没有先确认新副本可校验且 SQLite 完整。现在先验证 SHA-256 与 `PRAGMA integrity_check`，再轮换；校验和采用独占创建，失败时只清理由本次实际创建且未验证的文件，旧恢复点不受影响。
- 回归覆盖：增加合同用例，确保验证调用位于旧备份清理之前；备份专项测试 12/12 通过，正常备份/校验/保留策略与恢复流程继续通过。
- 本批验证：完整测试套件 491/491；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `0ab6175` 已推送到 GameOps `main`；本条记录已随优化记录（一百七十七）一并推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百七十一）

- SQLite 恢复保护：恢复命令此前只要求手工传入 `--service-stopped`，并不确认 archive 服务是否真的停止。现在会探测 `ARCHIVE_PORT` 上的本机 HTTP 服务；有响应或健康检查超时/状态不明时 fail-closed，只有连接明确被拒绝才进入恢复。README 同步说明该行为。
- 回归覆盖：启动真实隔离 archive 服务，带 `--service-stopped` 执行恢复仍被拒绝，并确认活动数据库数据未被替换；服务停止后的既有恢复与恢复前副本保护测试继续通过。
- 本批验证：完整测试套件 492/492；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `604a1f0` 已推送到 GameOps `main`；本条记录已随优化记录（一百七十七）一并推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百七十二）

- HTTP 限流容量保护：地址键达到内存上限后此前会驱逐最早的活跃计数，来源地址轮换可能重置窗口配额。现在预留一个有界共享溢出桶，新地址超出容量后共用限额，不再淘汰窗口仍有效的地址；最大内存键数保持不变。
- 回归覆盖：构造容量为 3 的限流器，验证溢出地址共享计数，并确认前两个活跃地址经过新地址轮换后仍被限流；新用例在旧实现下失败、修复后通过。
- 本批验证：完整测试套件 493/493；限流及 HTTP 合同专项 37/37；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `c1944d7` 已推送到 GameOps `main`；本条记录已随优化记录（一百七十七）一并推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百七十三）

- 限流器活跃键保护：`maxKeys` 达上限时不再删除最早地址的计数，而是把超容量新来源合并到共享溢出计数；限流存储仍有固定上限，已跟踪地址在窗口内不会因 key churn 获得重置配额。
- 回归覆盖：添加新来源轮换序列，确认溢出计数生效且早期活跃来源依旧受限；用例旧逻辑失败，修复后通过。
- 本批验证：完整测试套件 493/493；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `c1944d7` 已推送到 GameOps `main`；本条记录已随优化记录（一百七十七）一并推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百七十四）

- GitHub Actions 去重：`ci.yml` 与 `verify.yml` 曾同时响应 push/PR 并运行同一套检查、测试与构建。保留 CI 作为唯一自动入口，将 Verify 调整为手动 `workflow_dispatch`；同时固定两项 Actions 的 SHA、禁用 checkout 凭据持久化并设置 15 分钟超时。
- 回归覆盖：新增 workflow 合同测试，验证自动触发唯一性、手动流程触发器及 Actions 固定版本/凭据策略；旧配置下失败，调整后通过。
- 本批验证：完整测试套件 494/494；`npm run check`、`npm run check:public`、`git diff --check` 均通过。本地验证配置合同，不代表已观察到 GitHub 云端运行结果。
- 同步状态：源码提交 `48cb223` 已推送到 GameOps `main`；本条记录已随优化记录（一百七十七）一并推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百七十五）

- 创作者账号 ID 归一：此前将所有 `accountId` 转小写，大小写敏感的 opaque ID 可能误指向同一档案。现在仅去除首尾及内部空白、保留大小写；平台与展示名仍按原规则归一。
- 回归覆盖：相同 ID 的首尾空格仍映射同一档案；只在大小写上不同的 ID 保持不同身份。旧实现下新断言失败，修复后通过。
- 本批验证：完整测试套件 494/494；创作者专项 20/20；公共构建已刷新，`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `45b2cdf` 已推送到 GameOps `main`；本条记录已随优化记录（一百七十七）一并推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百七十六）

- 备份校验输入上限：`archive:verify` 与恢复流程此前会一次性读取整个 `.sha256` 旁文件。现在先确认其为普通文件且不超过 512 字节，再解析；异常大旁文件在读取内容前被拒绝。
- 回归覆盖：构造 1 MiB 的校验旁文件并跟踪读取调用，确认返回“校验文件过大”且未读取其内容；普通备份校验和恢复继续通过。
- 本批验证：完整测试套件 495/495；备份专项 14/14；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `0537bed` 已推送到 GameOps `main`；本条记录已随优化记录（一百七十七）一并推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百七十七）

- 登录用户名时序保护：格式有效但不存在的账号此前会直接返回，跳过 `scrypt`，与已存在账号的密码验证成本不同，可能辅助枚举账号。现在每个认证实例启动时生成随机虚拟密码哈希；不存在用户时也执行一次相同参数的 `scrypt`，最终仍统一返回认证失败。
- 回归覆盖：扩展登录用例统计哈希调用次数，未知用户与已知用户错误密码都执行一次；11/201 字符密码仍在哈希前被拒绝。用例旧逻辑下失败、修复后通过。
- 本批验证：完整 `npm test` 495/495；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `593d69f` 已推送到 GameOps `main`；优化记录（一百六十九）至（一百七十七）随本次 Obsidian 更新一并推送。

## 2026-09-28 优化记录（一百七十八）

- 备份校验和读取竞态：此前先检查旁文件大小再整文件读取，文件在两步间增大仍会触发无界分配。现通过打开的文件描述符检查普通文件与大小，并将单次累计读取硬限制为 513 字节（512 字节上限外多读 1 字节用于拒绝超限输入）；支持的平台同时禁止跟随符号链接。
- 回归覆盖：模拟大小检查读到 1 字节、实际文件已增长到 1 MiB 的竞态，确认读取严格停在 513 字节并报超限；原有备份/恢复用例通过。
- 本批验证：完整 `npm test` 495/495；备份专项 14/14；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `a78f942` 已推送到 GameOps `main`；本条记录随 Obsidian 更新推送到 `main`。

## 2026-09-28 优化记录（一百七十九）

- 首次启用账号的旧数据迁移：原本逐表把 `default` 归属转给管理员，各语句独立提交；中途失败会形成局部迁移。现将 7 张数据表的归属更新放入单个 `BEGIN IMMEDIATE` 事务，任一表失败即整体回滚。
- 故障注入：先启动隔离 archive 服务创建真实 schema，预置七类旧数据，并用 SQLite trigger 令第三张表更新失败；验证旧逻辑会留下前两表已迁移的部分状态，修复后七表仍全部属于 `default`。
- 本批验证：完整 `npm test` 496/496；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `1ebbc5a` 已推送到 GameOps `main`；本条记录随 Obsidian 更新推送到 `main`。

## 2026-09-28 优化记录（一百八十）

- 管理员账号配置保护：若 `ARCHIVE_ADMIN_USERNAME` 对应已有 `member`，服务此前会静默把它当作管理员 ID，却仍保留成员角色，导致账号管理不可用并可能把旧数据迁给该成员。现改为启动时明确失败，不自动提升角色；README 说明修复选择。
- 回归覆盖：先创建普通成员，再以该用户名启动认证初始化，旧逻辑下测试失败、修复后拒绝启动且不改角色。
- 本批验证：完整 `npm test` 497/497；专项认证测试通过；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `c5ca344` 已推送到 GameOps `main`；本条记录随 Obsidian 更新推送到 `main`。

## 2026-09-28 优化记录（一百八十一）

- SQLite 路径符号链接保护：权限加固此前通过 `statSync` 检查，会跟随 `ARCHIVE_DB_PATH` 或 `-wal/-shm/-journal` 侧文件的符号链接，并 chmod 目标文件；SQLite 随后可能把无关文件当数据库打开。现在使用 `lstatSync`，启动前拒绝符号链接。
- 回归覆盖：把 `archive.db` 链接到内容为普通文本、权限为 `0644` 的目标，验证服务以可识别错误退出，目标内容和权限保持不变；旧逻辑下测试失败。
- 本批验证：完整 `npm test` 498/498；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `41f9d86` 已推送到 GameOps `main`；本条记录随 Obsidian 更新推送到 `main`。

## 2026-09-28 优化记录（一百八十二）

- 本地模式启动兼容：认证关闭时管理员用户名不参与登录，但初始化此前仍校验 `ARCHIVE_ADMIN_USERNAME`；遗留邮箱式值会阻止个人模式 archive 服务启动。现仅在启用认证时规范化该用户名，本地模式忽略无关配置，线上校验不变。
- 回归覆盖：`ARCHIVE_AUTH_ENABLED=0` 且管理员用户名为 `admin@example.com` 时，旧逻辑抛出校验错误；调整后成功创建本地模式认证对象。
- 本批验证：完整 `npm test` 499/499；`npm run check`、`git diff --check` 均通过。
- 同步状态：源码提交 `ab7d196` 已推送到 GameOps `main`；本条记录随 Obsidian 更新推送到 `main`。

## 2026-09-28 优化记录（一百八十三）

- 线上 API 访问门禁与健康检查：HTTPS Nginx 模板原有服务器级 Basic Auth，但缺少回归保护；新增配置合同测试，确认所有 5 个代理服务仍受该门禁保护且路由没有关闭认证。部署文档同步要求自定义反代配置等效认证，并让健康检查命令交互提示密码，避免执行模板命令时意外收到 401 或把口令写入命令历史。
- 本批验证：Nginx 配置专项 5/5；完整 `npm test` 500/500；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `1376145` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百八十四）

- HTTPS 首次部署引导：Nginx 模板要求 `/etc/nginx/.htpasswd-gameops`，README 之前没有创建步骤，干净服务器会在 Nginx 校验时因认证文件缺失而卡住。现添加交互式 `htpasswd -c` 示例，说明后续添加用户必须去掉 `-c`（否则会覆盖现有账号），并提醒确认 Nginx worker 可读取该文件及 Basic Auth 与 archive 账号用途不同。
- 回归覆盖：新建文档合同测试校验部署指南与 Nginx 模板引用一致；先验证旧文档缺少命令时测试失败，再补说明后通过。
- 本批验证：项目与 Nginx 配置专项 11/11；完整 `npm test` 501/501；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `65808bc` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百八十五）

- HTTPS 响应安全头继承：缓存用的两个 Nginx location 分别定义 `add_header Cache-Control`，按 Nginx 默认继承规则会屏蔽服务器级 CSP、HSTS 等全部 `add_header`，影响首页和 JS/CSS。改用 `expires -1` 保持 HTML 不缓存、`expires 30d` 保留带指纹资源的长缓存，并让安全头继续继承。
- 回归覆盖：配置合同测试锁定服务器级 CSP/HSTS、location 不重置 `add_header`，同时检查 HTML/静态缓存周期；旧配置下测试失败，修复后通过。
- 本批验证：Nginx 配置专项 6/6；完整 `npm test` 502/502；`npm run check`、`npm run check:public`、`git diff --check` 均通过。当前环境无 Nginx 可执行文件，未运行 `nginx -t`。
- 同步状态：源码提交 `4d7b506` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百八十六）

- Nginx 安全头回归覆盖：此前只断言 CSP/HSTS 存在；现扩展为校验 HSTS、nosniff、Referrer-Policy、Permissions-Policy、CSP 五项都在服务器层设置并带 `always`，location 不重置继承。另将本地被忽略的 `HANDOFF.md` 刷新为当前测试数与 Launcher 只读检查结果；遵循 `.gitignore`，未强制纳入源码仓库。
- 本批验证：Nginx 配置专项 6/6；完整 `npm test` 502/502；`npm run check`、`git diff --check` 通过。当前环境无 Nginx 可执行文件，未运行 `nginx -t`。
- 同步状态：源码测试提交 `01f293c` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百八十七）

- 审计快照刷新：将本地 `HANDOFF.md` 与 `OPTIMIZATION.md` 的入口状态更新到 2026-09-28：当前提交 `01f293c`、502 项测试、Nginx 配置合同结果、未安装 Nginx 的验证限制，以及 Launcher runtime 仍过期的只读检查和差异清单。两份文件均被 `.gitignore` 明确排除，遵循仓库约定保留为本地文件，不强制提交。
- 验证：直接核对两份文件的日期、提交、测试数与 Launcher 差异清单；当前跟踪工作树保持干净。
- 同步状态：本记录推送至 Obsidian `main`；源码最新已推送提交为 `01f293c`，审计快照不进入源码仓库。

## 2026-09-28 优化记录（一百八十八）

- HTTPS 整站 Basic Auth 覆盖：此前测试只断言 API 代理块没有 `auth_basic off`；现在覆盖 HTTPS 模板全部 12 个 location，避免未来静态资源或 SPA 路由意外关闭整站门禁。源配置未变化。
- 本批验证：Nginx 配置专项 6/6；完整 `npm test` 502/502；`git diff --check` 通过。
- 同步状态：源码测试提交 `79bc67c` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。被 `.gitignore` 排除的本地审计快照已同步更新为 `79bc67c`。

## 2026-09-28 优化记录（一百八十九）

- HSTS 子域策略安全默认值：HTTPS 模板此前默认发送一年期 `includeSubDomains`，若部署在主域名，会让所有子域也强制走 HTTPS；未配置 HTTPS 的其他子服务会被浏览器阻断。现默认仅保护配置主机本身，并在 Nginx 模板与 README 明示：确认所有子域均可用 HTTPS 后再显式加 `includeSubDomains`。
- 回归覆盖：用例先在旧模板下失败，改为安全默认值与部署说明后通过。
- 本批验证：Nginx 配置专项 7/7；完整 `npm test` 503/503；`npm run check`、`npm run check:public`、`git diff --check` 通过。`nginx -t` 因当前环境未安装 Nginx 未运行。
- 同步状态：源码提交 `3d04ff1` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百九十）

- HTTP 到 HTTPS 重定向回归保护：HTTP 示例虽然保留了 API 反代 location，但依赖 server 级 `return 301 https://$host$request_uri` 使所有请求先升级到 HTTPS。新增合同测试，确保该跳转在 80 端口配置层级生效且早于 location；避免删改后 HTTP 绕过 HTTPS 模板的 Basic Auth。
- 本批验证：Nginx 配置专项 8/8；完整 `npm test` 504/504；`npm run check`、`git diff --check` 通过。
- 同步状态：源码测试提交 `365856b` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。Nginx 实际语法检查仍受当前环境未安装 Nginx 限制。

## 2026-09-28 优化记录（一百九十一）

- 离线恢复与数据保留：Edge 页面检查发现归档服务整体断开时只给“重试同步”，且失败返回的空队列可能覆盖同账号上次成功快照。现区分全量网络故障与单接口故障；全量断开时提供启动本机服务/重新连接入口，保留上次成功队列，不把不可读显示为 0，也不以失败数据覆盖缓存。单接口故障仍只提示重试。
- Host 重定向安全：HTTP Nginx 模板曾把客户端可控的 `$host` 用作 HTTPS 301 目标，现改为配置域名 `$server_name`，防止错误 Host 影响跳转目的地。
- 回归覆盖：全量归档请求拒绝、局部失败、离线恢复动作、旧快照保留与不覆盖；HTTP 重定向合同测试先复现旧配置失败再通过。
- 本批验证：完整 `npm test` 507/507；`npm run check`、`npm run check:public`、`git diff --check` 通过；Nginx 配置专项 8/8。当前环境未安装 Nginx，未运行 `nginx -t`；Edge 通过辅助功能树做了只读检查，未完成重载后的真实点击验收。
- 同步状态：源码提交 `d10dc66` 已推送至 GameOps `main`；本记录及此前待同步项目记录随本次笔记更新推送至 Obsidian `main`。

## 2026-09-28 优化记录（一百九十二）

- 存档存储故障诊断：每日工作台核心归档读取全部返回服务端错误时，额外查询一次 `/ready`（3 秒超时），仅依据 `503 + ready:false + storage_unavailable` 标记“服务在线但存储未就绪”；正常、局部失败和纯网络离线不增加探测。UI 给出存储检查/重试提示，保留同账号上次成功队列，不将未知状态显示为空队列。
- 文档口径：README 首屏改为准确描述个人工作台、本机与受认证 HTTPS 部署、以及“发现信号 → 采取行动 → 效果回流”闭环。
- 回归覆盖：探针仅在四项核心读取均返回 5xx 时调用；覆盖存储未就绪、存储可用、局部失败、全网络离线、AI 洞察重试与旧快照保留。
- 本批验证：完整 `npm test` 510/510；`npm run check`、`npm run check:public`、`git diff --check` 均通过。浏览器实机复验受 Mac 锁屏限制，未完成。
- 同步状态：源码提交 `9929bc7` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。Launcher 用户级运行目录仍等待明确授权，未修改。

## 2026-09-28 优化记录（一百九十三）

- 账号会话响应校验：登录与会话刷新此前会把 HTTP 200 的空 JSON、错误结构或缺 CSRF 响应应用为当前会话，可能清掉已验证账号或留下无法写入的不完整登录态。现要求认证响应包含有效用户 ID、用户名、角色与 CSRF token；仅接受明确的认证关闭响应，异常刷新保留上次验证状态，异常登录不广播账号变化。
- 回归覆盖：测试无效 JSON、空对象、无用户、缺 CSRF、有效认证关闭响应、无效登录成功响应及标准 401；无效响应不得覆盖账号、CSRF 或触发跨标签同步。
- 本批验证：会话专项 15/15；完整 `npm test` 513/513；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `acf23ec` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百九十四）

- 过期会话恢复：受保护 API 返回 401 时，客户端此前仍保留失效账号，登录表单可能被隐藏；退出接口遇到过期会话也只报错。现在业务 API 的 401 会清除同一会话上下文并广播跨标签变化；退出接口 401 按会话已失效处理；500 等暂时故障仍保留当前会话。请求发出后若账号/服务上下文改变，迟到的旧 401 不会清除新会话。
- 回归覆盖：普通 API 401 清账号并通知；旧请求 401 不得清新账号；退出 401 清理，退出 500 保留登录与 CSRF 状态。
- 本批验证：会话专项 18/18；完整 `npm test` 516/516；`npm run check`、`npm run check:public`、`git diff --check` 均通过。验证覆盖客户端状态机，浏览器实机交互仍受当前 Mac 锁屏限制。
- 同步状态：源码提交 `77d0eda` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（一百九十五）

- 会话到期校验：SQLite 中 `expires_at` 损坏时，`Date.parse()` 返回 `NaN`，旧比较会把该会话当作有效；此外过期会话的清理删除失败会抛出 500。现要求到期时间必须可解析且晚于当前时间，删除只作为 best-effort 清理，清理失败仍拒绝会话并返回未认证状态。
- 回归覆盖：向真实隔离 archive 服务写入无效时间戳后必须返回 401；注入 SQLite 删除触发器阻止清理时，过期会话仍返回 401。
- 本批验证：完整 `npm test` 518/518；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `786fbb7` 已推送到 GameOps `main`；本条记录已随 Obsidian 提交 `aeb4779` 推送到 `main`。

## 2026-09-28 优化记录（一百九十六）

- 存档备份轮换时保护新副本：旧逻辑按文件名时间排序，目录中出现未来时间戳文件时，保留数量为 1 可能删掉本次已校验的新备份、留下坏文件。现固定保留本次副本，并仅按旧副本文件修改时间选择清理对象；保留数量日志也包含新副本。
- 回归覆盖：以 `9999` 年命名的损坏旧文件模拟时钟偏差/导入异常；修复前用例失败，修复后必须只剩本次通过 checksum 与 SQLite 完整性校验的副本。
- 本批验证：备份专项 15/15；完整 `npm test` 519/519；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `4f89f04` 已推送到 GameOps `main`；本条记录已随 Obsidian 提交 `aeb4779` 推送到 `main`。

## 2026-09-28 优化记录（一百九十七）

- 本地控制器实例隔离：控制器状态文件此前只按系统用户命名，重启器也接受任意目录下的 `start-demo.js` 进程；同机运行主目录和工作树副本时，可能误停另一个项目。现状态路径按项目根目录指纹区分，进程匹配限定当前项目；旧状态文件仅在其记录的项目根目录属于当前项目时兼容清理。健康接口返回不可逆的项目实例指纹供重启器核对。
- 回归覆盖：验证同项目路径得到稳定状态文件、不同项目路径隔离，重启识别拒绝外部项目脚本和伪装命令；集成检查控制器启动时发布指纹/状态文件、关闭时清理自身文件。
- 本批验证：控制器专项与运行时清单 5/5；本地控制器 HTTP 集成及端口校验 2/2；完整测试套件 521/521；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 运行时限制：源码 Launcher 清单已更新，但用户级安装目录未改动；安装仍需明确授权。
- 同步状态：源码提交 `3c92a77` 已推送到 GameOps `main`；本条记录已随 Obsidian 提交 `1320522` 推送到 `main`。

## 2026-09-28 优化记录（一百九十八）

- 本地控制器重启状态竞态：旧控制器退出后，重启器此前仅按项目归属删除状态文件；若自动启动的新实例先写入同一路径，新 PID 记录也可能被旧重启器删掉。现清理时同时匹配待停止 PID，只清理旧实例记录，保留并发写入的新状态。
- 回归覆盖：同项目但 PID 已替换的状态不得作为旧实例清理目标；其他项目、错误指纹和损坏的 legacy 指纹均拒绝，未带指纹的同项目旧格式仍可兼容。
- 本批验证：控制器专项与运行时清单 6/6；本地控制器 HTTP 集成及端口校验 2/2；完整测试套件 522/522；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `114ca0a` 已推送到 GameOps `main`；本条记录已随 Obsidian 提交 `1320522` 推送到 `main`。

## 2026-09-28 优化记录（一百九十九）

- 本地控制器状态文件防符号链接：此前状态文件位于公共临时目录的可预测路径，启动会跟随已有链接写入。现按项目/用户放入独立 `0700` 目录，状态文件以 `0600` 写入；读写均不跟随符号链接并限制为 4 KiB，已有目录还会验证类型、所有者与权限。
- 回归覆盖：预建目录符号链接必须在 chmod/写入前拒绝；状态文件符号链接读写均拒绝且目标内容不变；超限状态文件在解析前拒绝。真实控制器启动/退出也验证了状态读写和清理流程。
- 本批验证：控制器专项与运行时清单 8/8；本地控制器 HTTP 集成及端口校验 2/2；完整测试套件 524/524；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 运行时限制：项目内 Launcher 清单包含状态安全代码；用户级 Launcher 仍未更新，等待明确授权。
- 同步状态：源码提交 `e8d7377` 已推送到 GameOps `main`；本条记录已随 Obsidian 提交 `5f2a93f` 推送到 `main`。

## 2026-09-28 优化记录（二百）

- 重启命令退出状态：新控制进程若以信号（如 `SIGTERM`）退出，Node 的退出码为 `null`；此前 `code || 0` 会把它转换成成功。现保留正常数字退出码，并把信号终止映射成失败码 1。
- 回归覆盖：正常退出码 0/非零保持原值，`code=null + signal` 必须返回失败。
- 本批验证：控制器/运行时清单专项 10/10；完整测试套件 525/525；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `b3601e6` 已推送到 GameOps `main`；本条记录随优化记录（二百零一）推送到 Obsidian `main`。

## 2026-09-28 优化记录（二百零一）

- 归档自动备份：归档服务启动约 10 秒后检查当天（Asia/Shanghai）是否已有通过 SHA-256 与 SQLite 完整性校验的备份；缺失时异步调用现有备份脚本，失败后每小时重试，继续沿用 7 份轮换。`ARCHIVE_AUTO_BACKUP_ENABLED=0` 可关闭；Node 测试环境默认不启动，显式设为 `1` 才启用。
- 备份进程只继承归档数据库、备份目录、保留份数与临时目录配置；备份脚本从 `.env` 只加载三个归档备份配置，不把 LLM 等无关密钥放进子进程环境。运行时清单同步加入调度器及其依赖。
- 验证：备份/调度器专项测试 20/20；完整 `npm test` 531/531；`npm run check`、`npm run check:public`、`git diff --check` 通过。真实备份子进程已生成并通过校验的文件；未进行用户级 Launcher 安装或浏览器 UI 验收。
- 边界：自动备份仍存于同一设备/存储环境，不是异地灾备；用户级 Launcher runtime 仍待明确授权更新。
- 同步状态：源码提交 `4b4dce1` 已推送到 GameOps `main`；本条记录及优化记录（二百）已随 Obsidian 提交 `d9f953f` 同步到 `main`。

## 2026-09-28 优化记录（二百零二）

- 归档轮换校验：轮换此前仅按文件修改时间挑选保留项，较新的损坏副本会占据名额并挤掉可恢复的历史副本。现只让通过 SHA-256 与 SQLite 完整性检查的副本进入 7 份保留排序；损坏的过期副本清理时会安全检查目标，最近一小时内变化的异常文件暂缓删除，避免误碰并发写入。
- 回归覆盖：新增“更新时间更近但校验失败”的副本不得驱逐有效恢复点；新鲜异常文件不被立即删除；旧未来时间戳文件仍不能导致新副本丢失。新用例在旧逻辑下先失败，修复后通过。
- 本批验证：归档备份/调度器专项 22/22；完整 `npm test` 533/533；`npm run check`、`npm run check:public`、`git diff --check` 全通过。
- 同步状态：源码提交 `ed257b7` 已推送到 GameOps `main`；本条记录随优化记录（二百零三）推送到 Obsidian `main`。

## 2026-09-28 优化记录（二百零三）

- 归档文件校验防符号链接：SHA-256 读取此前只对 `.sha256` 文件禁止跟随符号链接，数据库备份本体仍会跟随链接。现先通过 `lstat` 限定普通文件，以 `O_NOFOLLOW` 打开，并比对打开前后的设备号/ inode，拒绝符号链接和校验期间替换。
- 回归覆盖：新增备份文件符号链接用例，旧实现会跟随并读取目标，修复后明确拒绝；现有大文件流式哈希与归档恢复用例保持通过。
- 本批验证：归档备份专项 18/18；完整 `npm test` 534/534；`npm run check`、`npm run check:public`、`git diff --check` 全通过。
- 同步状态：源码提交 `f163a36` 已推送到 GameOps `main`；本条记录及优化记录（二百零二）随本次 Obsidian 同步推送。

## 2026-09-28 优化记录（二百零四）

- 归档备份可观测性：项目总览的数据服务状态面板新增“归档备份”，管理员可查看今日校验状态、最近成功日期、失败重试间隔；状态接口不返回数据库或备份文件路径。未登录用户和非管理员分别收到 401/403。
- 回归覆盖：验证调度器待运行、执行中、失败、成功及跨日状态转换；接口测试校验匿名拒绝、管理员允许、普通成员拒绝和响应字段白名单；前端测试覆盖健康、失败和受限状态文案。
- 本批验证：完整 `npm test` 535/535；`npm run build:public`、`npm run check:public`、`npm run check`、`git diff --check` 均通过。未进行浏览器实机交互验收。
- 同步状态：源码提交 `af35211` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（二百零五）

- 归档恢复目标校验：旧恢复流程以 `existsSync` 检查 SQLite 数据库及 `-wal/-shm/-journal` 侧文件，无法识别悬空符号链接，可能在留下危险侧链的同时继续替换数据库。现恢复前逐个用 `lstat` 检查，目标仅接受普通文件；符号链接及其他文件类型在复制安全副本或替换前被拒绝。
- 回归覆盖：新增真实备份恢复测试，旧实现会成功替换并留下悬空 `-wal` 链接；修复后明确失败，原数据库内容与链接均保留，且未生成部分安全副本。
- 本批验证：恢复专项 4/4；完整 `npm test` 536/536；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `b9909c2` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（二百零六）

- 项目总览状态刷新延迟：此前先等待 AI 健康检查（最多 2.4 秒），再启动 OCR、热点、评论与归档备份探测，独立检查被串行拖慢。现将 AI、其他本地服务和备份状态并发检查，并在最终渲染时读取 AI 的已验证状态，避免显示旧状态。
- 回归覆盖：使用延迟中的 AI 健康响应验证其他探测会立即开始，最终 AI 卡片仍展示本次检查得到的模型状态；旧逻辑下测试失败，修复后通过。
- 本批验证：完整 `npm test` 537/537；`npm run build:public`、`npm run check:public`、`npm run check`、`git diff --check` 均通过。
- 同步状态：源码提交 `47e42ff` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（二百零七）

- 备份状态读取隔离：管理员状态接口此前会同步调用备份调度器 `check()`；当备份目录含有当日恢复点时，HTTP 读取会同步执行 SHA-256 与 SQLite 完整性校验，可能阻塞 archive 服务。现接口只返回调度器缓存状态，完整校验仍由启动后的后台调度与定时重试执行；调度执行错误也不会被只读页面请求触发。
- 回归覆盖：认证集成测试将备份目录设置为普通文件并显式启用调度，管理员查询必须仍返回 `pending`；旧逻辑会立即运行目录校验并返回 `failed`，修复后通过。
- 本批验证：认证专项 11/11；完整 `npm test` 537/537；`npm run check`、`npm run check:public`、`git diff --check` 均通过。
- 同步状态：源码提交 `ce54b6b` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（二百零八）

- archive 服务退出清理：自动备份调度器原有 `stop()` 可取消定时器并终止正在运行的备份子进程，但服务未监听 `SIGINT/SIGTERM` 调用它，重启时可能遗留备份进程。现服务捕获两类信号，停止调度并关闭 HTTP 接收，3 秒后强制清理遗留连接。
- 回归覆盖：archive 真实 HTTP 冒烟进程收到 `SIGTERM` 后应以正常退出码关闭；旧代码以 `signal: SIGTERM` 直接中止，修复后通过。
- 本批验证：archive 启动/退出专项通过；完整 `npm test` 537/537；`npm run check`、`npm run check:public`、`git diff --check` 全通过。
- 同步状态：源码提交 `4c0586d` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（二百零九）

- 归档恢复目标符号链接回归：恢复流程已有实现会拒绝数据库路径为符号链接，但缺少直接测试。新增真实 SQLite 数据库与备份用例，验证恢复遇到目标数据库符号链接时明确失败，不替换链接、不修改链接目标，也不生成恢复前副本。
- 验证：符号链接恢复专项 2/2；完整 `npm test` 538/538；`npm run check`、`npm run check:public`、`git diff --check` 均通过。未进行浏览器实机交互验收。
- 同步状态：源码提交 `29789cb` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（二百一十）

- 归档恢复失败回滚回归：最终原子替换若失败，恢复脚本需要保留旧数据库及已移除的 SQLite 侧文件。新增子进程故障注入，在暂存数据库重命名时抛出 `EIO`，验证旧数据库字节、`-wal/-shm` 内容均完整，且恢复暂存文件会被清理。
- 验证：该故障注入专项通过；完整 `npm test` 539/539；`npm run check`、`npm run check:public`、`git diff --check` 均通过。确认现有回滚行为正确，本轮仅增补回归覆盖。
- 同步状态：源码提交 `b0c613b` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（二百一十一）

- 归档恢复服务竞态：服务停止检查此前只在验证备份前执行，校验和安全副本准备期间若重新启动服务，脚本仍会替换其数据库。现于破坏性侧文件清理和数据库替换之前再检查一次；故障时旧数据库不变。确定性测试在旧实现上复现了误替换，修复后验证拒绝恢复。
- 自动备份测试等待条件：全量测试偶发在 `VACUUM INTO` 创建数据库文件、校验文件仍在写入时提前调用验证器。现等待备份本体和校验文件通过完整校验后再断言，仍保留 10 秒失败超时。
- 验证：归档调度/恢复专项 27/27；完整 `npm test` 540/540；`npm run check`、`npm run check:public`、`git diff --check` 均通过。未进行浏览器实机交互验收。
- 同步状态：源码提交 `6d11cac` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（二百一十二）

- 恢复临时文件权限：实测发现恢复前数据库副本复制完成、后续 `chmod 600` 执行前短暂继承了源文件的 `0644` 权限。现恢复暂存库、安全副本与回滚侧文件均通过独占创建的 `0600` 目标和 1 MiB 分块复制写入；打开源文件时拒绝符号链接并校验 inode，复制失败仅清理本次创建的同一文件。
- 回归在最终权限设置前检查暂存库和安全副本权限均为 `0600`，并继续验证服务竞态与失败回滚；旧权限逻辑下安全副本用例会观察到 `0644`。
- 验证：归档调度/恢复专项 27/27；`npm run check`、`npm run check:public` 与差异检查通过；完整 `npm test` 540/540（随后仅增加零字节写入保护，专项再次通过）。未进行浏览器实机交互验收。
- 同步状态：源码提交 `26bc12a` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-28 优化记录（二百一十三）

- 归档安全副本一致性：停止 archive 服务后，仍可能有其他本地进程写入数据库。安全副本复制现在记录源文件字节数，并在复制前后比较同一已打开 inode 的大小、纳秒级修改时间和变更时间；若复制期间发生变化则拒绝恢复，并只清理本次创建的部分副本。
- 回归覆盖：注入一次并发追加写入，旧实现会继续恢复并替换数据库；新实现报“来源在复制期间发生变化”，原库保留外部写入，部分安全副本和暂存文件均清理。
- 验证：归档调度/恢复专项 28/28；完整 `npm test` 541/541；`npm run check`、`npm run check:public`、`git diff --check` 均通过。未进行浏览器实机交互验收。
- 同步状态：源码提交 `944f160` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百一十四）

- 修复 macOS Launcher 安装包：安装器此前以精简 `Info.plist` 覆盖 `osacompile` 生成的 AppleScript applet 元数据，并在修改后留下无效签名。现通过 PlistBuddy 保留原始 applet 配置、补充 `gameops://` URL Scheme，随后对完整 bundle ad-hoc 签名并严格验证，成功后才替换已安装版本。经授权更新并重启本机 Launcher，runtime `.env` 保留；控制器及六个服务健康接口均返回 HTTP 200。
- AI 洞察契约收紧：结果渲染将 watchouts 上限统一为 2 条，避免前端实际展示数超过提示约定；新增三条输入只展示两条的回归测试。
- 归档恢复测试隔离：恢复安全检查此前使用默认端口 8796，碰到在线 Launcher 时会把真实服务误判为测试目标。测试现在使用专属端口 19724；服务保持在线时仍能完整验证恢复保护逻辑。
- 验证：完整 `npm test` 544/544；`npm run check`、`npm run check:public`、`npm run launcher:check`、`git diff --check` 均通过；7 个本机服务健康接口均为 HTTP 200。未进行浏览器实机交互验收。
- 同步状态：源码提交 `2b40d22` 已推送到 GameOps `main`；本条记录随当前批次同步至 Obsidian `main`。

## 2026-09-29 优化记录（二百一十五）

- KOL/KOC 示例名单改为显式载入，默认空名单并跟随当前项目；示例数据载入后始终提示“仅供功能演示，不代表真实合作数据”。编辑名单会将来源降为未核验，表格导入标记为已导入。
- 创作者来源标记随项目档案和本机快照保存/恢复；旧档案或旧快照缺少来源字段时按“未核验”展示，不会误标为真实数据；恢复快照会重置来源，避免沿用上一次状态。
- 验证：针对性测试 34/34；完整 `npm test` 549/549；`npm run build:public`、`npm run check:public`、`npm run check`、`npm run launcher:check`、`git diff --check` 均通过。Edge 实测：当前项目鸣潮的创作者筛选默认空白；载入 10 条示例后来源警示正确；刷新后回到空白状态。
- 同步状态：源码提交 `3bd9ed5` 已推送到 GameOps `main`；本条记录随 Obsidian `main` 推送。

## 2026-09-29 优化记录（二百一十六）

- KOL/KOC 名单编辑后，旧评分对应的单条入库、批量入库、加入今日待办与效果回填均停用；只有重新生成筛选表后才恢复。freshness 检查也放在写入入口，避免仅依赖按钮禁用。
- 完整运营方案生成时，只有名单仍匹配已分析输入才复用历史效果回填行；名单已改动则基于当前输入重新分析，防止旧达人数据进入新报告。
- 验证：创作者专项 16/16；完整 `npm test` 552/552；`npm run build:public`、`npm run check:public`、`npm run check`、`npm run launcher:check`、`git diff --check` 均通过。Edge 实测：改名单后旧结果操作按钮全部禁用；重新筛选后按新输入显示未核验提示并恢复操作。刷新后恢复到鸣潮空名单。
- 同步状态：源码提交 `7cd7d63` 已推送到 GameOps `main`；本条记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百一十七）

- 演示前自检改为只认可与当前输入匹配的 KOL/KOC 评分结果；名单编辑后不再把旧评分计为“已有数据”，并提示重新生成筛选表。
- 回归覆盖：分别验证输入变更后旧行不通过、当前分析行通过；旧实现下测试失败。
- 运行状态复核：Launcher runtime 与源码一致，本机控制器及 6 个服务项均在线，归档存储 ready，因此无需覆盖安装或重启 Launcher。

## 2026-09-29 优化记录（二百一十八）

- 完整运营报告新增 KOL/KOC 来源未核验警告，指出达人评分与合作建议仅供参考，并提示核对账号、报价与数据；不再以“未检测到样例兜底标记”掩盖手动名单的核验状态。
- 回归覆盖：为报告质量状态提供“名单来源未核验”输入，确认输出明确警告且不落到通用无样例文案；旧实现下测试失败。
- 本批验证：创作者专项 18/18；完整 `npm test` 554/554；`npm run build:public`、`npm run check:public`、`npm run check`、`npm run launcher:check` 与 `git diff --check` 均通过。未进行浏览器实机交互验收。
- 同步状态：源码提交 `fcfda3d` 已推送到 GameOps `main`；本条记录随本批同步至 Obsidian `main`。

## 2026-09-29 优化记录（二百一十九）

- 创作者演示自检空输入提示：首次进入时尚未分析名单，旧逻辑把“尚无分析结果”误判为“名单已修改”，提示用户重新生成筛选表。现只有存在历史分析输入且当前名单不匹配时才显示过期提示；初始空状态仍建议导入或载入示例。
- 回归覆盖：同一测试验证过期名单、当前名单与首次空白状态，防止空白页误报。

## 2026-09-29 优化记录（二百二十）

- 每日工作台跨项目离线缓存隔离：平台历史读取失败时，原逻辑会沿用上一个项目的成功快照，却把它显示在新项目名下。现仅在前后项目一致时保留最后成功历史；切换项目后不展示旧项目快照。
- 回归覆盖：验证同项目离线刷新保留快照，切换到其他项目后快照清空且项目标识更新；修复前测试会读到旧项目数据。

## 2026-09-29 优化记录（二百二十一）

- AI 洞察补全热点平台口径：从平台快照、洞察上下文、上下文指纹和用户提示一路传递平台名至 LLM；提示词将平台当作不可信业务数据处理，隐私说明也披露该字段会在用户主动生成洞察时发送，避免跨平台建议或平台切换后复用旧洞察。
- 回归覆盖：验证平台写入输入标签、平台变更使洞察指纹变化、隐私说明披露发送字段、LLM 请求正文包含平台名。
- 本批验证：创作者专项 18/18；每日队列跨项目缓存专项 1/1；完整 `npm test` 554/554；`npm run build:public`、`npm run check:public`、`npm run check`、`npm run launcher:check`、`git diff --check` 均通过。Launcher runtime 与源码一致，控制器及 6 个服务在线，归档存储 ready。
- Launcher 安装备注：授权更新时 `lsregister` 因 Spotlight 返回 `-10822`；跳过 LaunchServices 登记后 runtime 与 app bundle 文件更新成功，并通过已安装 runtime 的重启脚本恢复 6 个服务。直接 `open -a` 仍返回 `-10827`，因此 macOS 应用注册/启动尚未验证成功；浏览器中的服务健康与数据接口已恢复。
- 同步状态：源码提交 `f6f77c7` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百二十二）

- 创作者档案身份升级：当旧档案只有主页 URL、后续补充账号 ID 并改名时，按主页别名找回并迁移原档案；若主键与主页别名并存，则合并合作历史，避免重复档案或历史断链。
- 合作复盘保存：仅选择“推荐再次合作/不建议合作”也会生成合作历史；默认“待观察”不会单独制造空记录，保存提示按实际是否记录复盘显示。
- 存档写入幂等保护：快照、待办、发布台账和风险工单保存规范化请求的 SHA-256 指纹；同一幂等键重放不同内容返回 409，而相同内容仍安全重试。指纹不回传 API；未编辑的旧记录会补齐指纹，已编辑旧记录保持兼容。
- 晨报调度容错：单项目领取运行记录失败会被隔离，不阻止其他项目继续；运行状态写失败和定时任务意外异常均被捕获并记录，避免未处理 Promise 影响服务进程。
- 达人 Brief 补足明确输入：生成建议时带上填写的目标游戏与目标受众，不更改现有评分口径。
- 验证：KOL/KOC 专项 23/23；幂等接口与晨报调度专项通过；完整 `npm test` 567/567；`npm run check`、`npm run build:public`、`npm run check:public`、`npm run launcher:check` 和 `git diff --check` 通过。Edge 页面确认 KOL/KOC 工作台可加载；当前没有可推进达人，生成卡片由专项测试验证。
- Launcher：runtime 安装完成并与源码一致。直接重启命令因 8793 控制器端口仍占用而返回 `EADDRINUSE`；只读状态确认现有控制器健康，6 个服务均运行、归档存储 ready，因此未重复重启。LaunchServices 注册仍未验证。
- 同步状态：源码提交 `2f5cc29` 已推送到 GameOps `main`；本记录已随 Obsidian 提交 `438aabc` 推送到 `main`。

## 2026-09-29 优化记录（二百二十三）

- 幂等键冲突提示可读化：存档接口仍以 HTTP 409 拒绝“同一幂等键写入不同内容”，`error` 改为可直接展示的中文恢复建议，并用独立 `code: idempotency_key_reused` 保留机器识别字段，避免界面把内部错误码直接显示给用户。
- Launcher 安全重启兜底：控制器健康在线但无法验证进程归属时，重启脚本明确拒绝重复启动并提示检查 `/status`；不尝试终止未知进程，也不再让用户只看到 `EADDRINUSE`。
- 验证：新增重启脚本回归用例；定向冲突测试通过；完整 `npm test` 568/568；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 通过。
- Launcher：已更新用户级 runtime 并保留运行配置，`npm run launcher:check` 通过；经安装 runtime 的安全重启脚本恢复控制器及 6 个服务，健康接口正常、存档 `ready`。本次跳过 LaunchServices 重新登记，故 Finder/`open -a` 启动仍未验证。
- 同步状态：源码提交 `c29a013` 已推送到 GameOps `main`；本记录已随 Obsidian 提交 `8c1df4a` 推送到 `main`。

## 2026-09-29 优化记录（二百二十四）

- 项目槽位恢复同步每日工作台：从本机槽位或项目快照恢复后，在输入与分析状态都复原完成时更新每日工作台的项目/版本主题提示，并刷新活动中的行动队列，避免页面仍显示旧项目、实际新待办却归属新项目。
- 回归覆盖：恢复“绝区零”及新版本主题后，断言项目上下文与待办队列刷新都读取恢复后的值；旧实现下测试失败。
- 验证：槽位专项 8/8；完整 `npm test` 569/569；`npm run check`、`npm run build:public`、`npm run check:public`、`npm run launcher:check` 和 `git diff --check` 通过。
- Edge 只读验收：刷新后每日工作台显示“已连接”，行动队列汇总 0 条；平台表格分别标明 B 站真实热点与小红书样例存档，没有把样例伪装成实时数据。未改动或覆盖个人项目槽位。
- Launcher runtime 已同步且检查一致；控制器及 6 个服务仍在线，存档 ready。无需重启后端。
- 同步状态：源码提交 `0a5eaba` 已推送到 GameOps `main`；本记录已随 Obsidian 提交 `192fcc5` 推送到 `main`。

## 2026-09-29 优化记录（二百二十五）

- 趋势图稀疏数据空态：单日存档不再被绘制成横跨整张图的 100% 色块，改为提示“仅有 1 天数据，积累更多存档后再看趋势”；图表 aria-label 也同步说明当前不足以判断趋势。多日数据图与无数据提示保持原行为。
- 回归覆盖：用单个热点日期验证不会生成 `.trend-bar`、用户可见空态与屏幕阅读器说明一致；旧实现下测试失败。
- 验证：图表专项 2/2；完整 `npm test` 570/570；`npm run check`、`npm run build:public`、`npm run check:public`、`npm run launcher:check` 和 `git diff --check` 通过。
- Edge 刷新后每日工作台保持已连接；图表辅助名称报告仅有 1 天数据。Launcher runtime 已同步，未重启未变更的后端服务。
- 同步状态：源码提交 `786bda5` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百二十六）

- AI 洞察补齐平台历史存档后备：当前页没有热点快照且工作队列为空时，改用当前项目 24 小时内最新、结构有效的服务端热点存档；当前页实时快照仍优先，过期、损坏或其他项目的存档不会进入洞察。
- 来源口径：热点范围和来源随存档传递；洞察输入与 LLM 提示均明确标注“服务端历史热点存档、存档时间、不是本次抓取结果”，避免把存档包装成实时数据。后续新存档增加筛选范围和热点条数。
- 回归覆盖：近期有效存档可启用洞察；过期/损坏/其他项目存档被排除；当前快照优先；历史来源标签传入 AI 提示。相关定向测试 3/3；完整 `npm test` 571/571；`npm run check`、`npm run build:public`、`npm run check:public`、`git diff --check` 均通过。
- Edge 只读验收：重载后页面连接正常。队列为 0、当前页无热点快照、仅有 9/29 的 B 站服务端存档时，AI 洞察按钮仍启用；未点击生成，没有触发外部 AI 调用。8/25 的小红书样例仍标为历史样例，不作为近期后备信号。
- Launcher：运行目录已与源码同步；使用已安装 runtime 的安全重启脚本后，六个服务在线且存档 `ready`。中途从源码目录重启因无法核验已安装进程归属而安全拒绝；未终止未知进程。
- 同步状态：源码提交 `b536481` 已推送到 GameOps `main`；本记录随本次更新推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百二十七）

- 跨标签页服务模式集成回归：把存档区与每日工作台的会话监听放进同一测试，验证 local → online 后发布/风险列表清空、旧待办请求取消、旧待办快照与 AI 洞察失效，并按新模式重新加载。
- 本次为测试覆盖加固，没有发现需要改动的业务逻辑；此前对项目槽位恢复的审计也确认当前实现已有上下文刷新与专项回归，不重复修改。
- 验证：完整 `npm test` 572/572；最终测试文件 163/163；`npm run check`、`git diff --check` 通过。
- 同步状态：源码提交 `bb4c183` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百二十八）

- 服务模式存储故障兜底：浏览器无法写入 `localStorage` 时，当前标签页继续使用用户刚选择的本地/线上模式，避免服务端点已切换但模式状态、队列缓存身份仍沿用旧值；跨标签 `storage` 更新会刷新该内存覆盖值，页面重载后仍遵循可用的持久值或默认模式。
- 回归覆盖：先确认旧实现可复现（写入异常后仍报告 local），再验证失败写入与跨标签模式变化都保持端点和模式一致。
- 验证：完整 `npm test` 572/572；服务模式定向 2/2；`npm run check`、`npm run build:public`、`npm run check:public`、`git diff --check` 通过。
- 同步状态：源码提交 `f177535` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百二十九）

- 清除站点数据后的跨标签复位：监听 `localStorage.clear()` 产生的 `storage` 事件（`key === null`），将当前页临时服务模式恢复为环境默认值，避免沿用已经被清除的旧模式。
- 回归覆盖：先复现线上模式下清空 storage 后当前页仍读到 online，再验证端点回到本地默认；服务模式专项 20/20。
- 验证：完整 `npm test` 573/573；`npm run check`、`npm run build:public`、`npm run check:public`、`git diff --check` 通过。
- 同步状态：源码提交 `9d2efa4` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百三十）

- 跨标签服务模式竞态：延迟到达的旧 `storage` 事件不再覆盖本机当前已持久化的模式，也不能在 `localStorage.clear()` 后重建旧模式；优先读取当前存储值，只有读取失败时才使用事件值兜底。
- 回归覆盖：验证旧 online 事件晚于用户选择 local、以及 storage 清除后旧模式事件晚到，两种情况下模式与请求端点都保持当前状态。
- 验证：完整 `npm test` 575/575；`npm run check`、`npm run build:public`、`npm run check:public`、`git diff --check` 通过。
- 同步状态：源码提交 `c9f8dec` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百三十一）

- 每日待办午夜边界：创建待办时主动刷新上海业务日期；如果默认截止日仍是昨天，会在提交前更新为今天，避免午夜后五分钟内新增任务立刻显示逾期。用户手动设定的截止日期仍由现有刷新逻辑保留。
- 回归覆盖：模拟日期已跨到 9 月 29 日、五分钟定时器尚未触发且输入仍是 9 月 28 日；新增待办的请求体现已使用 9 月 29 日。旧实现下用例失败。
- 验证：完整 `npm test` 576/576；`npm run check`、`npm run build:public`、`npm run check:public`、`git diff --check` 通过。
- 同步状态：源码提交 `7ddcac7` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百三十二）

- AI 洞察补足热点历史读取失败口径：当历史热点存档不可用时，将该状态传进输入标签和 LLM 提示；模型不得把“未同步”解释为“没有热点”或历史趋势。当前热点快照仍可单独作为当前信号使用。
- 回归覆盖：分别验证历史不可用无快照、历史不可用但有当前快照、以及可用服务端历史存档三种情况；LLM 集成测试确认不确定性与当前信号可用性都进入提示。

## 2026-09-29 优化记录（二百三十三）

- 存档备份并发轮转：对快照、校验与保留清理整体使用 SQLite 跨进程排他锁；竞争进程排队，异常退出时由 SQLite 释放锁。锁路径拒绝符号链接，避免误改链接目标权限。
- 回归覆盖：4 个并发备份、`keep=1` 后仍保留一份校验有效恢复点；符号链接锁被拒绝且目标文件内容/权限不变。

## 2026-09-29 优化记录（二百三十四）

- 创作者 CSV 导入往返：导出表中同时有达人“类型”和“内容类型”时，导入优先读取精确的“内容类型”表头，避免“垂类 KOC”等达人档位覆盖“攻略”等内容类型。
- 回归覆盖：以真实导出列顺序执行 CSV 解析、字段映射和创作者解析，确认内容类型原值保留。

## 2026-09-29 优化记录（二百三十五）

- 创作者当前候选效率分纳入实测成本：回填成本后 CPM/CPE 与性价比分使用实际成本；尚未回填则继续使用预估报价；显式 0 元成本仍按有效实测值处理，报价仍用于候选资格与推荐约束。
- 验证：实测成本、估算成本与零成本均覆盖 CPM 和性价比分；界面评分口径已同步说明。
- 本批完整验证：`npm test` 582/582；`npm run check`、`npm run build:public`、`npm run check:public`、`git diff --check` 均通过。未进行真实浏览器交互验收。
- 同步状态：源码提交与 GitHub 推送、Obsidian 记录提交与推送待完成。

## 2026-09-29 优化记录（二百三十六）

- 今日简报读取竞态：简报启动的队列请求被手动刷新抢占时，现在继续等待最新一轮请求结束，再采集简报数据，避免把仍在加载中的旧快照误报为待办、风险和发布回流全部不可用。
- 回归覆盖：一个用例控制简报读取被刷新替代，断言最新请求结束前不采集；另一个直接验证等待器会跟随更新后的请求 Promise。

## 2026-09-29 优化记录（二百三十七）

- Launcher 自检准确性：源文件缺失即使 runtime 仍有副本也会失败；检查已安装 app 配置中的 Node 路径是否存在且可执行，避免 Node 版本管理器升级清理旧路径后仍错误报绿。检查逻辑可隔离测试，提示不回显本机绝对路径。
- 本批验证：`npm test` 586/586；`npm run check`、`npm run build:public`、`npm run check:public` 和 `git diff --check` 均通过。更新前 `npm run launcher:check` 检出 runtime 的 `llm-server.js`、`scripts/backup-archive.js` 与源码不一致；待按既有授权安装后再次验证。
- 同步状态：源码提交 `6d46136` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百三十八）

- 管理员接管旧匿名数据时处理幂等键冲突：若 `default` 与管理员账号已有相同 `request_id`，迁移前仅重映射旧匿名行的键，保留管理员原键、两边业务数据和请求指纹，避免唯一约束使整个迁移回滚。
- 回归覆盖：快照、发布、风险工单、每日待办四类记录均构造同键冲突；验证管理员幂等键不变，旧行指纹与记录完整保留且获得确定性迁移键。
- 验证：完整 `npm test` 587/587；`npm run check`、`npm run build:public`、`npm run check:public`、`npm run launcher:check` 与 `git diff --check` 通过。Launcher runtime 已更新并与源码一致；安全重启后控制器报告六项服务运行，热点、评论、OCR、LLM 与存档健康检查通过。
- 边界：为规避已知 LaunchServices 扫描错误，安装跳过了注册步骤，因此系统协议注册状态仍未验证。项目/创作者档案及晨报记录的自然键冲突策略另待确认，不在本次猜测合并。
- 同步状态：源码提交 `92f0a5d` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百三十九）

- 管理员接管旧匿名数据前增加自然键冲突预检，覆盖项目档案、创作者库和晨报记录；在同一 SQLite 写事务内检查，发现冲突时报告表名与数量并回滚，避免只暴露 SQLite 唯一约束异常。
- 回归覆盖：三个表同时出现旧匿名/管理员自然键冲突时，启动明确返回 `OWNER_MIGRATION_CONFLICT`，两侧数据仍各自保留；旧幂等键冲突与事务失败回滚测试继续通过。
- 验证：完整 `npm test` 588/588；`npm run check`、`npm run build:public`、`npm run check:public`、`npm run launcher:check`、`git diff --check` 通过。Launcher runtime 已同步并重启；控制器、六项服务健康，存档 ready。
- 当前线上写入边界：运行服务返回 `auth_required:false`，尚未创建管理员账号；未擅自开启线上认证。启用前仍需确认个人本机模式或线上登录及管理员密码处理方式。
- 同步状态：源码提交 `d38a74b` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百四十）

- 创作者库并发写入标记改为严格递增：若系统时钟仍停留在已有 `updated_at` 的毫秒内，下一次成功写入使用前值 +1ms，防止两个标签页复用同一乐观锁版本，让旧快照覆盖新资料。
- 回归先用冻结服务时钟复现两次写入版本相同、陈旧写入被接受；修复后第二次标记递增，旧标记请求返回 409，最新个人库保持完整。
- 验证：创作者库定向测试 6/6；完整 `npm test` 589/589；`npm run check`、`npm run build:public`、`npm run check:public`、`npm run launcher:check`、`git diff --check` 通过。runtime 已同步并重启，控制器六项服务运行、存档 ready。
- 同步状态：源码提交 `80fc152` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百四十一）

- 创作者个人库线上同步：登录线上账号后，档案编辑在本地保存成功后进入 500ms 防抖队列，连续修改合并为一次云端同步；访客和 `file://` 本机模式不自动上传。账号切换、手动同步会取消待执行计时，云端合并写回不会递归触发自动同步；保留原有手动同步作为恢复入口。
- 页面已说明线上登录自动同步、访客/本机文件仅本地，以及旧库需要显式迁移；回归测试实际触发稳定账号的防抖计时器，并确认云端同步函数只调用一次。
- 回归覆盖：验证连续保存只留一个计时器、账号切换后旧计时不写入新账号、访客与本机文件模式不上传；旧同步隔离测试的 harness 同步注入取消依赖。
- 验证：完整 `npm test` 590/590；随后创作者库专项 11/11；`npm run check`、`npm run build:public`、`npm run check:public`、`npm run launcher:check`、`git diff --check` 通过。此为自动化与本机静态验证，未用真实线上登录账号做跨浏览器端到端验收。
- 同步状态：源码提交 `45caa78`、`5b87f6c` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百四十二）

- 创作者库断网恢复：同步遇到网络类连接错误时仅为当前已登录账号留下内存重试标记；浏览器触发 `online` 后经 500ms 防抖重试。账号/服务模式切换清除标记，访客和 `file://` 页面不上传，HTTP/数据校验错误不会借网络事件循环重试。状态文案区分连接中断、本机服务停机与数据未受影响。
- 回归覆盖：模拟账号 A 的重试标记在账号 B 登录后被清除；同账号在线恢复触发一次同步；本机文件页不重试；网络错误会留下标记，非网络错误不会；退出/账号切换取消标记，原有本地保护和 409 同步路径仍通过。
- 验证：完整 `npm test` 592/592；创作者库/可访问性/项目一致性定向 187/187；`npm run check`、`npm run build:public`、`npm run check:public`、`npm run launcher:check`、`git diff --check` 通过。未做真实线上浏览器断网/登录 E2E。
- 同步状态：源码提交 `2f77185` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百四十三）

- 创作者库无变化写入：同步接口先校验 `base_updated_at`，再对递归排序后的 JSON 做结构比较；内容相同即返回当前版本、不执行数据库写入或推进 `updated_at`，实际内容变化仍沿用原乐观锁与严格递增版本。
- 回归覆盖：同内容但对象键顺序不同仍被视作无变化；版本过期的同内容请求仍返回 409，不能绕过并发保护；版本匹配的无变化请求返回原 token，读回数据不变。
- 验证：创作者库服务 7/7；完整 `npm test` 593/593；`npm run check`、`npm run build:public`、`npm run check:public`、`npm run launcher:check`、`git diff --check` 通过。runtime 与源码一致；安全重启因无法核验旧控制器进程归属而拒绝操作，未强杀进程；只读 `/status` 确认控制器及六项服务运行、`/ready` 为 ready。线上认证当前仍为关闭状态。
- 同步状态：源码提交 `ef749fe` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百四十四）

- 创作者库跨标签页/浏览器数据新鲜度：线上登录用户每次从其他模块重新进入 KOL/KOC 合作筛选时刷新并合并云端档案；留在当前模块重复点击不重复请求，访客和 `file://` 本机模式保持本地，不触发远端同步。
- 回归覆盖：验证首次进入与离开后重返各触发一次同步，重复选择当前视图不重复同步；未登录和本机文件模式均不触发同步。
- 验证：新增导航行为测试通过；完整 `npm test` 594/594；`npm run check`、`npm run build:public`、`npm run check:public`、`npm run launcher:check`、`git diff --check` 通过。未使用真实线上账号做跨浏览器端到端验证。
- 同步状态：源码提交 `22dcfbb` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百四十五）

- 存档幂等键安全：旧版已编辑记录若没有可验证的请求指纹，不再被当成任意新请求的重复成功；重用该键时返回 `409 idempotency_key_reused`，避免发布、风险或待办被静默吞掉。旧请求仍会通过已存指纹正常重试；冲突不会改写原记录。
- 回归先复现旧逻辑错误地返回 200，再验证 409、旧记录保留、新内容未写入且同键记录数量不增加；现有指纹回填逻辑仍只处理未编辑的旧行。
- 验证：完整 `npm test` 597/597；`npm run check`、`npm run build:public`、顺序执行的 `npm run check:public`、`git diff --check` 通过。
- Launcher 状态：`launcher:check` 发现用户级 runtime 中的 `archive-server.js` 仍旧。按既有授权尝试安装（跳过系统协议注册），但替换运行中的 `GameOpsLauncher.app` 时系统返回 `EPERM`；安装未完成，未重启或强制终止进程。浏览器 QA 也因 macOS 锁屏无法读取页面。解除锁屏并确保 Launcher 可安全替换后需重试；当前不可声称本机运行时已包含该修复。
- 同步状态：源码提交 `4d506d7` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百四十六）

- 每日 AI 洞察刷新竞态：队列重新加载期间若项目/账号和洞察输入信号未变，继续等待原 AI 请求并保留按钮忙碌状态；信号或账号确实变化时丢弃过期响应，并显示“洞察已取消，请重新生成”，不再静默丢结果。
- 回归用延迟 AI 请求验证：同一信号在 loading 与完成渲染期间刷新仍展示成功结果；不同信号刷新会拒绝旧响应、隐藏旧结果并提示重新生成。
- 验证：AI 洞察/每日洞察/账号切换定向测试 14/14；完整 `npm test` 597/597，`npm run check`、public 构建/校验和 `git diff --check` 通过。当前浏览器自动交互未能执行，macOS 当时处于锁屏。
- 同步状态：源码提交 `1b86db6` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百四十七）

- 部署备份门禁：`deploy:check` 现在复用备份目录安全校验，提前拒绝文件系统根目录、用户主目录及其上级目录，避免服务上线后自动备份失败、没有有效恢复点；默认备份目录和安全的嵌套目录仍通过。
- 回归覆盖：根目录、用户主目录、其上级均返回部署失败和可读原因；专用临时子目录通过。
- 验证：部署检查专项 3/3；完整 `npm test` 597/597；`npm run check`、public 构建/校验、`git diff --check` 通过。
- 同步状态：源码提交 `1ccf6d3` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百四十八）

- 创作者个人库 HTML 注入回归防护：安全审计检查了个人库、合作历史、简报、AI 输出、热点详情和工作队列等动态渲染边界，未确认现有可利用注入；新增真实执行 `renderCreatorLibrary()` 的回归测试，将达人名称、平台、档案 key、备注、合作项目和复盘结果替换为恶意 HTML，确认输出只保留转义文本，不生成 `img`、`script` 或 `svg` 标签。
- 验证：创作者库专项 14/14；完整 `npm test` 598/598；`npm run check`、`npm run check:public`、`git diff --check` 通过。只新增测试，无运行时代码变化；浏览器交互仍受 macOS 锁屏限制，未做真实 DOM 浏览器验收。
- 同步状态：测试提交 `1fa8e32` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百四十九）

- LLM 上游地址拼接与部署校验：原实现直接把 `/chat/completions` 追加在原始字符串后，`LLM_BASE_URL` 带版本 query 时会请求错误路径（例如 `/v1?tenant=studio/chat/completions`）。现在通过 URL pathname 拼接 endpoint、保留 provider query，并拒绝内嵌账号密码和 fragment；`/ready` 与部署检查共用同一校验。
- 回归先在本机 OpenAI 兼容假上游上复现错误 request path，修复后确认收到 `/v1/chat/completions?tenant=studio`；另覆盖账号密码、fragment、HTTPS 规则及部署门禁，版本 query 仍可通过。
- 验证：上游 URL 定向 11/11；LLM 上游服务级定向 2/2；部署门禁专项 1/1；完整 `npm test` 601/601；`npm run check`、`npm run check:public`、`git diff --check` 通过。浏览器 UI 验收仍因 macOS 锁屏未完成。
- 同步状态：修复提交 `2ef9891` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百五十）

- 扩展线上多账号隔离端到端回归：以管理员和成员两个真实登录会话验证项目档案、创作者库、快照、发布记录与风险工单各自只读到本人数据；跨账号删除发布/风险记录返回 404；成员写入管理员同名项目档案不会覆盖管理员数据。
- 验证：`tests/archive-auth.test.js` 11/11；完整 `npm test` 601/601；`npm run check`、`npm run check:public`、`git diff --check` 通过。本次仅强化隔离测试，不改变认证或数据行为。
- 同步状态：测试提交 `4d37ac6` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百五十一）

- 归档恢复拒绝猜测监听端口：若恢复命令没有从当前环境或项目 `.env` 得到 `ARCHIVE_PORT`，现在在触碰数据库前退出；要求端口与正在运行的 archive 服务一致，避免 PM2 使用自定义端口时只探测默认 8796、误判停服并替换活动数据库。
- 回归在临时 SQLite 库中启动 19717 端口服务，模拟默认 8796 探针连接被拒绝；旧逻辑会在服务仍运行时成功替换数据库，新逻辑以配置错误拒绝且库内容不变。恢复文档补充端口配置示例。
- 验证：归档备份/恢复专项 25/25；完整 `npm test` 601/601；`npm run check`、`npm run check:public`、`git diff --check` 通过。
- 同步状态：源码提交 `e6dbb1c` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。

## 2026-09-29 优化记录（二百五十二）

- 跨标签切换账号后刷新账号隔离视图：新账号登录或服务模式变化时重新加载项目档案，并在每日工作台当前活动时安排待办/风险/发布回流队列刷新；退出登录时不请求受保护数据。移除登录表单重复触发的刷新，统一由已验证的会话变更事件驱动。
- 回归覆盖：账号 A→B 时项目档案与每日队列各刷新一次；退出登录不发起受保护数据请求；服务模式变化也加载当前模式的档案与队列。
- 验证：相关账号/服务模式用例通过；完整 `npm test` 601/601；`npm run build:public`、`npm run check`、`npm run check:public`、`git diff --check` 通过。真实浏览器 E2E 因 Mac 锁屏未完成。
- 同步状态：源码提交 `700a617` 已推送到 GameOps `main`；本记录待推送到 Obsidian `main`。
