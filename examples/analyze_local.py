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
    from crewai_product_analyst.crew import run_analysis
    result = run_analysis(topic=args.project_path.name, verbose=True)

    if args.output:
        args.output.write_text(result)
        print(f"Report saved to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
