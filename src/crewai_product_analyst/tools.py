import asyncio
import concurrent.futures
import json
import subprocess
from pathlib import Path

import httpx
from crewai.tools import tool
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


def _run_async(coro):
    """Safely run an async coroutine from a sync context."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    with concurrent.futures.ThreadPoolExecutor() as pool:
        return pool.submit(asyncio.run, coro).result()


async def _call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """Call an ai-analyze MCP tool via stdio transport."""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            text = result.content[0].text if result.content else "{}"
            return json.loads(text)


def _format_mcp_result(data: dict, project_name: str) -> str:
    """Format MCP analysis result into readable text for the agent."""
    lines = [
        f"# Code Analysis: {project_name}",
        f"**Total source files analyzed:** {data.get('total_files', 'N/A')}",
        "",
    ]

    # Quality section
    quality = data.get("quality", {})
    if quality:
        score = quality.get("score", quality.get("total_score", "N/A"))
        grade = quality.get("grade", "N/A")
        lines.append(f"## Quality Score: {score}/100 (Grade: {grade})")
        if "dimensions" in quality:
            for dim, val in quality["dimensions"].items():
                lines.append(f"- **{dim}**: {val}")
        lines.append("")

    # AST section
    ast_data = data.get("ast", {})
    if ast_data:
        ast_files = ast_data.get("files", [])
        lines.append(f"## AST Analysis ({len(ast_files)} files of {ast_data.get('analyzed_files', 'N/A')} total)")
        lines.append("")

        total_funcs = sum(len(f.get("functions", [])) for f in ast_files)
        total_classes = sum(len(f.get("classes", [])) for f in ast_files)
        total_smells = sum(len(f.get("code_smells", [])) for f in ast_files)
        complexities = [
            f.get("overall_complexity", {}).get("cyclomatic", 0)
            for f in ast_files
            if f.get("overall_complexity")
        ]
        avg_c = sum(complexities) / len(complexities) if complexities else 0

        lines.append(f"- **Functions:** {total_funcs}, **Classes:** {total_classes}, **Code Smells:** {total_smells}")
        lines.append(f"- **Avg cyclomatic complexity:** {avg_c:.1f}")

        # Severity breakdown
        severity_count: dict[str, int] = {}
        smell_types: dict[str, int] = {}
        for f in ast_files:
            for smell in f.get("code_smells", []):
                sev = smell.get("severity", "unknown")
                severity_count[sev] = severity_count.get(sev, 0) + 1
                name = smell.get("name", "unknown")
                smell_types[name] = smell_types.get(name, 0) + 1

        if severity_count:
            lines.append("")
            lines.append("### Code Smells by Severity")
            for sev in ["critical", "high", "medium", "low"]:
                if sev in severity_count:
                    lines.append(f"- **{sev}**: {severity_count[sev]}")

        if smell_types:
            top_smells = sorted(smell_types.items(), key=lambda x: -x[1])[:5]
            lines.append("")
            lines.append("### Most Common Smell Types")
            for name, count in top_smells:
                lines.append(f"- **{name}**: {count} occurrences")

        # Most complex files
        sorted_ast = sorted(ast_files, key=lambda f: f.get("overall_complexity", {}).get("cyclomatic", 0), reverse=True)
        lines.append("")
        lines.append("### Most Complex Files (Top 5)")
        for f in sorted_ast[:5]:
            c = f.get("overall_complexity", {})
            path_short = f.get("file_path", "").replace(data.get("project_path", ""), "").lstrip("/")
            lines.append(f"- **{path_short}** — C={c.get('cyclomatic', '?')}, {c.get('lines_of_code', '?')} LOC, {len(f.get('functions', []))} funcs")

        # Largest files
        largest = sorted(ast_files, key=lambda f: f.get("total_lines", 0), reverse=True)
        lines.append("")
        lines.append("### Largest Files (Top 5)")
        for f in largest[:5]:
            path_short = f.get("file_path", "").replace(data.get("project_path", ""), "").lstrip("/")
            lines.append(f"- **{path_short}** — {f.get('total_lines', '?')} lines, {len(f.get('functions', []))} functions, {len(f.get('classes', []))} classes")

    # Dependency section
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

    # Security section
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
    """Run code analysis on a project using AI-Analyze MCP server.
    Returns quality score, complexity metrics, code smells, dependencies, and security findings.
    Provide an absolute path like /Users/erishen/path/to/project."""
    path = Path(project_path).expanduser().resolve()
    if not path.exists():
        return f"Error: path {path} does not exist"

    try:
        data = _run_async(_call_mcp_tool("analyze_project", {
            "project_path": str(path),
            "analysis_types": "ast,quality,dependency",
        }))
    except Exception as e:
        return f"Error: MCP analysis failed: {e}"

    if "error" in data:
        return f"Analysis error: {data['error']}"

    return _format_mcp_result(data, path.name)
