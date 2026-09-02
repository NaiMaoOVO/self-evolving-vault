---
id: "2e7d0fb45461"
title: "小型 Transformer 1.5 小时训练超越众多 LLM"
author: "porridgeraisin"
published: "2026-09-01 09:52"
url: https://mvakde.github.io/blog/44-on-arc-1/
source_type: hackernews
source_name: "porridgeraisin"
fetched_at: 2026-09-02 08:22:45
score: "8.0/10"
tags: [transformer, ARC benchmark, efficient AI, machine learning, research]
sensitivity: 公开
source_report: horizon-2026-09-02-zh.md
---
# 小型 Transformer 1.5 小时训练超越众多 LLM

## AI 摘要（Horizon 日报）

作者训练了一个小型自回归 Transformer，仅用 1.5 小时从零开始训练，在 ARC 基准测试上取得了优于许多大型语言模型（LLM）的成绩。这一结果挑战了复杂推理任务必须依赖大规模预训练模型的假设，表明高效、小规模的模型也能解决复杂问题。该模型并非 LLM，而是专门针对 ARC 任务设计的，训练成本极低。作者强调，此前该基准测试主要由 LLM 或其微调版本主导，且训练成本高昂，而其他尝试要么使用复杂架构，要么需要极高的计算量。这一成果为 AI 效率和可访问性提供了新的可能性。

**「背景」** ARC（Abstraction and Reasoning Corpus）是一个旨在评估 AI 抽象推理能力的基准测试，通常被认为需要复杂的推理能力。此前，在该基准上取得好成绩的方法主要依赖大规模 LLM 或复杂的架构，训练成本极高。作者的工作表明，通过精心设计的小型 Transformer，可以在极低的训练成本下达到竞争性表现，这为 AI 研究提供了新的方向。

**「影响」** 这一成果可能促使 AI 社区重新评估对大规模预训练模型的依赖，推动更高效、更易获取的 AI 模型研究，尤其对资源受限的研究者和开发者具有实际意义。

**「社区讨论」** 作者在评论中澄清，该模型并非 LLM，而是小型自回归 Transformer，并指出其训练成本极低。有评论者提到，作者的方法可能使 ARC 基准测试的公平性得到改善，因为禁止离线训练和预训练可以防止模型通过大量训练数据“刷分”。也有评论者认为这一成果令人印象深刻，可能为作者带来更多机会。

## 原文 excerpt

44% on ARC-AGI-1 in 67 cents
I trained a small transformer from scratch in 1.5hrs on a 5090
 Beats many LLMs, and scores the same as TRM/HRM
This is an upgrade to my previous model 
 Faster, better, cheaper and still open source.
Also gets 7% on ARC-2
Discussion on Twitter, Code on github
This is the 3rd blog in a series of works on ARC-AGI. Prev: Blog 2, Blog 1.
Many ppl thought the prev result was impossible. It got attention from top researchers and went viral on X. Eg: Discussions by Lucas Beyer, Jeremy Howard, Rohan Anil, and comments by many others.
Why work on this?
I think sample efficiency is the most important problem in AI today and I want to solve it.
The intention behind this work is to (1) find the limits of sample efficiency when restricted to transformers / today’s deep learning methods and (2) reduce costs so iteration is much faster and cheaper.
ARC is a great benchmark to test this:
- Very few samples (only a 1000 puzzles) in a high dimensional space
- Its a metalearning benchmark, so each puzzle uses a different rule, with some common concepts
- Very few priors needed: every concept needed in the eval set is present in the train set
- It is incredibly easy for humans to solve, and accessible to even poor AI researchers
- Benchmark is still unsaturated (for data efficiency, ignore LLMs and approaches that use tons of synthetic data or human inductive biases)
Next, I’ll work on new research ideas to break these limits. I’ll try to keep costs low so that anyone in the world can work on this.
Tech details
How does it work?
The overall approach is similar to last time (full technical details here), but I added a bunch of upgrades. Here’s a quick summary of the approach:
- Each input-output pair is converted to a sequence of tokens. These sequences are autoregressively trained on by a small transformer. This is done from scratch at test time on both the train set and eval set puzzles (test labels hidden).
- To enable cross-task learning, each puzzle is

## 来源信息

- 来源类型：hackernews（porridgeraisin）
- 发布时间：2026-09-01 09:52
- 原始 URL：https://mvakde.github.io/blog/44-on-arc-1/
- 社区讨论：https://news.ycombinator.com/item?id=49519939
- 抓取时间：2026-09-02 08:22:45
- 敏感等级：公开（外部公开源）
