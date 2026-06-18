"""Example: analyze a local project using product-analyst.

Run:
    uv run python examples/analyze_local.py <project-path> [--output report.md]
"""

import argparse
import subprocess
import sys
from pathlib import Path


def get_project_summary(project_path: Path) -> str:
    """Gather basic project info for analysis context."""
    parts = []
    parts.append(f"# Project Summary: {project_path.name}")

    # Directory tree
    try:
        result = subprocess.run(
            ["find", str(project_path), "-maxdepth", "2", "-type", "f"],
            capture_output=True, text=True, timeout=10,
        )
        files = [
            p.replace(str(project_path) + "/", "")
            for p in result.stdout.strip().split("\n")
            if p and ".venv" not in p and "__pycache__" not in p and ".git" not in p and ".DS_Store" not in p
        ]
        parts.append(f"\n## Project Files ({len(files)})\n")
        parts.extend(f"- {f}" for f in sorted(files)[:50])
    except Exception as e:
        parts.append(f"\n(Could not list files: {e})")

    # pyproject.toml
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        parts.append(f"\n## pyproject.toml\n```\n{pyproject.read_text()[:2000]}\n```\n")

    # README
    for readme in ("README.md", "README.zh-CN.md"):
        rp = project_path / readme
        if rp.exists():
            parts.append(f"\n## {readme}\n{rp.read_text()[:2000]}\n")
            break

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Analyze a local project")
    parser.add_argument("project_path", type=Path, help="Path to project directory")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output file path")
    args = parser.parse_args()

    if not args.project_path.exists():
        print(f"Error: {args.project_path} does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"Gathering project info for {args.project_path.name}...")
    summary = get_project_summary(args.project_path)

    # Pass summary via env var for the Crew to use
    import os
    os.environ["PROJECT_ANALYSIS_CONTEXT"] = summary

    print("Running product analysis...")
    from crewai_product_analyst.crew import create_crew

    crew = create_crew(topic=args.project_path.name, verbose=True)
    result = crew.kickoff(inputs={"topic": args.project_path.name})

    raw = result.raw if hasattr(result, "raw") else str(result)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_path = args.output or output_dir / f"{args.project_path.name}_product_analysis.md"
    output_path.write_text(raw)
    print(f"\nReport saved to: {output_path.resolve()}")

    print("\n" + "=" * 60)
    print("TOKEN USAGE")
    print("=" * 60)
    tu = result.token_usage if hasattr(result, "token_usage") else None
    if tu:
        if hasattr(tu, "model_dump"):
            tu = tu.model_dump()
        if isinstance(tu, dict):
            for k, v in tu.items():
                print(f"  {k}: {v}")
        else:
            print(f"  {tu}")
    else:
        print("  (not available)")


if __name__ == "__main__":
    main()
