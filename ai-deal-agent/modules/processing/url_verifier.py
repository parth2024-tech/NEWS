import requests
from urllib.parse import urlparse
from typing import Dict, Any, List
import time

class URLVerifier:
    def __init__(self):
        pass

    def verify(self, claim_url: str, expected_website_url: str) -> Dict[str, Any]:
        result = {
            "status_code": None,
            "is_alive": False,
            "flag": None, # LIKELY_DEAD, UNVERIFIED_REDIRECT, HALLUCINATED, or None
            "redirect_url": None
        }
        
        if not claim_url or claim_url.lower() == "none" or claim_url.lower() == "n/a":
            result["flag"] = "HALLUCINATED"
            return result

        expected_domain = self._get_domain(expected_website_url)
        claim_domain = self._get_domain(claim_url)
        
        # Fast fail for obvious hallucinations
        if expected_domain and claim_domain and expected_domain not in claim_domain:
            result["flag"] = "HALLUCINATED"
            return result
            
        try:
            start_time = time.time()
            # Use HEAD for efficiency, allow redirects to trace where it ends up
            response = requests.head(claim_url, timeout=5, allow_redirects=True)
            result["status_code"] = response.status_code
            result["is_alive"] = response.status_code == 200
            
            if response.status_code == 404:
                result["flag"] = "LIKELY_DEAD"
            elif len(response.history) > 0:
                final_url = response.url
                result["redirect_url"] = final_url
                # If it redirects to the root homepage, it's a weak signal
                final_path = urlparse(final_url).path
                if final_path in ["", "/"]:
                    result["flag"] = "UNVERIFIED_REDIRECT"
                    
        except requests.exceptions.Timeout:
            result["flag"] = "TIMEOUT"
        except requests.exceptions.RequestException as e:
            result["flag"] = "ERROR"
            
        return result
        
    def _get_domain(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return ""
