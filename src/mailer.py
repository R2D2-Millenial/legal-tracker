import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_executive_email(updates, week_label, portal_url):
    sender = os.environ["GMAIL_USER"].strip()
    app_password = os.environ["GMAIL_APP_PASSWORD"].replace(" ", "").strip()
    recipients = [e.strip() for e in os.environ["RECIPIENT_EMAILS"].split(",") if e.strip()]

    # Separate items by impact
    high_impact = [u for u in updates if u.get("impact_level") == "High"]
    medium_impact = [u for u in updates if u.get("impact_level") == "Medium"]

    # --- SLOW WEEK FALLBACK LOGIC ---
    if high_impact:
        # Standard week: feature high impact items
        featured_items = high_impact
        section_title = f"High-Impact Developments This Week ({len(high_impact)}):"
        border_color = "#b91c1c"  # Red
        subject = f"Executive Legal Digest: {len(high_impact)} High-Impact Updates ({week_label})"
    elif medium_impact:
        # Slow week: feature up to 3 medium updates so the email remains valuable
        featured_items = medium_impact[:3]
        section_title = "No Critical High-Impact Alerts This Week — Key Compliance Updates:"
        border_color = "#d97706"  # Amber
        subject = f"Executive Legal Digest: Routine Compliance Digest ({week_label})"
    elif updates:
        # Very quiet week: feature whatever low-impact notices exist
        featured_items = updates[:3]
        section_title = "Quiet Week — Routine Procedural Notifications:"
        border_color = "#2563eb"  # Blue
        subject = f"Executive Legal Digest: Routine Regulatory Brief ({week_label})"
    else:
        # Total downtime (court vacations/holidays with 0 items parsed)
        featured_items = []
        section_title = "No New Regulatory Circulars Notified This Week"
        border_color = "#64748b"  # Gray
        subject = f"Executive Legal Digest: Weekly Status Report ({week_label})"

    # Build the card HTML
    items_summary = ""
    for item in featured_items:
        actions = item.get("inhouse_action_items", [])
        action_text = actions[0] if actions else "Monitor circular on portal."
        items_summary += f"""
        <div style="border-left: 4px solid {border_color}; padding-left: 12px; margin-bottom: 18px;">
            <p style="margin: 0; font-size: 11px; font-weight: bold; color: {border_color}; text-transform: uppercase;">
                [{item.get('authority', 'General')}] {item.get('law_domain', 'Regulatory')} &bull; {item.get('impact_level', 'Routine')} Impact
            </p>
            <h3 style="margin: 4px 0 6px 0; font-size: 15px; color: #111827;">{item.get('title', 'Notification')}</h3>
            <p style="margin: 0 0 6px 0; font-size: 13px; color: #374151;"><strong>Shift:</strong> {item.get('what_changed', 'Routine procedural circular.')}</p>
            <p style="margin: 0; font-size: 13px; color: #1e40af;"><strong>Action:</strong> {action_text}</p>
        </div>
        """

    # If literally zero items were captured across all feeds
    if not items_summary:
        items_summary = """
        <div style="background-color: #f8fafc; border: 1px dashed #cbd5e1; padding: 16px; border-radius: 8px; text-align: center;">
            <p style="margin: 0; font-size: 13px; color: #64748b;">All tracked regulatory bodies and courts remained in routine session with no material disruptions published.</p>
        </div>
        """

    remaining_count = max(0, len(updates) - len(featured_items))
    remaining_text = f"+ {remaining_count} additional routine notifications tracked." if remaining_count > 0 else "All circulars displayed above."

    html_body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1f2937; line-height: 1.5; max-width: 600px; margin: auto; padding: 20px;">
        <h2 style="color: #0f172a; margin-bottom: 4px;">In-House Legal Intelligence — {week_label}</h2>
        <p style="color: #64748b; font-size: 13px; margin-top: 0;">Weekly Regulatory Briefing for In-House Counsel</p>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 16px 0;" />
        
        <h3 style="color: #0f172a; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">{section_title}</h3>
        {items_summary}

        <p style="font-size: 13px; color: #475569;">{remaining_text}</p>

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
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))

    # Connect via Port 587 + STARTTLS
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
    try:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender, app_password)
        server.sendmail(sender, recipients, msg.as_string())
    finally:
        server.quit()
