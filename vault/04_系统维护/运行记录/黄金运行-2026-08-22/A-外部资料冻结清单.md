# A3 · 外部资料清单冻结（黄金运行-2026-08-22）

- 冻结时间：2026-08-22T15:2xZ（UTC，见各条目时间戳）
- 冻结原则：本轮隔离场景聚焦"游戏市场运营"；先冻结【源级清单】，抓取完成后、入库前再冻结【条目级清单：来源URL+抓取时间】，两段均落盘留证。
- 隔离配置副本：`horizon-run/data/config.json`（原始配置备份于 输入快照/horizon-config-backup-20260822T1515Z.json；原 ~/horizon/data/config.json 因沙箱拒绝写入而未被改动，证据：验证/工具-horizon配置补丁.py 运行输出的 PermissionError）

## 源级清单（Horizon 配置副本实际生效源）

| # | 源名 | 类型 | URL | 状态 | 备注 |
|---|------|------|-----|------|------|
| 1 | 机核gcores | rss | https://www.gcores.com/rss | 既有源（第03章配置） | 探活200 |
| 2 | GamesIndustry.biz | rss | https://www.gamesindustry.biz/feed | 既有源（第03章配置） | 行业媒体 |
| 3 | 游戏陀螺 | rss | https://www.youxituoluo.com/rss | 本轮新增 | 探活200 |
| 4 | GameLook | rss | http://www.gamelook.com.cn/feed/ | 本轮新增 | HEAD拒绝但GET 200 |
| 5 | Eurogamer | rss | https://www.eurogamer.net/feed | 本轮新增 | 探活200 |
| 6 | Rock Paper Shotgun | rss | https://www.rockpapershotgun.com/feed | 本轮新增 | 探活200 |
| B | 黄金运行-坏源测试 | rss | https://nonexistent-goldenrun.invalid/feed.xml | 本轮新增·故意坏源 | RFC2606保留TLD，DNS必然失败，用于Horizon失败真实性测试 |

- 隔离决策：副本中 hackernews.enabled=false、github 全部 enabled=false——黄金运行为隔离场景，避免聚合大源噪音与重复内容（08-21批次已入库17张），聚焦游戏行业源。此决策记录于 验证/工具-horizon配置补丁-v2-隔离副本.py。
- 抓取命令（后台执行）：`cd ~/horizon && ./.venv/bin/horizon -d <evidence>/horizon-run/data --hours 30`（uv 缓存被沙箱拒后的合法等价入口，机制同 runner 的 SM_HORIZON_CMD）；日志落盘 验证/B1-horizon抓取日志.log

## 条目级清单（抓取完成后、入库前锁定；2026-08-22T15:24Z）

抓取结果：Horizon 隔离轮共产出 **22** 条（zh 日报 horizon-2026-08-22-zh.md，418行）；另 1 条在富集阶段失败被跳过（rss:www.youxituoluo.com_rss:be2c7f7226e1790e，日志67行）——失败如实留证。坏源"黄金运行-坏源测试"按预期 DNS 失败（日志23行 WARNING Error fetching）。

本黄金运行的 **5 条冻结输入**（选择标准：覆盖市场数据/行业战略/竞品动态）：

| # | 标题 | 来源URL | 所属源 | 抓取时间(本地) |
|---|------|---------|--------|----------------|
| 1 | 网易 Q2 游戏收入 250 亿元，多款新品进入密集测试 | https://www.youxituoluo.com/534816.html | 游戏陀螺 | 2026-08-22 23:21–23:22 |
| 2 | 合成赛道寡头化：头部月入近亿美元，破局者靠题材创新 | https://www.youxituoluo.com/534817.html | 游戏陀螺 | 同上 |
| 3 | 索尼转向服务型游戏的巨大机会成本 | https://www.gamesindustry.biz/the-opportunity-cost-of-sonys-live-service-pivot-is-enormous-opinion | GamesIndustry.biz | 同上 |
| 4 | Xbox 主机广告或利好游戏业 | https://www.gamesindustry.biz/why-xboxs-console-ads-could-be-a-good-thing-for-gaming-opinion | GamesIndustry.biz | 同上 |
| 5 | 《绝区零》首席美术离职米哈游，将开发种田游戏 | https://www.youxituoluo.com/534818.html | 游戏陀螺 | 同上 |

- 其余 17 条（Roblox AI安全模型开源⭐7、Double Fine IP独立、GTA6泄露投毒警告等）随同一适配器批次一并入库保留来源——黄金运行输入以上表 5 条为准，其余作为主题上下文语料。
- 冻结即生效：适配器只解析本轮隔离 summaries（仅 zh/en 两个文件），不回扫历史。
- 入库执行：`cd ~/horizon && ./.venv/bin/python 系统/horizon_adapter.py --data-dir <evidence>/horizon-run/data`（幂等判重：frontmatter id + 目标文件名）。

## 已知降级/偏差登记

- 【沙箱限制】~/horizon 原配置不可写（PermissionError ×1，未重试）→ 采用官方 -d/-c 隔离副本机制，效果等价且不污染原配置。
- 【历史资料】教程要求2份，实收1份（详见 10-施工报告 降级标注汇总）。
