from crewai import Crew, Process

from crewai_product_analyst.agents import RESEARCHER, STRATEGIST, WRITER
from crewai_product_analyst.tasks import RESEARCH_TASK, STRATEGY_TASK, WRITING_TASK


def create_crew(topic: str, verbose: bool = True) -> Crew:
    return Crew(
        agents=[RESEARCHER, STRATEGIST, WRITER],
        tasks=[RESEARCH_TASK, STRATEGY_TASK, WRITING_TASK],
        process=Process.sequential,
        verbose=verbose,
    )


def run_analysis(topic: str, verbose: bool = True) -> str:
    crew = create_crew(topic=topic, verbose=verbose)
    result = crew.kickoff(inputs={"topic": topic})
    return result.raw if hasattr(result, "raw") else str(result)
