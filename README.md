# CrewAI Product Analyst

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

AI-powered product analysis tool powered by [CrewAI](https://www.crewai.com/) multi-agent orchestration. Uses three specialized AI agents to research, strategize, and write comprehensive product analysis reports.

## Skill 定义

```yaml
name: crewai-product-analyst
description: AI-powered product analysis for local projects using CrewAI multi-agent orchestration
version: 1.0.0
category: product-analysis
```

## 能力范围

```yaml
capabilities:
  - 本地项目产品分析：读取本地项目 README、文档、代码结构，输出产品级分析报告
  - 竞品分析：通过 Web Search 获取市场格局和竞品信息
  - 三阶段流水线：Research（产品研究）→ Strategy（策略分析）→ Writing（报告撰写）
  - 产品级输出：用户画像、功能矩阵、竞争格局、增长策略、路线图优先级
  - Markdown 报告：自动保存到 output/ 目录

limitations:
  - 不处理非产品类分析（技术审计、代码审查等不属于产品分析的范畴）
  - 不执行实际代码修改或工程操作
  - 不访问互联网上需要认证的私有数据源
  - 不涉及实时监控或持续集成
```

## 架构

### Agents

| Agent | Role | Responsibility | Tools |
|-------|------|----------------|-------|
| Researcher | 市场研究分析师 | 产品定义、用户画像、功能全景、竞争格局 | Web Search, Fetch Webpage, Read Local Project, Analyze Code Structure |
| Strategist | 产品策略顾问 | 定位评估、增长策略、路线图优先级、商业化建议 | (无独立工具，依赖 Researcher 输出) |
| Writer | 技术撰稿人 | 将分析和策略合成为可发布的报告 | (无独立工具，依赖 Researcher + Strategist 输出) |

### Pipeline

```
输入：本地项目路径
  ↓
Researcher → 产品研究备忘录
  │            产品定义、用户画像、功能矩阵、用户体验、竞争格局、市场评估
  ↓
Strategist → 策略分析备忘录
  │            核心发现、定位评估、增长策略、路线图、风险与挑战
  ↓
Writer → 产品分析报告（最终输出）
            执行摘要、产品深度解析、竞争分析、战略建议、结论
```

## 使用方法

### 分析本地项目

```bash
# 分析一个本地项目，自动保存报告到 output/
uv run python examples/analyze_local.py /path/to/project

# 指定输出路径
uv run python examples/analyze_local.py /path/to/project -o my-report.md
```

### 在线产品分析

```bash
# 分析一个公开产品或公司
product-analyst analyze "Notion AI"

# 保存到文件
product-analyst analyze "Cursor IDE" --output reports/cursor-analysis.md

# 安静模式（不显示 agent 日志）
product-analyst analyze "Perplexity AI" --quiet
```

### 查看 Token 使用情况

每次运行完成后会自动打印 Token 使用统计：

```
============================================================
TOKEN USAGE
  total_tokens: 256957
  prompt_tokens: 243833
  cached_prompt_tokens: 213248
  completion_tokens: 13124
  successful_requests: 21
============================================================
```

## 项目结构

```
crewai-product-analyst/
├── src/crewai_product_analyst/
│   ├── agents.py      # Agent 定义（Researcher / Strategist / Writer）
│   ├── tasks.py       # Task 定义（三阶段流水线描述）
│   ├── crew.py        # Crew 编排（顺序执行）
│   ├── tools.py       # 自定义工具
│   │   ├── Web Search           # DuckDuckGo 搜索
│   │   ├── Fetch Webpage        # 网页内容抓取
│   │   ├── Read Local Project   # 本地项目文件读取
│   │   └── Analyze Code Structure  # 代码结构分析（通过 ai-analyze CLI）
│   └── main.py         # CLI 入口
├── examples/
│   └── analyze_local.py   # 本地项目分析示例脚本
├── output/                 # 自动生成的报告（.gitignore）
├── pyproject.toml
├── .env.example
└── README.md
```

## Tools 说明

### Web Search
调用 DuckDuckGo Lite API 搜索互联网信息，用于竞品分析和市场调研。

### Fetch Webpage
抓取指定 URL 的文本内容，用于深入了解特定产品或公司。

### Read Local Project
读取本地项目的 README、配置文件、目录结构，理解产品定位和功能。

### Analyze Code Structure
通过 `ai-analyze` CLI（subprocess 调用）对本地项目进行 AST 分析，获取：
- 项目规模（文件数、函数/类数）
- 语言分布（Python / TypeScript 等）
- 最复杂/最大文件
- 代码坏味道分布
- 平均复杂度

数据用于推断产品成熟度和范围，**不作为最终报告的交付内容**。

## 配置

```bash
cp .env.example .env
```

编辑 `.env` 选择 LLM 提供商：

| Provider | 推荐 | 成本 |
|----------|------|------|
| DeepSeek | ✅ 推荐 | ~¥0.5 / 次完整分析 |
| OpenAI | 可选 | ~$0.8 / 次 |
| Ollama | 本地运行 | 免费 |

## 输出格式

每份报告包含以下章节：

1. **执行摘要** — 产品价值、市场机会、核心建议
2. **产品深度解析** — 目标用户、核心功能、用户体验旅程
3. **竞争分析与市场定位** — 差异化优势、竞争格局
4. **战略建议** — 定位调整、增长策略、路线图优先级
5. **结论** — 打分矩阵、行动建议、时间窗口

报告为 Markdown 格式，自动保存到 `output/` 目录下。

## 质量标准

```yaml
quality:
  product_focus: "报告必须是产品分析，而非代码审查。零原始代码指标（文件数、函数数、复杂度）出现在最终报告中。"
  data_grounding: "分析结论必须有数据支撑（README 引用、代码目录结构推断、竞品对比），不做无根据推测。"
  actionable: "战略建议必须具体、可执行，有优先级、有成本/影响力评估，而不是空泛的建议。"
  chinese_output: "所有输出为中文，术语准确、行文专业。"
```

## License

MIT
