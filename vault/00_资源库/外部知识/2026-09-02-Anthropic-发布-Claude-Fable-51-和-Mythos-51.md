---
id: "e7232d52f37f"
title: "Anthropic 发布 Claude Fable 5.1 和 Mythos 5.1"
author: "denysvitali"
published: "2026-09-01 17:53"
url: https://www.anthropic.com/claude-fable-and-mythos-5-1
source_type: hackernews
source_name: "denysvitali"
fetched_at: 2026-09-02 08:22:45
score: "8.0/10"
tags: [AI, Anthropic, Claude, LLM, Machine Learning]
sensitivity: 公开
source_report: horizon-2026-09-02-zh.md
---
# Anthropic 发布 Claude Fable 5.1 和 Mythos 5.1

## AI 摘要（Horizon 日报）

Anthropic 发布了 Claude Fable 5.1 和 Claude Mythos 5.1，主要改进包括写作风格提升和安全修复。Fable 5.1 的写作风格相比早期 Claude 模型更自然，减少了陈词滥调和未解释的术语，但有时句子更长、段落更少。此次更新包含三项破坏性变更，均针对思维链（chain-of-thought）意外泄露的补丁，例如阻止模型通过伪造的“think_deeply”工具输出原始思考内容，以及防止 Haiku 模型逐字重复其他模型的思考块。此外，Fable 5.1 的定价预计比 Fable 5 低约 25%，主要由于缓存读取价格降低。系统卡已发布，详细说明了安全评估和变更内容。

**「背景」** Anthropic 于 2026 年 9 月 1 日发布了 Claude Fable 5.1 和 Claude Mythos 5.1。这两个模型本质上是同一个模型，但安全防护级别不同：Fable 5.1 面向一般用户开放，而 Mythos 5.1 仅通过邀请制的可信访问计划提供，其安全防护专为网络安全和生命科学领域的工作设计。据文档显示，该模型支持 100 万 token 的上下文窗口，最大输出为 128,000 token，输入价格为每百万 token 10 美元，输出价格为每百万 token 50 美元。此次更新还降低了缓存读取价格，并修复了三个与思维链泄露相关的安全漏洞。

**「影响」** 对于使用 Claude API 的开发者，Fable 5.1 的降价和写作改进可能降低运营成本并提升生成文本质量，但破坏性变更可能影响依赖旧行为的应用，需要及时调整。

**「社区讨论」** 社区对写作改进和价格下调反应积极，但部分用户因订阅成本或对模型输出风格不满而持保留态度。有 Anthropic 员工表示 Fable 5.1 在写作风格上显著进步，并暗示未来在科学领域将有更多进展。

## 原文 excerpt

We’re introducing Claude Fable 5.1 and Claude Mythos 5.1. They’re the world’s most advanced models for coding and knowledge work—and their research capabilities offer an early glimpse of how AI models will contribute to scientific progress.
Claude Fable 5.1 and Claude Mythos 5.1 are the same model, but with different levels of safeguards. Fable 5.1 is generally available, while Mythos 5.1 is available only through our trusted access programs; its safeguards are specifically designed to support work in cybersecurity and the life sciences.
Alongside its increased capabilities, Fable 5.1 takes important steps towards addressing the feedback we’ve received from customers on price, data retention, and safeguards.
Price. Fable 5.1 will cost an estimated 25% less than Fable 5 for typical workloads, wherever usage is billed by token. This is because we’re reducing our pricing on cache reads (where the model reads inputs that have already been processed and stored). For highly agentic work, the savings will often be much larger—up to approximately 45%.
Data retention. Our new system of Enterprise Frontier Safeguards (EFS) gives customers complete privacy (the same as a zero data retention policy) while still being state-of-the-art at preventing adversarial use. EFS works by storing data in cloud infrastructure controlled entirely by the customer, not Anthropic. It will be made available to enterprise customers in phases, beginning later this fall. Until EFS is available, eligible customers will be able to use Fable 5.1 with zero data retention.
Safeguards. We’ve improved our safeguards to reduce false positives (where the system flags benign content). In cybersecurity, our newest safeguards block 60% fewer false positives than before. In part, this is because Fable 5.1 can now be used to discover software vulnerabilities—though not to develop exploits for them. In biology, we’ve established an access program, developed in partnership with the US government, to enable access 

## 来源信息

- 来源类型：hackernews（denysvitali）
- 发布时间：2026-09-01 17:53
- 原始 URL：https://www.anthropic.com/claude-fable-and-mythos-5-1
- 社区讨论：https://news.ycombinator.com/item?id=49525378
- 抓取时间：2026-09-02 08:22:45
- 敏感等级：公开（外部公开源）
