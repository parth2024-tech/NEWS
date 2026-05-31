import hashlib
from rapidfuzz import fuzz
from typing import List, Dict, Any, Set

class Deduplicator:
    def __init__(self):
        self.seen_hashes: Set[str] = set()
        self.processed_items: List[Dict[str, Any]] = []

    def get_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def process(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deduped = []
        for item in raw_data:
            content = item.get("content", "")
            if not content:
                continue
                
            # 1. Exact Hash Match
            content_hash = self.get_hash(content)
            if content_hash in self.seen_hashes:
                continue
                
            # 2. Fuzzy Matching against already processed items in this run
            # Compare first 200 chars
            snippet = content[:200]
            is_duplicate = False
            for processed in self.processed_items:
                processed_snippet = processed.get("content", "")[:200]
                # If fuzzy match ratio > 85%, consider it duplicate
                if fuzz.ratio(snippet, processed_snippet) > 85:
                    is_duplicate = True
                    break
                    
            if not is_duplicate:
                self.seen_hashes.add(content_hash)
                self.processed_items.append(item)
                deduped.append(item)
                
        print(f"Deduplicator: Reduced {len(raw_data)} items to {len(deduped)} items.")
        return deduped
