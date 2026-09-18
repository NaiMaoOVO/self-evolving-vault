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

## 关联

- 项目内评审详情：OPTIMIZATION.md（含第一至第四轮全部建议与进度标记）
- 会话中曾求助的子智能体模式：三路并行深读评审（前端/后端/产品）→ 合并去重 → 分批落地
