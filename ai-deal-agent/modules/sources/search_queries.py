import os
import requests
import datetime
from typing import List, Dict, Any

class SearchQueries:
    def __init__(self, templates: List[str]):
        self.brave_api_key = os.environ.get("BRAVE_SEARCH_API_KEY")
        self.tavily_api_key = os.environ.get("TAVILY_API_KEY")
        self.templates = templates

    def generate_daily_queries(self) -> List[str]:
        now = datetime.datetime.now()
        month = now.strftime("%B")
        year = now.strftime("%Y")
        
        # We rotate queries daily by taking a slice. Let's just run 3 per day to save credits, or all 10 if requested.
        # For this implementation, we run all defined templates formatted with current month/year.
        queries = []
        for t in self.templates:
            q = t.replace("{month}", month).replace("{year}", year)
            queries.append(q)
        return queries

    def execute_brave_search(self, query: str) -> List[Dict[str, Any]]:
        if not self.brave_api_key:
            return []
            
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.brave_api_key
        }
        params = {"q": query, "count": 10}
        
        results = []
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("web", {}).get("results", []):
                    results.append({
                        "url": item.get("url"),
                        "name": item.get("title"),
                        "content": item.get("description"), # Brave provides a snippet
                        "source_type": "search"
                    })
        except Exception as e:
            print(f"Brave Search Error for '{query}': {e}")
        return results

    def search_all(self) -> List[Dict[str, Any]]:
        queries = self.generate_daily_queries()
        all_results = []
        for q in queries:
            print(f"Executing search: {q}")
            results = self.execute_brave_search(q)
            all_results.extend(results)
        return all_results
