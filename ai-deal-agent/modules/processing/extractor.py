import os
from anthropic import Anthropic
from pydantic import BaseModel
from typing import List, Optional
import json

class ExtractedDeal(BaseModel):
    tool_name: str
    website_url: str
    premium_plan_name: str
    normal_monthly_cost_usd: Optional[float]
    discount_type: str
    discounted_price_or_value: str
    eligibility_requirement: str
    claim_url: str
    expiry_date_or_ongoing: str
    source_url: str
    source_type: str
    raw_snippet: str

class Extractor:
    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
             print("Warning: ANTHROPIC_API_KEY not found. Extraction will not work.")
             self.client = None
        else:
             self.client = Anthropic(api_key=self.api_key)
             
        # Load prompt
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "extraction_system.txt")
        try:
            with open(prompt_path, "r") as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            self.system_prompt = "Extract deals."

    def extract_deals(self, content: str, source_url: str, source_type: str) -> List[ExtractedDeal]:
        if not self.client:
            return []
            
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=2048,
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Source URL: {source_url}\nSource Type: {source_type}\n\nContent:\n{content}"
                    }
                ]
            )
            
            # The prompt instructs Claude to return JSON. We parse it here.
            # We assume Claude returns a JSON array of deals.
            raw_text = message.content[0].text
            # Very basic extraction of JSON array from text if surrounded by markdown
            if "```json" in raw_text:
                json_str = raw_text.split("```json")[1].split("```")[0].strip()
            else:
                json_str = raw_text.strip()
                
            data = json.loads(json_str)
            deals = []
            for item in data:
                deals.append(ExtractedDeal(**item))
            return deals
        except Exception as e:
            print(f"Extraction error for {source_url}: {e}")
            return []
