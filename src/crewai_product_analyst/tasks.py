from crewai import Task

from crewai_product_analyst.agents import RESEARCHER, STRATEGIST, WRITER


RESEARCH_TASK = Task(
    description=(
        "Analyze the product or company: {topic}\n\n"
        "First, use the **Read Local Project** tool to read the project directory. "
        "The project path is: /Users/erishen/Workspace/CNB/individular-invest/invest-kit/apps/asset-lens. "
        "Read the README, pyproject.toml, and project structure.\n\n"
        "Then, research the product/company using **Web Search** for market context.\n\n"
        "Your deliverables (all in **Chinese**):\n"
        "1. 项目概况 — 项目是什么，核心功能，目标用户\n"
        "2. 技术栈分析 — 使用的语言、框架、关键技术\n"
        "3. 项目结构 — 主要模块和代码组织方式\n"
        "4. 功能亮点 — 区别于同类项目的特性\n"
        "5. 市场定位 — 适用场景，优劣势分析\n\n"
        "包括具体的数据点和引用来源。"
    ),
    expected_output=(
        "An exhaustive research memo in Chinese with sections: "
        "项目概况, 技术栈分析, 项目结构, 功能亮点, 市场定位."
    ),
    agent=RESEARCHER,
)

STRATEGY_TASK = Task(
    description=(
        "Based on the research memo, develop a strategic analysis for {topic}.\n\n"
        "Your deliverables (all in **Chinese**):\n"
        "1. 核心发现 — 3-5 个关键洞察\n"
        "2. 改进机会 — 可优化或扩展的方向\n"
        "3. 潜在风险 — 技术债务、架构问题、安全风险\n"
        "4. 建议方案 — 按优先级排序的具体建议，附理由"
    ),
    expected_output=(
        "A strategy memo in Chinese with sections: "
        "核心发现, 改进机会, 潜在风险, 建议方案."
    ),
    agent=STRATEGIST,
)

WRITING_TASK = Task(
    description=(
        "Synthesize the research memo and strategy memo into a polished, "
        "publication-ready product analysis report for {topic}.\n\n"
        "Structure the report as:\n"
        "1. 执行摘要 — 3-5 句话概述最重要的发现\n"
        "2. 项目深度解析 — 功能、架构、技术栈\n"
        "3. 技术评估 — 代码质量、可维护性、扩展性\n"
        "4. 战略建议 — 改进方向、优先事项\n"
        "5. 结论 — 核心总结\n\n"
        "The report must be entirely in **Chinese**. "
        "Use professional, objective tone. "
        "Use headings, bullet points, and bold text for readability. "
        "Include specific code references where relevant."
    ),
    expected_output=(
        "A complete product analysis report in Chinese, ready for publication."
    ),
    agent=WRITER,
)
