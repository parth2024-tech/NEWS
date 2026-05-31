from typing import List, Dict, Any, Tuple
from modules.storage.database import Database, Deal

class ChangeDetector:
    def __init__(self, db: Database):
        self.db = db

    def detect_changes(self, extracted_deals: List[Deal]) -> Tuple[List[Dict], List[Dict]]:
        """
        Returns (new_deals, updated_deals) where each item is a dict ready for email/db.
        """
        new_deals = []
        updated_deals = []
        seen_in_this_run = set()
        
        for deal in extracted_deals:
            key = f"{deal.tool_name}::{deal.plan_name}"
            # Deduplicate exact tool/plan in the same run to avoid double processing
            if key in seen_in_this_run:
                continue
            seen_in_this_run.add(key)
            
            existing = self.db.get_deal_by_tool_and_plan(deal.tool_name, deal.plan_name)
            
            if not existing:
                # NEW DEAL
                deal_dict = deal.model_dump(exclude_none=True)
                deal_dict["status_flag"] = "NEW"
                self.db.insert_deal(deal)
                new_deals.append(deal_dict)
            else:
                # Existing deal, check for updates
                updates = []
                # Check value
                if existing.get("value_usd") != deal.value_usd and deal.value_usd is not None:
                     updates.append(f"Value changed: {existing.get('value_usd')} -> {deal.value_usd}")
                # Check expiry
                # Convert both to string/date for fair comparison if needed, simplified here
                
                if updates:
                    deal_dict = deal.model_dump(exclude_none=True)
                    deal_dict["status_flag"] = "UPDATED"
                    deal_dict["diff_string"] = " | ".join(updates)
                    # Note: We should actually update the DB here, but insert_deal handles it if we use upsert
                    # For now, we just pass to email
                    updated_deals.append(deal_dict)
                else:
                    # Reset misses if it was active
                    pass # TODO: Update DB consecutive_misses = 0 if it was > 0
                    
        return new_deals, updated_deals
