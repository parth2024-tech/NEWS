import os
from supabase import create_client, Client
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime

class Deal(BaseModel):
    id: Optional[str] = None
    tool_name: str
    plan_name: str
    discount_type: str
    value_usd: Optional[float] = None
    eligibility: str
    claim_url: str
    expiry_date: Optional[datetime.date] = None
    verification_status: str
    confidence_score: int
    source_type: str
    first_seen: Optional[datetime.datetime] = None
    last_confirmed: Optional[datetime.datetime] = None
    consecutive_misses: int = 0
    is_active: bool = True
    region: str = "global"

class Database:
    def __init__(self):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            print("Warning: SUPABASE_URL or SUPABASE_KEY not found. Operating in dry-run mode.")
            self.client = None
        else:
            self.client = create_client(supabase_url, supabase_key)

    def insert_deal(self, deal: Deal):
        if not self.client:
            print(f"[Dry Run] Would insert deal: {deal.tool_name} - {deal.plan_name}")
            return
            
        data = deal.model_dump(exclude_none=True)
        # Handle datetime serialization for Supabase
        if 'expiry_date' in data and data['expiry_date']:
             data['expiry_date'] = data['expiry_date'].isoformat()
        if 'first_seen' in data and data['first_seen']:
             data['first_seen'] = data['first_seen'].isoformat()
        if 'last_confirmed' in data and data['last_confirmed']:
             data['last_confirmed'] = data['last_confirmed'].isoformat()

        response = self.client.table("deals").insert(data).execute()
        return response

    def get_active_deals(self) -> List[Dict[str, Any]]:
        if not self.client:
            return []
        response = self.client.table("deals").select("*").eq("is_active", True).execute()
        return response.data

    def get_deal_by_tool_and_plan(self, tool_name: str, plan_name: str) -> Optional[Dict[str, Any]]:
        if not self.client:
            return None
        response = self.client.table("deals").select("*").eq("tool_name", tool_name).eq("plan_name", plan_name).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
