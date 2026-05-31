import os
import requests
from typing import Dict, Any

class TelegramAlert:
    def __init__(self):
        self.bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        
    def send_high_value_alert(self, deal: Dict[str, Any]):
        if not self.bot_token or not self.chat_id:
             print("Warning: Telegram credentials missing. High-value alert skipped.")
             return
             
        message = f"""🚨 *HIGH VALUE DEAL FOUND*
*Tool:* {deal.get('tool_name')}
*Value:* {deal.get('discounted_price_or_value')}
*Eligibility:* {deal.get('eligibility')}
*Expires:* {deal.get('expiry_date') or 'Ongoing'}
*Claim:* [Link]({deal.get('claim_url')})
*Source:* {deal.get('source_type')}
*Confidence:* {deal.get('confidence_score')}/10
"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"Telegram alert sent for {deal.get('tool_name')}")
            else:
                print(f"Failed to send Telegram alert: {response.text}")
        except Exception as e:
            print(f"Telegram API Error: {e}")

    def send_watchdog_alert(self, message: str):
        if not self.bot_token or not self.chat_id:
             return
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": f"⚠️ *AI Deal Agent Watchdog Alert*\n\n{message}",
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload, timeout=10)
        except:
            pass
