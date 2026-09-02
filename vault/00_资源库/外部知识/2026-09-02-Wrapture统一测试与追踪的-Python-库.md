---
id: "bf3e1e0703c0"
title: "Wrapture：统一测试与追踪的 Python 库"
author: "Simon Willison"
published: "2026-08-31 23:59"
url: https://simonwillison.net/2026/Aug/31/introducing-wrapture/
source_type: rss
source_name: "Simon Willison"
fetched_at: 2026-09-02 08:22:45
score: "7.0/10"
tags: [Python, Testing, Tracing, Monkeypatching, Open Source]
sensitivity: 公开
source_report: horizon-2026-09-02-zh.md
---
# Wrapture：统一测试与追踪的 Python 库

## AI 摘要（Horizon 日报）

Graham Dumpleton 发布了 Wrapture，这是一个基于 wrapt 的 Python 库，将 monkeypatching 扩展至测试和追踪领域。Wrapture 可以包装任何函数或方法，实现访问追踪或返回值覆盖，既可作为 unittest.mock 的替代方案，也能为现有项目添加追踪功能。它支持 OpenTelemetry，并提供基于配置的追踪机制，例如通过 TOML 配置捕获摘要并输出 JSONL 格式的追踪数据。该项目仅数周历史，但已展现出良好前景。值得注意的是，Wrapture 是 Dumpleton 首次完全由 AI 辅助驱动的项目，所有代码和文档均由 AI 助手在其指导下编写，但他强调这是经过精心设计的工程，而非随意的“vibe coding”。

**「背景」** Wrapture 是由 Graham Dumpleton 开发的一个 Python 库，他同时也是 wrapt、mod_wsgi 和 New Relic Python 代理的作者。Wrapture 扩展了 wrapt 的猴子补丁（monkeypatching）概念，将测试和追踪统一起来，允许开发者在不修改被观察代码的情况下，对任何函数或方法进行包装，以记录其调用或覆盖其返回值。该库支持 OpenTelemetry，并提供了基于配置的追踪机制，可作为 unittest.mock 的替代方案。

**「影响」** Wrapture 为 Python 开发者提供了一种统一的测试与追踪工具，可能简化现有项目的可观测性集成，并减少对 unittest.mock 的依赖。

## 原文 excerpt

31st August 2026 - Link Blog
Introducing wrapture. New from Graham Dumpleton (of wrapt, mod_wsgi, and New Relic's Python agent fame), who describes Wrapture as taking the monkeypatching ideas from wrapt and extending them to apply to testing and tracing at the same time.
Wrapture (full documentation here) makes it easy to wrap any function or method such that all access can be traced, or can be overridden to return a different value.
It acts as both an alternative to unittest.mock and a way to implement tracing against an existing project:
Attaching observation to code you do not control, recording what flows through it, and doing so without disturbing the program being watched, is a problem I have never really stopped thinking about.
Wrapture includes OpenTelemetry support and even has an entirely configuration-based mechanism for adding tracing to an existing Python project, which looks like this:
capture = "summary"
[[observe]]
target = "domain:Calculator"
name = ["outer", "inner"]
[[sink]]
type = "jsonlines"
path = "trace.jsonl"This is still a very young project - just a few weeks old - but it's off to a very promising start.
Interestingly, this is also Graham's first attempt at large entirely agent-driven project:
Every line of code and documentation in wrapture was written by an AI assistant working under my direction. I want to be upfront about that, and equally upfront about what it was not. This was not vibe coding, where a one-shot prompt produces a pile of generated code and the person driving hopes for the best because they lack the knowledge to judge what came back. Vibe coding has earned its bad reputation. I engineered wrapture carefully from the start. I have spent a long time in this particular corner of Python and knew exactly what the result needed to be, and the AI was the means of producing it rather than the source of the design.
In a follow-up post, Unit testing with wrapture, Graham shows the testing patterns supported by the new library:
def

## 来源信息

- 来源类型：rss（Simon Willison）
- 发布时间：2026-08-31 23:59
- 原始 URL：https://simonwillison.net/2026/Aug/31/introducing-wrapture/
- 抓取时间：2026-09-02 08:22:45
- 敏感等级：公开（外部公开源）
