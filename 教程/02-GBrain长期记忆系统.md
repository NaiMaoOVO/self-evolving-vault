# 02 GBrain长期记忆系统

## 目标

建立可重建的长期检索层，使新agent会话能先查记忆、再回Obsidian原文核对。

## 数据库决策

| 场景 | 默认路线 |
| --- | --- |
| 单人、本机、初次搭建 | PGLite |
| 已有Postgres、数据规模大或长期服务 | Postgres |
| 多人权限隔离、远程agent | 远程服务，单独安全设计 |

不得因为教程作者使用Postgres，就强迫所有读者选择Postgres。

## 施工提示词

```
请安装并配置GBrain。先读取官方仓库当前README、INSTALL_FOR_AGENTS.md、安装文档和目标agent的MCP文档，不使用记忆中的旧命令。步骤：1. 报告官方来源、当前版本、运行时、数据库选择和理由；2. 说明下载、写入路径、端口、权限和外部服务；3. 安装前检查是否已有brain，禁止覆盖；4. secret只写环境变量或被忽略的本地配置；5. 将当前Obsidian vault注册为命名数据源；6. 首次导入前统计Markdown文件数；7. 若embedding会发送私有文本，说明provider、发送内容和成本，等待用户明确授权；8. 完成import、索引和必要embedding；9. 配置Codex/Claude Code/Cursor的官方MCP连接；10. 在AGENTS.md加入brain-first协议：涉及用户、项目、历史决策和知识库内容，先search，再回源文件核对；11. 默认关闭dream、autopilot、自动写回和外发；12. 建立刷新契约：Obsidian写回→增量import→获授权后embedding→一致性检查；13. 建立路径变更、重复slug、失效页面和索引噪音的处理规则。必须生成：- GBrain配置说明；- 数据源清单；- 隐私边界；- 刷新协议；- 故障分类表；- 安装验收记录。
```

## 测试数据

在vault创建三条无敏感测试笔记：

- 精确关键词句；
- 同义语义句；
- 两条互相冲突且带日期的陈述。

## 验证提示词

```
请独立验证GBrain：1. 核对实际数据库引擎，不猜测；2. 对比vault Markdown数、已导入页面数、chunks和embedded数；3. 精确关键词检索必须命中正确来源；4. 语义检索必须命中相关页；5. 冲突查询必须同时返回两条来源，不擅自合并；6. 新建笔记后执行增量刷新，再检索；7. 新开agent会话，通过MCP检索同一测试句；8. 停止GBrain后确认Obsidian文件仍完整可读；9. 搜索vault和Git跟踪文件，确认无secret；10. doctor/health警告必须解释影响。分类失败：权限/沙盒、运行时、数据库连接、导入、索引一致性、embedding、MCP、外部provider。输出PASS/CONDITIONAL PASS/FAIL。
```

## 通过标准

- 跨会话检索可用且来源正确。
- GBrain故障不破坏Markdown真相源。
- 页面、索引和embedding状态可解释。
