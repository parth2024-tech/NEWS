import feedparser
from typing import List, Dict, Any

class RSSFeedsScraper:
    def __init__(self, sources: List[Dict[str, str]]):
        self.sources = sources

    def scrape_all(self) -> List[Dict[str, Any]]:
        results = []
        for source in self.sources:
            url = source.get("url")
            print(f"Parsing RSS feed: {url}")
            try:
                feed = feedparser.parse(url)
                # Take top 5 entries to avoid massive payload
                for entry in feed.entries[:5]:
                    content = entry.get('summary', '')
                    if 'content' in entry and len(entry.content) > 0:
                        content += "\n" + entry.content[0].value
                        
                    results.append({
                        "url": entry.link,
                        "name": entry.title,
                        "content": content,
                        "source_type": "newsletter" if "newsletter" in source.get("name", "").lower() or "tldr" in source.get("name", "").lower() else "blog"
                    })
            except Exception as e:
                print(f"Error parsing RSS {url}: {e}")
        return results
