import os
from anthropic import Anthropic
import json
from typing import Dict, Any

class LLMVerifier:
    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
             print("Warning: ANTHROPIC_API_KEY not found. Verification will not work.")
             self.client = None
        else:
             self.client = Anthropic(api_key=self.api_key)
             
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "verification_system.txt")
        try:
            with open(prompt_path, "r") as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            self.system_prompt = "Verify the deal."

    def verify_deal(self, deal_data: dict, http_result: dict) -> Dict[str, Any]:
        if not self.client:
            return {"verification_status": "UNVERIFIED", "confidence_score": 0}
            
        payload = {
            "candidate_deal": deal_data,
            "http_verification": http_result
        }
            
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=500,
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": json.dumps(payload, indent=2)
                    }
                ]
            )
            
            raw_text = message.content[0].text
            if "```json" in raw_text:
                json_str = raw_text.split("```json")[1].split("```")[0].strip()
            else:
                json_str = raw_text.strip()
                
            result = json.loads(json_str)
            return result
        except Exception as e:
            print(f"LLM Verification error for {deal_data.get('tool_name')}: {e}")
            return {"verification_status": "UNVERIFIED", "confidence_score": 0}
