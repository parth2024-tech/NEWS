import yaml
import os
import argparse
from modules.sources.official_pages import OfficialPagesScraper
from modules.sources.search_queries import SearchQueries
from modules.sources.rss_feeds import RSSFeedsScraper
from modules.sources.community import CommunityScraper
from modules.processing.deduplicator import Deduplicator
from modules.processing.extractor import Extractor
from modules.processing.url_verifier import URLVerifier
from modules.processing.verifier import LLMVerifier
from modules.storage.change_detector import ChangeDetector
from modules.delivery.sendgrid_sender import EmailSender
from modules.delivery.telegram_alert import TelegramAlert

def load_yaml(filename: str):
    path = os.path.join(os.path.dirname(__file__), "config", filename)
    with open(path, "r") as f:
        return yaml.safe_load(f)

def run_phase(phase: int):
    print(f"Starting AI Deal Agent - Phase {phase}")
    config = load_yaml("sources.yaml")
    queries_config = load_yaml("query_templates.yaml")
    
    db = Database()
    extractor = Extractor()
    email_sender = EmailSender()
    
    # Phase 3 Init
    url_verifier = URLVerifier() if phase >= 3 else None
    llm_verifier = LLMVerifier() if phase >= 3 else None
    telegram = TelegramAlert() if phase >= 3 else None
    
    # Init sources
    sources = config.get("sources", {})
    official_scraper = OfficialPagesScraper(sources.get("official_pages", []) + sources.get("partners", []))
    
    scraped_data = []
    
    if phase >= 1:
        print("Scraping official pages & partners...")
        scraped_data.extend(official_scraper.scrape_all())
        
    if phase >= 2:
        print("Scraping search queries...")
        searcher = SearchQueries(queries_config.get("queries", []))
        scraped_data.extend(searcher.search_all())
        
        print("Scraping RSS feeds...")
        rss = RSSFeedsScraper(sources.get("rss_feeds", []))
        scraped_data.extend(rss.scrape_all())
        
        print("Scraping communities...")
        comm = CommunityScraper(sources.get("communities", []))
        scraped_data.extend(comm.scrape_all())

    # Deduplication (Phase 2+)
    if phase >= 2:
        print("Deduplicating raw data...")
        deduplicator = Deduplicator()
        scraped_data = deduplicator.process(scraped_data)

    # Pass 1: Extraction
    print("Extracting deals...")
    all_extracted_deals = []
    for data in scraped_data:
        deals = extractor.extract_deals(data["content"], data["url"], data["source_type"])
        all_extracted_deals.extend(deals)
        
    print(f"Extracted {len(all_extracted_deals)} candidate deals.")

    db_deals = []
    watchlist_deals = []

    # Phase 3: Verification (Pass 2)
    if phase >= 3:
        print("Running Live URL and LLM Verifications...")
        for ext in all_extracted_deals:
            # 1. URL Check
            http_res = url_verifier.verify(ext.claim_url, ext.website_url)
            
            # 2. LLM Check
            verify_res = llm_verifier.verify_deal(ext.model_dump(), http_res)
            
            status = verify_res.get("verification_status", "UNVERIFIED")
            score = verify_res.get("confidence_score", 0)
            
            deal = Deal(
                tool_name=ext.tool_name,
                plan_name=ext.premium_plan_name,
                discount_type=ext.discount_type,
                eligibility=ext.eligibility_requirement,
                claim_url=ext.claim_url,
                verification_status=status,
                confidence_score=score,
                source_type=ext.source_type
            )
            
            if status in ["VERIFIED", "LIKELY_VALID"]:
                db_deals.append(deal)
                # Layer 10: Instant Alert
                if status == "VERIFIED" and (deal.value_usd and deal.value_usd > 500):
                    telegram.send_high_value_alert(deal.model_dump())
            elif status == "UNVERIFIED":
                watchlist_deals.append(deal.model_dump())
            # EXPIRED or REJECT are dropped
    else:
        # Pre-Phase 3 Mock Mapping
        for ext in all_extracted_deals:
            db_deals.append(Deal(
                tool_name=ext.tool_name, plan_name=ext.premium_plan_name, discount_type=ext.discount_type,
                eligibility=ext.eligibility_requirement, claim_url=ext.claim_url, verification_status="UNVERIFIED",
                confidence_score=0, source_type=ext.source_type
            ))

    # Storage & Change Detection
    new_deals_for_email = []
    updated_deals_for_email = []
    
    if phase >= 2:
        print("Detecting changes against database...")
        detector = ChangeDetector(db)
        new_deals_for_email, updated_deals_for_email = detector.detect_changes(db_deals)
        print(f"Found {len(new_deals_for_email)} new, {len(updated_deals_for_email)} updated.")
    else:
        for deal in db_deals:
            if not db.get_deal_by_tool_and_plan(deal.tool_name, deal.plan_name):
                db.insert_deal(deal)
                new_deals_for_email.append(deal.model_dump())

    # Delivery
    print("Sending daily report...")
    email_sender.builder.build_html(new_deals_for_email, updated_deals_for_email, watchlist_deals, db.get_active_deals() if phase >= 2 else [])
    email_sender.send_daily_report(new_deals_for_email, updated_deals_for_email)
    print("Run complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Deal Agent")
    parser.add_argument("--phase", type=int, default=2, help="Which phase to run (1-4)")
    args = parser.parse_args()
    
    run_phase(args.phase)

