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
            color: #0a192f;
        }}
        .update-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 22px;
            box-shadow: 0 2px 4px rgba(10, 25, 47, 0.04);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .update-card:hover {{
            box-shadow: 0 4px 12px rgba(10, 25, 47, 0.08);
        }}
        .card-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 14px;
        }}
        .meta-tags {{
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .badge {{
            font-size: 11px;
            font-weight: 700;
            padding: 2.5px 9px;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}
        .badge-authority {{
            background: #eff6ff;
            color: #1e3a8a;
            border: 1px solid #bfdbfe;
        }}
        .badge-domain {{
            background: #eef2ff;
            color: #3730a3;
            border: 1px solid #c7d2fe;
        }}
        .effective-date {{
            font-size: 12px;
            color: #64748b;
        }}
        .card-title {{
            font-size: 18px;
            font-weight: 700;
            color: #0a192f;
            margin-bottom: 14px;
            line-height: 1.35;
        }}
        .shift-box {{
            background: #fdfcf7;
            border-left: 3.5px solid #c59b27;
            padding: 12px 16px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 16px;
        }}
        .shift-box p {{
            font-size: 13.5px;
            color: #334155;
            line-height: 1.5;
        }}
        .section-label-gold {{
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #b48316;
            margin-bottom: 4px;
        }}
        .section-label-navy {{
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #0a192f;
            margin-bottom: 6px;
        }}
        .action-box {{
            margin-bottom: 16px;
        }}
        .action-box ul {{
            list-style-type: disc;
            padding-left: 20px;
        }}
        .action-box li {{
            font-size: 13.5px;
            color: #1e293b;
            margin-bottom: 5px;
        }}
        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #f1f5f9;
            padding-top: 14px;
            font-size: 12px;
            color: #64748b;
        }}
        .card-footer strong {{
            color: #0a192f;
        }}
        .card-footer a {{
            color: #1d4ed8;
            text-decoration: none;
            font-weight: 600;
        }}
        .card-footer a:hover {{
            color: #c59b27;
            text-decoration: underline;
        }}
        @media print {{
            .no-print {{ display: none !important; }}
            body {{ background: #fff; padding: 0; }}
            .update-card {{ break-inside: avoid; border: 1px solid #94a3b8; box-shadow: none; margin-bottom: 20px; }}
            .shift-box {{ border-left-color: #000; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1 class="brand-title">Juridigm <span>Shift</span></h1>
                <p class="subtitle">In-House Regulatory, Privacy & AI Intelligence Briefing | {week_label}</p>
            </div>
            <button class="print-btn no-print" onclick="window.print()">Export / Print as PDF</button>
        </header>

        <section class="filter-panel no-print">
            <div class="filter-title">Filter Updates by Risk & Domain</div>
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
                <button class="reset-btn" onclick="resetFilters()">Reset Filters</button>
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
