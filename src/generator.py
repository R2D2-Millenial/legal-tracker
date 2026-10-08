def build_html_dashboard(updates, week_label):
    cards_html = ""
    for item in updates:
        impact = item.get("impact_level", "Medium")
        
        # Color badges based on impact
        if impact == "High":
            badge_style = "background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca;"
        elif impact == "Low":
            badge_style = "background-color: #f0fdf4; color: #166534; border: 1px solid #bbf7d0;"
        else:
            badge_style = "background-color: #fefce8; color: #854d0e; border: 1px solid #fef08a;"

        # Clean up double bullets from AI output
        action_lis = ""
        for act in item.get("inhouse_action_items", []):
            clean_act = act.lstrip("•-* ").strip()
            action_lis += f"<li>{clean_act}</li>"

        cards_html += f"""
        <article class="update-card"
                 data-authority="{item.get('authority', '')}"
                 data-domain="{item.get('law_domain', '')}"
                 data-impact="{impact}">
            <div class="card-meta">
                <div class="meta-tags">
                    <span class="badge" style="{badge_style}">{impact} Impact</span>
                    <span class="badge badge-authority">{item.get('authority', 'General')}</span>
                    <span class="badge badge-domain">{item.get('law_domain', 'General')}</span>
                </div>
                <div class="effective-date">Effective: <strong>{item.get('effective_date', 'Immediate')}</strong></div>
            </div>

            <h2 class="card-title">{item.get('title', '')}</h2>

            <div class="shift-box">
                <div class="section-label-gold">Shift in Legal Position</div>
                <p>{item.get('what_changed', '')}</p>
            </div>

            <div class="action-box">
                <div class="section-label-navy">In-House Counsel Action Items</div>
                <ul>{action_lis}</ul>
            </div>

            <div class="card-footer">
                <span>Sector: <strong>{item.get('sector', 'General')}</strong></span>
                <a href="{item.get('source_url', '#')}" target="_blank" rel="noopener noreferrer">Read Primary Gazette / Source &rarr;</a>
            </div>
        </article>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Juridigm Shift — Regulatory Intelligence Hub | {week_label}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f8fafc;
            color: #0f172a;
            line-height: 1.55;
            padding: 36px 16px;
        }}
        .container {{
            max-width: 880px;
            margin: 0 auto;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 22px;
            margin-bottom: 24px;
            gap: 16px;
        }}
        .brand-title {{
            font-size: 28px;
            font-weight: 800;
            color: #0a192f;
            letter-spacing: -0.025em;
        }}
        .brand-title span {{
            color: #c59b27;
        }}
        .subtitle {{
            font-size: 13px;
            color: #475569;
            margin-top: 5px;
            font-weight: 500;
        }}
        .print-btn {{
            background-color: #0a192f;
            color: #fef08a;
            border: 1px solid #c59b27;
            padding: 9px 18px;
            font-size: 12px;
            font-weight: 600;
            border-radius: 7px;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s ease;
        }}
        .print-btn:hover {{
            background-color: #1e3a8a;
            color: #ffffff;
        }}
        .filter-panel {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-top: 3px solid #0a192f;
            border-radius: 10px;
            padding: 16px 20px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(10, 25, 47, 0.05);
        }}
        .filter-title {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            color: #64748b;
            margin-bottom: 12px;
            letter-spacing: 0.06em;
        }}
        .filter-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }}
        select, .reset-btn {{
            font-size: 13px;
            padding: 8px 12px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            background-color: #ffffff;
            color: #0a192f;
            outline: none;
        }}
        select:focus {{
            border-color: #c59b27;
        }}
        .reset-btn {{
            background-color: #f8fafc;
            color: #475569;
            cursor: pointer;
            font-weight: 500;
        }}
        .reset-btn:hover {{
            background-color: #e2e8f0;
