from crewai import Task

from crewai_product_analyst.agents import RESEARCHER, STRATEGIST, WRITER


RESEARCH_TASK = Task(
    description=(
        "Analyze the product or company: {topic}\n\n"
        "## Workflow (execute in order):\n\n"
        "1. **Read Local Project** — Read the project directory at:\n"
        "   /Users/erishen/Workspace/CNB/individular-invest/invest-kit/apps/asset-lens\n"
        "   Read README, docs/, pyproject.toml, and directory listing to understand:\n"
        "   - What problem does this product solve?\n"
        "   - Who is the target user?\n"
        "   - What are the key features and capabilities?\n"
        "   - What data sources / integrations does it rely on?\n\n"
        "2. **Analyze Code Structure** — Run AST analysis on the same path to get\n"
        "   the project's scale indicators (total files, modules, tests, dependencies).\n"
        "   Use this data to infer the product's maturity and scope, but do NOT list raw\n"
        "   code metrics as deliverables — treat it as internal reference for your analysis.\n\n"
        "3. **Web Search** — Search for market context:\n"
        "   - Competitors in the same space (open source and commercial)\n"
        "   - Industry trends and adoption patterns\n"
        "   - If the project is personal with no public presence, search for comparable\n"
        "     products in the same category instead.\n\n"
        "Your deliverables (all in **Chinese**), structured as a **product research memo**:\n"
        "1. 产品定义 — 一句话定位，核心解决什么问题，为谁解决\n"
        "2. 用户画像 — 典型用户是谁？他们的痛点和使用场景？\n"
        "3. 功能全景 — 核心功能矩阵，哪些功能最强，哪些缺失\n"
        "4. 用户体验分析 — 上手难度、CLI/Web 体验、文档质量\n"
        "5. 竞争格局 — 主要竞品对比，差异化优势在哪里\n"
        "6. 市场评估 — 适用场景，潜在市场体量和增长空间\n\n"
        "用数据说话，但数据点服务于产品讲述（如：\"200+ CLI 子命令表明项目功能极其全面\"）"
    ),
    expected_output=(
        "A product research memo in Chinese with sections: "
        "产品定义, 用户画像, 功能全景, 用户体验分析, 竞争格局, 市场评估."
    ),
    agent=RESEARCHER,
)

STRATEGY_TASK = Task(
    description=(
        "Based on the research memo, develop a product strategy for {topic}.\n\n"
        "Think like a product leader evaluating whether to invest in, partner with, or compete"
        " against this product. Your analysis should be actionable for a CEO or product VP.\n\n"
        "Your deliverables (all in **Chinese**):\n"
        "1. 核心发现 — 3-5 个关于产品价值和市场机会的关键洞察\n"
        "2. 产品定位评估 — 目前的定位是否清晰？建议如何调整？\n"
        "3. 增长策略 — 获客渠道、社区运营、推广优先级\n"
        "4. 产品路线图建议 — 下一个阶段应该做什么，不应该做什么\n"
        "5. 风险与挑战 — 市场风险、竞争风险、工程可持续性\n"
        "6. 行动建议 — 按影响力/成本排序的 3-5 个具体行动"
    ),
    expected_output=(
        "A strategy memo in Chinese with sections: "
        "核心发现, 产品定位评估, 增长策略, 产品路线图建议, 风险与挑战, 行动建议."
    ),
    agent=STRATEGIST,
)

WRITING_TASK = Task(
    description=(
        "Synthesize the research memo and strategy memo into a polished, "
        "publication-ready **product analysis report** for {topic}.\n\n"
        "This is a product report, not a code review. Structure it as:\n"
        "1. 执行摘要 — 3-5 句话概述产品价值、市场机会和关键建议\n"
        "2. 产品深度解析 — 目标用户、核心功能、用户体验旅程\n"
        "3. 竞争分析与市场定位 — 差异化优势、竞争格局\n"
        "4. 战略建议 — 定位调整、增长策略、路线图优先级\n"
        "5. 结论 — 一句话判断：这个产品值得投入吗？下一步建议\n\n"
        "The report must be entirely in **Chinese**. "
        "Use professional, objective tone. "
        "Use headings, bullet points, and bold text for readability. "
        "Code references are only relevant if they inform product understanding "
        "(e.g., 'Deep ML integration shows product ambition beyond simple tracking'). "
        "Do NOT include code quality metrics or raw AST data in the final report."
    ),
    expected_output=(
        "A complete product analysis report in Chinese, ready for publication."
    ),
    agent=WRITER,
)
