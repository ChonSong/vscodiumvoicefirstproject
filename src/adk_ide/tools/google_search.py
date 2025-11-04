"""Google Search tool integration for ADK agents."""
from typing import Any, Dict, Optional
import os


class GoogleSearchTool:
    """Google Search tool wrapper for ADK agents."""

    def __init__(self) -> None:
        self.name = "google_search"
        self.description = "Search the web using Google Search API"
        self._api_key: Optional[str] = os.environ.get("GOOGLE_API_KEY")
        self._search_engine_id: Optional[str] = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")

    async def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Google search."""
        query = payload.get("query", "")
        if not query:
            return {"error": "query parameter is required"}

        # Try to use Google Custom Search API if available
        if self._api_key and self._search_engine_id:
            try:
                import httpx  # type: ignore

                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": self._api_key,
                    "cx": self._search_engine_id,
                    "q": query,
                }
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        items = data.get("items", [])
                        return {
                            "status": "success",
                            "query": query,
                            "results": [
                                {
                                    "title": item.get("title", ""),
                                    "link": item.get("link", ""),
                                    "snippet": item.get("snippet", ""),
                                }
                                for item in items[:5]  # Limit to 5 results
                            ],
                        }
                    return {"error": f"Search API error: {response.status_code}"}
            except ImportError:
                pass
            except Exception as exc:
                return {"error": f"Search failed: {str(exc)}"}

        # Fallback: return mock results
        return {
            "status": "success",
            "query": query,
            "results": [
                {
                    "title": f"Search result for: {query}",
                    "link": "https://example.com",
                    "snippet": f"Mock search result snippet for query: {query}",
                }
            ],
            "note": "Mock results - configure GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID for real search",
        }


def get_google_search_tool() -> Optional[GoogleSearchTool]:
    """Get Google Search tool if API key is configured."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        return GoogleSearchTool()
    return None

