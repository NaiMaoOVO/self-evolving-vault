---
id: "074ef87072ed"
title: "DeepSeek 发布 v4-flash-vision-exp，新增视觉能力"
author: "dares2573"
published: "2026-08-21 10:33"
url: https://api-docs.deepseek.com/guides/vision/
source_type: hackernews
source_name: "dares2573"
fetched_at: 2026-08-22 03:27:15
score: "7.0/10"
tags: [DeepSeek, vision model, AI API, multimodal, machine learning]
sensitivity: 公开
source_report: horizon-2026-08-21-zh.md
---
# DeepSeek 发布 v4-flash-vision-exp，新增视觉能力

## AI 摘要（Horizon 日报）

DeepSeek 发布了 v4-flash-vision-exp，为其 flash 模型新增了视觉能力，填补了 API 在图像理解方面的空白。该模型将图像按尺寸转换为 token，并与文本 token 一起计费；推理前会自动调整图像大小，小于约 384×384 像素的图像会被放大，更大的图像则按比例缩小。社区反馈显示，该模型在读取 Playwright 截图方面表现有前景，但仍有局限性，例如在简单时钟识别测试中失败，而 Qwen3.8 27B 几乎能正确回答。此外，有用户指出，之前的 v4-flash 0731 版本经常错误地假设自己具备视觉能力，并虚构基于文本的图像分析工具，因此此次升级被视为重要改进。

**「背景」** DeepSeek 于 2026 年 8 月 21 日发布了实验性多模态模型 deepseek-v4-flash-vision-exp，为其 Flash 系列模型新增视觉能力。该模型通过 OpenAI 兼容的 Chat Completions、Anthropic 兼容的 Messages 和 Responses 接口提供，图像按尺寸转换为 token 计费，每张图像最多 384 个 token，价格与 V4-Flash 文本模型一致。此前，DeepSeek 的 Flash 模型仅支持文本，用户常需依赖外部工具处理图像，此次更新填补了这一功能空白。

**「影响」** 对于依赖 DeepSeek API 进行代码任务和自动化（如 Playwright 截图分析）的开发者，v4-flash-vision-exp 提供了更可靠的视觉处理能力，减少了因模型虚构视觉功能而导致的会话中断。

**「社区讨论」** 社区普遍认为该模型在视觉任务上有所改进，但仍有明显不足，例如时钟识别错误；同时有用户质疑纯文本版本的存在意义，认为视觉版本可能完全替代它，除非成本或延迟存在差异。

## 原文 excerpt

Vision
The deepseek-v4-flash-vision-exp model accepts images alongside text, so you can ask the model to describe pictures, read text from screenshots, analyze charts, and more.
Supported image formats: JPEG, PNG, GIF, and WebP. The format is detected from the actual file content, not from the file name or the declared MIME type.
Sending Images
There are three ways to provide an image to the model. All of them use the standard OpenAI-compatible Chat Completions format, where content is an array of blocks instead of a plain string. The same three methods are also available in the Responses API, where images are carried in input_image content parts.
The base_url for the examples below is https://api.deepseek.com.
1. Base64-encoded image (inline)
Encode the image and embed it directly in the request as a data: URL. This is the simplest option for local files. The encoded data counts toward the 48 MiB request body limit (see Limits).
import base64
from openai import OpenAI
client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")
with open("image.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")
response = client.chat.completions.create(
    model="deepseek-v4-flash-vision-exp",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What is in this image?"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                },
            ],
        }
    ],
)
print(response.choices[0].message.content)
curl https://api.deepseek.com/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <DeepSeek API Key>" \
  -d '{
    "model": "deepseek-v4-flash-vision-exp",
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "What is in this image?"},
          {"type": "image_url", "image_url": {"url": "data:

## 来源信息

- 来源类型：hackernews（dares2573）
- 发布时间：2026-08-21 10:33
- 原始 URL：https://api-docs.deepseek.com/guides/vision/
- 社区讨论：https://news.ycombinator.com/item?id=49386163
- 抓取时间：2026-08-22 03:27:15
- 敏感等级：公开（外部公开源）
