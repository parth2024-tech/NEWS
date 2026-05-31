import os
from firecrawl import FirecrawlApp
from typing import List, Dict, Any

class OfficialPagesScraper:
    def __init__(self, sources: List[Dict[str, str]]):
        api_key = os.environ.get("FIRECRAWL_API_KEY")
        if not api_key:
             print("Warning: FIRECRAWL_API_KEY not found. Official scraping will not work.")
             self.app = None
        else:
             self.app = FirecrawlApp(api_key=api_key)
        self.sources = sources

    def scrape_all(self) -> List[Dict[str, Any]]:
        results = []
        if not self.app:
            return results
            
        for source in self.sources:
            url = source.get("url")
            print(f"Scraping official page: {url}")
            try:
                # Use scrape_url which returns clean markdown
                result = self.app.scrape_url(url, params={'formats': ['markdown']})
                markdown_content = result.get('markdown', '')
                results.append({
                    "url": url,
                    "name": source.get("name"),
                    "content": markdown_content,
                    "source_type": "official"
                })
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                
        return results
