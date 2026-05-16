# 📈 GitHub Trending Notifier

> **底层逻辑**：通过自动化爬虫获取 GitHub 全球每日/每周趋势项目，利用 AI 进行摘要提取并通过邮件/即时通讯工具触达。保持对全球技术前沿的敏锐嗅觉。

---

## 🚀 核心价值 (Value)
*   **信息降噪**：从数百万仓库中筛选出最具潜力的 Top 10。
*   **AI 赋能**：利用 LLM (如 DeepSeek) 对项目进行中文摘要，降低阅读门槛。
*   **自动化闭环**：基于 GitHub Actions 实现零成本常驻运行。

## 🛠 技术链路 (Workflow)
1.  **Scraping**: 获取 Trending 页面数据。
2.  **Summarization**: 调用 API 生成项目画像。
3.  **Push**: 通过邮件发送至个人收件箱。

## 📖 快速上手 (Quick Start)
1. Fork 本仓库。
2. 在 Secrets 中配置 `GITHUB_TOKEN` 和邮件服务凭证。
3. 开启 Actions，享受每日技术推送。

---
*Created by Jacknie666*
