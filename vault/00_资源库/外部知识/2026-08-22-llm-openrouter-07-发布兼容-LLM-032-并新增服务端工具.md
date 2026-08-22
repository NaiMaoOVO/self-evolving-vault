---
id: "866d80edbe87"
title: "llm-openrouter 0.7 发布：兼容 LLM 0.32 并新增服务端工具"
author: "Simon Willison"
published: "2026-08-21 16:58"
url: https://simonwillison.net/2026/Aug/21/llm-openrouter/
source_type: rss
source_name: "Simon Willison"
fetched_at: 2026-08-22 23:26:22
score: "6.0/10"
tags: [LLM, OpenRouter, plugin, AI tools, release]
sensitivity: 公开
source_report: horizon-2026-08-22-zh.md
---
# llm-openrouter 0.7 发布：兼容 LLM 0.32 并新增服务端工具

## AI 摘要（Horizon 日报）

llm-openrouter 0.7 版本已发布，主要更新包括兼容 LLM 0.32、改用 OpenRouter 的 Responses API，并新增三个服务端工具：Shell、WebFetch 和 WebSearch。这些工具可通过类似 `-T WebSearch` 的选项启用。由于兼容 LLM 0.32，该插件现在可以显示通过 OpenRouter 提供的 LLM 的推理轨迹。此版本为增量更新，对使用 LLM 工具和 OpenRouter 的开发者具有实用价值。

**「背景」** llm-openrouter 是 Simon Willison 开发的 LLM 命令行工具的插件，用于连接 OpenRouter 服务。LLM 0.32 是 LLM 工具的一个新版本，可能引入了对推理轨迹等功能的支持。OpenRouter 的 Responses API 是其提供的接口，用于与多种语言模型交互。

**「影响」** 使用 llm-openrouter 的开发者可以升级到 0.7 以兼容 LLM 0.32，并利用新的服务端工具（如 WebSearch）增强功能，同时获得推理轨迹的显示能力。

## 原文 excerpt

21st August 2026
Now that this plugin is compatible with LLM 0.32 it can display the reasoning traces for LLMs available through OpenRouter.
- Updated for compatibility with LLM 0.32.
- Models now use OpenRouter's implementation of the Responses API.
- Three new server-side tools: Shell, WebFetch, and WebSearch. Enable these with options like
-T WebSearch.
Recent articles
- Conceptual integrity and counting lines of code - 19th August 2026
- Qwen 3.8 27B is excellent, but it defaults to wildly overthinking things - 16th August 2026
- Now we have a timeline of the OpenAI accidental attack against Hugging Face - 7th August 2026

## 来源信息

- 来源类型：rss（Simon Willison）
- 发布时间：2026-08-21 16:58
- 原始 URL：https://simonwillison.net/2026/Aug/21/llm-openrouter/
- 抓取时间：2026-08-22 23:26:22
- 敏感等级：公开（外部公开源）
