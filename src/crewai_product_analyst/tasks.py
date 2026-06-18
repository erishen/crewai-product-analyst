from crewai import Task

from crewai_product_analyst.agents import RESEARCHER, STRATEGIST, WRITER


RESEARCH_TASK = Task(
    description=(
        "Research the product or company: {topic}\n\n"
        "Your deliverables:\n"
        "1. Product overview — what it does, key features, target users\n"
        "2. Market positioning — market size, segment, pricing model\n"
        "3. Competitive landscape — top 3-5 competitors with differentiation\n"
        "4. Recent news — funding, launches, acquisitions (last 12 months)\n"
        "5. Strengths & weaknesses — from user reviews, analyst reports\n\n"
        "Include specific data points, quotes from reviews, and cite your sources."
    ),
    expected_output=(
        "A structured research memo in markdown with sections: "
        "Product Overview, Market Context, Competitive Landscape, "
        "Recent Developments, SWOT Analysis."
    ),
    agent=RESEARCHER,
)

STRATEGY_TASK = Task(
    description=(
        "Based on the research memo, develop a strategic analysis for {topic}.\n\n"
        "Your deliverables:\n"
        "1. Key strategic insights — 3-5 non-obvious takeaways\n"
        "2. Opportunities — unmet needs, adjacencies, growth vectors\n"
        "3. Threats — competitive moves, market shifts, regulatory risks\n"
        "4. Recommended actions — prioritized, specific, with rationale"
    ),
    expected_output=(
        "A strategy memo in markdown with sections: "
        "Key Insights, Opportunities, Threats, Recommended Actions."
    ),
    agent=STRATEGIST,
)

WRITING_TASK = Task(
    description=(
        "Synthesize the research memo and strategy memo into a polished, "
        "publication-ready product analysis report for {topic}.\n\n"
        "Structure the report as:\n"
        "1. Executive Summary — 3-5 sentence overview of the most important findings\n"
        "2. Product Deep Dive — what it does, who it's for, how it works\n"
        "3. Market & Competitive Analysis — positioning, landscape, differentiation\n"
        "4. Strategic Assessment — opportunities, threats, recommendations\n"
        "5. Conclusion — key takeaway\n\n"
        "The tone should be professional, objective, and insightful. "
        "Use headings, bullet points, and bold text for readability."
    ),
    expected_output=(
        "A complete product analysis report in markdown, ready for publication."
    ),
    agent=WRITER,
)
