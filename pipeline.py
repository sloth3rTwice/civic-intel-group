import os
import requests
import google.generativeai as genai
from weasyprint import HTML
import resend
import stripe
from datetime import datetime

# Initialize APIs from GitHub Secrets
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
resend.api_key = os.environ["RESEND_API_KEY"]
stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
STRIPE_PAYMENT_LINK = os.environ["STRIPE_PAYMENT_LINK"]

TARGET_ZIPS = ["77459", "77584", "77583", "77578", "77581", "77047"]

def fetch_municipal_data():
    print("Fetching daily municipal records...")
    return [{"address": "Sample Address, Manvel TX 77578", "issue": "Roof Damage / Code Violation", "date": "2026-11-08"}]

def generate_ai_brief(records):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Format these municipal property records into a professional 1-page lead brief for B2B contractors. Highlight high-income residential areas. Records: {records}"
    response = model.generate_content(prompt)
    return response.text

def create_pdf(brief_content):
    date_str = datetime.now().strftime("%Y-%m-%d")
    html_content = f"""
    <html>
        <head><style>body {{ font-family: Arial; padding: 20px; }} h1 {{ color: #2c3e50; }}</style></head>
        <body>
            <h1>Civic Intel Group - Daily Property Brief</h1>
            <p><strong>Date:</strong> {date_str}</p>
            <div>{brief_content}</div>
            <hr>
            <p>Access full owner contact details via your dashboard.</p>
        </body>
    </html>
    """
    pdf_path = f"/tmp/lead_brief_{date_str}.pdf"
    HTML(string=html_content).write_pdf(pdf_path)
    return pdf_path

def dispatch_leads(pdf_path):
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    params = {
        "from": "leads@civicintelgroup.com",
        "to": ["Doug.bain99@gmail.com"],
        "subject": f"New High-Income Property Leads - {datetime.now().strftime('%b %d')}",
        "html": f"<p>Your daily property brief is attached. To unlock the owner contact data and phone numbers, complete your daily access fee here: <a href='{STRIPE_PAYMENT_LINK}'>Unlock Leads ($35)</a></p>",
        "attachments": [{"filename": "daily_brief.pdf", "content": list(pdf_bytes)}]
    }
    email = resend.Emails.send(params)
    print(f"Dispatched: {email}")

if __name__ == "__main__":
    records = fetch_municipal_data()
    if records:
        brief = generate_ai_brief(records)
        pdf = create_pdf(brief)
        dispatch_leads(pdf)
        print("Pipeline execution complete.")
