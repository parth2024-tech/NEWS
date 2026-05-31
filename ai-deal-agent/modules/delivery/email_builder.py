from typing import List, Dict, Any

class EmailBuilder:
    def __init__(self):
        pass

    def build_html(self, new_deals: List[Dict], updated_deals: List[Dict], watchlist: List[Dict] = [], evergreen: List[Dict] = []) -> str:
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
                .alert-bar { background: #e74c3c; color: white; padding: 10px; text-align: center; font-weight: bold; }
                .section { margin: 20px; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
                .top-pick { background: #f9f9f9; border-left: 5px solid #f39c12; }
                table { width: 100%; border-collapse: collapse; }
                th, td { padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }
                th { background-color: #f2f2f2; }
                .claim-btn { display: inline-block; padding: 8px 15px; background: #3498db; color: white; text-decoration: none; border-radius: 3px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🤖 AI Deal Agent Daily Report</h2>
            </div>
        """
        
        # 1. Alert Bar (mock logic)
        expiring_soon = [d for d in new_deals + updated_deals if d.get('expiry_date') == 'soon'] # simplified
        if expiring_soon:
            html += '<div class="alert-bar">🚨 Action Required: Deals expiring in < 48 hours!</div>'

        # 2. Today's #1 Pick
        if new_deals:
            # Sort by value_usd if available, else just pick first
            sorted_new = sorted(new_deals, key=lambda x: x.get('value_usd') or 0, reverse=True)
            pick = sorted_new[0]
            html += f"""
            <div class="section top-pick">
                <h3>🏆 Today's #1 Pick: {pick.get('tool_name')} - {pick.get('plan_name')}</h3>
                <p><strong>Value:</strong> {pick.get('discounted_price_or_value')}</p>
                <p><strong>Eligibility:</strong> {pick.get('eligibility')}</p>
                <a href="{pick.get('claim_url')}" class="claim-btn">Claim Deal</a>
            </div>
            """

        # 3. New This Morning
        if new_deals:
            html += '<div class="section"><h3>🌟 New This Morning</h3><table><tr><th>Tool</th><th>Plan</th><th>Value</th><th>Eligibility</th><th>Claim</th></tr>'
            for d in new_deals:
                html += f"<tr><td>{d.get('tool_name')}</td><td>{d.get('plan_name')}</td><td>{d.get('discounted_price_or_value')}</td><td>{d.get('eligibility')}</td><td><a href='{d.get('claim_url')}'>Link</a></td></tr>"
            html += '</table></div>'

        # 4. Updated Deals
        if updated_deals:
            html += '<div class="section"><h3>🔄 Updated Deals</h3><ul>'
            for d in updated_deals:
                 html += f"<li><strong>{d.get('tool_name')}</strong>: {d.get('diff_string')}</li>"
            html += '</ul></div>'
            
        # 5. Watchlist (Unverified Deals)
        if watchlist:
            html += '<div class="section"><h3>👀 Watchlist (Unverified)</h3><ul>'
            for d in watchlist:
                 html += f"<li><strong>{d.get('tool_name')}</strong> - {d.get('plan_name')}: {d.get('discounted_price_or_value')} <a href='{d.get('claim_url')}'>Check manually</a></li>"
            html += '</ul></div>'

        # 6. Regional Spotlight (India focus)
        regional_deals = [d for d in new_deals + updated_deals + evergreen if d.get('region') in ['IN', 'global']]
        if regional_deals:
            spotlight = regional_deals[0] # Pick the first one
            html += f"""
            <div class="section">
                <h3>🌏 Regional Spotlight (India / Global)</h3>
                <p><strong>{spotlight.get('tool_name')}</strong>: {spotlight.get('discounted_price_or_value')} ({spotlight.get('eligibility')})</p>
                <a href="{spotlight.get('claim_url')}" class="claim-btn">View Deal</a>
            </div>
            """

        # 7. Top 5 Evergreen
        if evergreen:
            sorted_evergreen = sorted(evergreen, key=lambda x: x.get('value_usd') or 0, reverse=True)[:5]
            html += '<div class="section"><h3>🌲 Top 5 Evergreen Deals</h3><ul>'
            for d in sorted_evergreen:
                html += f"<li><strong>{d.get('tool_name')}</strong>: {d.get('discounted_price_or_value')} <a href='{d.get('claim_url')}'>Link</a></li>"
            html += '</ul></div>'
            
        if not new_deals and not updated_deals and not watchlist:
            html += '<div class="section"><p>No new deals found today. Keeping watch! 👁️</p></div>'

        html += """
        </body>
        </html>
        """
        return html
