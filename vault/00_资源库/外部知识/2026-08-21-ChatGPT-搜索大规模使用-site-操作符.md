---
id: "c8cbe369112d"
title: "ChatGPT 搜索大规模使用 site:操作符"
author: "Simon Willison"
published: "2026-08-20 23:57"
url: https://simonwillison.net/2026/Aug/20/chatgpt-search-now-uses-the-siteoperator-at-scale/
source_type: rss
source_name: "Simon Willison"
fetched_at: 2026-08-22 03:27:15
score: "7.0/10"
tags: [ChatGPT, search, GEO, AI product changes, site operator]
sensitivity: 公开
source_report: horizon-2026-08-21-zh.md
---
# ChatGPT 搜索大规模使用 site:操作符

## AI 摘要（Horizon 日报）

根据 Promptwatch 的追踪数据，ChatGPT 搜索中 site:操作符的使用比例在 8 月 8 日从之前的 0.3%-0.5%跃升至 16%-17%，这一变化与 OpenAI 在 8 月 6 日发布的 GPT-5.6 Sol 更新公告相吻合。Promptwatch 指出，这一变化可能反映了 OpenAI 对搜索工具的内部调整，尽管其系统提示仍不透明。此外，8 月 18 日的后续报告显示，ChatGPT 在搜索中引用 Reddit 的可能性大幅降低，但具体原因尚未明确。这些数据仅涵盖 Promptwatch 自动追踪的提示词，可能不代表全部用户行为。

**「背景」** ChatGPT 搜索是 OpenAI 在其聊天产品中集成的网络搜索功能，用户可以通过自然语言提问获取信息。site: 操作符是一种搜索语法，用于将搜索结果限制在特定域名内。Promptwatch 是一家专注于生成式引擎优化（GEO）的公司，通过自动化工具追踪 ChatGPT、Claude、Gemini 等 AI 产品的提示词和响应，以分析这些产品的行为变化。

**「影响」** 对于依赖 ChatGPT 搜索流量的网站所有者和 SEO/GEO 从业者，这一变化意味着优化策略需要更重视 site:操作符的使用，同时减少对 Reddit 等特定来源的依赖，因为 ChatGPT 的搜索行为已发生显著转变。

## 原文 excerpt

20th August 2026 - Link Blog
ChatGPT search now uses the site:operator at scale. Promptwatch is part of the emerging "GEO" space, for Generative Engine Optimization - the chatbot version of SEO, where companies offer tools and consulting to help your site increase its presence in replies to prompts inside tools like ChatGPT.
The Promptwatch product uses automation to track responses to prompts across end-user chat products like ChatGPT, Claude, and Gemini. They publish aggregate reports on this as part of their own content marketing strategy, which do seem to provide credible hints as to otherwise invisible design changes to those products.
Their own tracking shows a notable change aligned with the GPT-5.6 rollout earlier this month:
The percentage of all ChatGPT Search fanout queries that contain the site:operator, per day. The share hovered between 0.3% and 0.5% for weeks, dipped briefly to 0.15% on August 3 to 5 (consistent with a staged rollout or pre-launch experiment), then jumped to 16-17% on August 8.
It's important to note that these figures only reflect the prompts for which they have automated tracking enabled.
This corresponds to OpenAI's somewhat vague August 6th announcement:
For Plus and Pro users, we’re updating GPT‑5.6 Sol in Chat to be more reliable with facts and provide more focused answers.
Once again I am hampered by OpenAI's decision to actively obscure their system prompts, but from poking at ChatGPT I believe their latest search tool has a shape like search(query, recency, domains) rather than encouraging a site: operator directly.
In a follow-up on August 18th Promptwatch reported that ChatGPT appeared to have greatly reduced the likelihood of Reddit being used in those searches. My own attempts to ascertain if the system prompt has been updated to discourage Reddit sourcing have been unsuccessful - the most thorough leaked system prompt collection I know of doesn't yet show any relevant changes.
Recent articles
- Conceptual integrity and c

## 来源信息

- 来源类型：rss（Simon Willison）
- 发布时间：2026-08-20 23:57
- 原始 URL：https://simonwillison.net/2026/Aug/20/chatgpt-search-now-uses-the-siteoperator-at-scale/
- 抓取时间：2026-08-22 03:27:15
- 敏感等级：公开（外部公开源）
