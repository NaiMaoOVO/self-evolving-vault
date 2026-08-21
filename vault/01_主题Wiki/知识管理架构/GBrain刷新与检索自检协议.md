---
title: GBrain刷新与检索自检协议
type: knowledge
status: stable
created: 2026-08-22
updated: 2026-08-22
source: "[[AGENTS]]（vault/AGENTS.md brain-first 协议节）；施工记录/02-刷新协议.md（vault 外，../施工记录/02-刷新协议.md）"
confidence: high
sensitivity: 内部
---

# GBrain刷新与检索自检协议

## 适用条件

- 本工程 GBrain local 模式、brain=evolving-kb；embedding 禁用阶段（import 必须带 `--no-embed`）。
- 任何 vault 内容变化后（写回、新建、改名）。

## 事实

- 刷新契约：Obsidian 写回 → `gbrain import <vault> --no-embed` 增量导入 → 一致性检查。（来源：[[AGENTS]] brain-first 协议节；../施工记录/02-刷新协议.md）
- 一致性主指标：brain Pages 数应等于 vault 内 md 文件数（不含 .obsidian）；chunks 数有滞后噪音，不作主指标。（来源：../施工记录/02-刷新协议.md 实测）
- 文件名全局唯一规则：slug 由文件名生成，同名文件后导入覆盖先导入；重命名产生新旧 slug 并存，旧页面需 `gbrain delete`（软删除，72h 可恢复），删除 brain 页面属授权红线。（来源：同上）
- brain-first 协议：涉及用户、项目、历史决策和知识库内容的问题，先 gbrain 检索再回源核对；检索结果必须附带来源文件路径，无来源结果视为线索而非事实。（来源：[[AGENTS]]）
- 环境注意：gbrain shebang 依赖 bun，须 `export PATH="$HOME/.bun/bin:$PATH"` 后执行。（来源：本章施工实测，2026-08-22）

## 判断

- 【判断】"Pages 数 = md 数 + 抽查独特关键词命中"是当前阶段最低成本的完整性检验，两层缺一不可。

## 假设

- 【假设】embedding 启用后语义检索质量将显著改善——依据见 [[测试-同义语义]] 的"待补配"预期，属未验证预期。

## 证据链接

- [[AGENTS]]（vault 根，brain-first 协议）
- ../施工记录/02-刷新协议.md（vault 外，第02章验收实测）
- [[04_系统维护/蒸馏与结案/蒸馏-2026-08-22|蒸馏-2026-08-22]]（本章 import 实测）

## 冲突并列

- 暂无。

## 机会

- 第07/08章状态机可直接复用本协议作为"索引一致性"健康检查项。

## 风险

- 忽略 PATH 前缀会误报 `env: bun: No such file or directory`，被误判为 gbrain 故障。
- 增量 import 不清旧 slug：改名/移动文件后若不手动 delete，检索会出现双命中噪音。

## relations

- 来源：[[AGENTS]]；../施工记录/02-刷新协议.md
- 主题：[[01_主题Wiki/知识管理架构/GBrain刷新与检索自检协议|知识管理架构]]
- 项目：[[02_项目库/进行中项目/知识库搭建|知识库搭建]]
- 用途：刷新操作规程；状态机健康检查依据
