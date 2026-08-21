# 02-GBrain配置说明

- 施工日期：2026-08-21（安装与首次导入）/ 2026-08-22（MCP 配置与本文档）
- 施工者：第02章施工子智能体（第二阶段）

## 基本信息

| 项目 | 值 |
| --- | --- |
| gbrain 版本 | 0.46.24.0（0.46.25.0 可升级；`self_upgrade.mode=notify`，不自动升级） |
| 安装方式 | bun 全局安装，二进制位于 `~/.bun/bin/gbrain` |
| PATH 说明 | `~/.bun/bin` 不在默认 PATH，使用前需 `export PATH="$HOME/.bun/bin:$PATH"` 或用绝对路径 |
| 数据库引擎 | PGLite（本地单文件，无 server、无端口） |
| 数据库路径 | `~/.gbrain/brain.pglite`（schema 132） |
| schema pack | `gbrain-base-v2@1.0.0+f4f6494a`（当前，无升级提示） |
| brain 主目录 | `~/.gbrain/`（全部本地，无云端） |

## 关键配置（`gbrain config show` 实测）

| 配置项 | 值 | 说明 |
| --- | --- | --- |
| engine | pglite | 单人、本机、初次搭建 → 按教程默认路线选 PGLite |
| search.mode | conservative（db plane） | 检索扩展保守模式，减少无依据扩展 |
| embedding | **disabled（用户决定暂不配置，待补配）** | 当前 0 chunks embedded；语义检索降级为关键词（见下） |
| dream / autopilot / 自动写回 / 外发 | 全部关闭 | 用户决定；doctor 的 cycle_freshness 警告即由此产生，属预期 |

## embedding 待补配事项（未来启用前必须先处理）

- `gbrain config show` 显示 `embedding_disabled: true`；启用需用户单独按批授权（见 `02-隐私边界.md`）。
- doctor 实测警告（启用前需先修复，否则索引宽度不一致）：
  - embedding 列 `vector(1024)` 与声明的 `embedding_dimensions=1280` 不一致；
  - 默认 embedding model 为 `zeroentropyai:zembed-1`，其托管 API 将于 **2026-09-04 关停**，且当前未配置 API key。
- 可选迁移目标（doctor 给出）：`voyage:voyage-4 --dim 1024` 或 `openai:text-embedding-3-small --dim 1024`；启用前用 `gbrain migrate embeddings --to <p:model> --dry-run` 预览。

## 关键命令（本机实测有效）

```bash
export PATH="$HOME/.bun/bin:$PATH"   # 每次 shell 先执行

gbrain stats                         # 页面/chunk/embedding 计数
gbrain doctor [--fast]               # 健康检查（警告逐条见 02-安装验收记录.md）
gbrain sources list                  # 数据源清单
gbrain sources status                # 各源健康面板
gbrain search "关键词"                # 纯关键词检索（tsvector）
gbrain query "问题" [--no-expand] [--json]   # 混合检索（RRF + 扩展）；--json 含 source_id
gbrain import <dir> --no-embed       # 导入/增量导入 markdown 目录（embedding 禁用期必须带 --no-embed）
gbrain get <slug>                    # 读页面全文（含来源核对）
gbrain list --type note              # 页面清单
gbrain delete <slug>                 # 软删除（72h 内可 restore）；删除属授权红线操作
gbrain serve --surface verbs         # MCP stdio server（7 个记忆动词工具面；由客户端按需拉起，勿常驻）
```

## 已知行为特征（实测，无 embedding 状态下）

- 单个中文关键词检索可靠命中（如"量子苔藓""零电阻""预算"）。
- 多词组合查询行为不一致："项目X 预算"可命中（evidence=keyword_exact），"低等植物 零电阻"返回 `keyword_zero`（与默认 FTS 语言 english 的中文分词有关，`GBRAIN_FTS_LANGUAGE` 可调）。
- 跨文件纯语义检索（不用原词）当前不可用，`query` 明确报 `degraded: embed_unavailable`。
- 详见 `02-安装验收记录.md` 检索测试一节。
