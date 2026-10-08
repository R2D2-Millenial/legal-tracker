import smtplib
import ssl
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_executive_email(updates, week_label, portal_url):
    sender = os.environ.get("GMAIL_USER", "").strip()
    app_password = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "").strip()
    recipients_raw = os.environ.get("RECIPIENT_EMAILS", "").strip()
    recipients = [e.strip() for e in recipients_raw.split(",") if e.strip()]

    if not sender or not app_password or not recipients:
        print("Notice: Email credentials missing in GitHub Secrets. Skipping email dispatch.")
        return

    # Categorize items
    high_impact = [u for u in updates if u.get("impact_level") == "High"]
    medium_impact = [u for u in updates if u.get("impact_level") == "Medium"]

    if high_impact:
        featured_items = high_impact
        section_title = f"High-Impact Developments This Week ({len(high_impact)}):"
        border_color = "#b91c1c"
        subject = f"Executive Legal Digest: {len(high_impact)} High-Impact Updates ({week_label})"
    elif medium_impact:
        featured_items = medium_impact[:3]
        section_title = "Routine Compliance Updates This Week:"
        border_color = "#d97706"
        subject = f"Executive Legal Digest: Routine Compliance Digest ({week_label})"
    else:
        featured_items = updates[:3]
        section_title = "Regulatory & Procedural Briefings:"
        border_color = "#2563eb"
        subject = f"Executive Legal Digest: Regulatory Brief ({week_label})"

    items_summary = ""
    for item in featured_items:
        actions = item.get("inhouse_action_items", [])
        action_text = actions[0] if actions else "Review circular."
        items_summary += f"""
        <div style="border-left: 4px solid {border_color}; padding-left: 12px; margin-bottom: 18px;">
            <p style="margin: 0; font-size: 11px; font-weight: bold; color: {border_color}; text-transform: uppercase;">
                [{item.get('authority', 'General')}] {item.get('law_domain', 'Regulatory')} &bull; {item.get('impact_level', 'Routine')} Impact
            </p>
            <h3 style="margin: 4px 0 6px 0; font-size: 15px; color: #111827;">{item.get('title', 'Notification')}</h3>
            <p style="margin: 0 0 6px 0; font-size: 13px; color: #374151;"><strong>Shift:</strong> {item.get('what_changed', '')}</p>
            <p style="margin: 0; font-size: 13px; color: #1e40af;"><strong>Action:</strong> {action_text}</p>
        </div>
        """

    remaining_count = max(0, len(updates) - len(featured_items))
    remaining_text = f"+ {remaining_count} additional notifications tracked." if remaining_count > 0 else "All updates listed above."

    html_body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1f2937; line-height: 1.5; max-width: 600px; margin: auto; padding: 20px;">
        <h2 style="color: #0f172a; margin-bottom: 4px;">In-House Legal Intelligence — {week_label}</h2>
        <p style="color: #64748b; font-size: 13px; margin-top: 0;">Weekly Briefing for Counsel</p>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 16px 0;" />
        <h3 style="color: #0f172a; font-size: 14px; text-transform: uppercase;">{section_title}</h3>
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

    # Safe sender: Try Port 465 (SSL), then Port 587 (TLS), but never crash the website deployment
    context = ssl.create_default_context()
    sent = False

    # Attempt 1: Port 465 (Implicit SSL)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=20) as server:
            server.login(sender, app_password)
            server.sendmail(sender, recipients, msg.as_string())
            print("Executive Digest email sent successfully via SSL (465)!")
            sent = True
    except Exception as e1:
        print(f"Port 465 attempt encountered: {e1}")

    # Attempt 2: Port 587 (STARTTLS)
    if not sent:
        try:
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(sender, app_password)
                server.sendmail(sender, recipients, msg.as_string())
                print("Executive Digest email sent successfully via STARTTLS (587)!")
                sent = True
        except Exception as e2:
            print(f"Port 587 attempt encountered: {e2}")

    if not sent:
        print("\n" + "="*50)
        print("WARNING: Email could not be dispatched because Gmail rejected the login.")
        print("Common cause: Check GMAIL_USER and GMAIL_APP_PASSWORD in GitHub Secrets.")
        print("The website dashboard will still deploy successfully.")
        print("="*50 + "\n")
