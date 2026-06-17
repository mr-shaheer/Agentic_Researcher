import os
import json
from agents import function_tool
from tavily import AsyncTavilyClient

@function_tool
async def web_search(query: str) -> str:
    """Search the web and return up to top 3 relevant results bullet points."""
    client = AsyncTavilyClient(api_key = os.getenv("TAVILY_API_KEY"))
    response = await client.search(query, max_results = 3)
    
    results = [
        {
            "title": r["title"],
            "url": r["url"],
            "content": r["content"]
        }
        for r in response["results"]
    ]
    
    return json.dumps(results)