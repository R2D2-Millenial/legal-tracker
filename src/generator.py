def build_html_dashboard(updates, week_label):
    cards_html = ""
    for item in updates:
        impact = item.get("impact_level", "Medium")
        
        # Color badges based on impact
        if impact == "High":
            badge_style = "background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca;"
        elif impact == "Low":
            badge_style = "background-color: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe;"
        else:
            badge_style = "background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a;"

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
                    <span class="badge badge-gray">{item.get('authority', 'General')}</span>
                    <span class="badge badge-indigo">{item.get('law_domain', 'General')}</span>
                </div>
                <div class="effective-date">Effective: <strong>{item.get('effective_date', 'Immediate')}</strong></div>
            </div>

            <h2 class="card-title">{item.get('title', '')}</h2>

            <div class="shift-box">
                <div class="section-label">Shift in Legal Position</div>
                <p>{item.get('what_changed', '')}</p>
            </div>

            <div class="action-box">
                <div class="section-label">Legal & In-House Action Items</div>
                <ul>{action_lis}</ul>
            </div>

            <div class="card-footer">
                <span>Sector: <strong>{item.get('sector', 'General')}</strong></span>
                <a href="{item.get('source_url', '#')}" target="_blank" rel="noopener noreferrer">Read Official Source &rarr;</a>
            </div>
        </article>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Juridigm Shift — Regulatory Intelligence | {week_label}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            line-height: 1.5;
            padding: 32px 16px;
        }}
        .container {{
            max-width: 860px;
            margin: 0 auto;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 20px;
            margin-bottom: 24px;
            gap: 16px;
        }}
        .brand-title {{
            font-size: 26px;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: -0.02em;
        }}
        .brand-title span {{
            color: #3b82f6;
        }}
        .subtitle {{
            font-size: 13px;
            color: #64748b;
            margin-top: 4px;
        }}
        .print-btn {{
            background-color: #0f172a;
            color: #ffffff;
            border: none;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            white-space: nowrap;
        }}
        .print-btn:hover {{ background-color: #334155; }}
        .filter-panel {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 24px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }}
        .filter-title {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            color: #64748b;
            margin-bottom: 10px;
            letter-spacing: 0.05em;
        }}
        .filter-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        select, .reset-btn {{
            font-size: 13px;
            padding: 8px 12px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            background-color: #ffffff;
            color: #1e293b;
            outline: none;
        }}
        .reset-btn {{
            background-color: #f1f5f9;
            cursor: pointer;
            font-weight: 500;
        }}
        .reset-btn:hover {{ background-color: #e2e8f0; }}
        .update-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }}
        .card-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
        }}
        .meta-tags {{
            display: flex;
            gap: 6px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .badge {{
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}
        .badge-gray {{ background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }}
        .badge-indigo {{ background: #e0e7ff; color: #3730a3; border: 1px solid #c7d2fe; }}
        .effective-date {{
            font-size: 12px;
            color: #64748b;
        }}
        .card-title {{
            font-size: 17px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 14px;
            line-height: 1.35;
        }}
        .shift-box {{
            background: #f8fafc;
            border-left: 3px solid #cbd5e1;
            padding: 12px 14px;
            border-radius: 0 6px 6px 0;
            margin-bottom: 16px;
        }}
        .shift-box p {{
            font-size: 13.5px;
            color: #334155;
        }}
        .section-label {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #475569;
            margin-bottom: 4px;
        }}
        .action-box {{ margin-bottom: 16px; }}
        .action-box ul {{
            list-style-type: disc;
            padding-left: 20px;
            margin-top: 6px;
        }}
        .action-box li {{
            font-size: 13.5px;
            color: #1e293b;
            margin-bottom: 4px;
        }}
        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #f1f5f9;
            padding-top: 12px;
            font-size: 12px;
            color: #64748b;
        }}
        .card-footer a {{
            color: #2563eb;
            text-decoration: none;
            font-weight: 600;
        }}
        .card-footer a:hover {{ text-decoration: underline; }}
        @media print {{
            .no-print {{ display: none !important; }}
            body {{ background: #fff; padding: 0; }}
            .update-card {{ break-inside: avoid; border: 1px solid #94a3b8; box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1 class="brand-title">Juridigm <span>Shift</span></h1>
                <p class="subtitle">Weekly In-House Regulatory & Tech Intelligence | {week_label}</p>
            </div>
            <button class="print-btn no-print" onclick="window.print()">Export / Print as PDF</button>
        </header>

        <section class="filter-panel no-print">
            <div class="filter-title">Filter Intelligence Feed</div>
            <div class="filter-row">
                <select id="impactFilter" onchange="applyFilters()">
                    <option value="ALL">All Impact Levels</option>
                    <option value="High">High Impact</option>
                    <option value="Medium">Medium Impact</option>
                    <option value="Low">Low Impact</option>
                </select>
                <select id="domainFilter" onchange="applyFilters()">
                    <option value="ALL">All Legal Domains</option>
                    <option value="Data Privacy & DPDP">Data Privacy & DPDP</option>
                    <option value="AI & Emerging Tech">AI & Emerging Tech</option>
                    <option value="Corporate">Corporate / MCA</option>
                    <option value="Securities">Securities / SEBI</option>
                    <option value="Employment & Labour">Labour & Employment</option>
                    <option value="Foreign Exchange">RBI / FEMA</option>
                </select>
                <button class="reset-btn" onclick="resetFilters()">Reset</button>
            </div>
        </section>

        <main id="cardsContainer">
            {cards_html}
        </main>
    </div>

    <script>
        function applyFilters() {{
            const impact = document.getElementById('impactFilter').value;
            const domain = document.getElementById('domainFilter').value;
            const cards = document.querySelectorAll('.update-card');

            cards.forEach(card => {{
                const cardImpact = card.getAttribute('data-impact');
                const cardDomain = card.getAttribute('data-domain');
                const matchesImpact = impact === 'ALL' || cardImpact === impact;
                const matchesDomain = domain === 'ALL' || cardDomain.includes(domain);
                card.style.display = (matchesImpact && matchesDomain) ? 'block' : 'none';
            }});
        }}

        function resetFilters() {{
            document.getElementById('impactFilter').value = 'ALL';
            document.getElementById('domainFilter').value = 'ALL';
            applyFilters();
        }}
    </script>
</body>
</html>"""
    return html
