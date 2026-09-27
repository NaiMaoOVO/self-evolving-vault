---
title: 游戏内容运营AI工作台
type: project
status: active
created: 2026-08-23
updated: 2026-09-27
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
