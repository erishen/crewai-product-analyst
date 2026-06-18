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
