import os
from pathlib import Path
import subprocess

import httpx
from crewai.tools import tool


@tool("Web Search")
def web_search(query: str) -> str:
    """Search the web for recent information about a product or company."""
    try:
        response = httpx.get(
            "https://lite.duckduckgo.com/lite/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        return response.text[:3000]
    except Exception as e:
        return f"Search failed: {e}"


@tool("Fetch Webpage")
def fetch_webpage(url: str) -> str:
    """Fetch and extract text content from a URL."""
    try:
        response = httpx.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20,
            follow_redirects=True,
        )
        return response.text[:5000]
    except Exception as e:
        return f"Failed to fetch {url}: {e}"


@tool("Read Local Project")
def read_local_project(project_path: str) -> str:
    """Read a local project's structure, README, and config to understand what it does.
    Provide an absolute path like /Users/erishen/path/to/project."""
    path = Path(project_path).expanduser().resolve()
    if not path.exists():
        return f"Error: path {path} does not exist"

    parts = []
    parts.append(f"# Project: {path.name}\n")

    # README
    for readme in ("README.md", "README.zh-CN.md"):
        rp = path / readme
        if rp.exists():
            parts.append(f"## README\n{rp.read_text()[:3000]}\n")
            break

    # pyproject.toml / package.json
    for cfg in ("pyproject.toml", "package.json"):
        cp = path / cfg
        if cp.exists():
            content = cp.read_text()
            parts.append(f"## {cfg}\n```\n{content[:2000]}\n```\n")
            break

    # Top-level directory listing
    try:
        result = subprocess.run(
            ["ls", "-F", str(path)],
            capture_output=True, text=True, timeout=5,
        )
        files = [l for l in result.stdout.strip().split("\n") if l]
        parts.append(f"## Directory ({len(files)} entries)\n" + "\n".join(f"- {f}" for f in files))
    except Exception as e:
        parts.append(f"(Could not list dir: {e})")

    # README.zh-CN for more context
    rp_zh = path / "README.zh-CN.md"
    if rp_zh.exists():
        parts.append(f"\n## README.zh-CN\n{rp_zh.read_text()[:2000]}\n")

    return "\n".join(parts)


@tool("Analyze Code Structure")
def analyze_code_structure(project_path: str) -> str:
    """Run AST-based code structure analysis on a project.
    Returns detailed info about functions, classes, complexity, dependencies, and code smells.
    Provide an absolute path like /Users/erishen/path/to/project."""
    import json
    import tempfile

    path = Path(project_path).expanduser().resolve()
    if not path.exists():
        return f"Error: path {path} does not exist"

    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
    tmp_path = tmp.name
    tmp.close()

    try:
        result = subprocess.run(
            ["uv", "run", "ai-analyze", "ast", str(path), "--output", tmp_path],
            capture_output=True, text=True, timeout=300,
        )

        with open(tmp_path) as f:
            data = json.load(f)
    except subprocess.TimeoutExpired:
        return "Error: AST analysis timed out after 300 seconds"
    except json.JSONDecodeError as e:
        return f"Error: failed to parse AST analysis output: {e}\nSTDERR: {result.stderr[:1000]}"
    except Exception as e:
        return f"Error: AST analysis failed: {e}"
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    if "error" in data:
        return f"AST analysis error: {data['error']}"

    s = data["summary"]
    lines = [
        f"# Code Structure Analysis: {Path(data['project_path']).name}",
        "",
        f"**{s['total_files']}** files, **{s['total_functions']}** functions, **{s['total_classes']}** classes, **{s['total_code_smells']}** code smells",
        f"**Average cyclomatic complexity:** {s['average_complexity']:.1f}",
        "",
        "## Language Breakdown",
    ]

    for lang, stats in sorted(s["languages"].items()):
        lines.append(f"- **{lang}**: {stats['files']} files, {stats['functions']} functions, {stats['classes']} classes")

    # Top 10 most complex files
    sorted_files = sorted(data["files"], key=lambda f: f["overall_complexity"]["cyclomatic"], reverse=True)
    lines.extend(["", "## Most Complex Files (Top 10)"])

    for f in sorted_files[:10]:
        c = f["overall_complexity"]
        path_short = f["file_path"].replace(str(data["project_path"]), "").lstrip("/")
        lines.append(f"- **{path_short}** — C={c['cyclomatic']}, {c['lines_of_code']} LOC, {c['comment_lines']} comments")

    # Code smells summary
    all_smells = []
    for f in data["files"]:
        for smell in f.get("code_smells", []):
            all_smells.append(smell)

    if all_smells:
        severity_count = {}
        for smell in all_smells:
            sev = smell["severity"]
            severity_count[sev] = severity_count.get(sev, 0) + 1

        lines.extend(["", "## Code Smells by Severity"])
        for sev in ["critical", "high", "medium", "low"]:
            if sev in severity_count:
                lines.append(f"- **{sev}**: {severity_count[sev]}")

        # Most common smell types
        smell_types = {}
        for smell in all_smells:
            name = smell["name"]
            smell_types[name] = smell_types.get(name, 0) + 1

        top_smells = sorted(smell_types.items(), key=lambda x: -x[1])[:5]
        lines.extend(["", "## Most Common Smell Types"])
        for name, count in top_smells:
            lines.append(f"- **{name}**: {count} occurrences")

    # Key files with structure overview
    large_files = sorted(data["files"], key=lambda f: f["total_lines"], reverse=True)[:5]
    lines.extend(["", "## Largest Files (Top 5)"])
    for f in large_files:
        path_short = f["file_path"].replace(str(data["project_path"]), "").lstrip("/")
        lines.append(f"- **{path_short}** — {f['total_lines']} lines total, {len(f['functions'])} functions, {len(f['classes'])} classes")
        if f["imports"]:
            lines.append(f"  - Imports: {', '.join(f['imports'][:8])}")

    return "\n".join(lines)
