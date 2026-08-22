---
id: "2da3f824e886"
title: "Bun 1.4 稳定版发布，新增 Bun.WebView 浏览器自动化 API"
author: "Simon Willison"
published: "2026-08-20 15:37"
url: https://simonwillison.net/2026/Aug/20/bun-webview-json-api/
source_type: rss
source_name: "Simon Willison"
fetched_at: 2026-08-22 03:27:15
score: "8.0/10"
tags: [Bun, JavaScript, WebView, release, API]
sensitivity: 公开
source_report: horizon-2026-08-21-zh.md
---
# Bun 1.4 稳定版发布，新增 Bun.WebView 浏览器自动化 API

## AI 摘要（Horizon 日报）

Bun 1.4 稳定版于 2026 年 8 月 20 日发布，这是自几个月前备受争议的 Rust 重写以来的首个稳定版本。该版本新增了 1,517 项 Node.js 测试套件测试，修复了超过 2,900 个问题，并将空闲 CPU 使用率降低 5 倍，内存使用率降低最多 35%，Linux 启动速度提升 50%。新特性包括 Bun.Image、Bun.WebView、Bun.markdown、Bun.cron()、Bun.Terminal、bun run --parallel、bun test --parallel、bun audit fix、bun dedupe 和 bun prune。其中 Bun.WebView 尤为引人注目，它通过 macOS WebKit 或 Chrome DevTools 协议（CDP）控制本地 Chromium，为浏览器自动化提供了一流支持。Simon Willison 使用 Claude Code for web 构建了一个原型 JSON API，灵感来自 shot-scraper javascript CLI 工具，该 API 可加载网页并执行 JavaScript，测试表明运行完整 Chrome 处理复杂网页需要 192MB-256MB 的容器内存。

**「背景」** Bun 是一个 JavaScript 运行时，旨在提供比 Node.js 更快的性能和更集成的工具链。Bun 1.4 是自几个月前将核心从 Zig 重写为 Rust 以来的首个稳定版本，该版本增加了对 Node.js 26.3.0 的兼容性，新增了 1,517 个通过的测试，并引入了 Bun.WebView 等新 API。Bun.WebView 提供了内置的浏览器自动化支持，可通过 macOS WebKit 或通过 Chrome DevTools 协议控制本地 Chromium 进程。

**「影响」** 对于 JavaScript 开发者，Bun 1.4 的稳定版和 Bun.WebView 提供了内置的浏览器自动化能力，可能简化依赖 Puppeteer 或 Playwright 的现有工作流，并降低资源消耗。

## 原文 excerpt

20th August 2026
Today saw the long awaited release of Bun 1.4, the first stable version since the infamous Rust rewrite a few months ago.
Interestingly, the Rust rewrite was downplayed in the release notes, which introduced a bewildering array of new features and claimed 2,900 additional bug fixes:
Bun 1.4 adds +1,517 tests from the Node.js test suite - our biggest jump in Node.js compatibility since Bun 1.0. Bun v1.4 also fixes over 2,900 issues. It reduces idle CPU usage by 5x, reduces memory usage by up to 35%, and starts 50% faster on Linux. It adds
Bun.Image,Bun.WebView,Bun.markdown,Bun.cron(),Bun.Terminal,bun run --parallel,bun test --parallel,bun audit fix,bun dedupe, andbun prune. And it rewrites Bun from Zig to Rust.
Of these the one that most caught my eye was Bun.WebView, which adds first class support for browser automation to Bun core using either macOS WebKit or control of a local Chromium process via the Chrome DevTools Protocol (CDP).
I had Claude Code for web build a prototype of a web API providing the ability to load a web page and then execute JavaScript against it, inspired by my shot-scraper javascript CLI tool - partly to see how much RAM would be needed by such a service.
Here's that TypeScript server implementation, which appears to need a 192MB-256MB container to run a full Chrome against complex web pages - tested using cgroups.
Recent articles
- Conceptual integrity and counting lines of code - 19th August 2026
- Qwen 3.8 27B is excellent, but it defaults to wildly overthinking things - 16th August 2026
- Now we have a timeline of the OpenAI accidental attack against Hugging Face - 7th August 2026

## 来源信息

- 来源类型：rss（Simon Willison）
- 发布时间：2026-08-20 15:37
- 原始 URL：https://simonwillison.net/2026/Aug/20/bun-webview-json-api/
- 抓取时间：2026-08-22 03:27:15
- 敏感等级：公开（外部公开源）
