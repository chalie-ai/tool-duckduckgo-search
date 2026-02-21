"""
DuckDuckGo Search Tool Handler — Search the web for current information.

Returns titles, snippets, and URLs from DuckDuckGo (no API key required).
Config injected via runner.py; defaults fall back to os.getenv().
"""

import logging
import os

logger = logging.getLogger(__name__)


def execute(topic: str, params: dict, config: dict = None, telemetry: dict = None) -> dict:
    """
    Execute a web search query via DuckDuckGo.

    Args:
        topic: Conversation topic (passed by framework)
        params: {"query": str, "limit": int (optional, default 5)}
        config: {"DUCKDUCKGO_TIMEOUT"}

    Returns:
        {"results": [{"title", "snippet", "url"}], "count": int}
    """
    config = config or {}

    timeout = int(config.get("DUCKDUCKGO_TIMEOUT") or os.getenv("DUCKDUCKGO_TIMEOUT", "8"))

    query = params.get("query", "")
    limit = params.get("limit", 5)
    limit = max(1, min(10, limit))

    if not query or not query.strip():
        return {"results": [], "count": 0}

    query = query.strip()

    try:
        results = _search_ddg(query, limit, timeout)
    except Exception as e:
        logger.error(f"[DUCKDUCKGO SEARCH] Search failed: {e}")
        return {"results": [], "count": 0, "error": str(e)[:200]}

    formatted = []
    for r in results:
        snippet = r.get("snippet", "")
        if len(snippet) > 200:
            snippet = snippet[:197] + "..."
        formatted.append({
            "title": r.get("title", ""),
            "snippet": snippet,
            "url": r.get("url", "")
        })

    return {
        "results": formatted,
        "count": len(formatted),
    }


# ── Search backend ────────────────────────────────────────────────

def _search_ddg(query: str, limit: int, timeout: int) -> list:
    from duckduckgo_search import DDGS
    results = []
    with DDGS(timeout=timeout) as ddgs:
        for r in ddgs.text(query, max_results=limit):
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "url": r.get("href", "")
            })
    return results
