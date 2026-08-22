# 进化提案目录

用途：存放由重复反馈或结果数据驱动的规则进化提案（复制自 `04_系统维护/规则与画像/模板/进化提案模板.md`）。

命名约定：`提案-YYYY-MM-DD-议题.md`（如 `提案-2026-08-22-分析报告章节结构.md`）。

处理流程：
1. `系统/weekly_evolution.py review` 标注"可提稳定规则"的信号，人工复制模板到本目录填写。
2. 提案 status=`open`（观察中），每条提案只改一条规则（旧规则→新规则一一对应）。
3. 用户显式批准后执行 `系统/weekly_evolution.py apply <提案> --approved`：
   - 目标规则文件 `version+1`（增量，不自动改全局）；
   - 提案 status=`open → accepted`，`updated` 刷新。
4. 否决 status=`rejected`（附理由）；延后 status=`deferred`（附重启条件）。
5. 标 `evolved` 需在下一轮同类任务产出后附前后对照证据（进化协议.md 铁律三）。
