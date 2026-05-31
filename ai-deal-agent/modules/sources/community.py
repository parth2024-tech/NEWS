import requests
from typing import List, Dict, Any

class CommunityScraper:
    def __init__(self, sources: List[Dict[str, Any]]):
        self.sources = sources

    def scrape_hackernews(self, query: str) -> List[Dict[str, Any]]:
        # Algolia HN API
        url = "https://hn.algolia.com/api/v1/search_by_date"
        params = {
            "query": query,
            "tags": "story",
            "numericFilters": "points>50" # Filter by score > 50 to cut noise
        }
        results = []
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for hit in data.get("hits", []):
                    results.append({
                        "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                        "name": hit.get("title"),
                        "content": hit.get("story_text", "") or hit.get("title"),
                        "source_type": "community"
                    })
        except Exception as e:
            print(f"HN Scrape error for '{query}': {e}")
        return results

    def scrape_all(self) -> List[Dict[str, Any]]:
        results = []
        for source in self.sources:
            t = source.get("type")
            if t == "hackernews":
                q = source.get("query", "AI credits")
                print(f"Scraping HackerNews for: {q}")
                results.extend(self.scrape_hackernews(q))
            elif t == "reddit":
                # Mocked for Phase 2: normally uses pushshift or RSS bridge
                print(f"Reddit scraping initialized for {source.get('subreddits')}")
            elif t == "producthunt":
                # Mocked for Phase 2: requires PH API key
                print(f"ProductHunt scraping initialized for category: {source.get('category')}")
        return results
