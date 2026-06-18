# CrewAI Product Analyst

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

AI-powered product analysis tool powered by [CrewAI](https://www.crewai.com/) multi-agent orchestration. Uses three specialized AI agents to research, strategize, and write comprehensive product analysis reports.

## Features

- **3-Agent Pipeline** — Researcher gathers intel, Strategist forms insights, Writer polishes the report
- **One Command** — Run a full competitive product analysis with a single CLI command
- **Markdown Reports** — Publication-ready output with executive summary, market analysis, and strategic recommendations
- **LLM Agnostic** — Works with OpenAI, Ollama, or any OpenAI-compatible provider
- **Extensible** — Easy to add custom tools or swap agent roles

## Quick Start

```bash
# Install
uv sync

# Analyze a product
product-analyst analyze "Notion AI"
```

## Usage

```bash
# Basic analysis
product-analyst analyze "OpenAI o3"

# Save to file
product-analyst analyze "Cursor IDE" --output reports/cursor-analysis.md

# Quiet mode (no agent logs)
product-analyst analyze "Perplexity AI" --quiet

# Show version
product-analyst version
```

## Agents

| Agent | Role | Responsibility |
|-------|------|----------------|
| Researcher | Market Research Analyst | Gather product info, market data, competitive landscape |
| Strategist | Product Strategy Consultant | Synthesize insights, identify opportunities & threats |
| Writer | Technical Writer | Produce polished, publication-ready report |

## Pipeline

```
Topic → Researcher (research memo)
         → Strategist (strategy memo)
           → Writer (final report)
```

## Configuration

Copy `.env.example` to `.env` and set your LLM provider:

```bash
cp .env.example .env
```

By default CrewAI uses OpenAI. For Ollama, set:

```bash
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL_NAME=ollama/llama3.1
OPENAI_API_KEY=ollama
```

## Project Structure

```
crewai-product-analyst/
├── src/crewai_product_analyst/
│   ├── agents.py      # Agent definitions
│   ├── tasks.py        # Task definitions
│   ├── crew.py         # Crew orchestration
│   ├── tools.py        # Custom tools (web search, fetch)
│   └── main.py         # CLI entry point
├── pyproject.toml
├── .env.example
└── README.md
```

## License

MIT
