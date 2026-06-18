import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import httpx
from crewai.tools import tool


logger = logging.getLogger(__name__)


def _find_ai_analyze() -> Path | None:
    path = Path(__file__).resolve()
    for parent in path.parents:
        if (parent / "apps").is_dir() and (parent / "libs").is_dir():
            invest_kit_root = parent
            break
    else:
        return None
    candidate = invest_kit_root.parent.parent / "work" / "research" / "ai-analyze"
    return candidate if candidate.exists() else None


def _run_ai_analyze_ast(project_path: str) -> dict:
    ai_root = _find_ai_analyze()
    if not ai_root:
        return {"error": "ai-analyze project not found"}

    env = {**os.environ}
    src_path = str(ai_root / "src")
    env["PYTHONPATH"] = f"{src_path}:{env.get('PYTHONPATH', '')}"

    result = subprocess.run(
        [sys.executable, "-m", "cli", "ast", project_path],
        capture_output=True, text=True, timeout=300,
        env=env, cwd=str(ai_root),
    )

    if result.returncode != 0:
        return {"error": f"ai-analyze failed (rc={result.returncode}): {result.stderr[:1000]}"}

    for line in reversed(result.stdout.strip().split("\n")):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue

    return {"error": "no JSON output from ai-analyze", "stdout": result.stdout[:2000]}


def _format_analysis_result(data: dict, project_name: str) -> str:
    ast_data = data.get("summary", data.get("ast", {}))

    lines = [
        f"# Code Analysis: {project_name}",
        f"**Total source files analyzed:** {ast_data.get('total_files', data.get('total_files', 'N/A'))}",
        "",
    ]

    quality = data.get("quality", {})
    if quality:
        score = quality.get("score", quality.get("total_score", "N/A"))
        grade = quality.get("grade", "N/A")
        lines.append(f"## Quality Score: {score}/100 (Grade: {grade})")
        if "dimensions" in quality:
            for dim, val in quality["dimensions"].items():
                lines.append(f"- **{dim}**: {val}")
        lines.append("")
    if ast_data:
        lines.append(
            f"## AST Analysis ({ast_data.get('total_files', 0)} files)"
        )
        lines.append("")

        lines.append(
            f"- **Functions:** {ast_data.get('total_functions', 0)}, "
            f"**Classes:** {ast_data.get('total_classes', 0)}, "
            f"**Code Smells:** {ast_data.get('total_code_smells', 0)}"
        )
        lines.append(f"- **Avg cyclomatic complexity:** {ast_data.get('average_cyclomatic_complexity', '?')}")
        lines.append(f"- **Deep nesting (>4 levels):** {ast_data.get('deep_nesting_count', 0)} files")

        sev = ast_data.get("code_smells_by_severity", {})
        if sev:
            lines.append("")
            lines.append("### Code Smells by Severity")
            for s, c in sev.items():
                lines.append(f"- **{s}**: {c}")

        smells = ast_data.get("most_common_smell_types", {})
        if smells:
            lines.append("")
            lines.append("### Most Common Smell Types")
            for name, count in list(smells.items())[:5]:
                lines.append(f"- **{name}**: {count} occurrences")

        lang_bd = ast_data.get("language_breakdown", {})
        if lang_bd:
            lines.append("")
            lines.append("### Language Breakdown")
            for lang, stats in lang_bd.items():
                lines.append(f"- **{lang}**: {stats['files']} files, {stats['functions']} funcs, {stats['classes']} classes")

        complex_files = ast_data.get("most_complex_files", [])
        if complex_files:
            lines.append("")
            lines.append("### Most Complex Files (Top 5)")
            for f in complex_files:
                lines.append(
                    f"- **{f['file']}** — C={f['cyclomatic_complexity']}, "
                    f"{f['lines_of_code']} LOC, {f['functions']} funcs, {f['code_smells']} smells"
                )

        large_files = ast_data.get("largest_files", [])
        if large_files:
            lines.append("")
            lines.append("### Largest Files (Top 5)")
            for f in large_files:
                lines.append(
                    f"- **{f['file']}** — {f['total_lines']} lines, "
                    f"{f['functions']} funcs, {f['classes']} classes, {f['code_smells']} smells"
                )

    dep_data = data.get("dependency", {})
    if dep_data:
        lines.append("")
        lines.append("## Dependency Analysis")
        for key, val in dep_data.items():
            if isinstance(val, list) and len(val) <= 10:
                for item in val:
                    if isinstance(item, dict):
                        lines.append(f"- {item.get('source', item.get('file', '?'))} → {item.get('target', item.get('depends_on', '?'))}")
                    else:
                        lines.append(f"- {item}")
            elif isinstance(val, (int, float, str)):
                lines.append(f"- **{key}**: {val}")

    sec_data = data.get("security", {})
    if sec_data:
        findings = sec_data.get("findings", [])
        if findings:
            lines.append("")
            lines.append(f"## Security Findings ({len(findings)})")
            for finding in findings[:10]:
                sev = finding.get("severity", "")
                desc = finding.get("description", finding.get("message", ""))
                location = finding.get("location", finding.get("file", ""))
                lines.append(f"- [{sev}] {desc} @ {location}")

    return "\n".join(lines)


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

    for readme in ("README.md", "README.zh-CN.md"):
        rp = path / readme
        if rp.exists():
            parts.append(f"## README\n{rp.read_text()[:3000]}\n")
            break

    for cfg in ("pyproject.toml", "package.json"):
        cp = path / cfg
        if cp.exists():
            content = cp.read_text()
            parts.append(f"## {cfg}\n```\n{content[:2000]}\n```\n")
            break

    try:
        result = subprocess.run(
            ["ls", "-F", str(path)],
            capture_output=True, text=True, timeout=5,
        )
        files = [l for l in result.stdout.strip().split("\n") if l]
        parts.append(f"## Directory ({len(files)} entries)\n" + "\n".join(f"- {f}" for f in files))
    except Exception as e:
        parts.append(f"(Could not list dir: {e})")

    rp_zh = path / "README.zh-CN.md"
    if rp_zh.exists():
        parts.append(f"\n## README.zh-CN\n{rp_zh.read_text()[:2000]}\n")

    return "\n".join(parts)


@tool("Analyze Code Structure")
def analyze_code_structure(project_path: str) -> str:
    """Run code analysis on a project using AI-Analyze.
    Returns quality score, complexity metrics, code smells, dependencies, and security findings.
    Provide an absolute path like /Users/erishen/path/to/project."""
    path = Path(project_path).expanduser().resolve()
    if not path.exists():
        return f"Error: path {path} does not exist"

    try:
        data = _run_ai_analyze_ast(str(path))
    except Exception as e:
        return f"Error: analysis failed: {e}"

    if "error" in data:
        return f"Analysis error: {data['error']}"

    return _format_analysis_result(data, path.name)
