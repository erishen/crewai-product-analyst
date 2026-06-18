# CrewAI Product Analyst

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

基于 [CrewAI](https://www.crewai.com/) 多智能体编排的 AI 产品分析工具。使用三个专业 AI 智能体完成产品调研、战略分析和报告撰写。

## 功能特性

- **3 智能体流水线** — 研究员收集情报、策略师提炼见解、撰稿人润色报告
- **一条命令** — 一个 CLI 命令跑完完整的产品竞争分析
- **Markdown 报告** — 可直接发布的报告，含执行摘要、市场分析和战略建议
- **LLM 无关** — 支持 OpenAI、Ollama 或任何兼容 OpenAI 的提供商
- **可扩展** — 方便添加自定义工具或调整智能体角色

## 快速开始

```bash
# 安装依赖
uv sync

# 分析产品
product-analyst analyze "飞书"
```

## 使用方法

```bash
# 基本分析
product-analyst analyze "DeepSeek"

# 保存到文件
product-analyst analyze "通义千问" --output reports/tongyi-analysis.md

# 静默模式（不显示智能体日志）
product-analyst analyze "Kimi" --quiet

# 查看版本
product-analyst version
```

## 智能体

| 智能体 | 角色 | 职责 |
|--------|------|------|
| Researcher | 市场研究员 | 收集产品信息、市场数据、竞争对手情况 |
| Strategist | 产品策略顾问 | 提炼洞察、识别机会与威胁 |
| Writer | 技术撰稿人 | 产出可发布的高质量报告 |

## 流水线

```
产品/公司 → Researcher（调研备忘录）
            → Strategist（策略备忘录）
              → Writer（最终报告）
```

## 配置

复制 `.env.example` 为 `.env` 并配置 LLM 提供商：

```bash
cp .env.example .env
```

默认使用 OpenAI。如需使用 Ollama：

```bash
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL_NAME=ollama/llama3.1
OPENAI_API_KEY=ollama
```

## License

MIT
