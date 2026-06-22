# CrewAI Product Analyst

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

AI-powered product analysis tool powered by [CrewAI](https://www.crewai.com/) multi-agent orchestration. Uses three specialized AI agents to research, strategize, and write comprehensive product analysis reports.

## Skill Definition

```yaml
name: crewai-product-analyst
description: AI-powered product analysis for local projects using CrewAI multi-agent orchestration
version: 1.0.0
category: product-analysis
```

## Capabilities

```yaml
capabilities:
  - Local project analysis: reads README, docs, and code structure to produce product-level reports
  - Competitive analysis: uses Web Search to gather market landscape and competitor intelligence
  - Three-stage pipeline: Research → Strategy → Writing
  - Product-level output: user personas, feature matrix, competitive landscape, growth strategy, roadmap priorities
  - Markdown reports: auto-saved to output/ directory

limitations:
  - Does not handle non-product analysis (tech audits, code reviews, etc.)
  - Does not execute actual code changes or engineering operations
  - Does not access authenticated private data sources on the internet
  - Does not involve real-time monitoring or continuous integration
```

## Architecture

### Agents

| Agent | Role | Responsibility | Tools |
|-------|------|----------------|-------|
| Researcher | Market Research Analyst | Product definition, user personas, feature landscape, competitive landscape | Web Search, Fetch Webpage, Read Local Project, Analyze Code Structure |
| Strategist | Product Strategy Consultant | Positioning evaluation, growth strategy, roadmap priorities, monetization | (no independent tools, depends on Researcher output) |
| Writer | Technical Writer | Synthesizes analysis and strategy into a publishable report | (no independent tools, depends on Researcher + Strategist output) |

### Pipeline

```
Input: local project path
  ↓
Researcher → Product Research Memo
  │            Product definition, user personas, feature matrix, UX, competitive landscape
  ↓
Strategist → Strategy Analysis Memo
  │            Key findings, positioning evaluation, growth strategy, roadmap, risks
  ↓
Writer → Product Analysis Report (final output)
           Executive summary, product deep-dive, competitive analysis, strategic recommendations, conclusion
```

## Usage

### Analyze Local Project

```bash
# Analyze a local project, auto-save report to output/
uv run python examples/analyze_local.py /path/to/project

# Specify output path
uv run python examples/analyze_local.py /path/to/project -o my-report.md
```

### Online Product Analysis

```bash
# Analyze a public product or company
product-analyst analyze "Notion AI"

# Save to file
product-analyst analyze "Cursor IDE" --output reports/cursor-analysis.md

# Quiet mode (suppress agent logs)
product-analyst analyze "Perplexity AI" --quiet
```

### View Token Usage

Token usage statistics are printed automatically after each run:

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

## Project Structure

```
crewai-product-analyst/
├── src/crewai_product_analyst/
│   ├── agents.py      # Agent definitions (Researcher / Strategist / Writer)
│   ├── tasks.py       # Task definitions (three-stage pipeline)
│   ├── crew.py        # Crew orchestration (sequential execution)
│   ├── tools.py       # Custom tools
│   │   ├── Web Search            # DuckDuckGo search
│   │   ├── Fetch Webpage         # Web content scraping
│   │   ├── Read Local Project    # Local project file reader
│   │   └── Analyze Code Structure # AST analysis via ai-analyze CLI
│   └── main.py        # CLI entry point
├── examples/
│   └── analyze_local.py   # Local project analysis example script
├── output/                # Auto-generated reports (.gitignore)
├── pyproject.toml
├── .env.example
└── README.md
```

## Tools

### Web Search
Uses DuckDuckGo Lite API for internet searches, used for competitive analysis and market research.

### Fetch Webpage
Scrapes text content from a given URL for deeper understanding of specific products or companies.

### Read Local Project
Reads a local project's README, config files, and directory structure to understand product positioning and features.

### Analyze Code Structure
Uses `ai-analyze` CLI (subprocess call) to perform AST analysis on local projects, obtaining:
- Project scale (file count, function/class count)
- Language distribution (Python / TypeScript, etc.)
- Most complex / largest files
- Code smell distribution
- Average complexity

Data is used to infer product maturity and scope, **not delivered in the final report**.

## Configuration

```bash
cp .env.example .env
```

Edit `.env` to select your LLM provider:

| Provider | Recommendation | Cost |
|----------|---------------|------|
| DeepSeek | ✅ Recommended | ~$0.07 / full analysis |
| OpenAI | Optional | ~$0.80 / run |
| Ollama | Local | Free |

## Output Format

Each report includes the following sections:

1. **Executive Summary** — Product value, market opportunity, core recommendations
2. **Product Deep-Dive** — Target users, core features, user experience journey
3. **Competitive Analysis & Market Positioning** — Differentiation advantages, competitive landscape
4. **Strategic Recommendations** — Positioning adjustments, growth strategies, roadmap priorities
5. **Conclusion** — Scoring matrix, actionable recommendations, time window

Reports are in Markdown format and auto-saved to the `output/` directory.

## Quality Standards

```yaml
quality:
  product_focus: "Reports must be product analysis, not code reviews. Zero raw code metrics (file count, function count, complexity) in the final report."
  data_grounding: "Analysis conclusions must be data-backed (README quotes, code structure inference, competitive comparisons). No unsubstantiated speculation."
  actionable: "Strategic recommendations must be specific, executable, with priority and cost/impact assessments — not vague suggestions."
  chinese_output: "All output in Chinese, with accurate terminology and professional writing."
```

## License

MIT
