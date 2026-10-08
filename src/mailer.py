import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_executive_email(updates, week_label, portal_url):
    sender = os.environ["GMAIL_USER"]
    recipients = [e.strip() for e in os.environ["RECIPIENT_EMAILS"].split(",") if e.strip()]
    app_password = os.environ["GMAIL_APP_PASSWORD"]

    # Filter High-Impact for the digest highlights
    high_impact = [u for u in updates if u.get("impact_level") == "High"]
    other_count = len(updates) - len(high_impact)

    items_summary = ""
    for item in high_impact:
        items_summary += f"""
        <div style="border-left: 4px solid #b91c1c; padding-left: 12px; margin-bottom: 18px;">
            <p style="margin: 0; font-size: 11px; font-weight: bold; color: #b91c1c; text-transform: uppercase;">
                [{item['authority']}] {item['law_domain']}
            </p>
            <h3 style="margin: 4px 0 6px 0; font-size: 15px; color: #111827;">{item['title']}</h3>
            <p style="margin: 0 0 6px 0; font-size: 13px; color: #374151;"><strong>Shift:</strong> {item['what_changed']}</p>
            <p style="margin: 0; font-size: 13px; color: #1e40af;"><strong>Action:</strong> {item['inhouse_action_items'][0] if item['inhouse_action_items'] else 'Monitor notifications'}</p>
        </div>
        """

    html_body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1f2937; line-height: 1.5; max-width: 600px; margin: auto; padding: 20px;">
        <h2 style="color: #0f172a; margin-bottom: 4px;">In-House Legal Intelligence — {week_label}</h2>
        <p style="color: #64748b; font-size: 13px; margin-top: 0;">Weekly Executive Digest for Counsel</p>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 16px 0;" />
        
        <h3 style="color: #0f172a; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">High-Impact Developments This Week:</h3>
        {items_summary}

        <p style="font-size: 13px; color: #475569;">+ {other_count} additional medium/low regulatory notifications tracked.</p>

        <div style="margin-top: 24px; text-align: center;">
            <a href="{portal_url}" style="background-color: #0f172a; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-size: 13px; font-weight: 600; display: inline-block;">
                Open Full Web Dashboard & Filters &rarr;
            </a>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = f"Legal Intelligence <{sender}>"
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = f"Executive Legal Digest: {len(high_impact)} High-Impact Regulatory Updates ({week_label})"
    msg.attach(MIMEText(html_body, 'html'))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, app_password)
        server.sendmail(sender, recipients, msg.as_string())
