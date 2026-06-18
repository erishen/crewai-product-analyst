from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from crewai_product_analyst.crew import run_analysis

app = typer.Typer(help="AI-powered product analyst powered by CrewAI")
console = Console()


@app.command()
def analyze(
    topic: str = typer.Argument(..., help="Product or company to analyze"),
    output: Path = typer.Option(
        None, "--output", "-o", help="Output file path (default: stdout)"
    ),
    verbose: bool = typer.Option(True, "--verbose/--quiet"),
):
    """Run a full product analysis on the given topic."""
    console.print(Panel(f"Analyzing: [bold]{topic}[/bold]", title="Product Analyst"))

    result = run_analysis(topic=topic, verbose=verbose)

    if output:
        output.write_text(result)
        console.print(f"Report saved to [bold]{output}[/bold]")
    else:
        console.print(result)


@app.command()
def version():
    """Show version information."""
    from crewai_product_analyst import __version__

    console.print(f"crewai-product-analyst v{__version__}")


if __name__ == "__main__":
    app()
