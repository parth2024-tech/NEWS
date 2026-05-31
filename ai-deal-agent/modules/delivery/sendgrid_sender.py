import os
import base64
import csv
import io
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from typing import List, Dict, Any
from modules.delivery.email_builder import EmailBuilder

class EmailSender:
    def __init__(self):
        self.api_key = os.environ.get("SENDGRID_API_KEY")
        self.from_email = os.environ.get("EMAIL_FROM")
        self.to_email = os.environ.get("EMAIL_TO")
        self.builder = EmailBuilder()
        
        if not self.api_key or not self.from_email or not self.to_email:
             print("Warning: Email credentials not fully set up. Operating in dry-run mode.")
             self.client = None
        else:
             self.client = SendGridAPIClient(self.api_key)

    def generate_csv_attachment(self, deals: List[Dict], filename: str) -> Attachment:
        if not deals:
            return None
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=deals[0].keys())
        writer.writeheader()
        writer.writerows(deals)
        
        encoded_file = base64.b64encode(output.getvalue().encode('utf-8')).decode()
        
        attachment = Attachment()
        attachment.file_content = FileContent(encoded_file)
        attachment.file_type = FileType('text/csv')
        attachment.file_name = FileName(filename)
        attachment.disposition = Disposition('attachment')
        return attachment

    def send_daily_report(self, new_deals: List[Dict[str, Any]], updated_deals: List[Dict[str, Any]]):
        subject = "AI Deal Agent: Daily Report"
        if new_deals:
             # Sort by value if possible
             highest = max(new_deals, key=lambda x: x.get('value_usd') or 0)
             subject = f"🔓 {highest.get('tool_name')} + {len(new_deals)-1} new deals this morning"
             
        html_content = self.builder.build_html(new_deals, updated_deals)
        
        if not self.client:
             print(f"[Dry Run] Would send HTML email to {self.to_email}:")
             print(f"Subject: {subject}")
             print("Content: <HTML output hidden for brevity>")
             return
             
        message = Mail(
            from_email=self.from_email,
            to_emails=self.to_email,
            subject=subject,
            html_content=html_content
        )
        
        # Attachments
        new_csv = self.generate_csv_attachment(new_deals, "new_deals.csv")
        if new_csv:
            message.attachment = new_csv
            
        try:
            response = self.client.send(message)
            print(f"Email sent. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error sending email: {e}")
