# nova/web_search_agent.py

from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain.agents import Tool, initialize_agent, AgentType
import os

# 🔐 Set Tavily API key
os.environ["TAVILY_API_KEY"] = "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"

# 🧠 Tavily LangChain tool
search_tool = TavilySearchResults()

# Wrap it into LangChain Tool (if you want to use agents later)
tools = [
    Tool.from_function(
        func=search_tool.run,
        name="search",
        description="Search engine tool using Tavily"
    )
]

# 🔁 Simple wrapper function (no agent logic for now)
def run_web_search_agent(queries: list[str]):
    results = {}

    for query in queries:
        print(f"🔍 Searching: {query}")
        response = search_tool.invoke(query)
        print(f"DEBUG: response for query '{query}': {type(response)} - {str(response)[:300]}")
        # Ensure response is a list of dicts with 'url'
        if isinstance(response, list) and all(isinstance(r, dict) and 'url' in r for r in response):
            results[query] = response[:3]
        else:
            # Fallback: wrap string or unexpected format
            results[query] = []
    return results
