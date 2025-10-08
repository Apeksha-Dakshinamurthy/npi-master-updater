import os
from langchain_community.tools.tavily_search import TavilySearchResults

def get_tavily_tool(max_results=3):
    api_key = os.getenv('TAVILY_API_KEY')
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set")
    return TavilySearchResults(max_results=max_results, api_key=api_key)
